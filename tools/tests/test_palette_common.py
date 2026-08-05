"""The index-encoding core shared by both dab palettes.

A dab is painted as an *index*, not a colour: the paint target stores
R = albedo swatch index and G = tilt swatch index, and a 256x1 LUT resolves
each index to its real value. Every test here guards that round-trip. An
off-by-one in this module means every dab in the film is the wrong swatch.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import palette_common as pc


class IndexRoundTripTest(unittest.TestCase):
    """index -> brush colour -> 8-bit texel -> index, exact for all 256."""

    def test_every_index_survives_the_round_trip(self):
        for i in range(256):
            channel = pc.channel_for_index(i)
            texel = round(channel * 255)  # what an 8-bit image stores
            self.assertEqual(pc.index_for_channel(texel / 255), i, f"index {i}")

    def test_channel_for_index_spans_zero_to_one(self):
        self.assertEqual(pc.channel_for_index(0), 0.0)
        self.assertEqual(pc.channel_for_index(255), 1.0)

    def test_index_for_channel_clamps_out_of_range_input(self):
        self.assertEqual(pc.index_for_channel(-0.5), 0)
        self.assertEqual(pc.index_for_channel(1.5), 255)

    def test_index_out_of_range_is_rejected(self):
        with self.assertRaises(ValueError):
            pc.channel_for_index(256)
        with self.assertRaises(ValueError):
            pc.channel_for_index(-1)


class LutAddressingTest(unittest.TestCase):
    """The shader's multiply-add must hit each LUT texel dead centre."""

    def test_shader_math_matches_the_ideal_texel_centre(self):
        # lut_u_from_channel is what the node graph computes from the sampled
        # texel; lut_u_from_index is where we want to land. They must agree.
        for i in range(256):
            got = pc.lut_u_from_channel(pc.channel_for_index(i))
            self.assertAlmostEqual(got, pc.lut_u_from_index(i), places=12, msg=f"index {i}")

    def test_every_index_lands_inside_its_own_texel(self):
        for i in range(256):
            self.assertEqual(int(pc.lut_u_from_index(i) * 256), i, f"index {i}")

    def test_texel_centre_is_half_a_texel_in(self):
        self.assertAlmostEqual(pc.lut_u_from_index(0) * 256, 0.5)
        self.assertAlmostEqual(pc.lut_u_from_index(255) * 256, 255.5)


class OrderingHashTest(unittest.TestCase):
    """Painted pixels are index references, so palette order is load-bearing."""

    def test_same_ordering_hashes_the_same(self):
        names = ["flat", "h12_whisper", "h01_whisper"]
        self.assertEqual(pc.ordering_hash(names), pc.ordering_hash(list(names)))

    def test_reordering_changes_the_hash(self):
        a = pc.ordering_hash(["flat", "h12_whisper", "h01_whisper"])
        b = pc.ordering_hash(["flat", "h01_whisper", "h12_whisper"])
        self.assertNotEqual(a, b)

    def test_appending_changes_the_hash(self):
        a = pc.ordering_hash(["flat", "h12_whisper"])
        b = pc.ordering_hash(["flat", "h12_whisper", "h01_whisper"])
        self.assertNotEqual(a, b)


class LutImageTest(unittest.TestCase):
    def test_lut_rows_are_256_texels_wide_whatever_the_palette_size(self):
        row = pc.lut_row([(255, 0, 0), (0, 255, 0)])
        self.assertEqual(len(row), 256 * 3)

    def test_each_swatch_sits_at_its_own_index(self):
        row = pc.lut_row([(1, 2, 3), (4, 5, 6), (7, 8, 9)])
        self.assertEqual(tuple(row[0:3]), (1, 2, 3))
        self.assertEqual(tuple(row[3:6]), (4, 5, 6))
        self.assertEqual(tuple(row[6:9]), (7, 8, 9))

    def test_unused_indices_are_black_not_garbage(self):
        row = pc.lut_row([(1, 2, 3)])
        self.assertEqual(tuple(row[3:6]), (0, 0, 0))
        self.assertEqual(tuple(row[-3:]), (0, 0, 0))

    def test_a_palette_larger_than_256_is_rejected(self):
        with self.assertRaises(ValueError):
            pc.lut_row([(0, 0, 0)] * 257)


if __name__ == "__main__":
    unittest.main()
