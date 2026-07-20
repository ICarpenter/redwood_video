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
import re
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shotlib
import guides


def gp_data_collection():
    data = bpy.data
    return data.grease_pencils_v3 if hasattr(data, "grease_pencils_v3") \
        else data.grease_pencils


def normalize(text: str) -> str:
    """ASCII-safe text for Blender's default font."""
    return (text.replace("**", "").replace("♪", "*").replace("—", "-")
                .replace("–", "-").replace("…", "..."))


def read_script_prompts(path):
    """(sq, sh) -> full shot text from the script's markdown tables."""
    prompts, sq = {}, None
    if not path.exists():
        return prompts
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^## sq(\d{3})", line)
        if m:
            sq = m.group(1)
            continue
        m = re.match(r"^\|\s*(\d{3})\s*\|", line)
        if m and sq is not None:
            cells = [c.strip() for c in line.split("|")]
            if len(cells) >= 7:
                prompts[(sq, m.group(1))] = normalize(cells[5])
    return prompts


def note_material():
    mat = bpy.data.materials.get("note_ink")
    if mat is None:
        mat = bpy.data.materials.new("note_ink")
        mat.diffuse_color = (0.02, 0.02, 0.02, 1.0)
    return mat


def build_note(scene, code, prompt):
    """Script prompt as an in-viewport text object; never renders."""
    name = f"{code}_note"
    curve = bpy.data.curves.new(name, type="FONT")
    curve.body = prompt
    curve.size = 0.14
    if curve.text_boxes:
        curve.text_boxes[0].width = 6.8
    curve.materials.append(note_material())
    ob = bpy.data.objects.new(name, curve)
    ob.location = (-3.4, 0.0, 1.85)
    ob.rotation_euler = (math.radians(90), 0.0, 0.0)
    ob.hide_render = True
    ob.hide_select = True
    scene.collection.objects.link(ob)
    return ob


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


def ensure_guides_collection(scene):
    """Per-scene, non-rendering collection for movable drawing guides.

    Names are globally unique in Blender, so each board owns
    `<code>_guides`. hide_render keeps guides out of the animatic; it is set
    active so Asset-Browser drops land here. Returns True if newly created.
    """
    name = guides.guides_collection_name(scene.name)
    coll = scene.collection.children.get(name)
    created = coll is None
    if created:
        coll = bpy.data.collections.new(name)
        scene.collection.children.link(coll)
    coll.hide_render = True
    vl = scene.view_layers[0]
    lc = vl.layer_collection.children.get(coll.name)
    if lc is not None:
        vl.active_layer_collection = lc
    return created


def build_scene(shot, track, ink, prompt):
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

    build_note(scene, shot.code, prompt)

    if track is not None:
        se = scene.sequence_editor_create()
        strips = se.strips if hasattr(se, "strips") else se.sequences
        strips.new_sound(name="track", filepath=str(track), channel=1,
                         frame_start=1)

    ensure_guides_collection(scene)
    return scene


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    force = "--force" in argv

    root = shotlib.project_root()
    out = root / "boards" / "boards.blend"
    shots = shotlib.read_shotlist(root / "docs" / "shotlist.csv")
    prompts = read_script_prompts(root / "docs" / "treatment" / "script.md")
    track = shotlib.find_track(root)


    def prompt_for(shot):
        return prompts.get((shot.sq, shot.sh), normalize(shot.description))
    if track is None:
        print("warning: no track in audio/track/ — board scenes get no audio")

    healed = 0
    if out.exists() and not force:
        bpy.ops.wm.open_mainfile(filepath=str(out))
        existing = set(bpy.data.scenes.keys())
        todo = [s for s in shots if s.code not in existing]
        # heal scenes missing a world (black viewport/render without one),
        # missing the starter keyframe, or missing/stale script notes
        by_code = {s.code: s for s in shots}
        for sc in bpy.data.scenes:
            if ensure_guides_collection(sc):
                healed += 1
            if sc.world is None:
                sc.world = paper_world()
                healed += 1
            for ob in sc.objects:
                if ob.type in {"GREASEPENCIL", "GPENCIL"}:
                    for layer in ob.data.layers:
                        if len(layer.frames) == 0:
                            layer.frames.new(sc.frame_start)
                            healed += 1
            shot = by_code.get(sc.name)
            if shot is not None:
                note = sc.objects.get(f"{sc.name}_note")
                if note is None:
                    build_note(sc, sc.name, prompt_for(shot))
                    healed += 1
                elif note.data.body != prompt_for(shot):
                    note.data.body = prompt_for(shot)
                    healed += 1
        if not todo and not healed:
            print("boards.blend up to date: nothing to add")
            return
    else:
        todo = shots

    ink = ink_material()
    for shot in todo:
        build_scene(shot, track, ink, prompt_for(shot))

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
