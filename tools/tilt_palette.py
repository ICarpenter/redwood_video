#!/usr/bin/env python3
"""Tilt palette for the Mid-Century Print candidate — registry + generator.

The tilt-dab shading system (docs/treatment/style.md)
paints gouache facets as tangent-space normal colors drawn from a fixed,
film-wide palette: 12 clock directions x 4 lean tiers, plus flat. This
module is the single source of truth for that palette — the swatch math
lives here, and everything else (picker sheet, LUT, icons, JSON sidecar) is
materialized from it.

Run it to emit:

    assets/materials/tilt_palette/tilt_palette.png   picker sheet
    assets/materials/tilt_palette/tilt_lut.png       256x1 lookup
    assets/materials/tilt_palette/swatches/*.png     picker icons
    assets/materials/tilt_palette/tilt_palette.json  swatch data + ordering

Sheet layout: columns left->right are FLAT, then 12/1/2/.../11 o'clock;
rows top->bottom are whisper/soft/medium/strong. The sheet must be loaded
as Non-Color when sampling (normal colors are data, not color).

Any tier is available on any surface. The per-family tier table this module
used to carry (stucco = whisper+soft, diecast = whisper, ...) was dropped
2026-08-04 — it guessed at assignments before anything had been painted, and
the C10 test showed the guess was wrong. Tier is a call made at the brush.

Stdlib only. Import it for the math; run it for the artifacts.
"""

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import palette_common as pc

# --- registry ---------------------------------------------------------------

# Lean tiers in degrees. Tier order here is sheet row order (top -> bottom).
TIERS = {
    "whisper": 3.0,
    "soft": 7.0,
    "medium": 14.0,
    "strong": 25.0,
}

# Clock-hour directions (12 = up in tangent/UV space), sheet column order.
HOURS = [12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

FLAT_NAME = "flat"


def tilt_normal(hour, degrees):
    """Tangent-space unit normal for a lean of `degrees` toward `hour`."""
    theta = math.radians(hour % 12 * 30.0)  # 12 o'clock = +Y, clockwise
    m = math.radians(degrees)
    return (
        math.sin(m) * math.sin(theta),
        math.sin(m) * math.cos(theta),
        math.cos(m),
    )


def normal_to_rgb8(n):
    """Encode a unit normal as 8-bit normal-map color (n * 0.5 + 0.5)."""
    return tuple(round((c * 0.5 + 0.5) * 255) for c in n)


def swatches():
    """All swatches as {name: {hour, tier, degrees, normal, rgb8, hex}}."""
    out = {
        FLAT_NAME: _entry(None, None, 0.0, (0.0, 0.0, 1.0)),
    }
    for tier, deg in TIERS.items():
        for hour in HOURS:
            n = tilt_normal(hour, deg)
            out[f"h{hour:02d}_{tier}"] = _entry(hour, tier, deg, n)
    return out


def _entry(hour, tier, deg, n):
    rgb = normal_to_rgb8(n)
    return {
        "hour": hour,
        "tier": tier,
        "degrees": deg,
        "normal": [round(c, 6) for c in n],
        "rgb8": list(rgb),
        "hex": "#{:02x}{:02x}{:02x}".format(*rgb),
    }


# --- ordering ---------------------------------------------------------------
#
# LUT position is what a painted pixel references. The registry order — flat,
# then each tier's twelve hours in clock sequence — is already similarity
# ordering, so it becomes the LUT order unchanged: adjacent indices are
# adjacent clock hours in the same tier, and a blended texel at an
# antialiased dab edge lands on a neighbouring direction rather than a
# random one. Append new swatches; never reorder under existing artwork.


def ordered_names():
    """Every swatch name in LUT order."""
    return list(swatches())


# --- picker sheet ------------------------------------------------------------


def build_sheet():
    """Render the picker grid. Returns (width, height, rows)."""
    sw = swatches()
    cell_rows = []
    for tier in TIERS:
        row = [sw[FLAT_NAME]["rgb8"]]
        row += [sw[f"h{hour:02d}_{tier}"]["rgb8"] for hour in HOURS]
        cell_rows.append(row)
    # a gap after the flat column, so it reads as separate from the clock ring
    return pc.grid_sheet(cell_rows, gaps=(1,))


# --- main ---------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--out",
        default=str(Path(__file__).resolve().parent.parent / "assets/materials/tilt_palette"),
        help="output directory (default: assets/materials/tilt_palette)",
    )
    args = ap.parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    sw = swatches()
    ordering = ordered_names()

    width, height, rows = build_sheet()
    pc.write_png(out / "tilt_palette.png", width, height, rows)
    pc.write_lut_png(out / "tilt_lut.png", [sw[n]["rgb8"] for n in ordering])
    pc.write_swatch_icons(out / "swatches", {n: sw[n]["rgb8"] for n in sw})

    payload = {
        "meta": {
            "encoding": "tangent-space normal, rgb = n * 0.5 + 0.5, 8-bit",
            "colorspace": "Non-Color (data) — never sample as sRGB",
            "directions": "clock hours, 12 = +Y (up in UV space), clockwise",
            "tiers": "any tier is available on any surface; no family table",
            "sheet_columns": ["flat"] + [f"{h} o'clock" for h in HOURS],
            "sheet_rows": [f"{t} ({d} deg)" for t, d in TIERS.items()],
        },
        "tiers_degrees": TIERS,
        **pc.indexed_payload(sw, ordering),
    }
    (out / "tilt_palette.json").write_text(json.dumps(payload, indent=2) + "\n")

    print(f"wrote {out / 'tilt_palette.png'} ({width}x{height})")
    print(f"wrote {out / 'tilt_lut.png'} (256x1)")
    print(f"wrote {out / 'swatches'}/ ({len(sw)} icons)")
    print(f"wrote {out / 'tilt_palette.json'} ({len(sw)} swatches, order {payload['ordering_hash']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
