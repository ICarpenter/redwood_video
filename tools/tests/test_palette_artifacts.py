"""The four artifacts each palette generator emits.

These decode the real PNG bytes rather than trusting the writer, because the
whole index scheme rests on a LUT texel holding exactly the byte the palette
says it does. A silently wrong LUT would look like a palette bug, not an
encoding one, and would only surface once something had been painted.
"""
import json
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import albedo_palette as ap
import palette_common as pc
import tilt_palette as tp


def read_png(path):
    """Decode our own 8-bit RGB, non-interlaced, filter-0 PNGs.

    Deliberately minimal: it only understands what write_png emits, so it
    fails loudly if the writer ever changes shape.
    """
    data = Path(path).read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
    pos, width, height, idat = 8, None, None, b""
    while pos < len(data):
        length = struct.unpack(">I", data[pos : pos + 4])[0]
        tag = data[pos + 4 : pos + 8]
        payload = data[pos + 8 : pos + 8 + length]
        if tag == b"IHDR":
            width, height, depth, ctype = struct.unpack(">IIBB", payload[:10])
            assert (depth, ctype) == (8, 2), f"expected 8-bit RGB, got {depth}/{ctype}"
        elif tag == b"IDAT":
            idat += payload
        pos += 12 + length
    raw = zlib.decompress(idat)
    stride = width * 3
    rows = []
    for y in range(height):
        start = y * (stride + 1)
        assert raw[start] == 0, "expected filter type 0"
        rows.append(list(raw[start + 1 : start + 1 + stride]))
    return width, height, rows


class LutTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_lut_is_256_by_1(self):
        pc.write_lut_png(self.dir / "lut.png", [(1, 2, 3)])
        width, height, _ = read_png(self.dir / "lut.png")
        self.assertEqual((width, height), (256, 1))

    def test_each_swatch_decodes_at_its_own_index(self):
        values = [(10, 20, 30), (40, 50, 60), (70, 80, 90)]
        pc.write_lut_png(self.dir / "lut.png", values)
        _, _, rows = read_png(self.dir / "lut.png")
        for i, rgb in enumerate(values):
            self.assertEqual(tuple(rows[0][3 * i : 3 * i + 3]), rgb, f"index {i}")

    def test_albedo_lut_round_trips_every_swatch_exactly(self):
        """The end-to-end promise: paint index i, get swatch i back."""
        sw = ap.swatches()
        ordered = ap.ordered_names()
        pc.write_lut_png(self.dir / "lut.png", [sw[n]["rgb8"] for n in ordered])
        _, _, rows = read_png(self.dir / "lut.png")
        for i, name in enumerate(ordered):
            index = pc.index_for_channel(pc.channel_for_index(i))
            texel = tuple(rows[0][3 * index : 3 * index + 3])
            self.assertEqual(texel, tuple(sw[name]["rgb8"]), f"{name} at index {i}")

    def test_tilt_lut_round_trips_every_swatch_exactly(self):
        sw = tp.swatches()
        ordered = tp.ordered_names()
        pc.write_lut_png(self.dir / "lut.png", [sw[n]["rgb8"] for n in ordered])
        _, _, rows = read_png(self.dir / "lut.png")
        for i, name in enumerate(ordered):
            index = pc.index_for_channel(pc.channel_for_index(i))
            texel = tuple(rows[0][3 * index : 3 * index + 3])
            self.assertEqual(texel, tuple(sw[name]["rgb8"]), f"{name} at index {i}")


class IconTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_one_icon_per_swatch(self):
        pc.write_swatch_icons(self.dir, {"a": (1, 2, 3), "b": (4, 5, 6)})
        self.assertTrue((self.dir / "a.png").exists())
        self.assertTrue((self.dir / "b.png").exists())

    def test_icon_is_a_flat_square_of_its_swatch(self):
        pc.write_swatch_icons(self.dir, {"a": (10, 20, 30)}, size=32)
        width, height, rows = read_png(self.dir / "a.png")
        self.assertEqual((width, height), (32, 32))
        for row in rows:
            for x in range(width):
                self.assertEqual(tuple(row[3 * x : 3 * x + 3]), (10, 20, 30))


class GeneratorOutputTest(unittest.TestCase):
    """Both generators emit the same four artifacts into their own dir."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _check(self, module, stem, lut):
        module.main(["--out", str(self.dir)])
        for artifact in (f"{stem}.json", f"{stem}.png", lut):
            self.assertTrue((self.dir / artifact).exists(), f"missing {artifact}")
        icons = list((self.dir / "swatches").glob("*.png"))
        self.assertEqual(len(icons), len(module.swatches()))

        payload = json.loads((self.dir / f"{stem}.json").read_text())
        self.assertEqual(payload["ordering"], module.ordered_names())
        self.assertEqual(payload["ordering_hash"], pc.ordering_hash(module.ordered_names()))
        self.assertEqual(set(payload["swatches"]), set(module.swatches()))
        return payload

    def test_albedo_generator_emits_all_four(self):
        payload = self._check(ap, "albedo_palette", "albedo_lut.png")
        self.assertEqual(len(payload["ordering"]), len(ap.swatches()))

    def test_tilt_generator_emits_all_four(self):
        payload = self._check(tp, "tilt_palette", "tilt_lut.png")
        self.assertEqual(len(payload["ordering"]), 49)

    def test_json_index_matches_ordering_position(self):
        payload = self._check(ap, "albedo_palette", "albedo_lut.png")
        for i, name in enumerate(payload["ordering"]):
            self.assertEqual(payload["swatches"][name]["index"], i, name)


class TiltOrderingTest(unittest.TestCase):
    """tilt_palette already ordered flat-then-hours-by-tier; that IS
    similarity ordering, so it becomes the LUT order unchanged."""

    def test_flat_is_index_zero(self):
        self.assertEqual(tp.ordered_names()[0], tp.FLAT_NAME)

    def test_ordering_covers_every_swatch_once(self):
        ordered = tp.ordered_names()
        self.assertEqual(sorted(ordered), sorted(tp.swatches()))
        self.assertEqual(len(set(ordered)), len(ordered))

    def test_adjacent_indices_are_adjacent_clock_hours(self):
        ordered = tp.ordered_names()[1:]  # skip flat
        for a, b in zip(ordered, ordered[1:]):
            sa, sb = tp.swatches()[a], tp.swatches()[b]
            if sa["tier"] != sb["tier"]:
                continue
            gap = abs(tp.HOURS.index(sa["hour"]) - tp.HOURS.index(sb["hour"]))
            self.assertEqual(gap, 1, f"{a} -> {b}")


if __name__ == "__main__":
    unittest.main()
