# Redwood Video Project Scaffold Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the studio-style pipeline scaffold for the `redwood_video` music video — folders, git/LFS, docs, shotlist/beatmap CSVs, shot template, and the `tools/` scripts — per the approved spec.

**Architecture:** Pure-stdlib Python helpers in `tools/shotlib.py` shared by CLI scripts (`beatmap.py`, `build_shots.py`) and Blender-side scripts (`make_template.py`, `new_shot.py`) that run headless via `blender --background`. Shell scripts (`render_shot.sh`, `encode_delivery.sh`) share Blender discovery through `tools/env.sh`. `docs/shotlist.csv` is the single source of truth all tools read.

**Tech Stack:** Blender 5.1.2 (headless + bpy), Python 3 stdlib only (must run under both Homebrew python3 and Blender's bundled Python), bash, git + git-LFS, FFmpeg (delivery encodes only), `unittest` for tests.

**Spec:** `docs/superpowers/specs/2026-07-19-redwood-video-pipeline-design.md`

## Global Constraints

- Blender binary: `/Applications/Blender.app/Contents/MacOS/Blender` (Blender 5.1.2); every tool must honor a `$BLENDER` env override.
- Python scripts: stdlib only, no pip dependencies. Tests via `python3 -m unittest discover -s tools/tests -v` from the project root.
- Project settings: **24 fps, 1920×1080, AgX view transform, PNG 16-bit output** — set once in `tools/shot_template.blend`, never per shot.
- Timeline convention: **frame 1 = song time 0**; all shotlist frames are song-global.
- Naming: lowercase snake_case; sequences `sq010`, shots `sh010` — 3 digits, increments of 10.
- `docs/shotlist.csv` schema (exact header): `sq,sh,description,start_frame,end_frame,duration,assets,status`. `status` ∈ `boarded|blocked|animated|rendered|comped|final`. `assets` is `;`-separated paths under `assets/` (e.g. `chars/redwood;envs/forest`).
- git: never `git add -A` or `git add .` — always add explicit paths (test shots and scratch files float around the tree). Ignored: `render/`, `delivery/`, `edit/proxies/`, playblasts, `*.blend1`. LFS: blends, audio, images, video.
- Commit messages end with `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- Blender python scripts must survive the 4.x→5.x API rename of `SequenceEditor.sequences` → `.strips` (use the `hasattr` fallback shown in Task 6) and select the EEVEE engine id from the available enum (shown in Task 5).

---

### Task 1: Git plumbing — LFS, attributes, ignore

**Files:**
- Create: `.gitattributes`
- Create: `.gitignore`

**Interfaces:**
- Consumes: existing git repo at project root (already initialized, one commit).
- Produces: LFS tracking active for `*.blend` etc. — Task 5's template blend must land in LFS automatically.

- [ ] **Step 1: Install git-lfs (not currently installed)**

Run: `git lfs version || brew install git-lfs`
Then: `git lfs install`
Expected: `git lfs version` prints a version; `git lfs install` prints "Git LFS initialized."

- [ ] **Step 2: Write `.gitattributes`**

```gitattributes
*.blend filter=lfs diff=lfs merge=lfs -text
*.wav filter=lfs diff=lfs merge=lfs -text
*.mp3 filter=lfs diff=lfs merge=lfs -text
*.flac filter=lfs diff=lfs merge=lfs -text
*.aif filter=lfs diff=lfs merge=lfs -text
*.aiff filter=lfs diff=lfs merge=lfs -text
*.png filter=lfs diff=lfs merge=lfs -text
*.jpg filter=lfs diff=lfs merge=lfs -text
*.jpeg filter=lfs diff=lfs merge=lfs -text
*.webp filter=lfs diff=lfs merge=lfs -text
*.exr filter=lfs diff=lfs merge=lfs -text
*.hdr filter=lfs diff=lfs merge=lfs -text
*.mp4 filter=lfs diff=lfs merge=lfs -text
*.mov filter=lfs diff=lfs merge=lfs -text
```

- [ ] **Step 3: Write `.gitignore`**

```gitignore
# regenerable outputs
render/
delivery/
edit/proxies/
shots/**/playblast/

# blender litter
*.blend1
*.blend@

# python
__pycache__/

# macOS
.DS_Store

# local machine config
.claude/settings.local.json
```

- [ ] **Step 4: Verify LFS routing works**

Run: `touch lfs_probe.blend && git add lfs_probe.blend && git status --short && git rm --cached -q lfs_probe.blend && rm lfs_probe.blend`
Expected: `git status` shows `A  lfs_probe.blend`; `git check-attr filter lfs_probe.blend` (run before the cleanup if desired) reports `filter: lfs`.

- [ ] **Step 5: Commit**

```bash
git add .gitattributes .gitignore
git commit -m "chore: add LFS tracking and ignore rules

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 2: Folder skeleton, README, pipeline docs, shotlist

**Files:**
- Create: `README.md`
- Create: `docs/pipeline.md`
- Create: `docs/shotlist.csv`
- Create: `refs/palette.scss` (copy of `../assets/colors/palette.scss`)
- Create: `.gitkeep` files in empty tracked dirs

**Interfaces:**
- Consumes: nothing.
- Produces: `docs/shotlist.csv` with the exact header `sq,sh,description,start_frame,end_frame,duration,assets,status` — every later task validates against it. Directory layout all tools assume.

- [ ] **Step 1: Create the directory tree**

```bash
mkdir -p docs/ideation docs/treatment refs audio/track audio/stems \
  boards/animatic assets/chars assets/props assets/envs assets/materials \
  shots render edit/proxies delivery tools/tests
touch docs/ideation/.gitkeep docs/treatment/.gitkeep audio/track/.gitkeep \
  audio/stems/.gitkeep boards/animatic/.gitkeep assets/chars/.gitkeep \
  assets/props/.gitkeep assets/envs/.gitkeep assets/materials/.gitkeep \
  shots/.gitkeep edit/.gitkeep
```

(`render/`, `delivery/`, `edit/proxies/` are gitignored — no `.gitkeep`; tools recreate them on demand.)

- [ ] **Step 2: Copy the shared palette**

Run: `cp "../assets/colors/palette.scss" refs/palette.scss`

- [ ] **Step 3: Write `docs/shotlist.csv` (header only)**

```csv
sq,sh,description,start_frame,end_frame,duration,assets,status
```

- [ ] **Step 4: Write `README.md`**

````markdown
# redwood_video

An animated music video produced end-to-end in Blender — stylized clay look
(ClayPencil + Clay Doh + Grease Pencil), cut to a finished track.

- Design spec: `docs/superpowers/specs/2026-07-19-redwood-video-pipeline-design.md`
- Conventions: `docs/pipeline.md`
- Source of truth for shots: `docs/shotlist.csv`

## Layout

| Path | What lives there |
|---|---|
| `docs/` | ideation, treatment, shotlist.csv, beatmap.csv, pipeline docs |
| `refs/` | style references, palette |
| `audio/track/` | the final track (drop the WAV here) |
| `boards/` | Grease Pencil storyboards + animatic |
| `assets/` | chars/, props/, envs/, materials/ — linked libraries |
| `shots/` | per-shot .blends (`sq010/sh010/sh010.blend`) |
| `render/` | versioned frame sequences (gitignored) |
| `edit/` | VSE master edit |
| `delivery/` | final encodes (gitignored) |
| `tools/` | pipeline scripts + shot template |

## Phases

- [ ] 1. Ideation — concept notes in `docs/ideation/`, refs into `refs/`
- [ ] 2. Writing — treatment in `docs/treatment/`, beat map, first shotlist
- [ ] 3. Storyboards & animatic — `boards/` (Storypencil), durations → shotlist
- [ ] 4. Asset production — `assets/` registered in the Asset Browser
- [ ] 5. Animation — `shots/` via `tools/build_shots.py`, playblasts into edit
- [ ] 6. Rendering — `tools/render_shot.sh` per shot
- [ ] 7. Compositing — per-shot compositor (Uber Compositor)
- [ ] 8. Editing — `edit/edit.blend` against the track
- [ ] 9. Post & delivery — grade + `tools/encode_delivery.sh`

## Quickstart

```sh
# after dropping the track into audio/track/:
python3 tools/beatmap.py --bpm <BPM> --length <SECONDS>  # → docs/beatmap.csv
python3 tools/build_shots.py --dry-run                   # what would be created
python3 tools/build_shots.py                             # create missing shots
tools/render_shot.sh 010 010                             # render one shot
```

Blender is expected at `/Applications/Blender.app/Contents/MacOS/Blender`;
override with `$BLENDER`.
````

- [ ] **Step 5: Write `docs/pipeline.md`**

````markdown
# Pipeline conventions — quick reference

Full rationale: `superpowers/specs/2026-07-19-redwood-video-pipeline-design.md`

## Frames & timing
- 24 fps, 1920×1080, AgX view transform. Locked in `tools/shot_template.blend`.
- Timeline frame 1 = song time 0. All shot start/end frames are song-global.
- `docs/beatmap.csv` maps bar/beat → timeline frame
  (`python3 tools/beatmap.py --bpm <BPM> --length <SECONDS>`).

## Naming
- Sequences `sq010`, shots `sh010` — 3 digits, increments of 10.
- Lowercase snake_case everywhere; no spaces.

## Shotlist (`docs/shotlist.csv`) — source of truth
Columns: `sq,sh,description,start_frame,end_frame,duration,assets,status`
- `start_frame`/`end_frame` inclusive, song-global. `duration` = end−start+1
  (validated; may be left blank).
- `assets`: `;`-separated paths under `assets/`, e.g. `chars/redwood;envs/forest`.
- `status` flow: `boarded → blocked → animated → rendered → comped → final`.

## Assets
- One .blend per asset at `assets/<kind>/<name>/<name>.blend`.
- Each asset blend exposes ONE root collection named `<name>` — that is what
  shots link. Shots LINK, never append; rig animation via library overrides.
- Clay materials: `assets/materials/clay_library.blend` (Clay Doh-derived,
  palette-matched — built during look-dev).
- Polyhaven assets: fine. AI text-to-3D / Sketchfab: blockouts only, resculpt
  into the clay style before a shot renders.

## Shots
- All missing shots: `python3 tools/build_shots.py`
- One shot:
  `"$BLENDER" --background tools/shot_template.blend --python-exit-code 1 \
      --python tools/new_shot.py -- --sq 010 --sh 010`
- Playblasts: viewport render into `shots/sqXXX/shXXX/playblast/` (gitignored).

## Render
- `tools/render_shot.sh <sq> <sh> [vNNN]` → `render/sqXXX_shXXX/vNNN/` PNGs.
- Versions auto-increment; never overwrite an old version.

## Edit & delivery
- `edit/edit.blend` (VSE): track on channel 1, shots as image-sequence strips,
  upgraded animatic → playblast → final render without changing the cut.
- `tools/encode_delivery.sh <frames_dir> <audio> <name>` → `delivery/`
  ProRes master + H.264 (needs `brew install ffmpeg`).

## Git
- LFS: blends, audio, images, video (see `.gitattributes`).
- Ignored: `render/`, `delivery/`, playblasts, proxies, `*.blend1`.
- Commit explicit paths; never `git add -A`.
````

- [ ] **Step 6: Verify tree and commit**

Run: `find . -not -path './.git*' -type d | sort`
Expected: all directories from Step 1 listed.

```bash
git add README.md docs/pipeline.md docs/shotlist.csv refs/palette.scss \
  docs/ideation/.gitkeep docs/treatment/.gitkeep audio/track/.gitkeep \
  audio/stems/.gitkeep boards/animatic/.gitkeep assets/chars/.gitkeep \
  assets/props/.gitkeep assets/envs/.gitkeep assets/materials/.gitkeep \
  shots/.gitkeep edit/.gitkeep
git commit -m "feat: project skeleton, README, pipeline conventions, shotlist

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 3: `tools/shotlib.py` — shared pipeline helpers

**Files:**
- Create: `tools/shotlib.py`
- Test: `tools/tests/test_shotlib.py`

**Interfaces:**
- Consumes: `docs/shotlist.csv` schema from Task 2.
- Produces (exact signatures later tasks rely on):
  - `FPS: int = 24`, `STATUSES: tuple`, `DEFAULT_BLENDER: str`
  - `project_root() -> Path` — parent of `tools/`
  - `shot_code(sq: str, sh: str) -> str` — `"sq010_sh010"`
  - `shot_blend(sq: str, sh: str, root: Path | None = None) -> Path` — `shots/sq010/sh010/sh010.blend`
  - `render_dir(sq: str, sh: str, root: Path | None = None) -> Path` — `render/sq010_sh010`
  - `Shot` dataclass: fields `sq, sh, description, start_frame, end_frame, assets, status`; properties `duration`, `code`
  - `read_shotlist(path) -> list[Shot]` — raises `ValueError` with file:line on any invalid row
  - `beat_to_frame(beat: float, bpm: float, fps: int = FPS) -> int` — 0-based song frame
  - `next_version(render_shot_dir) -> str` — `"v001"`, `"v002"`, …
  - `find_blender() -> str` — `$BLENDER` → `PATH` → `DEFAULT_BLENDER`; raises `FileNotFoundError`

- [ ] **Step 1: Write the failing tests — `tools/tests/test_shotlib.py`**

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest discover -s tools/tests -v`
Expected: FAIL/ERROR — `ModuleNotFoundError: No module named 'shotlib'`

- [ ] **Step 3: Implement `tools/shotlib.py`**

```python
"""Shared helpers for the redwood_video pipeline.

Stdlib only: this module runs under both system Python and Blender's
bundled Python (imported by new_shot.py inside Blender).
"""
from __future__ import annotations

import csv
import os
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path

FPS = 24
STATUSES = ("boarded", "blocked", "animated", "rendered", "comped", "final")
DEFAULT_BLENDER = "/Applications/Blender.app/Contents/MacOS/Blender"
_FIELDS = ["sq", "sh", "description", "start_frame", "end_frame",
           "duration", "assets", "status"]
_V_RE = re.compile(r"^v(\d{3})$")


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def shot_code(sq: str, sh: str) -> str:
    return f"sq{sq}_sh{sh}"


def shot_blend(sq: str, sh: str, root: Path | None = None) -> Path:
    root = root or project_root()
    return root / "shots" / f"sq{sq}" / f"sh{sh}" / f"sh{sh}.blend"


def render_dir(sq: str, sh: str, root: Path | None = None) -> Path:
    root = root or project_root()
    return root / "render" / shot_code(sq, sh)


@dataclass
class Shot:
    sq: str
    sh: str
    description: str
    start_frame: int
    end_frame: int
    assets: list[str] = field(default_factory=list)
    status: str = "boarded"

    @property
    def duration(self) -> int:
        return self.end_frame - self.start_frame + 1

    @property
    def code(self) -> str:
        return shot_code(self.sq, self.sh)


def read_shotlist(path) -> list[Shot]:
    path = Path(path)
    shots: list[Shot] = []
    seen: set[str] = set()
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != _FIELDS:
            raise ValueError(f"{path}: header must be {','.join(_FIELDS)}")
        for lineno, row in enumerate(reader, start=2):
            sq, sh = row["sq"].strip(), row["sh"].strip()
            for label, val in (("sq", sq), ("sh", sh)):
                if not (len(val) == 3 and val.isdigit()):
                    raise ValueError(
                        f"{path}:{lineno}: {label} must be a 3-digit string, got {val!r}"
                    )
            try:
                start = int(row["start_frame"])
                end = int(row["end_frame"])
            except ValueError:
                raise ValueError(
                    f"{path}:{lineno}: start_frame/end_frame must be integers"
                ) from None
            if end < start:
                raise ValueError(f"{path}:{lineno}: end_frame {end} < start_frame {start}")
            duration = row["duration"].strip()
            if duration and int(duration) != end - start + 1:
                raise ValueError(
                    f"{path}:{lineno}: duration {duration} != end-start+1 ({end - start + 1})"
                )
            status = row["status"].strip()
            if status not in STATUSES:
                raise ValueError(
                    f"{path}:{lineno}: status {status!r} not one of {'|'.join(STATUSES)}"
                )
            code = shot_code(sq, sh)
            if code in seen:
                raise ValueError(f"{path}:{lineno}: duplicate shot {code}")
            seen.add(code)
            assets = [a.strip() for a in row["assets"].split(";") if a.strip()]
            shots.append(Shot(sq, sh, row["description"].strip(), start, end,
                              assets, status))
    return shots


def beat_to_frame(beat: float, bpm: float, fps: int = FPS) -> int:
    return round(beat * 60.0 / bpm * fps)


def next_version(render_shot_dir) -> str:
    d = Path(render_shot_dir)
    if not d.is_dir():
        return "v001"
    nums = [int(m.group(1)) for p in d.iterdir() if (m := _V_RE.match(p.name))]
    return f"v{max(nums, default=0) + 1:03d}"


def find_blender() -> str:
    cand = os.environ.get("BLENDER") or shutil.which("blender") or DEFAULT_BLENDER
    if not (shutil.which(cand) or os.path.exists(cand)):
        raise FileNotFoundError(f"Blender not found at {cand}; set $BLENDER")
    return cand
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest discover -s tools/tests -v`
Expected: all tests PASS (OK).

- [ ] **Step 5: Commit**

```bash
git add tools/shotlib.py tools/tests/test_shotlib.py
git commit -m "feat: shotlib shared pipeline helpers with tests

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 4: `tools/beatmap.py` — beat map generator

**Files:**
- Create: `tools/beatmap.py`
- Test: `tools/tests/test_beatmap.py`

**Interfaces:**
- Consumes: `shotlib.FPS`, `shotlib.beat_to_frame`, `shotlib.project_root`.
- Produces: `generate_rows(bpm: float, length_s: float, beats_per_bar: int = 4, fps: int = 24) -> list[dict]` with keys `bar, beat, time_s, frame` (frame is 1-based timeline frame); CLI writing `docs/beatmap.csv`.

- [ ] **Step 1: Write the failing tests — `tools/tests/test_beatmap.py`**

```python
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


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest discover -s tools/tests -v`
Expected: ERROR — `ModuleNotFoundError: No module named 'beatmap'` (shotlib tests still pass).

- [ ] **Step 3: Implement `tools/beatmap.py`**

```python
"""Generate docs/beatmap.csv: bar/beat -> seconds -> timeline frame.

Usage:
  python3 tools/beatmap.py --bpm 92 --length 214 [--beats-per-bar 4]
      [--fps 24] [--out docs/beatmap.csv]
"""
import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shotlib


def generate_rows(bpm, length_s, beats_per_bar=4, fps=shotlib.FPS):
    rows = []
    beat = 0
    while True:
        t = beat * 60.0 / bpm
        if t > length_s:
            break
        rows.append({
            "bar": beat // beats_per_bar + 1,
            "beat": beat % beats_per_bar + 1,
            "time_s": round(t, 3),
            # timeline frame 1 = song time 0 (see docs/pipeline.md)
            "frame": shotlib.beat_to_frame(beat, bpm, fps) + 1,
        })
        beat += 1
    return rows


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--bpm", type=float, required=True)
    p.add_argument("--length", type=float, required=True,
                   help="track length in seconds")
    p.add_argument("--beats-per-bar", type=int, default=4)
    p.add_argument("--fps", type=int, default=shotlib.FPS)
    p.add_argument("--out", type=Path,
                   default=shotlib.project_root() / "docs" / "beatmap.csv")
    args = p.parse_args(argv)

    rows = generate_rows(args.bpm, args.length, args.beats_per_bar, args.fps)
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["bar", "beat", "time_s", "frame"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} beats to {args.out}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest discover -s tools/tests -v`
Expected: all tests PASS.

- [ ] **Step 5: Smoke-test the CLI (write to a temp file, not docs/)**

Run: `python3 tools/beatmap.py --bpm 120 --length 10 --out "$(mktemp -d)/beatmap.csv"`
Expected: `wrote 21 beats to /…/beatmap.csv`

- [ ] **Step 6: Commit**

```bash
git add tools/beatmap.py tools/tests/test_beatmap.py
git commit -m "feat: beatmap generator (bpm -> bar/beat -> timeline frame)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 5: `tools/make_template.py` + `tools/shot_template.blend`

**Files:**
- Create: `tools/make_template.py`
- Create (generated): `tools/shot_template.blend`

**Interfaces:**
- Consumes: nothing (runs `--factory-startup`).
- Produces: `tools/shot_template.blend` — scene `shot`, 24 fps, 1920×1080, AgX, PNG/RGB/16-bit, EEVEE; collections `cam`, `chars`, `env`, `fx`; a camera object `cam` set as `scene.camera`. Tasks 6–8 open this file.

- [ ] **Step 1: Write `tools/make_template.py`**

```python
"""Build tools/shot_template.blend with the locked project settings.

Run:
  "$BLENDER" --background --factory-startup --python-exit-code 1 \
      --python tools/make_template.py
"""
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parent.parent

scene = bpy.context.scene
scene.name = "shot"

# EEVEE's enum id differs across Blender versions; pick what this build has.
engines = {
    item.identifier
    for item in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items
}
scene.render.engine = (
    "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engines else "BLENDER_EEVEE"
)

scene.render.fps = 24
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.render.image_settings.color_depth = "16"
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "None"
scene.sync_mode = "AUDIO_SYNC"

# Empty stage: wipe factory objects, build the shot collection layout.
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
for name in ("cam", "chars", "env", "fx"):
    coll = bpy.data.collections.new(name)
    scene.collection.children.link(coll)

cam_data = bpy.data.cameras.new("cam")
cam_obj = bpy.data.objects.new("cam", cam_data)
bpy.data.collections["cam"].objects.link(cam_obj)
scene.camera = cam_obj

out = ROOT / "tools" / "shot_template.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(out), relative_remap=True)
print(f"template saved: {out}")
```

- [ ] **Step 2: Generate the template**

Run:
```bash
BLENDER="${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}"
"$BLENDER" --background --factory-startup --python-exit-code 1 \
  --python tools/make_template.py
```
Expected: output ends with `template saved: …/tools/shot_template.blend`, exit code 0.

- [ ] **Step 3: Verify the saved settings by reopening the file**

Run:
```bash
"$BLENDER" --background tools/shot_template.blend --python-exit-code 1 \
  --python-expr "import bpy; s = bpy.context.scene; \
assert s.render.fps == 24, s.render.fps; \
assert (s.render.resolution_x, s.render.resolution_y) == (1920, 1080); \
assert s.view_settings.view_transform == 'AgX'; \
assert s.camera is not None; \
assert {'cam','chars','env','fx'} <= set(bpy.data.collections.keys()); \
print('TEMPLATE OK:', s.render.engine)"
```
Expected: `TEMPLATE OK: BLENDER_EEVEE…`, exit code 0.

- [ ] **Step 4: Confirm the blend goes to LFS, then commit**

Run: `git add tools/make_template.py tools/shot_template.blend && git lfs ls-files`
Expected: `git lfs ls-files` lists `tools/shot_template.blend`.

```bash
git commit -m "feat: shot template with locked render settings (1080p24 EEVEE AgX)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 6: `tools/new_shot.py` — create one shot from the template

**Files:**
- Create: `tools/new_shot.py`

**Interfaces:**
- Consumes: `shotlib.read_shotlist`, `shotlib.shot_blend`, `shotlib.shot_code`; `tools/shot_template.blend` (opened by the Blender invocation, not by this script); `docs/shotlist.csv`.
- Produces: `shots/sqXXX/shXXX/shXXX.blend` with scene named `sqXXX_shXXX`, frame range from the shotlist, the track (if present in `audio/track/`) as a sound strip at frame 1, and each `assets` entry linked as a collection. Invocation contract used by Task 7:
  `"$BLENDER" --background tools/shot_template.blend --python-exit-code 1 --python tools/new_shot.py -- --sq <sq> --sh <sh> [--force]`

- [ ] **Step 1: Write `tools/new_shot.py`**

```python
"""Create a shot .blend from the open template + its docs/shotlist.csv row.

Run with the template open, headless:
  "$BLENDER" --background tools/shot_template.blend --python-exit-code 1 \
      --python tools/new_shot.py -- --sq 010 --sh 010 [--force]
"""
import argparse
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shotlib

AUDIO_EXTS = {".wav", ".mp3", ".flac", ".aif", ".aiff"}


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sq", required=True)
    p.add_argument("--sh", required=True)
    p.add_argument("--force", action="store_true",
                   help="overwrite an existing shot file")
    return p.parse_args(argv)


def find_track(root: Path):
    track_dir = root / "audio" / "track"
    candidates = sorted(track_dir.iterdir()) if track_dir.is_dir() else []
    for p in candidates:
        if p.suffix.lower() in AUDIO_EXTS:
            return p
    return None


def add_track(scene, track: Path):
    se = scene.sequence_editor or scene.sequence_editor_create()
    # Blender 5.x renamed SequenceEditor.sequences -> .strips
    strips = se.strips if hasattr(se, "strips") else se.sequences
    strips.new_sound(name="track", filepath=str(track), channel=1, frame_start=1)


def link_asset(entry: str, root: Path, scene):
    name = entry.rstrip("/").split("/")[-1]
    path = root / "assets" / entry / f"{name}.blend"
    if not path.exists():
        print(f"warning: asset {entry!r} missing ({path}), skipped")
        return
    with bpy.data.libraries.load(str(path), link=True) as (data_from, data_to):
        if name not in data_from.collections:
            print(f"warning: no collection {name!r} in {path}, skipped")
            return
        data_to.collections = [name]
    for coll in data_to.collections:
        scene.collection.children.link(coll)


def main():
    args = parse_args()
    root = shotlib.project_root()
    shots = {s.code: s for s in shotlib.read_shotlist(root / "docs" / "shotlist.csv")}
    code = shotlib.shot_code(args.sq, args.sh)
    if code not in shots:
        sys.exit(f"error: {code} not found in docs/shotlist.csv")
    shot = shots[code]

    blend = shotlib.shot_blend(args.sq, args.sh, root)
    if blend.exists() and not args.force:
        sys.exit(f"error: {blend} exists (use --force to overwrite)")

    scene = bpy.context.scene
    scene.name = code
    # end before start: frames are song-global and may exceed the template's
    # default range; setting end first avoids any start>end clamping.
    scene.frame_end = shot.end_frame
    scene.frame_start = shot.start_frame

    track = find_track(root)
    if track:
        add_track(scene, track)
    else:
        print("warning: no track in audio/track/ — shot created without audio")

    for entry in shot.assets:
        link_asset(entry, root, scene)

    blend.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(blend), relative_remap=True)
    print(f"created {blend.relative_to(root)} [{shot.start_frame}-{shot.end_frame}]")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Add a temporary test row to the shotlist**

Run: `printf '010,010,pipeline test shot,1,8,8,,boarded\n' >> docs/shotlist.csv`

- [ ] **Step 3: Run the script and verify the shot file**

Run:
```bash
BLENDER="${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}"
"$BLENDER" --background tools/shot_template.blend --python-exit-code 1 \
  --python tools/new_shot.py -- --sq 010 --sh 010
"$BLENDER" --background shots/sq010/sh010/sh010.blend --python-exit-code 1 \
  --python-expr "import bpy; s = bpy.context.scene; \
assert s.name == 'sq010_sh010', s.name; \
assert (s.frame_start, s.frame_end) == (1, 8), (s.frame_start, s.frame_end); \
print('SHOT OK')"
```
Expected: first command prints `created shots/sq010/sh010/sh010.blend [1-8]` (plus a no-track warning); second prints `SHOT OK`. Exit codes 0.

- [ ] **Step 4: Verify the existing-file guard**

Run (same `$BLENDER`): `"$BLENDER" --background tools/shot_template.blend --python-exit-code 1 --python tools/new_shot.py -- --sq 010 --sh 010; echo "exit=$?"`
Expected: error message about `--force`, `exit=1`.

- [ ] **Step 5: Clean up test artifacts**

Run: `rm -rf shots/sq010 && git checkout -- docs/shotlist.csv && git status --short`
Expected: only `tools/new_shot.py` untracked/modified.

- [ ] **Step 6: Commit**

```bash
git add tools/new_shot.py
git commit -m "feat: new_shot script — stamp a shot blend from template + shotlist

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 7: `tools/build_shots.py` — batch shot creation

**Files:**
- Create: `tools/build_shots.py`
- Test: `tools/tests/test_build_shots.py`

**Interfaces:**
- Consumes: `shotlib.read_shotlist`, `shotlib.shot_blend`, `shotlib.find_blender`, `shotlib.Shot`; Task 6's invocation contract for `new_shot.py`.
- Produces: `plan_builds(shots: list[Shot], root: Path, force: bool = False) -> list[Shot]`; CLI `python3 tools/build_shots.py [--dry-run] [--force]`.

- [ ] **Step 1: Write the failing test — `tools/tests/test_build_shots.py`**

```python
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
```

- [ ] **Step 2: Run tests to verify the new one fails**

Run: `python3 -m unittest discover -s tools/tests -v`
Expected: ERROR — `ModuleNotFoundError: No module named 'build_shots'`; earlier suites still pass.

- [ ] **Step 3: Implement `tools/build_shots.py`**

```python
"""Create every missing shot .blend listed in docs/shotlist.csv.

Usage: python3 tools/build_shots.py [--dry-run] [--force]
"""
import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shotlib


def plan_builds(shots, root, force=False):
    return [
        s for s in shots
        if force or not shotlib.shot_blend(s.sq, s.sh, root).exists()
    ]


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--force", action="store_true",
                   help="rebuild shots that already exist")
    args = p.parse_args(argv)

    root = shotlib.project_root()
    shots = shotlib.read_shotlist(root / "docs" / "shotlist.csv")
    todo = plan_builds(shots, root, args.force)
    if len(todo) < len(shots):
        print(f"skipping {len(shots) - len(todo)} existing shot(s)")
    if not todo:
        print("nothing to build")
        return
    if args.dry_run:
        for s in todo:
            print(f"would build {s.code} [{s.start_frame}-{s.end_frame}]")
        return

    blender = shotlib.find_blender()
    for s in todo:
        print(f"building {s.code} ...")
        cmd = [
            blender, "--background",
            str(root / "tools" / "shot_template.blend"),
            "--python-exit-code", "1",
            "--python", str(root / "tools" / "new_shot.py"),
            "--", "--sq", s.sq, "--sh", s.sh,
        ]
        if args.force:
            cmd.append("--force")
        subprocess.run(cmd, check=True)
    print(f"built {len(todo)} shot(s)")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest discover -s tools/tests -v`
Expected: all tests PASS.

- [ ] **Step 5: End-to-end smoke test (two shots, then cleanup)**

Run:
```bash
printf '010,010,test a,1,8,8,,boarded\n010,020,test b,9,16,8,,boarded\n' >> docs/shotlist.csv
python3 tools/build_shots.py --dry-run
python3 tools/build_shots.py
python3 tools/build_shots.py   # second run: everything skipped
rm -rf shots/sq010 && git checkout -- docs/shotlist.csv
```
Expected: dry run lists both shots; first real run prints `built 2 shot(s)`; second prints `skipping 2 existing shot(s)` then `nothing to build`.

- [ ] **Step 6: Commit**

```bash
git add tools/build_shots.py tools/tests/test_build_shots.py
git commit -m "feat: build_shots batch creator driven by shotlist.csv

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 8: `tools/env.sh` + `tools/render_shot.sh` — headless rendering

**Files:**
- Create: `tools/env.sh`
- Create: `tools/render_shot.sh` (chmod +x)

**Interfaces:**
- Consumes: shot blends from Task 6/7; `shotlib.next_version` (via `python3 -c`).
- Produces: `tools/render_shot.sh <sq> <sh> [vNNN]` → PNG sequence in `render/sqXXX_shXXX/vNNN/`; `tools/env.sh` exporting `REDWOOD_ROOT` and validated `BLENDER` (sourced by Task 9's script too).

- [ ] **Step 1: Write `tools/env.sh`**

```bash
# Shared environment for redwood_video shell tools. Source, don't execute:
#   . "$(dirname "$0")/env.sh" || exit 1
REDWOOD_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BLENDER="${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}"
if ! command -v "$BLENDER" >/dev/null 2>&1 && [ ! -x "$BLENDER" ]; then
  echo "error: Blender not found at $BLENDER (set \$BLENDER)" >&2
  return 1
fi
export REDWOOD_ROOT BLENDER
```

- [ ] **Step 2: Write `tools/render_shot.sh`**

```bash
#!/usr/bin/env bash
# Headless-render one shot to render/<code>/<version>/ as a PNG sequence.
# Usage: tools/render_shot.sh <sq> <sh> [vNNN]
set -euo pipefail
. "$(dirname "$0")/env.sh" || exit 1

usage="usage: tools/render_shot.sh <sq> <sh> [vNNN]"
sq="${1:?$usage}"
sh_="${2:?$usage}"
code="sq${sq}_sh${sh_}"
blend="$REDWOOD_ROOT/shots/sq${sq}/sh${sh_}/sh${sh_}.blend"
[ -f "$blend" ] || { echo "error: $blend not found" >&2; exit 1; }

ver="${3:-$(python3 -c "
import sys
sys.path.insert(0, '$REDWOOD_ROOT/tools')
import shotlib
print(shotlib.next_version('$REDWOOD_ROOT/render/$code'))
")}"
out="$REDWOOD_ROOT/render/$code/$ver/${code}_####"

echo "rendering $code -> render/$code/$ver/"
"$BLENDER" --background "$blend" \
  --render-output "$out" \
  --render-format PNG -x 1 \
  --render-anim
echo "done: render/$code/$ver/"
```

Run: `chmod +x tools/render_shot.sh && bash -n tools/render_shot.sh && bash -n tools/env.sh`
Expected: no output (clean syntax).

- [ ] **Step 3: Create a small test shot and render it for real**

Run:
```bash
printf '010,010,render test,1,8,8,,boarded\n' >> docs/shotlist.csv
BLENDER="${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}"
"$BLENDER" --background tools/shot_template.blend --python-exit-code 1 \
  --python tools/new_shot.py -- --sq 010 --sh 010
tools/render_shot.sh 010 010
ls render/sq010_sh010/v001/ | wc -l
```
Expected: 8 PNG frames in `render/sq010_sh010/v001/` (empty stage renders fast; EEVEE headless uses Metal). If EEVEE cannot get a GPU context headless, report the failure — do not silently switch engines.

- [ ] **Step 4: Verify version auto-increment**

Run: `tools/render_shot.sh 010 010 && ls render/sq010_sh010/`
Expected: `v001` and `v002` both present.

- [ ] **Step 5: Clean up test artifacts**

Run: `rm -rf shots/sq010 render/sq010_sh010 && git checkout -- docs/shotlist.csv && git status --short`
Expected: only the two new tool scripts show as untracked.

- [ ] **Step 6: Commit**

```bash
git add tools/env.sh tools/render_shot.sh
git commit -m "feat: headless per-shot render script with version auto-increment

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 9: `tools/encode_delivery.sh` — delivery encodes

**Files:**
- Create: `tools/encode_delivery.sh` (chmod +x)

**Interfaces:**
- Consumes: `tools/env.sh` (for `REDWOOD_ROOT` only; Blender not needed), a rendered PNG frame dir + audio file.
- Produces: `tools/encode_delivery.sh <frames_dir> <audio_file> <name>` → `delivery/<name>_prores.mov` (ProRes 422 HQ + PCM) and `delivery/<name>_h264.mp4` (CRF 18 + AAC 320k).

- [ ] **Step 1: Install ffmpeg (not currently installed; needed for delivery)**

Run: `ffmpeg -version >/dev/null 2>&1 || brew install ffmpeg`
Expected: ffmpeg available afterward (`ffmpeg -version` prints a version). Note: brew install can take a few minutes.

- [ ] **Step 2: Write `tools/encode_delivery.sh`**

```bash
#!/usr/bin/env bash
# Encode a rendered PNG sequence + audio into delivery masters.
# Usage: tools/encode_delivery.sh <frames_dir> <audio_file> <name>
# Produces delivery/<name>_prores.mov and delivery/<name>_h264.mp4
set -euo pipefail
REDWOOD_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

command -v ffmpeg >/dev/null 2>&1 || {
  echo "error: ffmpeg not found — brew install ffmpeg" >&2; exit 1; }

usage="usage: tools/encode_delivery.sh <frames_dir> <audio_file> <name>"
frames="${1:?$usage}"
audio="${2:?$usage}"
name="${3:?$usage}"
[ -d "$frames" ] || { echo "error: $frames is not a directory" >&2; exit 1; }
[ -f "$audio" ] || { echo "error: $audio not found" >&2; exit 1; }

mkdir -p "$REDWOOD_ROOT/delivery"

ffmpeg -y -framerate 24 -pattern_type glob -i "$frames/*.png" -i "$audio" \
  -c:v prores_ks -profile:v 3 -pix_fmt yuv422p10le \
  -c:a pcm_s16le -shortest \
  "$REDWOOD_ROOT/delivery/${name}_prores.mov"

ffmpeg -y -framerate 24 -pattern_type glob -i "$frames/*.png" -i "$audio" \
  -c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p \
  -c:a aac -b:a 320k -movflags +faststart -shortest \
  "$REDWOOD_ROOT/delivery/${name}_h264.mp4"

echo "delivery/${name}_prores.mov"
echo "delivery/${name}_h264.mp4"
```

Run: `chmod +x tools/encode_delivery.sh && bash -n tools/encode_delivery.sh`
Expected: clean syntax.

- [ ] **Step 3: End-to-end test with generated media**

Run:
```bash
scratch="$(mktemp -d)"
mkdir -p "$scratch/frames"
ffmpeg -v error -f lavfi -i "testsrc=duration=1:size=1920x1080:rate=24" \
  "$scratch/frames/%04d.png"
ffmpeg -v error -f lavfi -i "sine=frequency=440:duration=1" "$scratch/tone.wav"
tools/encode_delivery.sh "$scratch/frames" "$scratch/tone.wav" encode_test
ffprobe -v error -show_entries stream=codec_name -of csv=p=0 delivery/encode_test_prores.mov
ffprobe -v error -show_entries stream=codec_name -of csv=p=0 delivery/encode_test_h264.mp4
rm -rf "$scratch" delivery/encode_test_prores.mov delivery/encode_test_h264.mp4
```
Expected: ffprobe prints `prores` + `pcm_s16le` for the .mov and `h264` + `aac` for the .mp4.

- [ ] **Step 4: Commit**

```bash
git add tools/encode_delivery.sh
git commit -m "feat: delivery encode presets (ProRes master + H.264)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Out of scope (created later by the phases themselves)

- `boards/boards.blend`, `edit/edit.blend` — created when storyboarding/editing begin (Storypencil verify-install happens at the storyboard phase).
- `assets/materials/clay_library.blend` and the Asset Browser catalog (`assets/blender_assets.cats.txt`) — built during look-dev; `shot_template.blend` gains its clay-library link then.
- `docs/beatmap.csv` — generated for real once the track (and its BPM) is dropped into `audio/track/`.

## Final verification (after all tasks)

```bash
python3 -m unittest discover -s tools/tests -v   # all green
git log --oneline                                 # ~11 commits: spec, plan, one per task
git lfs ls-files                                  # shot_template.blend
git status --short                                # clean
```
