#!/usr/bin/env python3
"""Albedo palette for the Mid-Century Print candidate — registry + generator.

The colour half of the dab palette, mirroring `tilt_palette.py`. A dab is an
(albedo x tilt) pair chosen at the brush, and the two palettes are fully
independent axes — any colour with any tilt.

This palette *offers* colours and says what each is for. It enforces nothing:
the mint reservation and the post-1980 annex are art direction recorded in
`docs/treatment/style-midcentury-print.md`, not constraints the tools police.
The `group` and `role` fields exist so the picker can show that guidance
while painting, not to gate anything.

Bases come from the treatment's two palette tables. Each carries drift
variants for dab-level colour variation, generated as HSV shifts rather than
RGB blends: measured 2026-08-04, an RGB multiply-cool swings paper-cream 174
degrees of hue into blue-grey while other bases barely move, whereas a hue
rotation moves every base by the same amount by construction.

Stdlib only. Import it for the math; run it for the artifacts.
"""
import argparse
import colorsys
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import palette_common as pc

# --- registry ---------------------------------------------------------------

# name -> (hex, group, role). Hexes are the treatment's; the test frame tunes
# them, and retuning here recolours every painted dab in the film.
_BASES = [
    # core — the MCM palette
    ("paper-cream", "#f2e4cc", "core", "light base: walls, concrete, highlights, clouds"),
    ("sand", "#d9c0a3", "core", "ground, road, mid-value neutrals"),
    ("khaki", "#c2a878", "core", "dry grass, secondary ground"),
    ("olive", "#8f7a3d", "core", "lawn, foliage masses"),
    ("sky-teal", "#3fbdb3", "core", "the daytime sky; deep and slightly desaturated"),
    ("terracotta", "#b0764a", "core", "roofs, brick, furniture accents"),
    ("rust", "#c95f33", "core", "hot accents: mountains, the cop car's pop"),
    ("dusty-rose", "#d8a8a8", "core", "sunset transition, distant warmth"),
    ("coral", "#f0a082", "core", "the sunset sky"),
    ("golden", "#eec078", "core", "sun disc, golden-hour wash"),
    ("mint", "#76e7cd", "core", "reserved: the truck and the sweet tea"),
    # annex — the 1980s-90s stratum
    ("charcoal-plastic", "#42403b", "annex", "electronics, tires, the CRT, cop-car trim"),
    ("faded-denim", "#7d94a8", "annex", "the boy's baggies; denim anywhere"),
    ("mall-mauve", "#a98794", "annex", "Mom's wardrobe, the afghan, the couch"),
    ("seafoam-grey", "#9db8ac", "annex", "90s kitchenware, a windbreaker"),
]

# Drift variants: (hue degrees, saturation factor, value factor).
DRIFTS = {
    "warm": (-8.0, 1.0, 1.0),
    "cool": (+8.0, 1.0, 1.0),
    "dusk": (-6.0, 1.0, 0.92),
    "pale": (0.0, 0.85, 1.0),
    "deep": (0.0, 1.15, 0.94),
}


def hex_to_rgb8(h):
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def rgb8_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)


BASES = {
    name: {
        "hex": hexcode,
        "rgb8": list(hex_to_rgb8(hexcode)),
        "group": group,
        "role": role,
    }
    for name, hexcode, group, role in _BASES
}


# --- drift ------------------------------------------------------------------


def apply_drift(rgb8, hue_deg, sat_mul, val_mul):
    """Shift a base in HSV. Hue wraps; saturation and value clamp."""
    r, g, b = (c / 255.0 for c in rgb8)
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    h = (h + hue_deg / 360.0) % 1.0
    s = min(1.0, max(0.0, s * sat_mul))
    v = min(1.0, max(0.0, v * val_mul))
    return tuple(round(c * 255) for c in colorsys.hsv_to_rgb(h, s, v))


def swatches():
    """All swatches as {name: {base, drift, group, role, rgb8, hex}}."""
    out = {}
    for name, base in BASES.items():
        out[name] = _entry(name, None, base, tuple(base["rgb8"]))
        for drift, params in DRIFTS.items():
            rgb = apply_drift(base["rgb8"], *params)
            out[f"{name}_{drift}"] = _entry(name, drift, base, rgb)
    return out


def _entry(base_name, drift, base, rgb):
    return {
        "base": base_name,
        "drift": drift,
        "group": base["group"],
        "role": base["role"],
        "rgb8": list(rgb),
        "hex": rgb8_to_hex(rgb),
    }


# --- ordering ---------------------------------------------------------------
#
# LUT position is what a painted pixel references. Sorting by hue then value
# keeps neighbouring indices near-neighbours in colour, so the blended texel
# at an antialiased dab edge resolves to a transitional swatch rather than a
# stray one. Append new swatches; never reorder under existing artwork.


def sort_key(name):
    rgb = swatches()[name]["rgb8"]
    r, g, b = (c / 255.0 for c in rgb)
    h, _, v = colorsys.rgb_to_hsv(r, g, b)
    return (round(h, 6), round(v, 6), name)


def ordered_names():
    """Every swatch name in LUT order."""
    return sorted(swatches(), key=sort_key)


# --- artifacts --------------------------------------------------------------

SHEET_COLUMNS = [None] + list(DRIFTS)  # base, then each drift


def build_sheet():
    """Picker grid: one row per base, columns base | warm | cool | dusk |
    pale | deep. Returns (width, height, rows)."""
    sw = swatches()
    cell_rows = []
    for name in BASES:
        row = [sw[name]["rgb8"]]
        row += [sw[f"{name}_{d}"]["rgb8"] for d in DRIFTS]
        cell_rows.append(row)
    return pc.grid_sheet(cell_rows, gaps=(1,))


def main(argv=None):
    ap_ = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap_.add_argument(
        "--out",
        default=str(Path(__file__).resolve().parent.parent / "assets/materials/albedo_palette"),
        help="output directory (default: assets/materials/albedo_palette)",
    )
    args = ap_.parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    sw = swatches()
    ordering = ordered_names()

    width, height, rows = build_sheet()
    pc.write_png(out / "albedo_palette.png", width, height, rows)
    pc.write_lut_png(out / "albedo_lut.png", [sw[n]["rgb8"] for n in ordering])
    pc.write_swatch_icons(out / "swatches", {n: sw[n]["rgb8"] for n in sw})

    payload = {
        "meta": {
            "colorspace": "sRGB — this palette is colour, unlike the tilt palette",
            "drifts": "HSV shifts (hue deg, saturation factor, value factor)",
            "guidance": (
                "group/role say what a swatch is for. Nothing is enforced — "
                "see docs/treatment/style-midcentury-print.md"
            ),
            "sheet_columns": ["base"] + list(DRIFTS),
            "sheet_rows": list(BASES),
        },
        "drifts": {k: list(v) for k, v in DRIFTS.items()},
        **pc.indexed_payload(sw, ordering),
    }
    (out / "albedo_palette.json").write_text(json.dumps(payload, indent=2) + "\n")

    print(f"wrote {out / 'albedo_palette.png'} ({width}x{height})")
    print(f"wrote {out / 'albedo_lut.png'} (256x1)")
    print(f"wrote {out / 'swatches'}/ ({len(sw)} icons)")
    print(f"wrote {out / 'albedo_palette.json'} ({len(sw)} swatches, order {payload['ordering_hash']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
