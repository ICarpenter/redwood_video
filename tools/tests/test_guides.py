import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import guides


class RegistryTest(unittest.TestCase):
    def test_counts(self):
        self.assertEqual(len(guides.GUIDES), 28)
        self.assertEqual(len(guides.guides_for_file(guides.CAST_FILE)), 5)
        self.assertEqual(len(guides.guides_for_file(guides.PROPS_FILE)), 23)

    def test_names_unique(self):
        names = [g.name for g in guides.GUIDES]
        self.assertEqual(len(names), len(set(names)))

    def test_every_guide_valid(self):
        for g in guides.GUIDES:
            self.assertIn(g.file, (guides.CAST_FILE, guides.PROPS_FILE))
            self.assertIn(g.catalog, guides.CATALOGS)
            self.assertGreater(g.height, 0.0)

    def test_lookup(self):
        self.assertEqual(guides.guide_by_name("boy").file, guides.CAST_FILE)
        self.assertIsNone(guides.guide_by_name("nope"))

    def test_box_guide(self):
        box = guides.guide_by_name("box")
        self.assertIsNotNone(box)
        self.assertEqual(box.file, guides.PROPS_FILE)
        self.assertEqual(box.catalog, "props")
        self.assertAlmostEqual(box.height, 1.2)

    def test_droppable_includes_property_set(self):
        self.assertEqual(len(guides.DROPPABLE), 30)
        self.assertIn("property", [g.name for g in guides.DROPPABLE])
        prop = guides.guide_by_name("property")
        self.assertIsNotNone(prop)
        self.assertEqual(prop.file, guides.PROPERTY_FILE)
        self.assertEqual(prop.catalog, "set")
        self.assertIn(prop.catalog, guides.CATALOGS)

    def test_property_not_in_buildable_guides(self):
        # property is marked in place, never built by guide_assets
        self.assertNotIn("property", [g.name for g in guides.GUIDES])

    def test_collection_name(self):
        self.assertEqual(
            guides.blocking_collection_name("sq010_sh010"), "sq010_sh010_blocking"
        )

    def test_drop_distance_is_a_positive_fallback(self):
        # Used only when the camera's view ray never meets the z=0 ground
        # plane (camera pointing at or above the horizon).
        self.assertGreater(guides.DROP_DISTANCE, 0.0)

    def test_old_names_are_gone(self):
        self.assertFalse(hasattr(guides, "guides_collection_name"))
        self.assertFalse(hasattr(guides, "DROP_LOCATION"))


class CatsFileTest(unittest.TestCase):
    def test_header_and_lines(self):
        text = guides.cats_file_text()
        self.assertIn("VERSION 1", text)
        for uuid, path, simple in guides.CATALOGS.values():
            self.assertIn(f"{uuid}:{path}:{simple}", text)

    def test_uuids_unique(self):
        uuids = [v[0] for v in guides.CATALOGS.values()]
        self.assertEqual(len(uuids), len(set(uuids)))

    def test_trailing_newline(self):
        self.assertTrue(guides.cats_file_text().endswith("\n"))


if __name__ == "__main__":
    unittest.main()


class TestSets(unittest.TestCase):
    def test_sets_are_droppable_but_not_guides(self):
        names = [s.name for s in guides.SETS]
        self.assertEqual(names, ["property", "trench"])
        for s in guides.SETS:
            self.assertNotIn(s.name, [g.name for g in guides.GUIDES])
            self.assertIn(s.name, [d.name for d in guides.DROPPABLE])
            self.assertEqual(s.catalog, "set")

    def test_trench_resolves_to_its_own_file(self):
        t = guides.guide_by_name("trench")
        self.assertIsNotNone(t)
        self.assertEqual(t.file, guides.TRENCH_FILE)
        self.assertTrue(t.file.startswith("assets/envs/"))

    def test_sheriff_war_is_a_cast_guide(self):
        w = guides.guide_by_name("sheriff_war")
        self.assertIsNotNone(w)
        self.assertEqual(w.file, guides.CAST_FILE)
        self.assertEqual(w.catalog, "cast")
        # same nominal height as the sheriff: it is the same man
        sh = guides.guide_by_name("sheriff")
        self.assertEqual(w.height, sh.height)
