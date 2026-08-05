"""The albedo half of the dab palette.

Colour swatches for the Mid-Century Print candidate: the treatment's core
and annex bases, each with drift variants for dab-level colour variation.
The palette offers options and says what they're for; nothing here enforces
anything (see the treatment's palette section).
"""
import colorsys
import statistics
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import albedo_palette as ap
import palette_common as pc


def hue_of(rgb8):
    r, g, b = (c / 255 for c in rgb8)
    return colorsys.rgb_to_hsv(r, g, b)[0] * 360.0


def sat_of(rgb8):
    r, g, b = (c / 255 for c in rgb8)
    return colorsys.rgb_to_hsv(r, g, b)[1]


def value_of(rgb8):
    r, g, b = (c / 255 for c in rgb8)
    return colorsys.rgb_to_hsv(r, g, b)[2]


def signed_hue_delta(a, b):
    """Shortest signed rotation from hue a to hue b, in degrees."""
    return (b - a + 180.0) % 360.0 - 180.0


class BasesTest(unittest.TestCase):
    def test_eleven_core_bases_and_four_annex(self):
        core = [b for b in ap.BASES.values() if b["group"] == "core"]
        annex = [b for b in ap.BASES.values() if b["group"] == "annex"]
        self.assertEqual(len(core), 11)
        self.assertEqual(len(annex), 4)

    def test_base_hexes_match_the_treatment(self):
        # docs/treatment/style-midcentury-print.md palette tables. If the
        # treatment retunes a swatch, this is the test that notices.
        self.assertEqual(ap.BASES["paper-cream"]["hex"], "#f2e4cc")
        self.assertEqual(ap.BASES["sky-teal"]["hex"], "#3fbdb3")
        self.assertEqual(ap.BASES["mint"]["hex"], "#76e7cd")
        self.assertEqual(ap.BASES["charcoal-plastic"]["hex"], "#42403b")
        self.assertEqual(ap.BASES["mall-mauve"]["hex"], "#a98794")

    def test_every_base_says_what_it_is_for(self):
        for name, base in ap.BASES.items():
            self.assertTrue(base["role"].strip(), f"{name} has no role text")


class DriftTest(unittest.TestCase):
    def test_each_base_carries_five_drifts_plus_itself(self):
        sw = ap.swatches()
        for name in ap.BASES:
            variants = [k for k in sw if sw[k]["base"] == name]
            self.assertEqual(len(variants), 6, f"{name} has {len(variants)}")

    def test_ninety_swatches_total(self):
        self.assertEqual(len(ap.swatches()), 90)

    def test_hue_rotation_applies_the_same_delta_to_every_base(self):
        """The reason drift is HSV and not an RGB multiply.

        Measured 2026-08-04: an RGB multiply-cool swings paper-cream 174
        degrees of hue into blue-grey, while other bases barely move. A hue
        rotation moves every base by the same amount by construction, so
        'cool' means one thing film-wide.

        Near-neutral bases are excluded: hue is numerically unstable when
        saturation approaches zero, so their delta is meaningless rather
        than wrong.
        """
        sw = ap.swatches()
        for drift, expected in (("warm", -8.0), ("cool", +8.0)):
            deltas = []
            for name, base in ap.BASES.items():
                if sat_of(base["rgb8"]) < 0.15:
                    continue
                got = sw[f"{name}_{drift}"]["rgb8"]
                deltas.append(signed_hue_delta(hue_of(base["rgb8"]), hue_of(got)))
            self.assertGreater(len(deltas), 8, "too few saturated bases to judge")
            for d in deltas:
                self.assertAlmostEqual(d, expected, delta=2.0)
            self.assertLess(statistics.pstdev(deltas), 1.0, f"{drift} is not uniform")

    def test_drifts_stay_inside_the_rgb_gamut(self):
        for name, s in ap.swatches().items():
            for c in s["rgb8"]:
                self.assertGreaterEqual(c, 0, name)
                self.assertLessEqual(c, 255, name)

    def test_pale_desaturates_and_deep_saturates(self):
        sw = ap.swatches()
        for name, base in ap.BASES.items():
            if sat_of(base["rgb8"]) < 0.15:
                continue
            self.assertLess(sat_of(sw[f"{name}_pale"]["rgb8"]), sat_of(base["rgb8"]), name)
            self.assertGreater(sat_of(sw[f"{name}_deep"]["rgb8"]), sat_of(base["rgb8"]), name)

    def test_dusk_darkens(self):
        sw = ap.swatches()
        for name, base in ap.BASES.items():
            self.assertLess(value_of(sw[f"{name}_dusk"]["rgb8"]), value_of(base["rgb8"]), name)


class OrderingTest(unittest.TestCase):
    """LUT position is what a painted pixel references, so order is data."""

    def test_ordered_by_hue_then_value(self):
        ordered = ap.ordered_names()
        keys = [ap.sort_key(n) for n in ordered]
        self.assertEqual(keys, sorted(keys))

    def test_ordering_is_deterministic(self):
        self.assertEqual(ap.ordered_names(), ap.ordered_names())

    def test_ordering_covers_every_swatch_exactly_once(self):
        ordered = ap.ordered_names()
        self.assertEqual(len(ordered), len(ap.swatches()))
        self.assertEqual(len(set(ordered)), len(ordered))

    def test_neighbouring_indices_are_near_neighbours_in_colour(self):
        """Antialiased dab edges blend two indices into a third. With a
        similarity-ordered LUT that third entry is a transitional colour
        rather than a stray one."""
        sw = ap.swatches()
        ordered = ap.ordered_names()
        jumps = [
            abs(signed_hue_delta(hue_of(sw[a]["rgb8"]), hue_of(sw[b]["rgb8"])))
            for a, b in zip(ordered, ordered[1:])
            if sat_of(sw[a]["rgb8"]) >= 0.15 and sat_of(sw[b]["rgb8"]) >= 0.15
        ]
        self.assertLess(statistics.median(jumps), 15.0)

    def test_palette_fits_the_lut(self):
        self.assertLessEqual(len(ap.swatches()), pc.LUT_WIDTH)


class NamingTest(unittest.TestCase):
    def test_swatch_names_are_unique(self):
        names = list(ap.swatches())
        self.assertEqual(len(names), len(set(names)))

    def test_a_base_keeps_its_own_bare_name(self):
        sw = ap.swatches()
        self.assertIn("terracotta", sw)
        self.assertIn("terracotta_warm", sw)
        self.assertEqual(sw["terracotta"]["drift"], None)
        self.assertEqual(sw["terracotta_warm"]["drift"], "warm")


if __name__ == "__main__":
    unittest.main()
