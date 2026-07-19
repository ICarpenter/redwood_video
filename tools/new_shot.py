"""Create a shot .blend from the open template + its docs/shotlist.csv row.

Run with the template open, headless:
  "$BLENDER" --background tools/shot_template.blend --python-exit-code 1 \
      --python tools/new_shot.py -- --sq 010 --sh 010 [--force]
"""
import argparse
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shotlib

AUDIO_EXTS = {".wav", ".mp3", ".flac", ".aif", ".aiff"}


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sq", required=True)
    p.add_argument("--sh", required=True)
    p.add_argument("--force", action="store_true",
                   help="overwrite an existing shot file")
    return p.parse_args(argv)


def find_track(root: Path):
    track_dir = root / "audio" / "track"
    candidates = sorted(track_dir.iterdir()) if track_dir.is_dir() else []
    for p in candidates:
        if p.suffix.lower() in AUDIO_EXTS:
            return p
    return None


def add_track(scene, track: Path):
    se = scene.sequence_editor or scene.sequence_editor_create()
    # Blender 5.x renamed SequenceEditor.sequences -> .strips
    strips = se.strips if hasattr(se, "strips") else se.sequences
    strips.new_sound(name="track", filepath=str(track), channel=1, frame_start=1)


def link_asset(entry: str, root: Path, scene):
    name = entry.rstrip("/").split("/")[-1]
    path = root / "assets" / entry / f"{name}.blend"
    if not path.exists():
        print(f"warning: asset {entry!r} missing ({path}), skipped")
        return
    with bpy.data.libraries.load(str(path), link=True) as (data_from, data_to):
        if name not in data_from.collections:
            print(f"warning: no collection {name!r} in {path}, skipped")
            return
        data_to.collections = [name]
    for coll in data_to.collections:
        scene.collection.children.link(coll)


def main():
    args = parse_args()
    root = shotlib.project_root()
    shots = {s.code: s for s in shotlib.read_shotlist(root / "docs" / "shotlist.csv")}
    code = shotlib.shot_code(args.sq, args.sh)
    if code not in shots:
        sys.exit(f"error: {code} not found in docs/shotlist.csv")
    shot = shots[code]

    blend = shotlib.shot_blend(args.sq, args.sh, root)
    if blend.exists() and not args.force:
        sys.exit(f"error: {blend} exists (use --force to overwrite)")

    scene = bpy.context.scene
    scene.name = code
    # end before start: frames are song-global and may exceed the template's
    # default range; setting end first avoids any start>end clamping.
    scene.frame_end = shot.end_frame
    scene.frame_start = shot.start_frame

    track = find_track(root)
    if track:
        add_track(scene, track)
    else:
        print("warning: no track in audio/track/ — shot created without audio")

    for entry in shot.assets:
        link_asset(entry, root, scene)

    blend.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(blend), relative_remap=True)
    print(f"created {blend.relative_to(root)} [{shot.start_frame}-{shot.end_frame}]")


if __name__ == "__main__":
    main()
