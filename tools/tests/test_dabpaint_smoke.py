import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import shotlib

ROOT = Path(__file__).resolve().parent.parent.parent
CHECK = ROOT / "tools" / "tests" / "check_dabpaint.py"


class DabPaintSmokeTest(unittest.TestCase):
    """End-to-end: write index i into the paint target, render, and confirm
    the pixel is swatch i. Builds its own scene and never touches a repo
    .blend, so it is safe to run while Blender is open elsewhere."""

    def setUp(self):
        try:
            self.blender = shotlib.find_blender()
        except FileNotFoundError:
            self.skipTest("Blender not found; set $BLENDER")

    def test_an_index_resolves_to_its_swatch_through_the_whole_chain(self):
        r = subprocess.run(
            [self.blender, "--background", "--factory-startup",
             "--python-exit-code", "1", "--python", str(CHECK)],
            capture_output=True, text=True,
        )
        self.assertEqual(r.returncode, 0, msg=r.stdout + "\n" + r.stderr)
        self.assertIn("DABPAINT CHECK OK", r.stdout)


if __name__ == "__main__":
    unittest.main()
