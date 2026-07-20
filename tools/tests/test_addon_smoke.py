import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import shotlib

ROOT = Path(__file__).resolve().parent.parent.parent
CHECK = ROOT / "tools" / "tests" / "check_addon.py"


class AddonSmokeTest(unittest.TestCase):
    def setUp(self):
        try:
            self.blender = shotlib.find_blender()
        except FileNotFoundError:
            self.skipTest("Blender not found; set $BLENDER")

    def test_add_guide_instance(self):
        r = subprocess.run(
            [self.blender, "--background", "--factory-startup",
             "--python-exit-code", "1", "--python", str(CHECK)],
            capture_output=True, text=True,
        )
        self.assertEqual(r.returncode, 0, msg=r.stdout + "\n" + r.stderr)
        self.assertIn("ADDON CHECK OK", r.stdout)


if __name__ == "__main__":
    unittest.main()
