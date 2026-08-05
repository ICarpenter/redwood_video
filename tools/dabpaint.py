#!/usr/bin/env python3
"""Dab painter — the decisions the add-on makes before it touches Blender.

The painter's whole trick is that the image you paint is not colour. It holds
two indices per texel — R = albedo swatch, G = tilt swatch — and a 256x1 LUT
per channel resolves them into a real colour and a real tangent normal. One
image means Blender paints it and Blender undoes it, so nothing can desync;
that is the reason for the design, not a detail of it
(docs/superpowers/specs/2026-08-04-tilt-dab-painter-design.md).

This module is bpy-free so it can be unit-tested headlessly, mirroring how
`guides.py` sits under `addons/redwood_guides.py`. The add-on is a thin shell
over what is decided here.
"""
import json
import re
from pathlib import Path

import palette_common as pc

# --- image specs -------------------------------------------------------------
#
# These are re-applied on every setup run rather than set once. An 8-bit
# Non-Color texel returns exactly i/255, which is what makes the round-trip
# exact; an sRGB colorspace or Linear interpolation breaks it *silently* —
# no error, just every dab quietly wrong. Healing beats trusting.

INDEX_MAP_SPEC = {
    "colorspace": "Non-Color",
    "interpolation": "Closest",
    "float_buffer": False,
}
ALBEDO_LUT_SPEC = {"colorspace": "sRGB", "interpolation": "Closest"}
TILT_LUT_SPEC = {"colorspace": "Non-Color", "interpolation": "Closest"}

RESOLUTIONS = (1024, 2048, 4096)

ALBEDO_PALETTE_DIR = "albedo_palette"
TILT_PALETTE_DIR = "tilt_palette"


# --- naming ------------------------------------------------------------------


def asset_stem(material_name, object_name):
    """The stem every generated file for this asset shares.

    The active material name, lowercased — `MCM_C10_Body` -> `mcm_c10_body`.
    Falls back to the object when the material is unnamed or absent.
    """
    raw = (material_name or "").strip() or (object_name or "").strip()
    return re.sub(r"[^a-z0-9]+", "_", raw.lower()).strip("_")


def index_map_name(stem):
    return f"{stem}_dabindex.png"


def baked_albedo_name(stem):
    return f"{stem}_albedo.png"


def baked_tilt_name(stem):
    return f"{stem}_tilt.png"


# --- brush encoding ----------------------------------------------------------


def brush_color_for(albedo_index, tilt_index):
    """The brush colour that paints this (albedo, tilt) pair.

    Any albedo composes with any tilt: they are separate channels, so there
    is no pair table and nothing to keep consistent. Blue is unused.
    """
    return (
        pc.channel_for_index(albedo_index),
        pc.channel_for_index(tilt_index),
        0.0,
    )


def indices_from_texels(texels):
    """Recover (albedo, tilt) from an 8-bit RGB texel triple."""
    r, g = texels[0], texels[1]
    return (pc.index_for_channel(r / 255), pc.index_for_channel(g / 255))


# --- palettes ----------------------------------------------------------------


class PaletteMissing(Exception):
    """Raised with the command that builds the missing artifact."""


GENERATOR_FOR = {
    "albedo_palette.json": "python3 tools/albedo_palette.py",
    "tilt_palette.json": "python3 tools/tilt_palette.py",
}


class Palette:
    """A generated palette, read-only, as the add-on sees it."""

    def __init__(self, payload):
        self.ordering = list(payload["ordering"])
        self.ordering_hash = payload["ordering_hash"]
        self._swatches = payload["swatches"]

    def __len__(self):
        return len(self.ordering)

    def swatch(self, name):
        return self._swatches[name]

    def index_of(self, name):
        if name not in self._swatches:
            raise KeyError(f"no swatch named {name!r} in this palette")
        return self._swatches[name]["index"]

    def name_at(self, index):
        return self.ordering[index]

    def rgb8_in_lut_order(self):
        return [self._swatches[n]["rgb8"] for n in self.ordering]

    def has_drifted(self, stored_hash):
        """True when the palette has been *reordered* since `stored_hash`.

        Appending is safe — index N still means what it meant. Reordering
        repaints every existing dab, so it is worth a loud warning. An empty
        stored hash means first-time setup, which is not drift.
        """
        return bool(stored_hash) and stored_hash != self.ordering_hash


def load_palette(path):
    path = Path(path)
    if not path.exists():
        cmd = GENERATOR_FOR.get(path.name, f"the generator for {path.name}")
        raise PaletteMissing(f"{path} is missing — run: {cmd}")
    return Palette(json.loads(path.read_text()))


# --- setup health ------------------------------------------------------------


def setup_issues(colorspace, interpolation, has_uv, luts_linked):
    """Everything wrong with the current setup, each in its own message.

    All four of these fail silently in Blender — a wrong colorspace paints
    plausible-looking garbage rather than erroring — so the panel says them
    out loud and the setup operator heals them.
    """
    issues = []
    if colorspace != INDEX_MAP_SPEC["colorspace"]:
        issues.append(
            f"index map colorspace is {colorspace}, not "
            f"{INDEX_MAP_SPEC['colorspace']} — every dab decodes wrong"
        )
    if interpolation != INDEX_MAP_SPEC["interpolation"]:
        issues.append(
            f"index map interpolation is {interpolation}, not "
            f"{INDEX_MAP_SPEC['interpolation']} — indices blend into neighbours"
        )
    if not has_uv:
        issues.append("object has no UV layer — there is nowhere to paint")
    if not luts_linked:
        issues.append("LUT images are not linked — run Make Paintable to heal")
    return issues
