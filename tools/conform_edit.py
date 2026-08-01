#!/usr/bin/env python3
"""Build edit/edit.blend from scratch: track on channel 1, one strip per
docs/shotlist.csv row on channel 2 at its song-global position, choosing the
best available tier per shot:

  1. rendered frames (latest render/<code>/vNNN/) -> image strip
  2. layout scene named <code> in layout/layout.blend -> linked scene strip
  3. otherwise -> slug (text strip: shot code + description)

So the edit is watchable at every stage: slugs -> layout -> renders, same
cut throughout.

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
import layoutlib


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    force = "--force" in argv

    root = shotlib.project_root()
    out = root / "edit" / "edit.blend"
    if out.exists() and not force:
        sys.exit(f"error: {out} exists — rebuilding discards manual edit work "
                 "(rerun with -- --force to overwrite)")

    track = shotlib.find_track(root)
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

    shots = shotlib.read_shotlist(root / "docs" / "shotlist.csv")

    # link all available layout scenes (named by shot code) in one pass
    layout_scenes = {}
    layout_blend = root / "layout" / "layout.blend"
    if layout_blend.exists():
        codes = {s.code for s in shots}
        with bpy.data.libraries.load(str(layout_blend), link=True) as (src, dst):
            dst.scenes = [name for name in src.scenes if name in codes]
        # a shot earns its strip once it is drawn OR blocked out. Blocking and
        # paper both render, so the strip shows blocking, a drawing, or a
        # drawing over blocking — whatever the scene actually holds.
        layout_scenes = {sc.name: sc for sc in bpy.data.scenes
                         if sc.library is not None and layoutlib.shot_ready(sc)}
        stale = sorted(name for name, sc in layout_scenes.items()
                       if sc.get("exported"))
        if stale:
            print(f"note: {len(stale)} layout scene(s) already exported to "
                  f"shot files — their blocking may be stale: {', '.join(stale)}")

    counts = {"render": 0, "layout": 0, "slug": 0}
    for shot in shots:
        rdir = shotlib.render_dir(shot.sq, shot.sh, root)
        versions = sorted(d for d in rdir.iterdir()
                          if d.is_dir() and d.name.startswith("v")) \
            if rdir.is_dir() else []
        frames = sorted(versions[-1].glob("*.png")) if versions else []

        if frames:
            strip = strips.new_image(name=f"{shot.code}_{versions[-1].name}",
                                     filepath=str(frames[0]), channel=2,
                                     frame_start=shot.start_frame)
            for f in frames[1:]:
                strip.elements.append(f.name)
            counts["render"] += 1
        elif shot.code in layout_scenes:
            strip = strips.new_scene(name=f"{shot.code}_layout",
                                     scene=layout_scenes[shot.code],
                                     channel=2, frame_start=shot.start_frame)
            strip.frame_final_duration = shot.duration
            # render the layout scene's camera view; its own sequencer (the
            # scrub-audio strip) must not feed the edit
            strip.scene_input = "CAMERA"
            counts["layout"] += 1
        else:
            strip = strips.new_effect(name=f"{shot.code}_slug", type="TEXT",
                                      channel=2, frame_start=shot.start_frame,
                                      length=shot.duration)
            strip.text = f"{shot.code}\n{shot.description}"
            strip.font_size = 56
            strip.wrap_width = 0.8
            counts["slug"] += 1

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
    print(f"conformed edit/edit.blend: track [1-{scene.frame_end}], "
          f"{counts['render']} render / {counts['layout']} layout / "
          f"{counts['slug']} slug strip(s), {marked} section marker(s)")


if __name__ == "__main__":
    main()
