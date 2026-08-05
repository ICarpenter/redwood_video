"""The albedo palette: neutrals, bold primaries, and shaded hue families.

Derived from a colour census of refs/styles/ and refs/pallete refs/ (60s and
80s), 31 images, 2.48M pixels. The palette offers colours and says what each
is for; nothing here enforces anything.
"""
import colorsys
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import albedo_palette as ap
import palette_common as pc


def hsv(rgb8):
    return colorsys.rgb_to_hsv(*(c / 255 for c in rgb8))


class StructureTest(unittest.TestCase):
    def test_four_or_five_bold_primaries(self):
        bold = [n for n, s in ap.swatches().items() if s["group"] == "bold"]
        bases = {ap.swatches()[n]["family"] for n in bold}
        self.assertGreaterEqual(len(bases), 4)
        self.assertLessEqual(len(bases), 5)

    def test_every_major_hue_family_is_present(self):
        families = {s["family"] for s in ap.swatches().values()
                    if s["group"] == "family"}
        for expected in ("red", "orange", "yellow", "green",
                         "teal", "blue", "purple", "pink"):
            self.assertIn(expected, families)

    def test_every_family_carries_light_and_dark_shades(self):
        by_family = {}
        for name, s in ap.swatches().items():
            if s["group"] == "family":
                by_family.setdefault(s["family"], set()).add(s["shade"])
        for family, shades in by_family.items():
            self.assertEqual(shades, set(ap.SHADES), f"{family} has {shades}")

    def test_neutrals_span_paper_to_ink(self):
        neutrals = [s for s in ap.swatches().values() if s["group"] == "neutral"]
        values = sorted(hsv(s["rgb8"])[2] for s in neutrals)
        self.assertGreater(values[-1], 0.93, "no paper-white neutral")
        self.assertLess(values[0], 0.20, "no near-black neutral")

    def test_palette_fits_the_lut(self):
        self.assertLessEqual(len(ap.swatches()), pc.LUT_WIDTH)

    def test_swatch_names_are_unique(self):
        names = list(ap.swatches())
        self.assertEqual(len(names), len(set(names)))

    def test_every_swatch_says_what_it_is_for(self):
        for name, s in ap.swatches().items():
            self.assertTrue(s["role"].strip(), f"{name} has no role")

    def test_mint_survives_a_palette_rebuild(self):
        """Mint is film canon, not a census result — the truck and the sweet
        tea. A palette derived purely from clustering drops it, because the
        refs contain no truck. It has to be carried deliberately."""
        sw = ap.swatches()
        self.assertIn("mint", sw)
        self.assertIn("reserved", sw["mint"]["role"].lower())

    def test_mint_stays_distinct_from_the_teal_sky(self):
        """The separation the treatment relies on: sky-teal is deep and
        dusty, mint pale and saturated. If they converge, mint stops being
        a signal."""
        mint = hsv(ap.swatches()["mint"]["rgb8"])
        teal = hsv(ap.swatches()["teal"]["rgb8"])
        self.assertGreater(mint[2], teal[2], "mint is not paler than teal")


class BoldnessTest(unittest.TestCase):
    """The bold primaries are the rare saturated notes the refs spend
    sparingly — a bold that is not actually saturated is not a bold."""

    def test_bold_primaries_are_genuinely_saturated(self):
        for name, s in ap.swatches().items():
            if s["group"] == "bold" and s["shade"] == "base":
                self.assertGreater(hsv(s["rgb8"])[1], 0.60, name)

    def test_bold_teal_and_yellow_are_present(self):
        """The two the census is loudest about: teal is 19.5% of all bold
        pixels, yellow 9.3%."""
        families = {s["family"] for s in ap.swatches().values()
                    if s["group"] == "bold"}
        self.assertIn("teal", families)
        self.assertIn("yellow", families)

    def test_neutrals_are_not_saturated(self):
        """Near-blacks are exempt: at V below ~0.15 a one-byte channel
        difference reads as high saturation while the colour is visually
        black, so the number stops meaning anything."""
        for name, s in ap.swatches().items():
            if s["group"] == "neutral":
                h, sat, v = hsv(s["rgb8"])
                if v < 0.15:
                    continue
                self.assertLess(sat, 0.35, f"{name} (V {v:.2f})")


class ShadeRampTest(unittest.TestCase):
    def test_shades_run_light_to_dark_without_ties(self):
        for family in ap.FAMILIES:
            values = [hsv(ap.swatches()[ap.swatch_name(family, sh)]["rgb8"])[2]
                      for sh in ap.SHADES]
            self.assertEqual(values, sorted(values, reverse=True),
                             f"{family} shades are not monotonic: {values}")
            self.assertEqual(len(set(values)), len(values),
                             f"{family} has duplicate values")

    def test_hue_stays_put_across_a_family(self):
        """Shadow colour is the render's job — the global shadow tint shifts
        hue at shading time. Baking a hue shift into the ramp would double it,
        the same reason albedo carries no directional shading."""
        for family in ap.FAMILIES:
            hues = []
            for sh in ap.SHADES:
                h, s, v = hsv(ap.swatches()[ap.swatch_name(family, sh)]["rgb8"])
                if s > 0.15:
                    hues.append(h * 360)
            spread = max(hues) - min(hues)
            self.assertLess(spread, 12.0, f"{family} hue drifts {spread:.1f} deg")

    def test_shades_stay_inside_the_gamut(self):
        for name, s in ap.swatches().items():
            for c in s["rgb8"]:
                self.assertGreaterEqual(c, 0, name)
                self.assertLessEqual(c, 255, name)


class OrderingTest(unittest.TestCase):
    def test_ordering_covers_every_swatch_once(self):
        ordered = ap.ordered_names()
        self.assertEqual(sorted(ordered), sorted(ap.swatches()))
        self.assertEqual(len(set(ordered)), len(ordered))

    def test_ordering_is_deterministic(self):
        self.assertEqual(ap.ordered_names(), ap.ordered_names())

    def test_a_family_occupies_a_contiguous_run_of_indices(self):
        """Adjacent LUT indices should be near-neighbours in colour, so the
        blended texel at an antialiased dab edge lands on a transitional
        swatch. Scattering a family across the LUT breaks that."""
        ordered = ap.ordered_names()
        sw = ap.swatches()
        seen_runs = {}
        for i, name in enumerate(ordered):
            key = (sw[name]["group"], sw[name]["family"])
            seen_runs.setdefault(key, []).append(i)
        for key, idxs in seen_runs.items():
            self.assertEqual(idxs, list(range(idxs[0], idxs[0] + len(idxs))),
                             f"{key} is not contiguous: {idxs}")


if __name__ == "__main__":
    unittest.main()
