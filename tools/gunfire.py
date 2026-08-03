#!/usr/bin/env python3
"""Connect armed guns to squibs: fire event -> raycast -> impact.

For every frame a gun's fire rig actually fires, this casts a ray out of the
muzzle, finds what it hits, and bakes an impact there that goes off a few
frames later. One command turns a burst of gunfire into damage on whatever was
downrange.

WHY BAKED AND NOT LIVE
----------------------
A live geometry-nodes raycast would have to live on the GUN, so its holes would
travel with the gun instead of sticking to the wall. Baking resolves each hit
once, in world space, and parents the impacts to the thing that was hit — so
they stay put, and they follow that object if it moves.

Re-bake after changing the gun's aim or animation; --force replaces a previous
bake on the same gun.

Raycasting notes, both measured:
  - scene.ray_cast DOES see collection-instance geometry. It returns the source
    object INSIDE the linked collection (e.g. `af_torso`), not the instance, so
    the instancer is recovered by matching the returned instance matrix.
  - a miss is usually real. The boy's rifle in sq060_sh010 passes cleanly
    between two action figures; that is aim, not a broken cast.

Run (Blender must be CLOSED — this writes layout/layout.blend):

  "$BLENDER" --background --python-exit-code 1 \
      --python tools/gunfire.py -- --bake=sq060_sh010:mg_ctrl \
      [--surface=dirt] [--delay=3] [--life=12] [--range=120] \
      [--impulse] [--dry-run] [--force]
"""
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shotlib
import squib

IMPACT_GROUP = "squib_impacts"


def fire_frames(ctrl, f0, f1):
    """Frames where this gun's `fire` control actually goes off.

    Read by sampling rather than by walking fcurves: Blender 5.x uses slotted
    actions, so the curve for a custom property sits behind
    action.layers[].strips[].channelbag(slot), and sampling is both simpler and
    immune to that structure changing.
    """
    scene = bpy.context.scene
    out, was_hot = [], False
    for f in range(int(f0), int(f1) + 1):
        scene.frame_set(f)
        hot = ctrl.get("fire", 0.0) > 0.5
        if hot and not was_hot:
            out.append(f)
        was_hot = hot
    return out


def muzzle_ray(ctrl, dg):
    """(origin, direction) out of the barrel. Guns are authored firing +X."""
    m = ctrl.evaluated_get(dg).matrix_world
    return m.translation.copy(), (m.to_quaternion() @ Vector((1, 0, 0))).normalized()


def instancer_for(scene, matrix, fallback):
    """Recover which collection INSTANCE a ray hit, from its instance matrix."""
    best, best_d = None, 1e9
    for ob in scene.objects:
        if ob.instance_collection is None:
            continue
        d = (ob.matrix_world.translation - matrix.translation).length
        if d < best_d:
            best, best_d = ob, d
    return best if best_d < 0.001 else fallback


def bake(scene_name, ctrl_name, surface, delay, life, max_range, impulse,
         dry_run, force):
    root = shotlib.project_root()
    lay = root / "layout" / "layout.blend"
    bpy.ops.wm.open_mainfile(filepath=str(lay))
    scene = bpy.data.scenes.get(scene_name)
    if scene is None:
        sys.exit(f"error: no scene {scene_name!r}")
    bpy.context.window.scene = scene
    ctrl = scene.objects.get(ctrl_name)
    if ctrl is None:
        sys.exit(f"error: no object {ctrl_name!r} in {scene_name}; arm the gun "
                 "first with tools/fire_rig.py --arm=...")
    if "fire" not in ctrl:
        sys.exit(f"error: {ctrl_name!r} has no `fire` property — not an armed gun")

    events = fire_frames(ctrl, scene.frame_start, scene.frame_end)
    print(f"{scene_name}/{ctrl_name}: {len(events)} shot(s) fired")

    hits, misses = [], 0
    for f in events:
        scene.frame_set(f)
        dg = bpy.context.evaluated_depsgraph_get()
        origin, direction = muzzle_ray(ctrl, dg)
        ok, loc, nrm, _idx, ob, mat = scene.ray_cast(
            dg, origin + direction * 0.35, direction, distance=max_range)
        if not ok:
            misses += 1
            continue
        target = instancer_for(scene, mat, ob)
        hits.append({"frame": f + delay, "point": loc.copy(),
                     "normal": nrm.copy(), "target": target,
                     "dir": direction.copy()})
        print(f"  f{f:5d} -> {target.name:22s} at "
              f"{tuple(round(v, 2) for v in loc)}  (+{delay}f)")
    if misses:
        print(f"  {misses} shot(s) hit nothing within {max_range} m")
    if not hits:
        print("no impacts to bake")
        return
    if dry_run:
        print(f"--dry-run: would bake {len(hits)} impact(s)")
        return

    grp = bpy.data.node_groups.get(IMPACT_GROUP)
    if grp is None:
        with bpy.data.libraries.load(str(root / squib.LIB), link=True) as (src, dst):
            if IMPACT_GROUP not in src.node_groups:
                sys.exit(f"error: {IMPACT_GROUP} not in {squib.LIB}; run "
                         "tools/squib.py -- --install --force")
            dst.node_groups = [IMPACT_GROUP]
        grp = dst.node_groups[0]

    # one impacts object per target, parented to it so holes travel with it
    by_target = {}
    for h in hits:
        by_target.setdefault(h["target"].name, []).append(h)

    coll = bpy.data.collections.get(f"{scene_name}_blocking")
    made = 0
    for tname, group in by_target.items():
        target = scene.objects[tname]
        name = f"impacts_{ctrl_name}_{tname}"
        old = scene.objects.get(name)
        if old is not None:
            if not force:
                print(f"  {name} exists, left alone (use --force)")
                continue
            bpy.data.objects.remove(old, do_unlink=True)

        me = bpy.data.meshes.new(name)
        inv = target.matrix_world.inverted()
        rot = inv.to_3x3()
        me.from_pydata([inv @ h["point"] for h in group], [], [])
        me.update()
        ob = bpy.data.objects.new(name, me)
        (coll or scene.collection).objects.link(ob)
        ob.parent = target
        # points are already in the target's local space, so the parent
        # inverse must stay IDENTITY. Setting it to inv as well applies the
        # inverse twice and parks every impact near the world origin --
        # measured: a hit at (-1.91, 23.18, 0.79) rendered at (0.20, -0.07,
        # 0.78), behind the camera.
        ob.matrix_parent_inverse = Matrix.Identity(4)

        a = me.attributes.new("hit_frame", "FLOAT", "POINT")
        a.data.foreach_set("value", [float(h["frame"]) for h in group])
        b = me.attributes.new("hit_normal", "FLOAT_VECTOR", "POINT")
        flat = []
        for h in group:
            flat.extend((rot @ h["normal"]).normalized())
        b.data.foreach_set("vector", flat)

        mod = ob.modifiers.new("squib_impacts", "NODES")
        mod.node_group = grp
        ids = {s.name: s.identifier for s in grp.interface.items_tree
               if getattr(s, "in_out", None) == "INPUT"}
        mod[ids["Surface"]] = squib.SURFACE_NAMES.index(surface)
        mod[ids["Life"]] = float(life)
        made += 1
        print(f"  baked {len(group)} impact(s) onto {tname} -> {name}")

        if impulse:
            # Recorded, not simulated. A rigid-body sim needs collision bodies
            # the linked property does not have -- measured in sq040_sh044,
            # where a simulated hubcap fell straight through the ground to
            # z=-2.8. So the force is written as data a hand-animated reaction
            # (or a later sim) can read: for each hit, when it lands, where it
            # landed, and which way it was travelling.
            ob["impulse_frames"] = [h["frame"] for h in group]
            ob["impulse_points"] = [c for h in group for c in h["point"]]
            ob["impulse_dirs"] = [c for h in group for c in h["dir"]]
            ob["impulse_target"] = tname

    bpy.ops.wm.save_mainfile()
    print(f"baked {len(hits)} impact(s) across {made} target(s)")


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    spec = None
    surface, delay, life, rng = "dirt", 3, 12.0, 120.0
    for a in argv:
        if a.startswith("--bake="):
            spec = a.split("=", 1)[1]
        elif a.startswith("--surface="):
            surface = a.split("=", 1)[1]
        elif a.startswith("--delay="):
            delay = int(a.split("=", 1)[1])
        elif a.startswith("--life="):
            life = float(a.split("=", 1)[1])
        elif a.startswith("--range="):
            rng = float(a.split("=", 1)[1])
    if not spec or ":" not in spec:
        sys.exit("usage: --bake=<scene>:<gun_ctrl> [--surface=...] [--delay=N] "
                 "[--life=N] [--range=N] [--impulse] [--dry-run] [--force]")
    if surface not in squib.SURFACE_NAMES:
        sys.exit(f"error: surface must be one of {', '.join(squib.SURFACE_NAMES)}")
    sc, ct = spec.split(":", 1)
    bake(sc, ct, surface, delay, life, rng, "--impulse" in argv,
         "--dry-run" in argv, "--force" in argv)


if __name__ == "__main__":
    main()
