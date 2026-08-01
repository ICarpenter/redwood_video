#!/usr/bin/env python3
"""Export one layout scene into its own shot .blend, on demand.

Shot files are a DERIVED EXPORT, not a stage. Most shots never need one: a
layout scene already carries the camera, the blocking, the property, and the
frame range. Export a shot when it earns its own file — a per-shot compositor,
a sim, a 4K re-render, lighting that must not touch its neighbours.

One-way. After export the shot file is authoritative and the layout scene is a
stale reference; this stamps `exported = True` on it so conform_edit says so
instead of silently cutting old blocking.

Run (Blender closed):
  "$BLENDER" --background --python-exit-code 1 \
      --python tools/export_shot.py -- --shot sq010_sh040 [--force]
"""
import argparse
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layoutlib
import shotlib


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--shot", required=True, help="shot code, e.g. sq010_sh040")
    p.add_argument("--force", action="store_true",
                   help="overwrite an existing shot file")
    return p.parse_args(argv)


def export(code, force=False):
    root = shotlib.project_root()
    layout = root / "layout" / "layout.blend"
    if not layout.exists():
        sys.exit(f"error: {layout.relative_to(root)} does not exist")

    shots = {s.code: s for s in shotlib.read_shotlist(root / "docs" / "shotlist.csv")}
    if code not in shots:
        sys.exit(f"error: {code} not found in docs/shotlist.csv")
    shot = shots[code]

    blend = shotlib.shot_blend(shot.sq, shot.sh, root)
    if blend.exists() and not force:
        sys.exit(f"error: {blend.relative_to(root)} exists (use --force)")

    bpy.ops.wm.open_mainfile(filepath=str(layout))
    scene = bpy.data.scenes.get(code)
    if scene is None:
        sys.exit(f"error: no layout scene {code!r}")

    # mark the source BEFORE stripping, so layout.blend keeps the record
    scene["exported"] = True
    bpy.ops.wm.save_mainfile()

    for other in list(bpy.data.scenes):
        if other is not scene:
            bpy.data.scenes.remove(other)

    # renders carry AgX; the layout scene deliberately used Standard
    layoutlib.apply_project_settings(scene, view_transform="AgX")
    # The scene carries a track strip for scrubbing. conform_edit never sees
    # it because it sets scene_input="CAMERA", but render_shot.sh renders the
    # scene directly — and a scene whose sequencer holds only a sound strip
    # renders the SEQUENCER, not the camera, i.e. black frames. Turn it off.
    scene.render.use_sequencer = False
    scene.frame_start = shot.start_frame
    scene.frame_end = shot.end_frame

    # Removing the other 38 scenes unlinks their cameras, papers and notes
    # but does not free them — they survive as zero-user datablocks and ship
    # in the exported file. Measured on sq010_sh040: 120 orphans, 58% of the
    # file's datablocks. Purge before saving.
    bpy.data.orphans_purge(do_local_ids=True, do_linked_ids=False,
                           do_recursive=True)

    blend.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(blend), relative_remap=True)
    print(f"exported {blend.relative_to(root)} "
          f"[{shot.start_frame}-{shot.end_frame}], "
          f"{len(layoutlib.blocking_instances(scene))} blocking instance(s)")
    return blend


def main():
    args = parse_args()
    export(args.shot, force=args.force)


if __name__ == "__main__":
    main()
