import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import build_shots
import shotlib


class PlanBuildsTest(unittest.TestCase):
    def test_skips_existing_unless_forced(self):
        shots = [
            shotlib.Shot("010", "010", "a", 1, 8, [], "boarded"),
            shotlib.Shot("010", "020", "b", 9, 16, [], "boarded"),
        ]
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            existing = shotlib.shot_blend("010", "010", root)
            existing.parent.mkdir(parents=True)
            existing.touch()

            todo = build_shots.plan_builds(shots, root)
            self.assertEqual([s.code for s in todo], ["sq010_sh020"])

            forced = build_shots.plan_builds(shots, root, force=True)
            self.assertEqual(len(forced), 2)


if __name__ == "__main__":
    unittest.main()
