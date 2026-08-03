#!/usr/bin/env python3
"""Declarative registry of animatic scale-guides.

Stdlib only — imported by guide_assets.py, make_layout.py, and the
redwood_guides add-on inside Blender, and by the test suite under system
Python. No bpy here (same rule shotlib.py follows).

Layout scenes hold the property linked at identity (world origin, ground at
z=0) and change framing by moving the camera, never the set. Guides are
authored facing -Y, feet at Z=0, centred on X=0; they are dropped in WORLD
space onto the property, so a guide's transform says where that character
stands. They live in a per-scene `<code>_blocking` collection.
"""
from __future__ import annotations

from dataclasses import dataclass

# Fallback distance along the camera's view ray when it never meets the
# z=0 ground plane (camera level or tilted up). Metres.
DROP_DISTANCE = 8.0

BLOCKING_SUFFIX = "_blocking"


def blocking_collection_name(scene_name: str) -> str:
    """Per-scene blocking collection name (globally unique, one per shot)."""
    return f"{scene_name}{BLOCKING_SUFFIX}"


# Project-root-relative paths to the asset files.
CAST_FILE = "assets/chars/cast.blend"
PROPS_FILE = "assets/props/props.blend"
PROPERTY_FILE = "assets/envs/property/property.blend"
TRENCH_FILE = "assets/envs/trench/trench.blend"

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
    file: str      # CAST_FILE, PROPS_FILE, or PROPERTY_FILE
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
    GuideSpec("box", PROPS_FILE, "props", 1.2),
    GuideSpec("scale_stick", PROPS_FILE, "props", 2.0),
    GuideSpec("egg_salad_sando", PROPS_FILE, "props", 0.07),
    GuideSpec("gun_cabinet", PROPS_FILE, "props", 1.95),
    GuideSpec("mushroom_cloud", PROPS_FILE, "props", 14.0),
    GuideSpec("clothesline", PROPS_FILE, "props", 2.2),
    # Flashback variant of the sheriff: same body, M1 helmet instead of the
    # stetson. A separate collection rather than a reposed instance — guides
    # are rigid, so a variant is the documented way to get a distinct look
    # (see docs/layout.md).
    GuideSpec("sheriff_war", CAST_FILE, "cast", 1.8),
]

# The whole property SET is linkable too, but it is NOT built by guide_assets
# (marked in place via --mark-property) and never dimension-checked. Its
# height is nominal (house ridge). Kept out of GUIDES so the build/check
# paths stay "cast + props only". DROPPABLE is the 14 guides plus the
# property set, used by guide_by_name and shotlist asset validation — NOT by
# the add-on's Add Guide dropdown, which offers GUIDES only: the property is
# linked at identity in every layout scene already and must never be
# instanced again (see docs/layout.md).
SET_GUIDE = GuideSpec("property", PROPERTY_FILE, "set", 5.2)

# Mini sets: single-asset files under assets/envs/<name>/<name>.blend, each
# exposing ONE root collection named after itself. Unlike `property` these ARE
# meant to be instanced — a mini set is pulled into the one shot that needs it
# and placed away from the property, which stays linked at identity underneath.
# Like `property` they are NOT dimension-checked: a trench's lowest point is
# its floor at z<0, which would fail the feet-at-zero rule every character
# guide has to satisfy.
SETS: list[GuideSpec] = [
    SET_GUIDE,
    GuideSpec("trench", TRENCH_FILE, "set", 2.4),
]
DROPPABLE: list[GuideSpec] = GUIDES + SETS


def guides_for_file(file: str) -> list[GuideSpec]:
    return [g for g in GUIDES if g.file == file]


def guide_by_name(name: str) -> "GuideSpec | None":
    return next((g for g in DROPPABLE if g.name == name), None)


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
