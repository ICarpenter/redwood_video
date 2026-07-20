import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import shotlib

HEADER = "sq,sh,description,start_frame,end_frame,duration,assets,status\n"


class ShotPathsTest(unittest.TestCase):
    def test_shot_code(self):
        self.assertEqual(shotlib.shot_code("010", "020"), "sq010_sh020")

    def test_shot_blend_path(self):
        root = Path("/proj")
        self.assertEqual(
            shotlib.shot_blend("010", "020", root),
            Path("/proj/shots/sq010/sh020/sh020.blend"),
        )

    def test_render_dir(self):
        self.assertEqual(
            shotlib.render_dir("010", "020", Path("/proj")),
            Path("/proj/render/sq010_sh020"),
        )


class BeatToFrameTest(unittest.TestCase):
    def test_120bpm_24fps(self):
        self.assertEqual(shotlib.beat_to_frame(0, 120), 0)
        self.assertEqual(shotlib.beat_to_frame(1, 120), 12)
        self.assertEqual(shotlib.beat_to_frame(4, 120), 48)

    def test_rounding(self):
        # 92 bpm: beat 1 = 0.6522 s = 15.65 frames -> 16
        self.assertEqual(shotlib.beat_to_frame(1, 92), 16)


class ReadShotlistTest(unittest.TestCase):
    def write(self, body, header=HEADER):
        f = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False)
        f.write(header + body)
        f.close()
        self.addCleanup(os.unlink, f.name)
        return Path(f.name)

    def test_happy_path(self):
        p = self.write("010,010,opening,1,48,48,chars/redwood;envs/forest,boarded\n")
        (shot,) = shotlib.read_shotlist(p)
        self.assertEqual(shot.code, "sq010_sh010")
        self.assertEqual(
            (shot.start_frame, shot.end_frame, shot.duration), (1, 48, 48)
        )
        self.assertEqual(shot.assets, ["chars/redwood", "envs/forest"])

    def test_scripted_status_ok(self):
        p = self.write("010,010,x,1,48,,,scripted\n")
        (shot,) = shotlib.read_shotlist(p)
        self.assertEqual(shot.status, "scripted")

    def test_blank_duration_and_assets_ok(self):
        p = self.write("020,030,mid,49,72,,,animated\n")
        (shot,) = shotlib.read_shotlist(p)
        self.assertEqual(shot.duration, 24)
        self.assertEqual(shot.assets, [])

    def test_bad_status(self):
        p = self.write("010,010,x,1,48,48,,later\n")
        with self.assertRaisesRegex(ValueError, "status"):
            shotlib.read_shotlist(p)

    def test_duration_mismatch(self):
        p = self.write("010,010,x,1,48,40,,boarded\n")
        with self.assertRaisesRegex(ValueError, "duration"):
            shotlib.read_shotlist(p)

    def test_bad_ids(self):
        p = self.write("10,010,x,1,48,,,boarded\n")
        with self.assertRaisesRegex(ValueError, "3-digit"):
            shotlib.read_shotlist(p)

    def test_end_before_start(self):
        p = self.write("010,010,x,48,1,,,boarded\n")
        with self.assertRaisesRegex(ValueError, "end_frame"):
            shotlib.read_shotlist(p)

    def test_duplicate_shot(self):
        p = self.write(
            "010,010,x,1,48,,,boarded\n010,010,y,49,60,,,boarded\n"
        )
        with self.assertRaisesRegex(ValueError, "duplicate"):
            shotlib.read_shotlist(p)

    def test_bad_header(self):
        p = self.write("010,010\n", header="sq,sh\n")
        with self.assertRaisesRegex(ValueError, "header"):
            shotlib.read_shotlist(p)

    def test_non_numeric_duration(self):
        p = self.write("010,010,x,1,48,abc,,boarded\n")
        with self.assertRaisesRegex(ValueError, r"duration"):
            shotlib.read_shotlist(p)

    def test_short_row(self):
        p = self.write("010,010,x,1,48\n")
        with self.assertRaisesRegex(ValueError, r"columns"):
            shotlib.read_shotlist(p)


class ReadSectionsTest(unittest.TestCase):
    HEADER = "section,start_bar,end_bar,start_frame,end_frame\n"

    def write(self, body):
        f = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False)
        f.write(self.HEADER + body)
        f.close()
        self.addCleanup(os.unlink, f.name)
        return Path(f.name)

    def test_happy_path(self):
        p = self.write("intro,0,19,1,776\nverse_1,19,39,777,1593\n")
        intro, verse = shotlib.read_sections(p)
        self.assertEqual((intro.name, intro.start_frame, intro.end_frame),
                         ("intro", 1, 776))
        self.assertEqual((verse.start_bar, verse.end_bar), (19, 39))

    def test_end_before_start(self):
        p = self.write("intro,0,19,776,1\n")
        with self.assertRaisesRegex(ValueError, "end_frame"):
            shotlib.read_sections(p)

    def test_duplicate_section(self):
        p = self.write("intro,0,19,1,776\nintro,19,39,777,1593\n")
        with self.assertRaisesRegex(ValueError, "duplicate"):
            shotlib.read_sections(p)


class FindTrackTest(unittest.TestCase):
    def test_finds_audio_file(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "audio" / "track").mkdir(parents=True)
            (root / "audio" / "track" / "song.wav").touch()
            (root / "audio" / "track" / "notes.txt").touch()
            self.assertEqual(shotlib.find_track(root).name, "song.wav")

    def test_none_when_empty(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(shotlib.find_track(Path(d)))


class NextVersionTest(unittest.TestCase):
    def test_missing_dir(self):
        self.assertEqual(shotlib.next_version(Path("/nonexistent/x")), "v001")

    def test_increments_ignoring_noise(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "v001").mkdir()
            (Path(d) / "v002").mkdir()
            (Path(d) / "notes.txt").touch()
            self.assertEqual(shotlib.next_version(Path(d)), "v003")


class FindBlenderTest(unittest.TestCase):
    def test_env_override(self):
        old = os.environ.get("BLENDER")
        os.environ["BLENDER"] = sys.executable  # any file that exists
        try:
            self.assertEqual(shotlib.find_blender(), sys.executable)
        finally:
            if old is None:
                del os.environ["BLENDER"]
            else:
                os.environ["BLENDER"] = old


if __name__ == "__main__":
    unittest.main()
