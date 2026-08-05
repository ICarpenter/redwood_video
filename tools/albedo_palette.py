#!/usr/bin/env python3
"""Albedo palette for the Mid-Century Print candidate — registry + generator.

The colour half of the dab palette, mirroring `tilt_palette.py`. A dab is an
(albedo x tilt) pair chosen at the brush, and the two palettes are fully
independent axes — any colour with any tilt.

This palette *offers* colours and says what each is for. It enforces nothing:
the mint reservation and the post-1980 annex are art direction recorded in
`docs/treatment/style-midcentury-print.md`, not constraints the tools police.

## Where these came from

A colour census of the reference set (2026-08-04): 31 images across
`refs/styles/`, `refs/pallete refs/60s/` and `refs/pallete refs/80s/`,
2.48M pixels, k-means in display sRGB. Two passes, because the obvious one
lies: clustering by coverage returns almost nothing but paper — 45% of the
corpus sits in the warm cream band — while the colours that define the look
are rare by area. The second pass clustered only pixels above 0.55
saturation, 7.6% of the whole, and that is where the bold five come from.

What the refs actually said, as a share of saturated pixels: orange 45%
(mostly the tan/wood/skin band rather than true orange), red 17%, teal 11%,
yellow 8%, blue 7%, pink 6%, magenta 3%, purple 2% — and **green 1.4%**.

So green is the one region the references do not support, and the film needs
three of them — the sheriff's olive-drab uniform, plants and lawn, and the
grey-green of cacti and agave. They are derived rather than sampled: from the
desaturated sage that does appear (`#a8ceb5`, `#a1d0bc`, `#9eb29d`) and from
the olive already in the treatment, not from a saturated green the refs never
contained. `olive`, `green` and `sage` are the least evidenced part of this
palette; if anything here reads wrong on a lawn, start there.

Four families exist for named production needs rather than census weight —
`rust` (the mountains), `coral` (the sunset sky), `olive` (the uniform) and
`sky` (the dome at its palest). A census of poster art has no opinion about a
sheriff or a cactus.

Stdlib only. Import it for the math; run it for the artifacts.
"""
import argparse
import colorsys
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import palette_common as pc

# --- shades ------------------------------------------------------------------
#
# Hue is held constant across a family. Shadow colour belongs to the render —
# the global shadow tint shifts hue at shading time — so baking a shift into
# the ramp would double it, the same reason albedo carries no directional
# shading. The ramp moves value and saturation only.

SHADES = ("pale", "light", "base", "dark", "deep")

# Lights interpolate *toward* white rather than multiplying value, so a base
# that is already bright still gets five distinct steps. Multiplying clamped
# yellow's pale and light to the same colour, which is a duplicate swatch
# wearing two names and two LUT slots.
_RAMP = {
    "pale": (0.40, 0.72),   # (saturation factor, lift toward white)
    "light": (0.70, 0.40),
    "base": (1.00, 0.00),
    "dark": (1.08, -0.30),  # negative: value multiplied by (1 + lift)
    "deep": (1.14, -0.55),
}

# --- neutrals ----------------------------------------------------------------
#
# The paper the film is printed on, and by far the largest part of the census
# — the single biggest cluster in the whole corpus is #fafaf9 at 22.6%.

_NEUTRALS = [
    ("paper-white", "#fafaf9", "the brightest paper; clouds, highlights"),
    ("paper-cream", "#f0eae0", "the default light base: walls, concrete"),
    ("cream", "#ebd7c5", "warmer paper; interior walls, skin base"),
    ("sand", "#dac3a9", "ground, road, mid-value neutrals"),
    ("tan", "#c7a484", "dry earth, cardboard, secondary ground"),
    ("taupe", "#b7a693", "aged plaster, worn wood"),
    ("stone", "#8a8782", "concrete in shadow, weathered grey"),
    ("slate", "#6b6875", "the 80s mauve-grey; electronics, shadow mass"),
    ("umber", "#6a5346", "dark wood, soil, deep structural darks — curated down from the census centre #72503c, which is too saturated to sit among neutrals"),
    ("ink", "#373134", "near-black warm; tires, the CRT, line-weight mass"),
    ("pitch", "#160e0f", "the darkest note in the film; use sparingly"),
]

# --- bold primaries ----------------------------------------------------------
#
# The rare saturated notes the refs spend deliberately. Ordered by their share
# of saturated pixels in the census.

_BOLD = [
    ("teal", "#0abdb4", "19.5% of all bold pixels — the MCM signature: the "
                        "daytime sky, the 60s poster, appliance enamel"),
    ("rose", "#c93b5e", "12.4% — the 80s raspberry; Mom's world. The census "
                        "centre #c3506b is the dusty version (S 0.59) and "
                        "reads muted beside the other four, so this is pushed "
                        "to bold strength, short of the hot #f2236d"),
    ("yellow", "#fad413", "9.3% — the sun disc, the yellow car, signage"),
    ("red", "#c53b30", "the gouache vest red; hot accents, danger"),
    ("magenta", "#f61480", "the 80s note at full voltage; use once a scene"),
]

# --- hue families ------------------------------------------------------------
#
# A curated base per family, each shaded five ways. Bases are census centres
# except where noted.

_FAMILIES = [
    ("red", "#c04a3c", "brick, roof tile, the cop car's pop"),
    ("rust", "#c65a2e", "the mountains, weathered metal, hot desert accents"),
    ("coral", "#f4a886", "the sunset sky, distant warmth, low sun on stucco"),
    ("orange", "#dd9c55", "terracotta, warm afternoon light, cardboard"),
    ("yellow", "#e8b74a", "golden hour, kitchen enamel, signage"),
    ("olive", "#6f7343", "the sheriff's uniform, dry grass, olive-drab kit"),
    ("green", "#789c66", "plants, lawn, foliage masses — DERIVED, see above"),
    ("sage", "#9db8ac", "cacti, agave, 90s kitchenware — grey-green desert "
                        "planting; DERIVED, see above"),
    ("mint", "#76e7cd", "RESERVED — the truck and the sweet tea, and nothing "
                        "else. Not a census colour: it is film canon from "
                        "docs/treatment/style-midcentury-print.md, kept pale "
                        "AND saturated so it stays distinct from both the "
                        "teal sky and the greyed annex. Shaded so the truck "
                        "can be painted; still spent nowhere else"),
    ("teal", "#3fbdb3", "the deep daytime sky, glass, appliance enamel"),
    ("sky", "#8bd5e3", "the sky dome at its palest; hazy distance, clerestory"),
    ("blue", "#5e94ae", "denim, distance, shadowed sky"),
    ("purple", "#7a6f92", "dusk, the 80s mauve, deep shadow mass"),
    ("pink", "#e48e96", "dusty rose; wardrobe, the pink kitchen"),
]

FAMILIES = [name for name, _, _ in _FAMILIES]
BOLD = [name for name, _, _ in _BOLD]


# --- colour helpers ----------------------------------------------------------


def hex_to_rgb8(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb8_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def shade(rgb8, sat_mul, lift):
    """Move a base along its value ramp, holding hue.

    `lift` > 0 interpolates toward white by that fraction of the headroom;
    < 0 scales value down. Lifting rather than multiplying keeps the steps
    distinct on bases that are already near the top.
    """
    r, g, b = (c / 255.0 for c in rgb8)
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    s = min(1.0, max(0.0, s * sat_mul))
    v = v + (1.0 - v) * lift if lift >= 0 else v * (1.0 + lift)
    v = min(1.0, max(0.0, v))
    return tuple(round(c * 255) for c in colorsys.hsv_to_rgb(h, s, v))


def swatch_name(family, shade_name):
    return family if shade_name == "base" else f"{family}_{shade_name}"


# --- registry ----------------------------------------------------------------


def swatches():
    """All swatches as {name: {group, family, shade, role, rgb8, hex}}."""
    out = {}

    for name, hexcode, role in _NEUTRALS:
        rgb = hex_to_rgb8(hexcode)
        out[name] = _entry("neutral", name, "base", role, rgb)

    # Bold gets base plus one step either side: these are meant to be spent at
    # full strength, so the full five-shade ramp would only dilute them.
    for name, hexcode, role in _BOLD:
        base = hex_to_rgb8(hexcode)
        key = f"bold-{name}"
        out[key] = _entry("bold", name, "base", role, base)
        out[f"{key}_light"] = _entry(
            "bold", name, "light", role, shade(base, 0.72, 0.45))
        out[f"{key}_dark"] = _entry(
            "bold", name, "dark", role, shade(base, 1.08, -0.32))

    for name, hexcode, role in _FAMILIES:
        base = hex_to_rgb8(hexcode)
        for shade_name in SHADES:
            sat_mul, val_mul = _RAMP[shade_name]
            out[swatch_name(name, shade_name)] = _entry(
                "family", name, shade_name, role, shade(base, sat_mul, val_mul))
    return out


def _entry(group, family, shade_name, role, rgb):
    return {
        "group": group,
        "family": family,
        "shade": shade_name,
        "role": role,
        "rgb8": list(rgb),
        "hex": rgb8_to_hex(rgb),
    }


# --- ordering ----------------------------------------------------------------
#
# LUT position is what a painted pixel references. Families are kept in
# contiguous runs, light to dark, so neighbouring indices are near-neighbours
# in colour and the blended texel at an antialiased dab edge resolves to a
# transitional swatch rather than a stray one. Append; never reorder.

_GROUP_ORDER = {"neutral": 0, "bold": 1, "family": 2}
_SHADE_ORDER = {s: i for i, s in enumerate(SHADES)}


def sort_key(name):
    s = swatches()[name]
    group = _GROUP_ORDER[s["group"]]
    if s["group"] == "neutral":
        order = [n for n, _, _ in _NEUTRALS].index(s["family"])
        return (group, order, 0, name)
    if s["group"] == "bold":
        order = BOLD.index(s["family"])
        return (group, order, _SHADE_ORDER[s["shade"]], name)
    return (group, FAMILIES.index(s["family"]), _SHADE_ORDER[s["shade"]], name)


def ordered_names():
    """Every swatch name in LUT order."""
    return sorted(swatches(), key=sort_key)


# --- artifacts ---------------------------------------------------------------


def build_sheet():
    """Picker grid: neutrals, then the bold five, then the shaded families."""
    sw = swatches()
    rows = []
    rows.append([sw[n]["rgb8"] for n, _, _ in _NEUTRALS])
    rows.append([sw[f"bold-{n}{suffix}"]["rgb8"]
                 for n, _, _ in _BOLD
                 for suffix in ("_light", "", "_dark")])
    for name, _, _ in _FAMILIES:
        rows.append([sw[swatch_name(name, s)]["rgb8"] for s in SHADES])
    return pc.grid_sheet(rows, gaps=(0,))


def main(argv=None):
    ap_ = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap_.add_argument(
        "--out",
        default=str(Path(__file__).resolve().parent.parent
                    / "assets/materials/albedo_palette"),
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
            "derived_from": (
                "colour census of refs/styles/ + refs/pallete refs/{60s,80s}, "
                "31 images, 2.48M pixels, 2026-08-04"
            ),
            "green_caveat": (
                "green is 1.4% of saturated pixels in the refs. olive, green "
                "and sage are derived from the desaturated sage that does "
                "appear, not sampled from a saturated green"
            ),
            "shades": "hue held constant; shadow hue belongs to the render",
            "guidance": (
                "group/family/role say what a swatch is for. Nothing is "
                "enforced — see docs/treatment/style-midcentury-print.md"
            ),
        },
        "shades": list(SHADES),
        "bold": BOLD,
        "families": FAMILIES,
        **pc.indexed_payload(sw, ordering),
    }
    (out / "albedo_palette.json").write_text(json.dumps(payload, indent=2) + "\n")

    counts = {}
    for s in sw.values():
        counts[s["group"]] = counts.get(s["group"], 0) + 1
    print(f"wrote {out / 'albedo_palette.png'} ({width}x{height})")
    print(f"wrote {out / 'albedo_lut.png'} (256x1)")
    print(f"wrote {out / 'swatches'}/ ({len(sw)} icons)")
    print(f"wrote {out / 'albedo_palette.json'} ({len(sw)} swatches, "
          f"order {payload['ordering_hash']})")
    print("  " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
