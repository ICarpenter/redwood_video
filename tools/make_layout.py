#!/usr/bin/env python3
"""Seed layout/layout.blend: one camera-driven scene per shotlist row.

Each scene links the property collection at IDENTITY (world origin, ground
at z=0 — the pipeline's first invariant: the property never moves), gets a
starting camera as the shot's sole framing authority, a per-scene
`<code>_blocking` collection for world-space blocking, and a Grease Pencil
"paper" fit to the camera's frustum for animatic drawing. Scene name = shot
code (sqXXX_shXXX); frame range = the shot's song-global frames; the track
sits on each scene's sequencer so drawing happens with audio scrubbing in
context.

Default run ADDS scenes for new shotlist rows and leaves existing scenes
untouched (safe after drawing/blocking has begun), while healing anything a
scene is missing or has drifted from: world, project settings, blocking
collection, linked property (reset to identity if it has drifted), starter
keyframe, script note (text and camera-parenting), or a paper unfit to its
camera. A camera-less scene cannot be given a framing authority
automatically, so it is reported instead of silently skipped. --force
rebuilds the whole file from scratch, DESTROYING all drawing and blocking.

Run:
  "$BLENDER" --background --factory-startup --python-exit-code 1 \
      --python tools/make_layout.py [-- --force]
"""
import math
import re
import sys
from pathlib import Path

import bpy
from mathutils import Matrix

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shotlib
import guides
import layoutlib

GP_TYPES_LOCAL = layoutlib.GP_TYPES


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


def park_note(note, cam):
    """Parent an existing note to `cam` at its fixed viewport offset.

    The single owner of the note's pose, so build_scene and the heal loop
    below cannot drift apart on where the note sits — that drift is exactly
    what put it at the old 2D pose, unparented, whenever heal ran instead of
    build.
    """
    note.parent = cam
    note.matrix_parent_inverse = Matrix.Identity(4)
    note.location = (-1.6, 0.9, -4.0)
    note.rotation_euler = (0.0, 0.0, 0.0)


def build_and_park_note(scene, code, prompt, cam):
    """Create the script-prompt note and park it as a camera child."""
    note = build_note(scene, code, prompt)
    park_note(note, cam)
    return note


def layout_world():
    """Neutral grey so greybox blocking reads. Scenes made via the data API
    have NO world at all, which renders black."""
    w = bpy.data.worlds.get("layout")
    if w is None:
        w = bpy.data.worlds.new("layout")
        w.use_nodes = True
        bg = w.node_tree.nodes.get("Background")
        if bg is not None:
            bg.inputs["Color"].default_value = (0.55, 0.6, 0.65, 1.0)
            bg.inputs["Strength"].default_value = 1.0
    return w


def ink_material():
    mat = bpy.data.materials.get("board_ink")
    if mat is None:
        mat = bpy.data.materials.new("board_ink")
        if hasattr(bpy.data.materials, "create_gpencil_data"):
            bpy.data.materials.create_gpencil_data(mat)
    return mat


def ensure_blocking_collection(scene):
    """Per-scene collection for world-space blocking instances.

    Names are globally unique in Blender, so each shot owns `<code>_blocking`.
    Set active so Asset-Browser drops land here. Returns True if newly created.

    Render visibility is NOT set here — blocking renders by default and only
    the hand-set `hide_blocking` scene property turns it off
    (layoutlib.apply_hide_blocking).
    """
    name = guides.blocking_collection_name(scene.name)
    created = scene.collection.children.get(name) is None
    coll = layoutlib.blocking_collection(scene, create=True)
    vl = scene.view_layers[0]
    lc = vl.layer_collection.children.get(coll.name)
    if lc is not None:
        vl.active_layer_collection = lc
    return created


def _at_identity(ob) -> bool:
    """True if ob's location/rotation_euler/scale are all exactly identity."""
    return (tuple(ob.location) == (0.0, 0.0, 0.0)
            and tuple(ob.rotation_euler) == (0.0, 0.0, 0.0)
            and tuple(ob.scale) == (1.0, 1.0, 1.0))


def link_property(scene):
    """Link the property set at IDENTITY — the pipeline's first invariant.

    The set never moves. Framing changes by moving the camera. An existing
    instance is not just trusted: hide_select deters accidental nudges but
    does not stop Alt+H, the outliner, or a script, so a drifted instance is
    snapped back to identity here rather than left as the drift the old
    stage_boards.py used to bake in. Returns the instance object, or None if
    the property file is missing.
    """
    name = "property"
    existing = next((o for o in scene.objects
                     if o.instance_collection is not None
                     and o.instance_collection.name == name), None)
    if existing is not None:
        if not _at_identity(existing):
            existing.location = (0.0, 0.0, 0.0)
            existing.rotation_euler = (0.0, 0.0, 0.0)
            existing.scale = (1.0, 1.0, 1.0)
            print(f"warning: {scene.name}: property had drifted off identity — reset")
        return existing

    root = shotlib.project_root()
    path = root / guides.PROPERTY_FILE
    if not path.exists():
        print(f"warning: {guides.PROPERTY_FILE} missing — scene has no set")
        return None

    linked = next((c for c in bpy.data.collections
                   if c.name == name and c.library
                   and Path(c.library.filepath).name == path.name), None)
    if linked is None:
        with bpy.data.libraries.load(str(path), link=True) as (src, dst):
            if name not in src.collections:
                sys.exit(f"error: no collection {name!r} in {path}")
            dst.collections = [name]
        linked = dst.collections[0]

    inst = bpy.data.objects.new(name, None)
    inst.instance_type = "COLLECTION"
    inst.instance_collection = linked
    inst.location = (0.0, 0.0, 0.0)
    inst.rotation_euler = (0.0, 0.0, 0.0)
    inst.scale = (1.0, 1.0, 1.0)
    inst.hide_select = True   # you cannot nudge the set by accident
    scene.collection.objects.link(inst)
    return inst


def build_scene(shot, track, ink, prompt):
    scene = bpy.data.scenes.new(shot.code)
    scene.world = layout_world()
    layoutlib.apply_project_settings(scene, view_transform="Standard")
    scene.frame_start = shot.start_frame
    scene.frame_end = shot.end_frame

    cam_data = bpy.data.cameras.new(f"{shot.code}_cam")
    cam = bpy.data.objects.new(f"{shot.code}_cam", cam_data)
    # A starting point only — stage_shots.py and hand framing move it. The
    # set never moves, so this is the one thing that decides the shot.
    cam.location = (0.0, -10.0, 1.6)
    cam.rotation_euler = (math.radians(90), 0.0, 0.0)
    scene.collection.objects.link(cam)
    scene.camera = cam

    gp_data = gp_data_collection().new(f"{shot.code}_board")
    if hasattr(gp_data, "materials") and ink is not None:
        gp_data.materials.append(ink)
    layer = gp_data.layers.new("lines")
    # starter keyframe so drawing works immediately; layoutlib.has_strokes
    # looks inside the frame, so an empty one does not count as drawn
    layer.frames.new(shot.start_frame)
    gp = bpy.data.objects.new(f"{shot.code}_board", gp_data)
    scene.collection.objects.link(gp)
    layoutlib.fit_paper(gp, cam)

    build_and_park_note(scene, shot.code, prompt, cam)

    if track is not None:
        se = scene.sequence_editor_create()
        strips = se.strips if hasattr(se, "strips") else se.sequences
        strips.new_sound(name="track", filepath=str(track), channel=1,
                         frame_start=1)

    ensure_blocking_collection(scene)
    link_property(scene)
    layoutlib.apply_hide_blocking(scene)
    return scene


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    force = "--force" in argv

    root = shotlib.project_root()
    out = root / "layout" / "layout.blend"
    shots = shotlib.read_shotlist(root / "docs" / "shotlist.csv")
    prompts = read_script_prompts(root / "docs" / "treatment" / "script.md")
    track = shotlib.find_track(root)


    def prompt_for(shot):
        return prompts.get((shot.sq, shot.sh), normalize(shot.description))
    if track is None:
        print("warning: no track in audio/track/ — layout scenes get no audio")

    healed = 0
    if out.exists() and not force:
        bpy.ops.wm.open_mainfile(filepath=str(out))
        existing = set(bpy.data.scenes.keys())
        todo = [s for s in shots if s.code not in existing]
        # heal scenes missing a world (black viewport/render without one),
        # project settings drift, the blocking collection, a linked property
        # (or one that has drifted off identity), the starter keyframe,
        # missing/stale/unparented script notes, or a paper unfit to its
        # camera. A missing camera cannot be healed automatically — it is
        # the shot's only framing authority — so it is reported instead.
        by_code = {s.code: s for s in shots}
        for sc in bpy.data.scenes:
            if ensure_blocking_collection(sc):
                healed += 1
            # honour a hand-set hide_blocking; no tool ever writes it
            if layoutlib.apply_hide_blocking(sc):
                healed += 1
            if sc.world is None:
                sc.world = layout_world()
                healed += 1
            # project settings have exactly one owner (layoutlib); reapply
            # unconditionally to heal drift. Returns None, so it cannot feed
            # `healed` — that is fine, it is not optional the way the rest
            # of this loop's fixes are.
            layoutlib.apply_project_settings(sc, view_transform="Standard")
            for ob in sc.objects:
                if ob.type in GP_TYPES_LOCAL:
                    for layer in ob.data.layers:
                        if len(layer.frames) == 0:
                            layer.frames.new(sc.frame_start)
                            healed += 1
            cam = sc.camera
            if cam is None:
                print(f"warning: {sc.name}: no camera — shot has no framing authority")
            shot = by_code.get(sc.name)
            if shot is not None:
                note = sc.objects.get(f"{sc.name}_note")
                if note is None:
                    if cam is not None:
                        build_and_park_note(sc, sc.name, prompt_for(shot), cam)
                    else:
                        build_note(sc, sc.name, prompt_for(shot))
                    healed += 1
                else:
                    if note.data.body != prompt_for(shot):
                        note.data.body = prompt_for(shot)
                        healed += 1
                    if cam is not None and note.parent is not cam:
                        park_note(note, cam)
                        healed += 1
            prop = next((o for o in sc.objects
                        if o.instance_collection is not None
                        and o.instance_collection.name == "property"), None)
            had_property = prop is not None
            property_drifted = had_property and not _at_identity(prop)
            if link_property(sc) is not None and (not had_property or property_drifted):
                healed += 1
            for ob in sc.objects:
                if cam is not None and ob.type in GP_TYPES_LOCAL and ob.parent is not cam:
                    layoutlib.fit_paper(ob, cam)
                    healed += 1
        if not todo and not healed:
            print("layout.blend up to date: nothing to add")
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
    print(f"layout.blend: +{len(todo)} layout scene(s), {healed} healed, "
          f"{len(bpy.data.scenes)} total")


if __name__ == "__main__":
    main()
