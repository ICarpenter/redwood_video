#!/usr/bin/env python3
"""Shared bpy helpers for board scenes.

shotlib.py and guides.py are deliberately bpy-free so they import under system
Python. This is their counterpart for code that must touch Blender data, shared
by make_boards.py, stage_boards.py, and conform_edit.py — all three need to ask
the same questions about a board, and the answers must agree.
"""
from __future__ import annotations

import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import guides

GP_TYPES = {"GREASEPENCIL", "GPENCIL"}


def has_strokes(scene) -> bool:
    """True once the board's Grease Pencil holds actual strokes.

    Board scenes ship with an empty starter keyframe, so keyframe existence is
    not enough — look inside the frames (GPv3: frame.drawing.strokes; legacy:
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


def guides_collection(scene, create=False):
    """The scene's guides collection, or None. Created and linked if asked."""
    name = guides.guides_collection_name(scene.name)
    coll = scene.collection.children.get(name)
    if coll is not None or not create:
        return coll
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
    scene.collection.children.link(coll)
    return coll


def guide_instances(scene) -> list:
    """Collection-instance empties staged in this board's guides collection."""
    coll = guides_collection(scene)
    if coll is None:
        return []
    return [o for o in coll.objects if o.instance_collection is not None]


def sync_guide_visibility(scene) -> bool:
    """Guides render only until the board is drawn. True if this changed it.

    An undrawn board is blocked out with guides, so they must reach the edit —
    conform_edit renders the board scene's camera and would otherwise get blank
    paper. Once real strokes exist the drawing IS the board, and the guides drop
    back out of the render so they never show through the artwork.

    Re-run after a drawing session to keep the edit honest.
    """
    coll = guides_collection(scene)
    if coll is None:
        return False
    hide = has_strokes(scene)
    if coll.hide_render == hide:
        return False
    coll.hide_render = hide
    return True


def board_ready(scene) -> bool:
    """True if this board has something worth cutting into the edit.

    Either real strokes, or guides staged for a blocking pass. Deliberately
    NOT stroke-only: blocking major story beats with guides is a stage the edit
    should be watchable at, same as slugs and renders.
    """
    return has_strokes(scene) or bool(guide_instances(scene))
