#!/usr/bin/env python3
"""Re-point existing board scenes at the shotlist's frame ranges.

make_boards.py only ever ADDS scenes for new shotlist rows — an existing scene
is skipped wholesale, so re-timing a shot in docs/shotlist.csv leaves its board
sitting on the old range. This closes that gap.

docs/shotlist.csv is the source of truth. For every board scene that already
exists, frame_start/frame_end are reset to its row. Frame ranges ONLY: no scene
is created or removed, no Grease Pencil data is touched, no guide is moved.
Scenes with no matching shotlist row are reported and left alone.

Idempotent: a second run reports nothing to do.

Run (Blender must be closed — this writes boards/boards.blend):
  "$BLENDER" --background --factory-startup --python-exit-code 1 \
      --python tools/resync_boards.py [-- --dry-run]
"""
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shotlib


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    dry_run = "--dry-run" in argv

    root = shotlib.project_root()
    out = root / "boards" / "boards.blend"
    if not out.exists():
        sys.exit(f"error: {out.relative_to(root)} does not exist; "
                 "run tools/make_boards.py first")

    shots = {s.code: s for s in
             shotlib.read_shotlist(root / "docs" / "shotlist.csv")}
    bpy.ops.wm.open_mainfile(filepath=str(out))

    changed, orphans = [], []
    for scene in bpy.data.scenes:
        shot = shots.get(scene.name)
        if shot is None:
            orphans.append(scene.name)
            continue
        if (scene.frame_start, scene.frame_end) == (shot.start_frame, shot.end_frame):
            continue
        print(f"  {scene.name}: {scene.frame_start}-{scene.frame_end} "
              f"-> {shot.start_frame}-{shot.end_frame}")
        if not dry_run:
            scene.frame_start = shot.start_frame
            scene.frame_end = shot.end_frame
        changed.append(scene.name)

    for name in orphans:
        print(f"  note: scene {name!r} has no shotlist row; left alone")

    if not changed:
        print("boards.blend frame ranges already match the shotlist")
        return
    if dry_run:
        print(f"--dry-run: {len(changed)} scene(s) would be resynced")
        return
    bpy.ops.wm.save_mainfile()
    print(f"resynced {len(changed)} scene(s) in {out.relative_to(root)}")


if __name__ == "__main__":
    main()
