#!/usr/bin/env python3
"""Shared index-encoding core for the dab palettes.

The dab painter does not paint colour. It paints *indices*: the paint target
stores R = albedo swatch index, G = tilt swatch index, both 0-255, and a
256x1 LUT per channel resolves an index into its real value — a colour for
albedo, a tangent-space normal for tilt. One painted image means Blender's
own undo is the only undo, which is the reason for the whole design
(docs/superpowers/specs/2026-08-04-tilt-dab-painter-design.md).

This module owns the arithmetic that makes the round-trip exact. Everything
here is stdlib-only and free of bpy so it can be unit-tested headlessly and
imported by both the generators and the add-on.
"""
import hashlib
import struct
import zlib
from pathlib import Path

LUT_WIDTH = 256

# --- index encoding ----------------------------------------------------------


def channel_for_index(index):
    """Brush channel value (0..1) that paints `index` into an 8-bit image."""
    if not 0 <= index < LUT_WIDTH:
        raise ValueError(f"index {index} outside 0..{LUT_WIDTH - 1}")
    return index / 255.0


def index_for_channel(value):
    """Recover the index from a sampled 8-bit channel value. Clamps."""
    return round(min(1.0, max(0.0, value)) * 255)


# --- LUT addressing ----------------------------------------------------------
#
# A 256-wide LUT is sampled by UV, so an index has to become the *centre* of
# its texel: (i + 0.5) / 256. The shader only has the sampled channel value
# i/255 to work from, hence the multiply-add below. Landing off-centre makes
# a swatch bleed into its neighbour, which is silent and looks like a palette
# bug rather than an addressing one.


def lut_u_from_channel(value):
    """What the node graph computes from a sampled index texel."""
    return value * (255.0 / LUT_WIDTH) + 0.5 / LUT_WIDTH


def lut_u_from_index(index):
    """Where that value has to land: the centre of texel `index`."""
    return (index + 0.5) / LUT_WIDTH


# --- LUT image ---------------------------------------------------------------


def lut_row(rgb8_values):
    """One 256-texel RGB row: swatch i at index i, unused indices black."""
    if len(rgb8_values) > LUT_WIDTH:
        raise ValueError(f"{len(rgb8_values)} swatches exceeds the {LUT_WIDTH}-entry LUT")
    row = bytearray(LUT_WIDTH * 3)
    for i, rgb in enumerate(rgb8_values):
        row[3 * i : 3 * i + 3] = bytes(rgb)
    return row


# --- ordering ----------------------------------------------------------------


def ordering_hash(names):
    """Fingerprint of palette *order*.

    Painted pixels reference swatches by position, so appending is safe and
    reordering silently repaints the film. The add-on stores this and warns
    when a palette has moved under existing artwork.
    """
    return hashlib.sha256("\n".join(names).encode()).hexdigest()[:16]


# --- PNG (minimal stdlib writer) ---------------------------------------------


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


# --- artifacts ---------------------------------------------------------------


def write_lut_png(path, rgb8_values):
    """The 256x1 lookup every asset's material links.

    Load it Non-Color with Closest interpolation — an sRGB colorspace or
    linear filtering breaks the exact round-trip silently.
    """
    write_png(path, LUT_WIDTH, 1, [lut_row(rgb8_values)])


def write_swatch_icons(dirpath, mapping, size=32):
    """One flat square per swatch, for the add-on's picker grid."""
    d = Path(dirpath)
    d.mkdir(parents=True, exist_ok=True)
    for name, rgb in mapping.items():
        row = bytearray(bytes(tuple(rgb)) * size)
        write_png(d / f"{name}.png", size, size, [row] * size)


def indexed_payload(swatches, ordering):
    """JSON body shared by both generators: order, its hash, and the swatches
    stamped with the LUT index each one occupies."""
    sw = {name: dict(data) for name, data in swatches.items()}
    for i, name in enumerate(ordering):
        sw[name]["index"] = i
    return {
        "ordering": list(ordering),
        "ordering_hash": ordering_hash(ordering),
        "swatches": sw,
    }


# --- picker sheet ------------------------------------------------------------

CELL = 96
GUTTER = 4
MARGIN = 8
BG = (32, 32, 32)


def grid_sheet(cell_rows, cell=CELL, gutter=GUTTER, margin=MARGIN, bg=BG, gaps=()):
    """Render a grid of flat colour cells. Returns (width, height, rows).

    cell_rows: list of rows, each a list of rgb8 tuples.
    gaps: column indices to insert extra separation *before*.
    """
    ncols = max(len(r) for r in cell_rows)
    nrows = len(cell_rows)
    extra = len(gaps) * gutter * 2
    width = 2 * margin + ncols * cell + (ncols - 1) * gutter + extra
    height = 2 * margin + nrows * cell + (nrows - 1) * gutter
    rows = [bytearray(bytes(bg) * width) for _ in range(height)]

    def x_of(cx):
        return margin + cx * (cell + gutter) + sum(gutter * 2 for g in gaps if cx >= g)

    for cy, row_cells in enumerate(cell_rows):
        y0 = margin + cy * (cell + gutter)
        for cx, rgb in enumerate(row_cells):
            x0 = x_of(cx)
            px = bytes(tuple(rgb))
            for y in range(y0, y0 + cell):
                r = rows[y]
                for x in range(x0, x0 + cell):
                    r[3 * x : 3 * x + 3] = px
    return width, height, rows
