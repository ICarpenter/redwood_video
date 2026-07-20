#!/usr/bin/env python3
"""Build edit/edit.blend from scratch: track on channel 1, every rendered
shot's LATEST version as an image strip on channel 2 at its song-global
position.

DESTRUCTIVE: regenerating replaces the whole edit — any hand-cut changes in
an existing edit/edit.blend are lost. It therefore refuses to overwrite
without --force.

Run:
  "$BLENDER" --background --factory-startup --python-exit-code 1 \
      --python tools/conform_edit.py [-- --force]
"""
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shotlib

AUDIO_EXTS = {".wav", ".mp3", ".flac", ".aif", ".aiff"}


def find_track(root: Path):
    track_dir = root / "audio" / "track"
    candidates = sorted(track_dir.iterdir()) if track_dir.is_dir() else []
    for p in candidates:
        if p.suffix.lower() in AUDIO_EXTS:
            return p
    return None


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    force = "--force" in argv

    root = shotlib.project_root()
    out = root / "edit" / "edit.blend"
    if out.exists() and not force:
        sys.exit(f"error: {out} exists — rebuilding discards manual edit work "
                 "(rerun with -- --force to overwrite)")

    track = find_track(root)
    if track is None:
        sys.exit("error: no track in audio/track/ — the edit needs its spine")

    scene = bpy.context.scene
    scene.name = "edit"
    scene.render.fps = 24
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "16"
    # Standard, NOT AgX: shot renders already carry AgX baked in — the edit
    # must pass them through untouched or the transform applies twice
    scene.view_settings.view_transform = "Standard"
    scene.sync_mode = "AUDIO_SYNC"

    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    se = scene.sequence_editor_create()
    strips = se.strips if hasattr(se, "strips") else se.sequences

    snd = strips.new_sound(name="track", filepath=str(track), channel=1,
                           frame_start=1)
    scene.frame_start = 1
    scene.frame_end = int(snd.frame_final_end) - 1

    placed = 0
    render_root = root / "render"
    shot_dirs = sorted(render_root.iterdir()) if render_root.is_dir() else []
    for shot_dir in shot_dirs:
        if not shot_dir.is_dir():
            continue
        versions = sorted(d for d in shot_dir.iterdir()
                          if d.is_dir() and d.name.startswith("v"))
        if not versions:
            continue
        frames = sorted(versions[-1].glob("*.png"))
        if not frames:
            continue
        # frame number of the first rendered file = the shot's start frame
        start = int(frames[0].stem.rsplit("_", 1)[-1])
        strip = strips.new_image(name=f"{shot_dir.name}_{versions[-1].name}",
                                 filepath=str(frames[0]), channel=2,
                                 frame_start=start)
        for f in frames[1:]:
            strip.elements.append(f.name)
        placed += 1

    # song-section markers from docs/sections.csv (if present)
    marked = 0
    sections_csv = root / "docs" / "sections.csv"
    if sections_csv.exists():
        scene.timeline_markers.clear()
        for sec in shotlib.read_sections(sections_csv):
            scene.timeline_markers.new(sec.name, frame=sec.start_frame)
            marked += 1

    out.parent.mkdir(exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out), relative_remap=True)
    print(f"conformed edit/edit.blend: track [1-{scene.frame_end}] "
          f"+ {placed} shot strip(s) + {marked} section marker(s)")


if __name__ == "__main__":
    main()
