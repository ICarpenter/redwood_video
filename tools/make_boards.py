#!/usr/bin/env python3
"""Seed boards/boards.blend: one empty Grease Pencil scene per shotlist row.

Scene name = shot code (sqXXX_shXXX); frame range = the shot's song-global
frames; the track sits on each scene's sequencer so drawing happens with
audio scrubbing in context. conform_edit picks a board up automatically once
its Grease Pencil has any keyframe.

Default run ADDS scenes for new shotlist rows and leaves existing scenes
untouched (safe after drawing has begun). --force rebuilds the whole file
from scratch, DESTROYING all drawings.

Run:
  "$BLENDER" --background --factory-startup --python-exit-code 1 \
      --python tools/make_boards.py [-- --force]
"""
import math
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shotlib


def gp_data_collection():
    data = bpy.data
    return data.grease_pencils_v3 if hasattr(data, "grease_pencils_v3") \
        else data.grease_pencils


def paper_world():
    w = bpy.data.worlds.get("paper")
    if w is None:
        w = bpy.data.worlds.new("paper")
        w.color = (1.0, 1.0, 1.0)
        w.use_nodes = True
        bg = w.node_tree.nodes.get("Background")
        if bg is not None:
            bg.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
            bg.inputs["Strength"].default_value = 1.0
    return w


def ink_material():
    mat = bpy.data.materials.get("board_ink")
    if mat is None:
        mat = bpy.data.materials.new("board_ink")
        if hasattr(bpy.data.materials, "create_gpencil_data"):
            bpy.data.materials.create_gpencil_data(mat)
    return mat


def build_scene(shot, track, ink):
    scene = bpy.data.scenes.new(shot.code)
    scene.world = paper_world()
    scene.render.fps = 24
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.view_settings.view_transform = "Standard"
    scene.sync_mode = "AUDIO_SYNC"
    scene.frame_start = shot.start_frame
    scene.frame_end = shot.end_frame

    cam_data = bpy.data.cameras.new(f"{shot.code}_cam")
    cam = bpy.data.objects.new(f"{shot.code}_cam", cam_data)
    cam.location = (0.0, -10.0, 0.0)
    cam.rotation_euler = (math.radians(90), 0.0, 0.0)
    scene.collection.objects.link(cam)
    scene.camera = cam

    gp_data = gp_data_collection().new(f"{shot.code}_board")
    if hasattr(gp_data, "materials") and ink is not None:
        gp_data.materials.append(ink)
    layer = gp_data.layers.new("lines")
    # starter keyframe so drawing works immediately; conform only graduates
    # a board once the frame contains actual strokes
    layer.frames.new(shot.start_frame)
    gp = bpy.data.objects.new(f"{shot.code}_board", gp_data)
    scene.collection.objects.link(gp)

    if track is not None:
        se = scene.sequence_editor_create()
        strips = se.strips if hasattr(se, "strips") else se.sequences
        strips.new_sound(name="track", filepath=str(track), channel=1,
                         frame_start=1)
    return scene


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    force = "--force" in argv

    root = shotlib.project_root()
    out = root / "boards" / "boards.blend"
    shots = shotlib.read_shotlist(root / "docs" / "shotlist.csv")
    track = shotlib.find_track(root)
    if track is None:
        print("warning: no track in audio/track/ — board scenes get no audio")

    healed = 0
    if out.exists() and not force:
        bpy.ops.wm.open_mainfile(filepath=str(out))
        existing = set(bpy.data.scenes.keys())
        todo = [s for s in shots if s.code not in existing]
        # heal scenes missing a world (black viewport/render without one)
        # or missing the starter keyframe on their GP layers
        for sc in bpy.data.scenes:
            if sc.world is None:
                sc.world = paper_world()
                healed += 1
            for ob in sc.objects:
                if ob.type in {"GREASEPENCIL", "GPENCIL"}:
                    for layer in ob.data.layers:
                        if len(layer.frames) == 0:
                            layer.frames.new(sc.frame_start)
                            healed += 1
        if not todo and not healed:
            print("boards.blend up to date: nothing to add")
            return
    else:
        todo = shots

    ink = ink_material()
    for shot in todo:
        build_scene(shot, track, ink)

    # drop the factory default scene once real scenes exist
    default = bpy.data.scenes.get("Scene")
    if default is not None and len(bpy.data.scenes) > 1:
        bpy.data.scenes.remove(default)

    out.parent.mkdir(exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out), relative_remap=True)
    print(f"boards.blend: +{len(todo)} board scene(s), {healed} healed, "
          f"{len(bpy.data.scenes)} total")


if __name__ == "__main__":
    main()
