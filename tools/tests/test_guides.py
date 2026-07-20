import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import guides


class RegistryTest(unittest.TestCase):
    def test_counts(self):
        self.assertEqual(len(guides.GUIDES), 12)
        self.assertEqual(len(guides.guides_for_file(guides.CAST_FILE)), 3)
        self.assertEqual(len(guides.guides_for_file(guides.PROPS_FILE)), 9)

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

    def test_droppable_includes_property_set(self):
        self.assertEqual(len(guides.DROPPABLE), 13)
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
            guides.guides_collection_name("sq010_sh010"), "sq010_sh010_guides"
        )


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
