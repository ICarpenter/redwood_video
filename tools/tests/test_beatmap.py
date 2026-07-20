import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import beatmap


class GenerateRowsTest(unittest.TestCase):
    def test_two_seconds_at_120(self):
        rows = beatmap.generate_rows(bpm=120, length_s=2)
        # beats at 0, 0.5, 1.0, 1.5, 2.0 s; timeline frame 1 = song time 0
        self.assertEqual([r["frame"] for r in rows], [1, 13, 25, 37, 49])
        self.assertEqual(
            [(r["bar"], r["beat"]) for r in rows],
            [(1, 1), (1, 2), (1, 3), (1, 4), (2, 1)],
        )
        self.assertEqual(rows[1]["time_s"], 0.5)

    def test_length_cutoff(self):
        rows = beatmap.generate_rows(bpm=60, length_s=2.5)
        self.assertEqual(len(rows), 3)  # beats at 0, 1, 2 s

    def test_rejects_non_positive_bpm(self):
        with self.assertRaisesRegex(ValueError, "bpm"):
            beatmap.generate_rows(bpm=0, length_s=10)
        with self.assertRaisesRegex(ValueError, "bpm"):
            beatmap.generate_rows(bpm=-80, length_s=10)

    def test_rejects_negative_length(self):
        with self.assertRaisesRegex(ValueError, "length"):
            beatmap.generate_rows(bpm=120, length_s=-1)


if __name__ == "__main__":
    unittest.main()
