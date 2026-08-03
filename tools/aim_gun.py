#!/usr/bin/env python3
"""Point an armed gun at something, one aim key per shot fired.

`fire_rig.py` says WHEN a gun fires; this says WHERE it is pointing when it
does, and `gunfire.py` then bakes what the rounds hit. Aim is driven through a
TRACK_TO on an empty rather than by keying the gun's rotation, so the gun keeps
whatever mount and recoil animation it already has and only its facing changes.

Two modes, which are the two things gunfire needs to do:

  --mode=targets   step across named objects, one per shot. Hitting what you
                   are shooting at is otherwise surprisingly unlikely: the
                   boy's target practice missed 5 of 5 in sq040_sh050 because
                   his rounds threaded the gaps between figures.

  --mode=trail     walk the ground behind a moving object. Rounds land where
                   it WAS `--lag` frames ago, so the impacts chase it. This is
                   the near-miss spray that drives someone into a run.

Aim keys land a few frames BEFORE each shot so the gun has settled by the time
the muzzle flash opens.

Run (Blender must be CLOSED — this writes layout/layout.blend):

  "$BLENDER" --background --python-exit-code 1 --python tools/aim_gun.py -- \
      --scene=sq060_sh010 --ctrl=mg_ctrl.004 --mode=trail --follow=boy.016 \
      [--lag=16] [--spread=0.8] [--z=0.02] [--hold=2] \
      [--at=3085:8.6,9.0,1.8] [--at=3109:8.6,11.4,1.9] [--dry-run]

  "$BLENDER" --background --python-exit-code 1 --python tools/aim_gun.py -- \
      --scene=sq040_sh050 --ctrl=mg_ctrl.002 --mode=targets \
      --targets=action_figure.018,action_figure.019 [--part-z=1.2]
"""
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shotlib

LEAD = 4          # frames before the shot that the aim key is set
LAG = 16          # trail mode: how far behind the runner the rounds land
SPREAD = 0.8      # trail mode: side-to-side wander of the walking spray
GROUND_Z = 0.02   # trail mode: aim just above the turf, not into it


def fire_frames(ctrl, f0, f1):
    """Frames where this gun's `fire` control goes off (sampled, see gunfire)."""
    scene = bpy.context.scene
    out, was_hot = [], False
    for f in range(int(f0), int(f1) + 1):
        scene.frame_set(f)
        hot = ctrl.get("fire", 0.0) > 0.5
        if hot and not was_hot:
            out.append(f)
        was_hot = hot
    return out


def aim_empty(scene, ctrl):
    """The empty this gun tracks — reuse its TRACK_TO target if it has one."""
    for c in ctrl.constraints:
        if c.type == "TRACK_TO" and c.target is not None:
            return c.target, False
    ob = bpy.data.objects.new(f"{ctrl.name}_aim", None)
    ob.empty_display_type = "SPHERE"
    ob.empty_display_size = 0.25
    coll = bpy.data.collections.get(f"{scene.name}_blocking") or scene.collection
    coll.objects.link(ob)
    con = ctrl.constraints.new("TRACK_TO")
    con.target = ob
    # guns fire along local +X, and TRACK_TO overrides rotation only — the
    # mount transform and any recoil on location survive untouched
    con.track_axis = "TRACK_X"
    con.up_axis = "UP_Z"
    return ob, True


def to_parent_space(ob, world_point):
    """The .location that puts `ob` at `world_point` right now."""
    if ob.parent is None:
        return world_point.copy()
    return (ob.parent.matrix_world @ ob.matrix_parent_inverse).inverted() \
        @ world_point


def world_centre(ob, part_z=None):
    """A point `part_z` up the target, in the TARGET's own space.

    Not `matrix_world.translation.z + part_z`: a figure that has been knocked
    over still has its origin on the ground, so a world-Z offset aims into
    thin air above it. Measured — 3 of the boy's 7 rounds missed that way, and
    they were exactly the shots aimed at the two rotated figures.
    """
    return ob.matrix_world @ Vector((0.0, 0.0, part_z or 0.0))


def trail_points(scene, follow, frames, lag, spread, ground_z):
    """Where each round lands: the runner's own path, `lag` frames stale.

    Sampled from the runner rather than offset from its current position, so
    the spray follows the actual route including the dive, and the impacts
    read as chasing rather than as leading.
    """
    path = {}
    for f in range(scene.frame_start, scene.frame_end + 1):
        scene.frame_set(f)
        path[f] = follow.matrix_world.translation.copy()
    out = []
    for i, f in enumerate(frames):
        src = path[max(scene.frame_start, f - lag)]
        # alternate which side of the track the round lands, so a burst reads
        # as a spray walking up behind someone instead of a dotted line
        side = spread * (1.0 if i % 2 == 0 else -1.0) * (0.5 + 0.5 * (i % 3))
        out.append(Vector((src.x + side, src.y, ground_z)))
    return out


def run(scene_name, ctrl_name, mode, targets, follow_name, lag, spread,
        ground_z, part_z, hold, overrides, dry_run):
    root = shotlib.project_root()
    bpy.ops.wm.open_mainfile(filepath=str(root / "layout" / "layout.blend"))
    scene = bpy.data.scenes.get(scene_name)
    if scene is None:
        sys.exit(f"error: no scene {scene_name!r}")
    bpy.context.window.scene = scene
    ctrl = scene.objects.get(ctrl_name)
    if ctrl is None:
        sys.exit(f"error: no object {ctrl_name!r} in {scene_name}")
    if "fire" not in ctrl:
        sys.exit(f"error: {ctrl_name!r} is not an armed gun (no `fire`)")

    frames = fire_frames(ctrl, scene.frame_start, scene.frame_end)
    if not frames:
        sys.exit(f"error: {ctrl_name!r} never fires in {scene_name}")

    if mode == "targets":
        obs = []
        for nm in targets:
            ob = scene.objects.get(nm)
            if ob is None:
                sys.exit(f"error: no target {nm!r} in {scene_name}")
            obs.append(ob)
        points = []
        for i, f in enumerate(frames):
            scene.frame_set(f)
            points.append(world_centre(obs[i % len(obs)], part_z))
    else:
        follow = scene.objects.get(follow_name)
        if follow is None:
            sys.exit(f"error: no object {follow_name!r} in {scene_name}")
        points = trail_points(scene, follow, frames, lag, spread, ground_z)

    for f, xyz in overrides.items():
        if f in frames:
            points[frames.index(f)] = Vector(xyz)
        else:
            print(f"  warning: --at={f} is not a fire frame; ignored "
                  f"(fires at {frames})")

    for f, p in zip(frames, points):
        print(f"  f{f:5d} aim ({p.x:6.2f},{p.y:6.2f},{p.z:5.2f})")
    if dry_run:
        print(f"--dry-run: {len(frames)} aim key(s), no save")
        return

    target_ob, created = aim_empty(scene, ctrl)
    if target_ob.animation_data and target_ob.animation_data.action:
        target_ob.animation_data_clear()

    for f, p in zip(frames, points):
        # settle before the shot, hold through it. Both keys are solved
        # separately in the PARENT's frame: aim empties are often parented to
        # the thing being shot at (boy_aim hangs off boy.016), so writing a
        # world point straight into .location puts the aim wherever the parent
        # happens to be — measured 8 m off, and the whole spray landed in the
        # wrong half of the yard.
        for kf in (max(scene.frame_start, f - LEAD), f + hold):
            scene.frame_set(kf)
            target_ob.location = to_parent_space(target_ob, p)
            target_ob.keyframe_insert("location", frame=kf)

    bpy.ops.wm.save_mainfile()
    print(f"aimed {ctrl_name} at {len(frames)} point(s) via "
          f"{target_ob.name}{' (created)' if created else ''}")


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    o = {"scene": None, "ctrl": None, "mode": "targets", "follow": None,
         "lag": LAG, "spread": SPREAD, "z": GROUND_Z, "part-z": 1.2,
         "hold": 2}
    targets, overrides = [], {}
    for a in argv:
        if a.startswith("--targets="):
            targets = [s for s in a.split("=", 1)[1].split(",") if s]
        elif a.startswith("--at="):
            spec = a.split("=", 1)[1]
            fr, _, xyz = spec.partition(":")
            overrides[int(fr)] = tuple(float(v) for v in xyz.split(","))
        elif a.startswith("--"):
            k, _, v = a[2:].partition("=")
            if k in o and v:
                o[k] = type(o[k])(v) if isinstance(o[k], (int, float)) else v
    if not o["scene"] or not o["ctrl"]:
        sys.exit("usage: --scene=<scene> --ctrl=<gun_ctrl> "
                 "--mode=targets --targets=a,b | --mode=trail --follow=<object> "
                 "[--lag=N] [--spread=F] [--z=F] [--part-z=F] [--hold=N] "
                 "[--at=FRAME:x,y,z] [--dry-run]")
    if o["mode"] == "targets" and not targets:
        sys.exit("error: --mode=targets needs --targets=<obj>,<obj>,...")
    if o["mode"] == "trail" and not o["follow"]:
        sys.exit("error: --mode=trail needs --follow=<object>")
    run(o["scene"], o["ctrl"], o["mode"], targets, o["follow"], int(o["lag"]),
        float(o["spread"]), float(o["z"]), float(o["part-z"]), int(o["hold"]),
        overrides, "--dry-run" in argv)


if __name__ == "__main__":
    main()
