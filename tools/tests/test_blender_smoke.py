import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import shotlib

ROOT = Path(__file__).resolve().parent.parent.parent
CHECK = ROOT / "tools" / "tests" / "check_blender.py"


class BlenderSmokeTest(unittest.TestCase):
    def setUp(self):
        try:
            self.blender = shotlib.find_blender()
        except FileNotFoundError:
            self.skipTest("Blender not found; set $BLENDER")

    def test_guide_and_layout_checks(self):
        r = subprocess.run(
            [self.blender, "--background", "--factory-startup",
             "--python-exit-code", "1", "--python", str(CHECK)],
            capture_output=True, text=True,
        )
        self.assertEqual(r.returncode, 0, msg=r.stdout + "\n" + r.stderr)
        self.assertIn("ALL CHECKS OK", r.stdout)


if __name__ == "__main__":
    unittest.main()
