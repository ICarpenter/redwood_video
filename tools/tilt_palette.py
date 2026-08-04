#!/usr/bin/env python3
"""Tilt palette for the Mid-Century Print candidate — registry + generator.

The tilt-dab shading system (docs/treatment/style-midcentury-print.md)
paints gouache facets as tangent-space normal colors drawn from a fixed,
film-wide palette: 12 clock directions x 4 lean tiers, plus flat. This
module is the single source of truth for that palette — the swatch math
lives here, and everything else (picker sheet, JSON sidecar, the future
Ucupaint dab-kit builder) is materialized from it.

Run it to emit:

    assets/materials/tilt_palette/tilt_palette.png   picker sheet
    assets/materials/tilt_palette/tilt_palette.json  swatch data + legality

Sheet layout: columns left->right are FLAT, then 12/1/2/.../11 o'clock;
rows top->bottom are whisper/soft/medium/strong. The sheet must be loaded
as Non-Color when sampling (normal colors are data, not color).

Stdlib only. Import it for the math; run it for the artifacts.
"""

import argparse
import json
import math
import struct
import sys
import zlib
from pathlib import Path

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

# Which tiers each material family may paint with. "+crease" grants strong
# for crease accents only.
FAMILIES = {
    "stucco_siding_cream": ["whisper", "soft"],
    "terrain_road": ["soft", "medium"],
    "grass_foliage": ["medium", "strong"],  # vertical-biased, elongated dabs
    "diecast": ["whisper", "strong"],  # strong = crease accents only
    "characters": ["whisper", "soft"],
}

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


# --- picker sheet (minimal stdlib PNG writer) --------------------------------

CELL = 96
GUTTER = 4
MARGIN = 8
FLAT_GAP = 8  # extra separation between the flat column and the clock ring
BG = (32, 32, 32)


def _png_chunk(tag, payload):
    data = tag + payload
    return struct.pack(">I", len(payload)) + data + struct.pack(">I", zlib.crc32(data))


def write_png(path, width, height, rows):
    """rows: list of `height` bytearrays, each 3*width RGB bytes."""
    raw = b"".join(b"\x00" + bytes(r) for r in rows)
    png = (
        b"\x89PNG\r\n\x1a\n"
        + _png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + _png_chunk(b"IDAT", zlib.compress(raw, 9))
        + _png_chunk(b"IEND", b"")
    )
    Path(path).write_bytes(png)


def build_sheet():
    """Render the picker grid. Returns (width, height, rows)."""
    sw = swatches()
    cols = 1 + len(HOURS)
    tiers = list(TIERS)
    width = 2 * MARGIN + cols * CELL + (cols - 1) * GUTTER + FLAT_GAP
    height = 2 * MARGIN + len(tiers) * CELL + (len(tiers) - 1) * GUTTER
    rows = [bytearray(BG * width) for _ in range(height)]

    def blit(cx, cy, rgb):
        x0 = MARGIN + cx * (CELL + GUTTER) + (FLAT_GAP if cx > 0 else 0)
        y0 = MARGIN + cy * (CELL + GUTTER)
        px = bytes(rgb)
        for y in range(y0, y0 + CELL):
            row = rows[y]
            for x in range(x0, x0 + CELL):
                row[3 * x : 3 * x + 3] = px

    for r, tier in enumerate(tiers):
        blit(0, r, sw[FLAT_NAME]["rgb8"])
        for c, hour in enumerate(HOURS):
            blit(1 + c, r, sw[f"h{hour:02d}_{tier}"]["rgb8"])
    return width, height, rows


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
    width, height, rows = build_sheet()
    write_png(out / "tilt_palette.png", width, height, rows)

    payload = {
        "meta": {
            "encoding": "tangent-space normal, rgb = n * 0.5 + 0.5, 8-bit",
            "colorspace": "Non-Color (data) — never sample as sRGB",
            "directions": "clock hours, 12 = +Y (up in UV space), clockwise",
            "sheet_columns": ["flat"] + [f"{h} o'clock" for h in HOURS],
            "sheet_rows": [f"{t} ({d} deg)" for t, d in TIERS.items()],
        },
        "tiers_degrees": TIERS,
        "families": FAMILIES,
        "swatches": sw,
    }
    (out / "tilt_palette.json").write_text(json.dumps(payload, indent=2) + "\n")

    print(f"wrote {out / 'tilt_palette.png'} ({width}x{height})")
    print(f"wrote {out / 'tilt_palette.json'} ({len(sw)} swatches)")
    for fam, tiers in FAMILIES.items():
        print(f"  {fam:22s} -> {', '.join(tiers)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
