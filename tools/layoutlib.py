#!/usr/bin/env python3
"""Shared bpy helpers for layout scenes.

shotlib.py and guides.py are deliberately bpy-free so they import under system
Python. This is their counterpart for code that must touch Blender data, shared
by make_layout.py, stage_shots.py, continue_shot.py, export_shot.py, and
conform_edit.py — they all need to ask the same questions about a shot, and the
answers must agree.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix

sys.path.insert(0, str(Path(__file__).resolve().parent))
import guides

GP_TYPES = {"GREASEPENCIL", "GPENCIL"}

# Frame half-width in paper-local units. Every paper is scaled so the camera
# frame spans +/- this at the paper's plane, whatever the lens or distance.
# 3.6 preserves the historical 10m/50mm board scale, which is what keeps
# sq010_sh010's existing 119 strokes framed exactly as drawn.
PAPER_HALF_WIDTH = 3.6

# Distance from camera to paper, in metres. Chosen for framing, NOT for
# occlusion: Grease Pencil strokes composite over mesh geometry in EEVEE
# unconditionally — measured in Blender 5.1.2, identical results at 0.11m in
# front of a wall and 10m behind it, under both stroke_depth_order modes. So
# nothing can hide the paper and the distance is free. 10m makes the scale
# below exactly 1.0 at a 50mm lens, which matches sq010_sh010's existing
# strokes 1:1.
PAPER_DISTANCE = 10.0


def has_strokes(scene) -> bool:
    """True once the shot's Grease Pencil holds actual strokes.

    Scenes ship with an empty starter keyframe, so keyframe existence is not
    enough — look inside the frames (GPv3: frame.drawing.strokes; legacy:
    frame.strokes).
    """
    for ob in scene.objects:
        if ob.type not in GP_TYPES:
            continue
        for layer in ob.data.layers:
            for fr in layer.frames:
                strokes = getattr(fr, "strokes", None)
                if strokes is None:
                    drawing = getattr(fr, "drawing", None)
                    strokes = getattr(drawing, "strokes", ()) if drawing else ()
                if len(strokes):
                    return True
    return False


def blocking_collection(scene, create=False):
    """The scene's blocking collection, or None. Created and linked if asked."""
    name = guides.blocking_collection_name(scene.name)
    coll = scene.collection.children.get(name)
    if coll is not None or not create:
        return coll
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
    scene.collection.children.link(coll)
    return coll


def blocking_instances(scene) -> list:
    """Collection-instance empties staged in this shot's blocking collection."""
    coll = blocking_collection(scene)
    if coll is None:
        return []
    return [o for o in coll.objects if o.instance_collection is not None]


def shot_ready(scene) -> bool:
    """True if this shot has something worth cutting into the edit.

    Either real strokes, or blocking staged. Deliberately NOT stroke-only:
    blocking major story beats is a stage the edit should be watchable at,
    same as slugs and renders.
    """
    return has_strokes(scene) or bool(blocking_instances(scene))


def apply_hide_blocking(scene) -> bool:
    """Honour the hand-set `hide_blocking` scene property. True if changed.

    Blocking and paper both render by default — the drawing is an overlay on
    top of blocked 3D, not a replacement for it. A shot taken fully 2D sets
    scene["hide_blocking"] = True by hand. NO TOOL EVER WRITES IT; that is
    exactly what distinguishes it from the automatic rule it replaces.
    """
    coll = blocking_collection(scene)
    if coll is None:
        return False
    hide = bool(scene.get("hide_blocking", False))
    if coll.hide_render == hide:
        return False
    coll.hide_render = hide
    return True


def apply_project_settings(scene, view_transform="AgX") -> None:
    """The project's locked render settings, in one place.

    Applied to shot_template.blend and to every layout scene, so the two can
    never drift. Layout scenes pass view_transform="Standard" — they show
    greybox blocking and flat GP ink, which AgX only muddies. Renders keep
    AgX, and the edit passes them through with Standard so it is not applied
    twice.
    """
    scene.render.fps = 24
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "16"
    scene.view_settings.view_transform = view_transform
    # the block this replaces set `look` too; dropping it would make "one
    # place" a lie the moment a scene carries a non-default look
    scene.view_settings.look = "None"
    scene.sync_mode = "AUDIO_SYNC"


def paper_distance(cam) -> float:
    """Distance from camera to paper. Framing choice, not a depth trick."""
    return PAPER_DISTANCE


def fit_paper(gp, cam, distance=None) -> None:
    """Park the GP paper in front of the camera, sized to the frustum.

    The paper sits in front of the camera purely so drawing happens in
    camera space (a stable, camera-relative surface to draw on as the shot
    is framed) — not because distance protects it from occlusion. It
    doesn't need to: see PAPER_DISTANCE for why nothing can hide it and the
    distance is free.

    Parents `gp` to `cam` and sets its local transform so a stroke at paper
    coordinate x=PAPER_HALF_WIDTH lands exactly on the right edge of frame,
    for any lens or distance. Local rotation is -90 deg about X: the paper's
    XZ drawing plane maps onto the camera's XY screen plane, which is the
    relationship the original boards had (GP unrotated at the origin, camera
    rotated +90 deg about X). Preserving it is what keeps existing strokes
    framed as drawn.
    """
    d = paper_distance(cam) if distance is None else distance
    half_w = d * (cam.data.sensor_width / 2.0) / cam.data.lens
    s = half_w / PAPER_HALF_WIDTH
    gp.parent = cam
    gp.matrix_parent_inverse = Matrix.Identity(4)
    gp.location = (0.0, 0.0, -d)
    gp.rotation_euler = (math.radians(-90), 0.0, 0.0)
    gp.scale = (s, s, s)
