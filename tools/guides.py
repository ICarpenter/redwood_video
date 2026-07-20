#!/usr/bin/env python3
"""Declarative registry of animatic scale-guides.

Stdlib only — imported by guide_assets.py, make_boards.py, and the
redwood_guides add-on inside Blender, and by the test suite under system
Python. No bpy here (same rule shotlib.py follows).

Board scenes place a Grease Pencil paper plane at the origin with the camera
at (0,-10,0) looking +Y. Guides are authored facing -Y (front toward camera),
feet at Z=0, centred on X=0; dropped at DROP_LOCATION they sit just behind the
paper (Y=0) so strokes overlay them. They live in a per-scene collection whose
render toggle is off, so conform_edit only ever sees the GP strokes.
"""
from __future__ import annotations

from dataclasses import dataclass

DROP_LOCATION = (0.0, 1.5, 0.0)

GUIDES_SUFFIX = "_guides"


def guides_collection_name(scene_name: str) -> str:
    """Per-scene guides collection name (globally unique, one per board)."""
    return f"{scene_name}{GUIDES_SUFFIX}"


# Project-root-relative paths to the asset files.
CAST_FILE = "assets/chars/cast.blend"
PROPS_FILE = "assets/props/props.blend"
PROPERTY_FILE = "assets/envs/property/property.blend"

# Hard-coded catalog UUIDs → regenerating the cats file never churns it.
# key -> (uuid, catalog path, simple name)
CATALOGS = {
    "cast": ("7c3e1a2b-0001-4a00-8000-000000000001", "guides/cast", "guides-cast"),
    "props": ("7c3e1a2b-0002-4a00-8000-000000000002", "guides/props", "guides-props"),
    "set": ("7c3e1a2b-0003-4a00-8000-000000000003", "guides/set", "guides-set"),
}


@dataclass(frozen=True)
class GuideSpec:
    name: str      # collection name == asset name
    file: str      # CAST_FILE or PROPS_FILE
    catalog: str   # key into CATALOGS
    height: float  # target overall Z extent in metres (checked, loose tolerance)


GUIDES: list[GuideSpec] = [
    GuideSpec("boy", CAST_FILE, "cast", 1.3),
    GuideSpec("mom", CAST_FILE, "cast", 1.7),
    GuideSpec("sheriff", CAST_FILE, "cast", 1.8),
    GuideSpec("machine_gun", PROPS_FILE, "props", 0.3),
    GuideSpec("printer", PROPS_FILE, "props", 1.4),
    GuideSpec("action_figure", PROPS_FILE, "props", 1.8),
    GuideSpec("delivery_truck", PROPS_FILE, "props", 3.2),
    GuideSpec("cruiser", PROPS_FILE, "props", 1.6),
    GuideSpec("rosco", PROPS_FILE, "props", 0.22),
    GuideSpec("big_pistol", PROPS_FILE, "props", 0.5),
    GuideSpec("santa", PROPS_FILE, "props", 1.8),
    GuideSpec("scale_stick", PROPS_FILE, "props", 2.0),
]


def guides_for_file(file: str) -> list[GuideSpec]:
    return [g for g in GUIDES if g.file == file]


def guide_by_name(name: str) -> "GuideSpec | None":
    return next((g for g in GUIDES if g.name == name), None)


def cats_file_text() -> str:
    lines = [
        "# This is an Asset Catalog Definition file for Blender.",
        "#",
        "# Empty lines and lines starting with `#` will be ignored.",
        "# The first non-ignored line should be the version indicator.",
        '# Other lines are of the format "UUID:catalog/path/for/assets:simple catalog name"',
        "",
        "VERSION 1",
        "",
    ]
    for uuid, path, simple in CATALOGS.values():
        lines.append(f"{uuid}:{path}:{simple}")
    return "\n".join(lines) + "\n"
