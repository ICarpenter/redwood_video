#!/usr/bin/env python3
"""Install the gun fire rig, and arm gun instances in layout scenes.

WHY A CONTROL OBJECT AND NOT A COLLECTION PROPERTY
--------------------------------------------------
A collection custom property cannot be animated: Collections have no
animation_data and keyframe_insert raises "not animatable". A driver reading
one also does not survive being linked. Both measured, not assumed.

An OBJECT's custom property is keyable, and object-to-object drivers remap
correctly through a library override — which is the only way a shot reaches
inside a linked collection at all. So each gun collection carries:

    <p>_ctrl   ["fire"] 0..1     <- the one thing a shot keyframes
      <p>_rig  driven: kick + muzzle rise
        geometry, <p>_flash (scale driven)

Idle is fire=0 and matches the gun exactly as it was before the rig existed.

Run (Blender must be CLOSED for both modes — they write .blend files):

  # add the rig to machine_gun / rosco / big_pistol in props.blend
  "$BLENDER" --background --factory-startup --python-exit-code 1 \
      --python tools/fire_rig.py -- --install

  # override a gun instance in a shot and key a looping burst on it
  "$BLENDER" --background --python-exit-code 1 \
      --python tools/fire_rig.py -- --arm=sq060_sh010:machine_gun.011 \
      [--period=18] [--start=3024] [--end=3350] [--dry-run]

`--arm` is idempotent: a gun already overridden and keyed is reported and
skipped unless --force.
"""
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import guides
import guide_assets
import shotlib

# prefix -> (collection, muzzle_x, muzzle_z, flash_radius, flash_length)
RIGGED_GUNS = {
    "machine_gun": ("mg", 0.705, 0.20, 0.10, 0.22),
    "rosco":       ("ro", 0.12, 0.15, 0.05, 0.11),
    "big_pistol":  ("bp", 0.37, 0.34, 0.07, 0.15),
}

DEFAULT_PERIOD = 18      # frames per shot-cycle; matches the hand-made recoil
FLASH_FRAMES = 2         # how long the flash is open inside each cycle


def install():
    """Add the rig to each gun collection in the hand-maintained props.blend."""
    root = shotlib.project_root()
    path = root / guides.PROPS_FILE
    if not path.exists():
        sys.exit(f"error: {guides.PROPS_FILE} does not exist")
    bpy.ops.wm.open_mainfile(filepath=str(path))

    added, skipped = [], []
    for name, (prefix, mx, mz, fr, fl) in RIGGED_GUNS.items():
        coll = bpy.data.collections.get(name)
        if coll is None:
            sys.exit(f"error: no `{name}` collection in {guides.PROPS_FILE}")
        if guide_assets.fire_rig(coll, prefix, mx, mz, flash_r=fr, flash_len=fl):
            added.append(name)
        else:
            skipped.append(name)

    if added:
        bpy.ops.wm.save_mainfile()
    print(f"fire_rig install: added {added or 'none'}, "
          f"already rigged {skipped or 'none'}")


def _burst_keys(ctrl, start, end, period):
    """Key one flash per `period` frames across [start, end]."""
    prev = bpy.context.preferences.edit.keyframe_new_interpolation_type
    bpy.context.preferences.edit.keyframe_new_interpolation_type = "LINEAR"
    n = 0
    f = start
    while f <= end:
        ctrl["fire"] = 0.0
        ctrl.keyframe_insert('["fire"]', frame=f)
        ctrl["fire"] = 1.0
        ctrl.keyframe_insert('["fire"]', frame=min(f + 1, end))
        ctrl["fire"] = 0.0
        ctrl.keyframe_insert('["fire"]', frame=min(f + 1 + FLASH_FRAMES, end))
        n += 1
        f += period
    ctrl["fire"] = 0.0
    bpy.context.preferences.edit.keyframe_new_interpolation_type = prev
    return n


def _serialise_constraints(ob):
    """Constraints as plain (type, {prop: value}) data.

    Must be plain data, not RNA references: the override DELETES the instance
    empty, and a reference into a freed constraint reads back with type == ""
    which ObjectConstraints.new() rejects. Target pointers are kept as-is —
    they point at other objects, which survive.
    """
    out = []
    for con in ob.constraints:
        data = {}
        for prop in con.bl_rna.properties:
            if prop.is_readonly or prop.identifier in {"rna_type", "type"}:
                continue
            try:
                data[prop.identifier] = getattr(con, prop.identifier)
            except Exception:
                pass
        out.append((con.type, data))
    return out


def _apply_constraints(ob, serialised):
    for ctype, data in serialised:
        con = ob.constraints.new(ctype)
        for key, value in data.items():
            try:
                setattr(con, key, value)
            except Exception:
                pass
    return [c.type for c in ob.constraints]


def _snapshot(inst, frame):
    """Everything the instance empty carries that the override would destroy.

    make_override_library REMOVES the instancing empty and replaces it with the
    overridden hierarchy. Measured: arming sq060_sh010 without this drops the
    rifle's parent (the boy), its TRACK_TO aim, and its mount transform on the
    floor. The mount transform is sampled at `frame` because it is animated —
    the old hand-made recoil lived on the empty's location.
    """
    bpy.context.scene.frame_set(frame)
    return {
        "parent": inst.parent,
        "pinv": inst.matrix_parent_inverse.copy(),
        "loc": tuple(inst.location),
        "rot": tuple(inst.rotation_euler),
        "scale": tuple(inst.scale),
        "rot_mode": inst.rotation_mode,
        "constraints": _serialise_constraints(inst),
        "collections": [c.name for c in inst.users_collection],
    }


def _restore(ctrl, snap):
    """Put the snapshot onto the rig root so it takes over the empty's job."""
    ctrl.rotation_mode = snap["rot_mode"]
    if snap["parent"] is not None:
        ctrl.parent = snap["parent"]
        ctrl.matrix_parent_inverse = snap["pinv"]
    ctrl.location = snap["loc"]
    ctrl.rotation_euler = snap["rot"]
    ctrl.scale = snap["scale"]
    return _apply_constraints(ctrl, snap["constraints"])


def arm(scene_name, inst_name, period, start, end, dry_run, force):
    root = shotlib.project_root()
    out = root / "layout" / "layout.blend"
    bpy.ops.wm.open_mainfile(filepath=str(out))

    scene = bpy.data.scenes.get(scene_name)
    if scene is None:
        sys.exit(f"error: no scene {scene_name!r} in layout/layout.blend")
    bpy.context.window.scene = scene

    inst = scene.objects.get(inst_name)
    if inst is None:
        sys.exit(f"error: no object {inst_name!r} in {scene_name} (already armed?)")
    if inst.instance_collection is None:
        sys.exit(f"error: {inst_name!r} is not a collection instance")
    gun = inst.instance_collection.name
    if gun not in RIGGED_GUNS:
        sys.exit(f"error: {gun!r} has no fire rig; known: "
                 f"{', '.join(sorted(RIGGED_GUNS))}")
    prefix = RIGGED_GUNS[gun][0]

    start = start if start is not None else scene.frame_start
    end = end if end is not None else scene.frame_end

    # Idempotency comes from the INSTANCE still existing: arming deletes it.
    # Do NOT guard on "is there already a <prefix>_ctrl in this scene" — that
    # is true as soon as any gun of the same type is armed, which silently
    # refused to arm the cop's rifle in sq060_sh010 because the boy's was
    # already done.

    print(f"{scene_name}/{inst_name} ({gun}): override + burst every {period}f "
          f"across {start}-{end}")
    if dry_run:
        print("--dry-run: nothing written")
        return

    snap = _snapshot(inst, start)
    print(f"  captured mount: parent={snap['parent'].name if snap['parent'] else None} "
          f"loc={tuple(round(v, 3) for v in snap['loc'])} "
          f"constraints={[c[0] for c in snap['constraints']]}")

    for ob in scene.objects:
        ob.select_set(False)
    bpy.context.view_layer.objects.active = inst
    inst.select_set(True)
    before = {o.name for o in scene.objects}
    res = bpy.ops.object.make_override_library()
    if "FINISHED" not in res:
        sys.exit(f"error: make_override_library returned {res}")
    created = [scene.objects[n] for n in
               ({o.name for o in scene.objects} - before) if n in scene.objects]

    # Scope to the objects THIS override just created. Searching
    # bpy.data.objects instead finds the first mg_ctrl in the file — i.e. a
    # different shot's control — and silently transplants onto it, wrecking
    # both scenes. Hit exactly that.
    ctrl = next((o for o in created
                 if o.name.startswith(f"{prefix}_ctrl") and not o.library), None)
    if ctrl is None:
        sys.exit(f"error: no local {prefix}_ctrl after override — is the rig "
                 "installed? run --install first")

    restored = _restore(ctrl, snap)
    print(f"  transplanted onto {ctrl.name}: constraints={restored}")

    # NOT re-filed into <scene>_blocking: an overridden collection refuses
    # (un)link of its objects — "Could not (un)link the object 'mg_rig'
    # because the collection 'machine_gun' is overridden". They live in the
    # overridden `machine_gun` collection the operator created, which is the
    # correct home for them anyway.

    shots = _burst_keys(ctrl, start, end, period)
    bpy.ops.wm.save_mainfile()
    print(f"armed {ctrl.name}: {shots} muzzle flash(es), "
          f"{len(created)} object(s) overridden")


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    dry_run = "--dry-run" in argv
    force = "--force" in argv
    arm_spec = period = start = end = None
    for a in argv:
        if a.startswith("--arm="):
            arm_spec = a.split("=", 1)[1]
        elif a.startswith("--period="):
            period = int(a.split("=", 1)[1])
        elif a.startswith("--start="):
            start = int(a.split("=", 1)[1])
        elif a.startswith("--end="):
            end = int(a.split("=", 1)[1])

    if "--install" in argv:
        install()
        return
    if arm_spec:
        if ":" not in arm_spec:
            sys.exit("error: --arm=<scene>:<instance>")
        scene_name, inst_name = arm_spec.split(":", 1)
        arm(scene_name, inst_name, period or DEFAULT_PERIOD,
            start, end, dry_run, force)
        return
    sys.exit("usage: --install | --arm=<scene>:<instance> "
             "[--period=N] [--start=N] [--end=N] [--dry-run] [--force]")


if __name__ == "__main__":
    main()
