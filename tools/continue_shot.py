#!/usr/bin/env python3
"""Continue one shot from another: snapshot copy-forward of camera + blocking.

Because the property is linked at identity in EVERY layout scene, both scenes
share a world origin — so continuing a shot is a direct world-matrix copy. No
transform math, no relative-space conversion. That is the invariant paying for
itself.

Snapshot semantics, not a live link: the destination is independent from the
moment it is written, so re-blocking the source later never disturbs it.

Run (Blender closed — this writes layout/layout.blend):
  "$BLENDER" --background --python-exit-code 1 \
      --python tools/continue_shot.py -- --from sq010_sh040 --to sq010_sh045 \
      [--at-frame 490] [--force] [--dry-run]
"""
import argparse
import sys
from pathlib import Path

import bpy
from mathutils import Matrix

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layoutlib
import shotlib


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--from", dest="src", required=True, help="source shot code")
    p.add_argument("--to", dest="dst", required=True, help="destination shot code")
    p.add_argument("--at-frame", type=int, default=None,
                   help="frame to read the source at (default: its last frame)")
    p.add_argument("--force", action="store_true",
                   help="also overwrite blocking already present in the destination")
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args(argv)


def snapshot(scene, frame):
    """World matrices of the camera and every blocking instance at `frame`.

    Keyed by instance-collection name, which is stable: instance OBJECTS get
    auto-suffixed (boy.001, box.002) but the collection they instance does not.
    """
    scene.frame_set(frame)
    # matrix_world is identity in --background until a depsgraph evaluation,
    # and camera.matrix_world silently returns garbage rather than erroring.
    # It must be THIS scene's depsgraph: bpy.context.evaluated_depsgraph_get()
    # returns the CONTEXT scene's, and the source scene here is never the
    # context scene — that exact mistake put a camera at the world origin
    # during the migration and nothing raised.
    deps = scene.view_layers[0].depsgraph
    # scene.frame_set() above normally builds this scene's depsgraph (it is
    # None beforehand, for a scene that has never been evaluated at all, and
    # populated after). So this should not be reachable through snapshot()'s
    # own flow — it is defensive insurance in case that ever stops being
    # true, since the alternative is evaluated_get() raising an opaque
    # TypeError instead of anything actionable. A legible refusal costs
    # nothing here.
    if deps is None:
        sys.exit(f"error: scene {scene.name!r} has no evaluated depsgraph — "
                 "it has never been evaluated (a scene created in-memory "
                 "rather than loaded from a file). Cannot read world "
                 "matrices from it.")
    snap = {}
    for ob in layoutlib.blocking_instances(scene):
        m = ob.evaluated_get(deps).matrix_world.copy()
        snap[ob.instance_collection.name] = (tuple(tuple(r) for r in m), None)
    cam = scene.camera
    if cam is not None:
        m = cam.evaluated_get(deps).matrix_world.copy()
        snap["__camera__"] = (tuple(tuple(r) for r in m), cam.data.lens)
    # A degenerate read is indistinguishable from a real one unless checked.
    # If every matrix came back at the origin, the depsgraph did not evaluate
    # and copying this forward would silently plant the destination at 0,0,0.
    if snap and all(Matrix(rows).to_translation().length < 1e-6
                    for rows, _ in snap.values()):
        sys.exit(f"error: {scene.name} evaluated to all-identity matrices at "
                 f"frame {frame} — refusing to copy a degenerate snapshot")
    return snap


def apply_snapshot(scene, snap, force=False):
    """Write a snapshot into `scene`. Returns (created, skipped)."""
    coll = layoutlib.blocking_collection(scene, create=True)
    present = {o.instance_collection.name: o
               for o in layoutlib.blocking_instances(scene)}
    created = skipped = 0

    for name, (rows, _lens) in snap.items():
        if name == "__camera__":
            continue
        m = Matrix(rows)
        existing = present.get(name)
        if existing is not None and not force:
            skipped += 1
            continue
        if existing is not None:
            existing.matrix_world = m
            continue
        linked = next((c for c in bpy.data.collections if c.name == name), None)
        if linked is None:
            print(f"warning: collection {name!r} not linked in this file, skipped")
            continue
        inst = bpy.data.objects.new(name, None)
        inst.instance_type = "COLLECTION"
        inst.instance_collection = linked
        coll.objects.link(inst)
        inst.matrix_world = m
        created += 1

    cam_entry = snap.get("__camera__")
    if cam_entry is not None and scene.camera is not None:
        rows, lens = cam_entry
        scene.camera.matrix_world = Matrix(rows)
        if lens is not None:
            scene.camera.data.lens = lens
        # the paper's fit depends on the lens
        for ob in scene.objects:
            if ob.type in layoutlib.GP_TYPES:
                layoutlib.fit_paper(ob, scene.camera)
    return created, skipped


def main():
    args = parse_args()
    root = shotlib.project_root()
    out = root / "layout" / "layout.blend"
    if not out.exists():
        sys.exit(f"error: {out.relative_to(root)} does not exist; "
                 "run tools/make_layout.py first")
    bpy.ops.wm.open_mainfile(filepath=str(out))

    src = bpy.data.scenes.get(args.src)
    dst = bpy.data.scenes.get(args.dst)
    if src is None:
        sys.exit(f"error: no scene {args.src!r} in layout.blend")
    if dst is None:
        sys.exit(f"error: no scene {args.dst!r} in layout.blend")

    frame = args.at_frame if args.at_frame is not None else src.frame_end
    if not (src.frame_start <= frame <= src.frame_end):
        sys.exit(f"error: frame {frame} outside {args.src} "
                 f"[{src.frame_start}-{src.frame_end}]")

    snap = snapshot(src, frame)
    names = sorted(k for k in snap if k != "__camera__")
    print(f"{args.src} @ {frame}: camera + {len(names)} blocking "
          f"({', '.join(names) or 'none'})")

    if args.dry_run:
        print(f"--dry-run: would continue {args.dst} from this state")
        return

    created, skipped = apply_snapshot(dst, snap, force=args.force)
    bpy.ops.wm.save_mainfile()
    print(f"continue_shot: {args.dst} created {created}, skipped {skipped}"
          f"{' (use --force to overwrite)' if skipped else ''}")


if __name__ == "__main__":
    main()
