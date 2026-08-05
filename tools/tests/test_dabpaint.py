"""The bpy-free core of the dab painter add-on.

Everything the add-on decides *before* it touches Blender lives here: what an
asset's files are called, what colour the brush has to carry to paint a given
(albedo, tilt) pair, and whether a palette has moved under existing artwork.
Keeping it out of bpy is what makes it testable at all.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import albedo_palette as ap
import dabpaint
import palette_common as pc


class AssetStemTest(unittest.TestCase):
    """<asset> is the active material name lowercased — every generated file
    for an asset shares the stem, so they sort together and can't drift."""

    def test_uses_the_active_material_name_lowercased(self):
        self.assertEqual(dabpaint.asset_stem("MCM_C10_Body", "LowBody"), "mcm_c10_body")

    def test_falls_back_to_the_object_when_there_is_no_material(self):
        self.assertEqual(dabpaint.asset_stem(None, "LowBody"), "lowbody")
        self.assertEqual(dabpaint.asset_stem("", "LowBody"), "lowbody")

    def test_characters_that_break_filenames_become_underscores(self):
        self.assertEqual(dabpaint.asset_stem("MCM Toon.001", "x"), "mcm_toon_001")
        self.assertEqual(dabpaint.asset_stem("a/b", "x"), "a_b")

    def test_every_generated_file_shares_the_stem(self):
        stem = dabpaint.asset_stem("MCM_C10_Body", "LowBody")
        self.assertEqual(dabpaint.index_map_name(stem), "mcm_c10_body_dabindex.png")
        self.assertEqual(dabpaint.baked_albedo_name(stem), "mcm_c10_body_albedo.png")
        self.assertEqual(dabpaint.baked_tilt_name(stem), "mcm_c10_body_tilt.png")


class BrushColorTest(unittest.TestCase):
    """The add-on's only job during a stroke: having set brush.color."""

    def test_encodes_albedo_in_red_and_tilt_in_green(self):
        self.assertEqual(dabpaint.brush_color_for(0, 0), (0.0, 0.0, 0.0))
        self.assertEqual(dabpaint.brush_color_for(255, 255), (1.0, 1.0, 0.0))

    def test_blue_is_unused_and_stays_zero(self):
        for a, t in ((0, 0), (17, 200), (255, 3)):
            self.assertEqual(dabpaint.brush_color_for(a, t)[2], 0.0)

    def test_the_two_axes_are_independent(self):
        """Any albedo with any tilt — no pair table, nothing to keep in sync."""
        self.assertEqual(dabpaint.brush_color_for(10, 200)[0], pc.channel_for_index(10))
        self.assertEqual(dabpaint.brush_color_for(10, 200)[1], pc.channel_for_index(200))

    def test_every_pair_survives_the_round_trip(self):
        for a in range(0, 256, 7):
            for t in range(0, 256, 11):
                colour = dabpaint.brush_color_for(a, t)
                texels = tuple(round(c * 255) for c in colour)
                self.assertEqual(dabpaint.indices_from_texels(texels), (a, t))

    def test_an_index_outside_the_palette_is_refused(self):
        with self.assertRaises(ValueError):
            dabpaint.brush_color_for(256, 0)


class PaletteLoadingTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        ap.main(["--out", str(self.dir)])
        self.path = self.dir / "albedo_palette.json"

    def tearDown(self):
        self.tmp.cleanup()

    def test_swatches_come_back_in_lut_order(self):
        p = dabpaint.load_palette(self.path)
        self.assertEqual(p.ordering, ap.ordered_names())
        self.assertEqual(p.index_of(p.ordering[0]), 0)
        self.assertEqual(p.index_of(p.ordering[-1]), len(p.ordering) - 1)

    def test_a_swatch_reports_its_colour_and_its_guidance(self):
        p = dabpaint.load_palette(self.path)
        mint = p.swatch("mint")
        self.assertEqual(mint["hex"], "#76e7cd")
        self.assertEqual(mint["family"], "mint")
        self.assertIn("truck", mint["role"])

    def test_an_unknown_swatch_is_refused_by_name(self):
        p = dabpaint.load_palette(self.path)
        with self.assertRaises(KeyError):
            p.index_of("chartreuse")

    def test_a_missing_palette_names_the_command_that_builds_it(self):
        with tempfile.TemporaryDirectory() as empty:
            with self.assertRaises(dabpaint.PaletteMissing) as cm:
                dabpaint.load_palette(Path(empty) / "albedo_palette.json")
            self.assertIn("python3 tools/albedo_palette.py", str(cm.exception))

    def test_a_missing_tilt_palette_names_its_own_generator(self):
        with tempfile.TemporaryDirectory() as empty:
            with self.assertRaises(dabpaint.PaletteMissing) as cm:
                dabpaint.load_palette(Path(empty) / "tilt_palette.json")
            self.assertIn("python3 tools/tilt_palette.py", str(cm.exception))


class OrderingDriftTest(unittest.TestCase):
    """Painted pixels reference swatches by position. Appending is safe;
    reordering silently repaints everything already painted."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        ap.main(["--out", str(self.dir)])
        self.path = self.dir / "albedo_palette.json"

    def tearDown(self):
        self.tmp.cleanup()

    def test_an_untouched_palette_reports_no_drift(self):
        p = dabpaint.load_palette(self.path)
        self.assertFalse(p.has_drifted(p.ordering_hash))

    def test_a_reordered_palette_is_caught(self):
        p = dabpaint.load_palette(self.path)
        stale = pc.ordering_hash(list(reversed(p.ordering)))
        self.assertTrue(p.has_drifted(stale))

    def test_no_stored_hash_is_not_treated_as_drift(self):
        """A first-time setup has nothing to compare against."""
        p = dabpaint.load_palette(self.path)
        self.assertFalse(p.has_drifted(""))


class ImageSpecTest(unittest.TestCase):
    """8-bit Non-Color Closest is what makes the round-trip exact. Linear
    interpolation or an sRGB colorspace breaks it silently, so the spec is
    data the shell applies and re-applies rather than a one-time setup."""

    def test_index_map_is_non_color_and_unfiltered(self):
        spec = dabpaint.INDEX_MAP_SPEC
        self.assertEqual(spec["colorspace"], "Non-Color")
        self.assertEqual(spec["interpolation"], "Closest")
        self.assertFalse(spec["float_buffer"])

    def test_albedo_lut_is_srgb_and_tilt_lut_is_not(self):
        self.assertEqual(dabpaint.ALBEDO_LUT_SPEC["colorspace"], "sRGB")
        self.assertEqual(dabpaint.TILT_LUT_SPEC["colorspace"], "Non-Color")

    def test_both_luts_are_sampled_closest(self):
        self.assertEqual(dabpaint.ALBEDO_LUT_SPEC["interpolation"], "Closest")
        self.assertEqual(dabpaint.TILT_LUT_SPEC["interpolation"], "Closest")

    def test_offered_resolutions_are_powers_of_two(self):
        for r in dabpaint.RESOLUTIONS:
            self.assertEqual(r & (r - 1), 0, f"{r} is not a power of two")


class DriftReportTest(unittest.TestCase):
    def test_a_healthy_setup_reports_nothing_wrong(self):
        issues = dabpaint.setup_issues(
            colorspace="Non-Color", interpolation="Closest",
            has_uv=True, luts_linked=True,
        )
        self.assertEqual(issues, [])

    def test_each_drift_is_named_in_its_own_message(self):
        issues = dabpaint.setup_issues(
            colorspace="sRGB", interpolation="Linear",
            has_uv=False, luts_linked=False,
        )
        joined = " ".join(issues).lower()
        self.assertEqual(len(issues), 4)
        for expected in ("colorspace", "interpolation", "uv", "lut"):
            self.assertIn(expected, joined)


if __name__ == "__main__":
    unittest.main()
