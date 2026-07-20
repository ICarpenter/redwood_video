# Scale Guides Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give every board scene recognisable, correctly-scaled, movable 3D stand-ins for the cast and hero props to draw over — none of which ever render into the animatic.

**Architecture:** A pure-Python registry (`tools/guides.py`) declares the guides, catalog UUIDs, and placement constants. A Blender build script (`tools/guide_assets.py`) assembles each guide from primitives into `assets/chars/cast.blend` and `assets/props/props.blend`, marks each collection as a catalogued Asset, and writes `assets/blender_assets.cats.txt`. `make_boards.py` ensures every board scene owns a non-rendering `<shotcode>_guides` collection. An add-on (`tools/addons/redwood_guides.py`) drops linked guide instances into that collection facing the board camera.

**Tech Stack:** Python 3 (stdlib only for `guides.py`), Blender 5.1.2 `bpy` (EEVEE, Asset API), pytest/unittest, git-lfs for `.blend` files.

## Global Constraints

- **Blender:** 5.1.2 at `$BLENDER` (default `/Applications/Blender.app/Contents/MacOS/Blender`); not on PATH. Resolve via `shotlib.find_blender()`.
- **`guides.py` is stdlib-only** — no `bpy`. It is imported both under system Python (tests) and Blender's Python (`guide_assets.py`, `make_boards.py`, the add-on). Same rule `shotlib.py` follows.
- **Units are real-world metres.** Feet at Z = 0, centred on X = 0, front facing −Y (toward the board camera at `(0,-10,0)` looking +Y). Guides drop at `DROP_LOCATION = (0.0, 1.5, 0.0)` — just behind the GP paper plane.
- **Guides never render.** They live in a per-scene collection with `hide_render = True`.
- **Per-scene collection name = `f"{scene.name}_guides"`** (Blender collection names are globally unique; a bare `guides` would collide across 38 scenes).
- **Catalog UUIDs are hard-coded** in `guides.py` so regenerating `blender_assets.cats.txt` never churns it.
- **`.blend` outputs are LFS binaries.** Confirm `*.blend` is LFS-tracked before committing generated files.
- **`--force` guard:** build scripts refuse to overwrite an existing (hand-maintained) asset file without `--force`; `--out=<dir>` builds throwaway copies.
- **Commit trailers:** end every commit message with
  `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>` and
  `Claude-Session: https://claude.ai/code/session_01Q5Hhdvq9TU6goE9exjCHyB`.

---

## File Structure

- `tools/guides.py` *(create)* — stdlib registry: `GuideSpec`, `GUIDES`, `CATALOGS`, `DROP_LOCATION`, `guides_collection_name()`, `cats_file_text()`, lookups.
- `tools/guide_assets.py` *(create)* — `bpy` build script: primitive helpers, one builder per guide, asset-marking, cats-file writing, `--previews`, `--check`, `--mark-property`, `--force`/`--out` guard.
- `tools/make_boards.py` *(modify)* — add `ensure_guides_collection()`; call it for new and existing scenes.
- `tools/addons/redwood_guides.py` *(create)* — "Add Guide" N-panel operator.
- `tools/tests/test_guides.py` *(create)* — pure-Python registry + cats-file tests.
- `tools/tests/check_blender.py` *(create)* — in-Blender assertions (guide build + make_boards).
- `tools/tests/test_blender_smoke.py` *(create)* — pytest wrapper that shells out to Blender, skips if absent.
- `assets/chars/cast.blend`, `assets/props/props.blend`, `assets/blender_assets.cats.txt` *(generated + committed)*.
- `assets/envs/property/property.blend` *(modify via `--mark-property`)* — mark `property` collection as an Asset.
- `docs/boards.md` *(create)*, `docs/tools.md` *(modify)*, `docs/treatment/site.md` *(modify)* — workflow + cross-links.

---

## Task 1: `tools/guides.py` registry (pure Python)

**Files:**
- Create: `tools/guides.py`
- Test: `tools/tests/test_guides.py`

**Interfaces:**
- Produces:
  - `DROP_LOCATION: tuple[float,float,float]`
  - `GUIDES_SUFFIX: str`, `guides_collection_name(scene_name: str) -> str`
  - `CAST_FILE`, `PROPS_FILE`, `PROPERTY_FILE: str` (project-root-relative)
  - `CATALOGS: dict[str, tuple[str,str,str]]` (key → (uuid, path, simple_name))
  - `@dataclass(frozen=True) GuideSpec(name: str, file: str, catalog: str, height: float)`
  - `GUIDES: list[GuideSpec]`
  - `guides_for_file(file: str) -> list[GuideSpec]`
  - `guide_by_name(name: str) -> GuideSpec | None`
  - `cats_file_text() -> str`

- [ ] **Step 1: Write the failing test**

Create `tools/tests/test_guides.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tools/tests/test_guides.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'guides'`.

- [ ] **Step 3: Write minimal implementation**

Create `tools/guides.py`:

```python
#!/usr/bin/env python3
"""Declarative registry of animatic scale-guides.

Stdlib only — imported by guide_assets.py, make_boards.py, and the
redwood_guides add-on inside Blender, and by the test suite under system
Python. No bpy here (same rule shotlib.py follows).

Board scenes place a Grease Pencil paper plane at the origin with the camera
at (0,-10,0) looking +Y. Guides are authored facing -Y (front toward camera),
feet at Z=0, centred on X=0; dropped at DROP_LOCATION they sit just behind the
paper (Y=0) so strokes overlay them. They live in a per-scene collection whose
render toggle is off, so conform_edit only ever sees the GP strokes.
"""
from __future__ import annotations

from dataclasses import dataclass

DROP_LOCATION = (0.0, 1.5, 0.0)

GUIDES_SUFFIX = "_guides"


def guides_collection_name(scene_name: str) -> str:
    """Per-scene guides collection name (globally unique, one per board)."""
    return f"{scene_name}{GUIDES_SUFFIX}"


# Project-root-relative paths to the asset files.
CAST_FILE = "assets/chars/cast.blend"
PROPS_FILE = "assets/props/props.blend"
PROPERTY_FILE = "assets/envs/property/property.blend"

# Hard-coded catalog UUIDs → regenerating the cats file never churns it.
# key -> (uuid, catalog path, simple name)
CATALOGS = {
    "cast": ("7c3e1a2b-0001-4a00-8000-000000000001", "guides/cast", "guides-cast"),
    "props": ("7c3e1a2b-0002-4a00-8000-000000000002", "guides/props", "guides-props"),
    "set": ("7c3e1a2b-0003-4a00-8000-000000000003", "guides/set", "guides-set"),
}


@dataclass(frozen=True)
class GuideSpec:
    name: str      # collection name == asset name
    file: str      # CAST_FILE or PROPS_FILE
    catalog: str   # key into CATALOGS
    height: float  # target overall Z extent in metres (checked, loose tolerance)


GUIDES: list[GuideSpec] = [
    GuideSpec("boy", CAST_FILE, "cast", 1.3),
    GuideSpec("mom", CAST_FILE, "cast", 1.7),
    GuideSpec("sheriff", CAST_FILE, "cast", 1.8),
    GuideSpec("machine_gun", PROPS_FILE, "props", 0.3),
    GuideSpec("printer", PROPS_FILE, "props", 1.4),
    GuideSpec("action_figure", PROPS_FILE, "props", 1.8),
    GuideSpec("delivery_truck", PROPS_FILE, "props", 3.2),
    GuideSpec("cruiser", PROPS_FILE, "props", 1.6),
    GuideSpec("rosco", PROPS_FILE, "props", 0.22),
    GuideSpec("big_pistol", PROPS_FILE, "props", 0.5),
    GuideSpec("santa", PROPS_FILE, "props", 1.8),
    GuideSpec("scale_stick", PROPS_FILE, "props", 2.0),
]


def guides_for_file(file: str) -> list[GuideSpec]:
    return [g for g in GUIDES if g.file == file]


def guide_by_name(name: str) -> "GuideSpec | None":
    return next((g for g in GUIDES if g.name == name), None)


def cats_file_text() -> str:
    lines = [
        "# This is an Asset Catalog Definition file for Blender.",
        "#",
        "# Empty lines and lines starting with `#` will be ignored.",
        "# The first non-ignored line should be the version indicator.",
        '# Other lines are of the format "UUID:catalog/path/for/assets:simple catalog name"',
        "",
        "VERSION 1",
        "",
    ]
    for uuid, path, simple in CATALOGS.values():
        lines.append(f"{uuid}:{path}:{simple}")
    return "\n".join(lines) + "\n"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tools/tests/test_guides.py -v`
Expected: PASS (all cases).

- [ ] **Step 5: Commit**

```bash
git add tools/guides.py tools/tests/test_guides.py
git commit -m "feat: guides registry (scale-guide specs, catalogs, placement)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Q5Hhdvq9TU6goE9exjCHyB"
```

---

## Task 2: `tools/guide_assets.py` build script

**Files:**
- Create: `tools/guide_assets.py`
- Create: `tools/tests/check_blender.py`
- Create: `tools/tests/test_blender_smoke.py`

**Interfaces:**
- Consumes: `guides.GUIDES`, `guides.GuideSpec`, `guides.CATALOGS`, `guides.guides_for_file`, `guides.CAST_FILE`, `guides.PROPS_FILE`, `guides.PROPERTY_FILE`, `guides.cats_file_text`; `shotlib.project_root`, `shotlib.find_blender`.
- Produces (module-level, importable inside Blender):
  - `build_guide_file(specs: list[GuideSpec], out_path: Path) -> None` — wipes data, builds + marks collections, runs structural check, saves.
  - `check_structural(specs) -> None` / `check_dimensions(specs) -> None` — assert on current `bpy.data`.
  - `run_check() -> None` — build both files to a temp dir + dimension-check; prints `GUIDE CHECK OK`.
  - `mark_property_asset() -> None` — mark the `property` collection in `property.blend`.
  - `render_previews(specs, outdir: Path) -> None`.
  - `BUILDERS: dict[str, callable]` — name → builder(coll).

Because the deliverable is `bpy` code that can't run under plain pytest, the test cycle here is: write the in-Blender assertions (`check_blender.py`) + the pytest gate, run them to fail, implement the script, run them to pass.

- [ ] **Step 1: Write the failing tests (in-Blender check + pytest gate)**

Create `tools/tests/check_blender.py`:

```python
"""Run INSIDE Blender to assert guide + boards invariants. Exits non-zero on
failure (via --python-exit-code 1). Invoked by test_blender_smoke.py and
runnable by hand:

  "$BLENDER" --background --factory-startup --python-exit-code 1 \
      --python tools/tests/check_blender.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # tools/

import bpy  # noqa: E402
import guides  # noqa: E402
import guide_assets  # noqa: E402
import make_boards  # noqa: E402

# 1. Guide asset files build, mark, catalog, and dimension-check.
guide_assets.run_check()

# 2. make_boards ensures a non-rendering, idempotent per-scene guides coll.
sc = bpy.data.scenes.new("sq999_sh999")
created = make_boards.ensure_guides_collection(sc)
assert created is True, "guides collection should be created on first call"
gname = guides.guides_collection_name(sc.name)
gc = sc.collection.children.get(gname)
assert gc is not None, f"missing {gname}"
assert gc.hide_render is True, "guides collection must not render"
assert make_boards.ensure_guides_collection(sc) is False, "must be idempotent"

print("ALL CHECKS OK")
```

Create `tools/tests/test_blender_smoke.py`:

```python
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

    def test_guide_and_boards_checks(self):
        r = subprocess.run(
            [self.blender, "--background", "--factory-startup",
             "--python-exit-code", "1", "--python", str(CHECK)],
            capture_output=True, text=True,
        )
        self.assertEqual(r.returncode, 0, msg=r.stdout + "\n" + r.stderr)
        self.assertIn("ALL CHECKS OK", r.stdout)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m pytest tools/tests/test_blender_smoke.py -v`
Expected: FAIL — Blender runs `check_blender.py`, which errors on `import guide_assets` (module does not exist yet), returns non-zero. (If `$BLENDER` is unset/missing the test is SKIPPED — that's acceptable locally but the implementer must run it on the Blender machine before marking this task done.)

- [ ] **Step 3: Write the implementation**

Create `tools/guide_assets.py`:

```python
#!/usr/bin/env python3
"""Build the animatic scale-guide asset files.

Writes assets/chars/cast.blend and assets/props/props.blend: one collection
per guide (see tools/guides.py), each assembled from primitives into a
recognisable silhouette, marked as a catalogued Asset. Also writes
assets/blender_assets.cats.txt. Guides are authored in real metres, facing -Y,
feet at Z=0, centred on X=0 (see guides.py for the board-camera rationale).

Run (default → the real asset paths; refuses to clobber without --force):
  "$BLENDER" --background --factory-startup --python-exit-code 1 \
      --python tools/guide_assets.py

Flags (after --):
  --force                 overwrite the real asset files
  --out=<dir>            build throwaway copies into <dir> (cats file too)
  --previews=<dir>       render each guide to <dir>/<name>.png
  --check                build to a temp dir + assert invariants, then exit
  --mark-property        mark the `property` collection in property.blend
"""
import math
import sys
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import guides
import shotlib

# --- dimension-check tolerances -----------------------------------------
FEET_TOL = 0.03    # |min Z| — feet must sit on the floor
CENTRE_TOL = 0.12  # |centre X| — centred on the drawing axis
HEIGHT_TOL = 0.25  # relative tolerance on target height (art wiggle room)

PALETTE = {
    "skin":     (0.85, 0.62, 0.45),
    "boy":      (0.20, 0.40, 0.70),
    "mom":      (0.72, 0.30, 0.52),
    "sheriff":  (0.28, 0.36, 0.30),
    "hat":      (0.32, 0.26, 0.18),
    "metal":    (0.30, 0.32, 0.35),
    "plastic":  (0.80, 0.75, 0.22),
    "tire":     (0.06, 0.06, 0.06),
    "truck":    (0.45, 0.28, 0.20),
    "cruiser":  (0.14, 0.20, 0.45),
    "lightbar": (0.85, 0.20, 0.20),
    "santa":    (0.72, 0.13, 0.13),
    "white":    (0.90, 0.90, 0.90),
    "ref":      (0.90, 0.50, 0.10),
    "dark":     (0.10, 0.10, 0.12),
    "wood":     (0.50, 0.35, 0.20),
}


def _mat(color_key):
    name = f"guide_{color_key}"
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        col = PALETTE.get(color_key, (0.5, 0.5, 0.5))
        bsdf = m.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (*col, 1.0)
            bsdf.inputs["Roughness"].default_value = 0.9
        m.diffuse_color = (*col, 1.0)
    return m


def _move_to(ob, coll):
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    coll.objects.link(ob)


def box(coll, name, cx, cy, cz, sx, sy, sz, color):
    """Box centred at (cx,cy,cz) with full sizes (sx,sy,sz)."""
    hx, hy, hz = sx / 2, sy / 2, sz / 2
    x0, x1, y0, y1, z0, z1 = cx-hx, cx+hx, cy-hy, cy+hy, cz-hz, cz+hz
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
         (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    f = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1),
         (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(v, [], f)
    me.update()
    me.materials.append(_mat(color))
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    return ob


def cyl(coll, name, cx, cy, cz, radius, depth, color, axis="Z"):
    rot = {"Z": (0, 0, 0), "X": (0, math.radians(90), 0),
           "Y": (math.radians(90), 0, 0)}[axis]
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth,
                                        location=(cx, cy, cz), rotation=rot,
                                        vertices=16)
    ob = bpy.context.active_object
    ob.name = name
    ob.data.materials.append(_mat(color))
    _move_to(ob, coll)
    return ob


def ball(coll, name, cx, cy, cz, radius, color):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=(cx, cy, cz),
                                         segments=16, ring_count=8)
    ob = bpy.context.active_object
    ob.name = name
    ob.data.materials.append(_mat(color))
    _move_to(ob, coll)
    return ob


# --- builders (initial geometry; refine against --previews) --------------
# Each takes the target collection; builds facing -Y, feet at Z=0, centred X=0.

def build_boy(c):
    box(c, "boy_leg_l", -0.11, 0, 0.30, 0.16, 0.18, 0.60, "boy")
    box(c, "boy_leg_r", 0.11, 0, 0.30, 0.16, 0.18, 0.60, "boy")
    box(c, "boy_torso", 0, 0, 0.85, 0.42, 0.24, 0.55, "boy")
    box(c, "boy_arm_l", -0.30, 0, 0.85, 0.10, 0.10, 0.48, "skin")
    box(c, "boy_arm_r", 0.30, 0, 0.85, 0.10, 0.10, 0.48, "skin")
    ball(c, "boy_head", 0, 0, 1.20, 0.15, "skin")


def build_mom(c):
    box(c, "mom_skirt", 0, 0, 0.42, 0.52, 0.34, 0.84, "mom")
    box(c, "mom_torso", 0, 0, 1.05, 0.42, 0.24, 0.52, "mom")
    box(c, "mom_apron", 0, -0.18, 0.62, 0.30, 0.04, 0.60, "white")
    box(c, "mom_arm_l", -0.30, 0, 1.05, 0.10, 0.10, 0.46, "skin")
    box(c, "mom_arm_r", 0.30, 0, 1.05, 0.10, 0.10, 0.46, "skin")
    ball(c, "mom_head", 0, 0, 1.52, 0.16, "skin")
    for i in range(6):
        a = math.radians(30 + i * 24)
        ball(c, f"mom_curler_{i}", 0.13 * math.cos(a), 0.02,
             1.62 + 0.06 * math.sin(a), 0.04, "white")


def build_sheriff(c):
    box(c, "sh_leg_l", -0.13, 0, 0.34, 0.18, 0.20, 0.68, "sheriff")
    box(c, "sh_leg_r", 0.13, 0, 0.34, 0.18, 0.20, 0.68, "sheriff")
    ball(c, "sh_belly", 0, -0.06, 0.98, 0.30, "sheriff")
    box(c, "sh_torso", 0, 0, 1.20, 0.46, 0.26, 0.40, "sheriff")
    box(c, "sh_arm_l", -0.34, 0, 1.10, 0.11, 0.11, 0.50, "sheriff")
    box(c, "sh_arm_r", 0.34, 0, 1.10, 0.11, 0.11, 0.50, "sheriff")
    ball(c, "sh_head", 0, 0, 1.58, 0.16, "skin")
    cyl(c, "sh_hat_brim", 0, 0, 1.70, 0.28, 0.03, "hat", axis="Z")
    cyl(c, "sh_hat_crown", 0, 0, 1.77, 0.15, 0.14, "hat", axis="Z")


def build_machine_gun(c):
    box(c, "mg_receiver", 0.0, 0, 0.18, 0.55, 0.12, 0.14, "metal")
    cyl(c, "mg_barrel", 0.48, 0, 0.20, 0.03, 0.55, "metal", axis="X")
    box(c, "mg_mag", 0.02, 0, 0.06, 0.10, 0.08, 0.16, "metal")
    box(c, "mg_stock", -0.40, 0, 0.15, 0.30, 0.10, 0.16, "wood")
    box(c, "mg_grip", -0.10, 0, 0.05, 0.08, 0.08, 0.12, "wood")


def build_printer(c):
    box(c, "pr_base", 0, 0, 0.10, 0.90, 0.90, 0.20, "plastic")
    for i, (x, y) in enumerate([(-0.4, -0.4), (0.4, -0.4), (-0.4, 0.4), (0.4, 0.4)]):
        cyl(c, f"pr_post_{i}", x, y, 0.75, 0.03, 1.10, "metal", axis="Z")
    box(c, "pr_gantry", 0, 0, 1.00, 0.90, 0.12, 0.08, "metal")
    box(c, "pr_head", 0, 0, 0.95, 0.12, 0.12, 0.14, "metal")
    box(c, "pr_top", 0, 0, 1.35, 0.90, 0.90, 0.10, "plastic")


def build_action_figure(c):
    box(c, "af_leg_l", -0.14, 0, 0.45, 0.18, 0.20, 0.90, "plastic")
    box(c, "af_leg_r", 0.14, 0, 0.45, 0.18, 0.20, 0.90, "plastic")
    box(c, "af_torso", 0, 0, 1.20, 0.50, 0.28, 0.60, "plastic")
    box(c, "af_arm_l", -0.36, 0, 1.20, 0.12, 0.12, 0.58, "plastic")
    box(c, "af_arm_r", 0.36, 0, 1.20, 0.12, 0.12, 0.58, "plastic")
    ball(c, "af_head", 0, 0, 1.65, 0.15, "skin")


def build_delivery_truck(c):
    box(c, "dt_cargo", 0.3, 0, 1.80, 2.20, 2.00, 2.40, "truck")
    box(c, "dt_cab", -1.6, 0, 1.20, 1.00, 2.00, 1.60, "cruiser")
    for i, (x, y) in enumerate([(-1.4, -1.0), (-1.4, 1.0),
                                (1.1, -1.0), (1.1, 1.0)]):
        cyl(c, f"dt_wheel_{i}", x, y, 0.40, 0.40, 0.30, "tire", axis="Y")


def build_cruiser(c):
    box(c, "cr_body", 0, 0, 0.70, 3.60, 1.70, 0.60, "cruiser")
    box(c, "cr_cabin", 0, 0, 1.15, 1.90, 1.60, 0.60, "cruiser")
    for i, (x, y) in enumerate([(-1.2, -0.85), (-1.2, 0.85),
                                (1.2, -0.85), (1.2, 0.85)]):
        cyl(c, f"cr_wheel_{i}", x, y, 0.35, 0.35, 0.25, "tire", axis="Y")
    box(c, "cr_lightbar", 0, 0, 1.50, 0.60, 0.40, 0.12, "lightbar")


def build_rosco(c):
    box(c, "ro_slide", 0.0, 0, 0.15, 0.22, 0.05, 0.06, "metal")
    box(c, "ro_grip", -0.07, 0, 0.065, 0.06, 0.05, 0.13, "dark")


def build_big_pistol(c):
    box(c, "bp_slide", 0.0, 0, 0.34, 0.52, 0.10, 0.12, "metal")
    cyl(c, "bp_barrel", 0.30, 0, 0.34, 0.05, 0.14, "metal", axis="X")
    box(c, "bp_grip", -0.16, 0, 0.15, 0.12, 0.10, 0.30, "dark")


def build_santa(c):
    box(c, "sa_body", 0, 0, 0.60, 0.60, 0.42, 1.20, "santa")
    box(c, "sa_belt", 0, -0.01, 0.72, 0.62, 0.44, 0.12, "dark")
    ball(c, "sa_head", 0, 0, 1.42, 0.22, "skin")
    ball(c, "sa_hat", 0, 0, 1.62, 0.15, "santa")
    ball(c, "sa_hat_tip", 0.05, 0, 1.76, 0.05, "white")
    box(c, "sa_tape", 0, -0.22, 0.90, 0.20, 0.02, 0.34, "white")


def build_scale_stick(c):
    cyl(c, "ss_pole", 0, 0, 1.00, 0.03, 2.00, "ref", axis="Z")
    for i in range(1, 5):
        col = "white" if i % 2 else "ref"
        cyl(c, f"ss_tick_{i}", 0, 0, i * 0.5, 0.12, 0.02, col, axis="Z")


BUILDERS = {
    "boy": build_boy, "mom": build_mom, "sheriff": build_sheriff,
    "machine_gun": build_machine_gun, "printer": build_printer,
    "action_figure": build_action_figure, "delivery_truck": build_delivery_truck,
    "cruiser": build_cruiser, "rosco": build_rosco, "big_pistol": build_big_pistol,
    "santa": build_santa, "scale_stick": build_scale_stick,
}


# --- build / check / previews -------------------------------------------

def _wipe():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    scene = bpy.context.scene
    for coll in list(bpy.data.collections):
        try:
            scene.collection.children.unlink(coll)
        except (RuntimeError, ReferenceError):
            pass
        bpy.data.collections.remove(coll)


def build_guide_file(specs, out_path):
    _wipe()
    scene = bpy.context.scene
    for spec in specs:
        coll = bpy.data.collections.new(spec.name)
        scene.collection.children.link(coll)
        BUILDERS[spec.name](coll)
        coll.asset_mark()
        uuid, _path, simple = guides.CATALOGS[spec.catalog]
        coll.asset_data.catalog_id = uuid
        coll.asset_data.catalog_simple_name = simple
    check_structural(specs)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out_path), relative_remap=True)
    print(f"guide file saved: {out_path}")


def _coll_bounds(coll):
    xs, ys, zs = [], [], []
    for ob in coll.objects:
        for corner in ob.bound_box:
            wc = ob.matrix_world @ Vector(corner)
            xs.append(wc.x); ys.append(wc.y); zs.append(wc.z)
    return (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))


def check_structural(specs):
    for spec in specs:
        coll = bpy.data.collections.get(spec.name)
        assert coll is not None, f"missing collection {spec.name}"
        assert coll.asset_data is not None, f"{spec.name} not marked as asset"
        expect = guides.CATALOGS[spec.catalog][0]
        assert coll.asset_data.catalog_id == expect, \
            f"{spec.name} catalog {coll.asset_data.catalog_id} != {expect}"
        assert len(coll.objects) > 0, f"{spec.name} is empty"


def check_dimensions(specs):
    for spec in specs:
        coll = bpy.data.collections.get(spec.name)
        x0, x1, _y0, _y1, z0, z1 = _coll_bounds(coll)
        assert abs(z0) <= FEET_TOL, f"{spec.name} feet z={z0:.3f} not at 0"
        cx = (x0 + x1) / 2
        assert abs(cx) <= CENTRE_TOL, f"{spec.name} centre x={cx:.3f} off-axis"
        h = z1 - z0
        assert abs(h - spec.height) <= HEIGHT_TOL * spec.height, \
            f"{spec.name} height {h:.2f} != {spec.height} (+-{HEIGHT_TOL:.0%})"


def run_check():
    tmp = Path(tempfile.mkdtemp(prefix="guides_check_"))
    for rel in (guides.CAST_FILE, guides.PROPS_FILE):
        specs = guides.guides_for_file(rel)
        build_guide_file(specs, tmp / Path(rel).name)
        check_dimensions(specs)
    print("GUIDE CHECK OK")


def render_previews(specs, outdir):
    outdir.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    engines = {i.identifier for i in
               bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items}
    scene.render.engine = ("BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engines
                           else "BLENDER_EEVEE")
    scene.render.resolution_x = scene.render.resolution_y = 512
    scene.render.film_transparent = True
    for spec in specs:
        coll = bpy.data.collections.get(spec.name)
        x0, x1, _y0, _y1, z0, z1 = _coll_bounds(coll)
        span = max(x1 - x0, z1 - z0, 0.3) * 1.4
        cam_data = bpy.data.cameras.new(f"prev_{spec.name}")
        cam_data.type = "ORTHO"
        cam_data.ortho_scale = span
        cam = bpy.data.objects.new(f"prev_{spec.name}", cam_data)
        cam.location = (0.0, -8.0, (z0 + z1) / 2)
        cam.rotation_euler = (math.radians(90), 0.0, 0.0)
        scene.collection.objects.link(cam)
        scene.camera = cam
        for other in guides.guides_for_file(spec.file):
            oc = bpy.data.collections.get(other.name)
            oc.hide_render = (other.name != spec.name)
        scene.render.filepath = str(outdir / f"{spec.name}.png")
        bpy.ops.render.render(write_still=True)
        bpy.data.objects.remove(cam, do_unlink=True)
        print(f"preview: {spec.name}")


def mark_property_asset():
    root = shotlib.project_root()
    path = root / guides.PROPERTY_FILE
    bpy.ops.wm.open_mainfile(filepath=str(path))
    coll = bpy.data.collections.get("property")
    if coll is None:
        sys.exit("error: no `property` collection in property.blend")
    if coll.asset_data is None:
        coll.asset_mark()
    uuid, _p, simple = guides.CATALOGS["set"]
    coll.asset_data.catalog_id = uuid
    coll.asset_data.catalog_simple_name = simple
    # ensure the shared cats file exists next to assets/
    (root / "assets" / "blender_assets.cats.txt").write_text(guides.cats_file_text())
    bpy.ops.wm.save_as_mainfile(filepath=str(path), relative_remap=True)
    print(f"marked property collection as asset in {path}")


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    force = "--force" in argv
    out_dir = previews = None
    for a in argv:
        if a.startswith("--out="):
            out_dir = Path(a.split("=", 1)[1])
        elif a.startswith("--previews="):
            previews = Path(a.split("=", 1)[1])

    if "--check" in argv:
        run_check()
        return
    if "--mark-property" in argv:
        mark_property_asset()
        return

    root = shotlib.project_root()
    for rel in (guides.CAST_FILE, guides.PROPS_FILE):
        specs = guides.guides_for_file(rel)
        out_path = (out_dir / Path(rel).name) if out_dir else (root / rel)
        if out_dir is None and out_path.exists() and not force:
            sys.exit(f"error: {out_path.relative_to(root)} exists and is now "
                     "hand-maintained. Edit it in Blender, or pass --force to "
                     "regenerate (DESTROYS manual edits); --out=<dir> for a "
                     "throwaway build.")
        build_guide_file(specs, out_path)
        if previews:
            render_previews(specs, previews)

    cats_dir = out_dir if out_dir else (root / "assets")
    cats_dir.mkdir(parents=True, exist_ok=True)
    (cats_dir / "blender_assets.cats.txt").write_text(guides.cats_file_text())
    print("cats file written")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tools/tests/test_blender_smoke.py -v` (on the Blender machine, `$BLENDER` set).
Expected: PASS — output contains `GUIDE CHECK OK` and `ALL CHECKS OK`.
Also run the whole suite: `python3 -m pytest tools/tests/ -v` → all pass (pure-Python tests + the smoke test).

- [ ] **Step 5: Commit**

```bash
git add tools/guide_assets.py tools/tests/check_blender.py tools/tests/test_blender_smoke.py
git commit -m "feat: guide_assets build script + Blender smoke checks

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Q5Hhdvq9TU6goE9exjCHyB"
```

---

## Task 3: Generate + commit the asset files, mark property

This task runs the generators, eyeballs the silhouettes, iterates the builder numbers if needed, and commits the binary outputs. No new code unless previews demand geometry tweaks (edit `guide_assets.py` builders and rerun).

**Files:**
- Generate + commit: `assets/chars/cast.blend`, `assets/props/props.blend`, `assets/blender_assets.cats.txt`
- Modify + commit: `assets/envs/property/property.blend`

- [ ] **Step 1: Confirm `.blend` is LFS-tracked**

Run: `git check-attr filter -- assets/chars/cast.blend`
Expected: `assets/chars/cast.blend: filter: lfs`. If not, add `*.blend filter=lfs diff=lfs merge=lfs -text` to `.gitattributes` and commit that first.

- [ ] **Step 2: Build the asset files**

Run:
```bash
"$BLENDER" --background --factory-startup --python-exit-code 1 \
    --python tools/guide_assets.py
```
Expected: `guide file saved: .../cast.blend`, `.../props.blend`, `cats file written`. Files exist:
```bash
ls -la assets/chars/cast.blend assets/props/props.blend assets/blender_assets.cats.txt
```

- [ ] **Step 3: Render previews and eyeball them**

Run:
```bash
"$BLENDER" --background --factory-startup --python-exit-code 1 \
    --python tools/guide_assets.py -- --force \
    --previews=/private/tmp/claude-501/-Users-icarpenter-blender-redwood-video/c3b19852-cde0-4ad6-b600-d919f4364db2/scratchpad/guide_previews
```
Open the PNGs. Each guide should be recognisable in front elevation. If a silhouette reads wrong, adjust that builder's numbers in `guide_assets.py`, rerun this step (with `--force`), and repeat. Surface the previews to the human for a thumbs-up before committing.

- [ ] **Step 4: Mark the property set as an asset**

Run:
```bash
"$BLENDER" --background --factory-startup --python-exit-code 1 \
    --python tools/guide_assets.py -- --mark-property
```
Expected: `marked property collection as asset in .../property.blend`.

- [ ] **Step 5: Re-run the smoke test, then commit**

Run: `python3 -m pytest tools/tests/test_blender_smoke.py -v` → PASS.

```bash
git add assets/chars/cast.blend assets/props/props.blend \
        assets/blender_assets.cats.txt assets/envs/property/property.blend
git commit -m "feat: generate cast + props scale guides; catalog + mark property asset

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Q5Hhdvq9TU6goE9exjCHyB"
```
(If `guide_assets.py` builders were tweaked in Step 3, `git add tools/guide_assets.py` too.)

---

## Task 4: `make_boards.py` guides-collection heal

**Files:**
- Modify: `tools/make_boards.py`

**Interfaces:**
- Consumes: `guides.guides_collection_name`.
- Produces: `ensure_guides_collection(scene) -> bool` (True if it created the collection). Verified by `tools/tests/check_blender.py` (already written in Task 2).

- [ ] **Step 1: The test already exists and currently fails**

`check_blender.py` calls `make_boards.ensure_guides_collection`, which does not exist yet. Confirm the failure is now *only* the missing function (guides build already passes):

Run: `python3 -m pytest tools/tests/test_blender_smoke.py -v`
Expected: FAIL at `ensure_guides_collection` (AttributeError inside Blender → non-zero exit). (Skipped if no `$BLENDER`.)

- [ ] **Step 2: Add the import**

In `tools/make_boards.py`, the existing block is:

```python
sys.path.insert(0, str(Path(__file__).resolve().parent))
import shotlib
```

Change it to:

```python
sys.path.insert(0, str(Path(__file__).resolve().parent))
import shotlib
import guides
```

- [ ] **Step 3: Add the `ensure_guides_collection` function**

In `tools/make_boards.py`, add this function just above `def build_scene(` :

```python
def ensure_guides_collection(scene):
    """Per-scene, non-rendering collection for movable drawing guides.

    Names are globally unique in Blender, so each board owns
    `<code>_guides`. hide_render keeps guides out of the animatic; it is set
    active so Asset-Browser drops land here. Returns True if newly created.
    """
    name = guides.guides_collection_name(scene.name)
    coll = scene.collection.children.get(name)
    created = coll is None
    if created:
        coll = bpy.data.collections.new(name)
        scene.collection.children.link(coll)
    coll.hide_render = True
    vl = scene.view_layers[0]
    lc = vl.layer_collection.children.get(coll.name)
    if lc is not None:
        vl.active_layer_collection = lc
    return created
```

- [ ] **Step 4: Call it for new scenes**

In `build_scene`, the function currently ends with:

```python
    if track is not None:
        se = scene.sequence_editor_create()
        strips = se.strips if hasattr(se, "strips") else se.sequences
        strips.new_sound(name="track", filepath=str(track), channel=1,
                         frame_start=1)
    return scene
```

Insert the call before `return scene`:

```python
    if track is not None:
        se = scene.sequence_editor_create()
        strips = se.strips if hasattr(se, "strips") else se.sequences
        strips.new_sound(name="track", filepath=str(track), channel=1,
                         frame_start=1)

    ensure_guides_collection(scene)
    return scene
```

- [ ] **Step 5: Heal existing scenes**

In `main`, the heal loop starts with:

```python
        for sc in bpy.data.scenes:
            if sc.world is None:
                sc.world = paper_world()
                healed += 1
```

Add a guides-collection heal at the top of that loop body:

```python
        for sc in bpy.data.scenes:
            if ensure_guides_collection(sc):
                healed += 1
            if sc.world is None:
                sc.world = paper_world()
                healed += 1
```

- [ ] **Step 6: Run the smoke test to verify it passes**

Run: `python3 -m pytest tools/tests/test_blender_smoke.py -v`
Expected: PASS — `ALL CHECKS OK` (guides collection created, `hide_render` True, idempotent).

- [ ] **Step 7: Heal the real boards file**

Run:
```bash
"$BLENDER" --background --factory-startup --python-exit-code 1 \
    --python tools/make_boards.py
```
Expected: `boards.blend: +0 board scene(s), 38 healed, N total` (38 guides collections created on this first run; reruns report 0 healed).

- [ ] **Step 8: Commit**

```bash
git add tools/make_boards.py boards/boards.blend
git commit -m "feat: make_boards seeds a non-rendering per-scene guides collection

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Q5Hhdvq9TU6goE9exjCHyB"
```

---

## Task 5: `redwood_guides` add-on

**Files:**
- Create: `tools/addons/redwood_guides.py`

**Interfaces:**
- Consumes: `guides.GUIDES`, `guides.guide_by_name`, `guides.guides_collection_name`, `guides.DROP_LOCATION`; `make_boards.ensure_guides_collection`.
- Produces: an enabled add-on adding **View3D ▸ Sidebar ▸ Redwood ▸ Add Guide**.

The add-on's logic is thin and depends on live Blender library-linking, so it is verified by manual acceptance (Step 3) rather than an automated test — the shared, testable pieces (registry, naming, transform) already live in `guides.py` under Task 1's tests.

- [ ] **Step 1: Write the add-on**

Create `tools/addons/redwood_guides.py`:

```python
"""Redwood scale-guide dropper.

Drops a linked instance of a cast/prop guide into the current board scene's
non-rendering guides collection, facing the board camera. Locates the project
by walking up from the open .blend (boards.blend), so enable it with a board
file open. Asset-Browser drag-drop is the manual equivalent.
"""
import sys
from pathlib import Path

import bpy

bl_info = {
    "name": "Redwood Guides",
    "author": "redwood_video",
    "version": (1, 0),
    "blender": (5, 1, 0),
    "location": "View3D > Sidebar > Redwood",
    "description": "Drop movable scale-guides into board scenes",
    "category": "Object",
}


def _project_root():
    """Walk up from the open file to a dir containing tools/ and assets/."""
    if not bpy.data.filepath:
        return None
    for p in Path(bpy.data.filepath).resolve().parents:
        if (p / "tools" / "guides.py").exists() and (p / "assets").is_dir():
            return p
    return None


def _load_guides():
    root = _project_root()
    if root is None:
        return None, None
    tools = str(root / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    import guides  # noqa: E402
    import make_boards  # noqa: E402
    return root, (guides, make_boards)


# Cache the item tuples: Blender can crash if an EnumProperty items callback
# returns strings that Python then garbage-collects. Keep a strong reference.
_ITEMS_CACHE = [("__none__", "Open a board file first", "")]


def _guide_items(self, context):
    global _ITEMS_CACHE
    root, mods = _load_guides()
    if mods is not None:
        guides_mod, _ = mods
        _ITEMS_CACHE = [(g.name, g.name.replace("_", " "), g.catalog)
                        for g in guides_mod.GUIDES]
    return _ITEMS_CACHE


class REDWOOD_OT_add_guide(bpy.types.Operator):
    bl_idname = "redwood.add_guide"
    bl_label = "Add Guide"
    bl_description = "Link the chosen guide into this scene's guides collection"
    bl_options = {"REGISTER", "UNDO"}

    guide: bpy.props.EnumProperty(name="Guide", items=_guide_items)

    def execute(self, context):
        root, mods = _load_guides()
        if mods is None:
            self.report({"ERROR"}, "Open boards.blend from the project first")
            return {"CANCELLED"}
        guides_mod, make_boards = mods
        spec = guides_mod.guide_by_name(self.guide)
        if spec is None:
            self.report({"ERROR"}, f"Unknown guide {self.guide}")
            return {"CANCELLED"}

        scene = context.scene
        make_boards.ensure_guides_collection(scene)
        gcoll = scene.collection.children[
            guides_mod.guides_collection_name(scene.name)]

        filepath = str(root / spec.file)
        linked = next((c for c in bpy.data.collections
                       if c.name == spec.name and c.library
                       and Path(c.library.filepath).name == Path(spec.file).name),
                      None)
        if linked is None:
            with bpy.data.libraries.load(filepath, link=True) as (src, dst):
                if spec.name not in src.collections:
                    self.report({"ERROR"},
                                f"{spec.name} not in {spec.file}")
                    return {"CANCELLED"}
                dst.collections = [spec.name]
            linked = dst.collections[0]

        inst = bpy.data.objects.new(spec.name, None)
        inst.instance_type = "COLLECTION"
        inst.instance_collection = linked
        inst.location = guides_mod.DROP_LOCATION
        gcoll.objects.link(inst)

        for ob in context.selected_objects:
            ob.select_set(False)
        inst.select_set(True)
        context.view_layer.objects.active = inst
        self.report({"INFO"}, f"Added {spec.name}")
        return {"FINISHED"}


class REDWOOD_PT_guides(bpy.types.Panel):
    bl_label = "Add Guide"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Redwood"

    def draw(self, context):
        col = self.layout.column()
        if _project_root() is None:
            col.label(text="Open boards.blend from the project", icon="ERROR")
            return
        col.prop(context.scene, "redwood_guide", text="")
        op = col.operator("redwood.add_guide", icon="OUTLINER_OB_EMPTY")
        op.guide = context.scene.redwood_guide


def register():
    bpy.utils.register_class(REDWOOD_OT_add_guide)
    bpy.utils.register_class(REDWOOD_PT_guides)
    bpy.types.Scene.redwood_guide = bpy.props.EnumProperty(
        name="Guide", items=_guide_items)


def unregister():
    del bpy.types.Scene.redwood_guide
    bpy.utils.unregister_class(REDWOOD_PT_guides)
    bpy.utils.unregister_class(REDWOOD_OT_add_guide)


if __name__ == "__main__":
    register()
```

- [ ] **Step 2: Sanity-check it imports/registers headless**

Run:
```bash
"$BLENDER" --background --factory-startup --python-exit-code 1 \
    --python-expr "import sys; sys.path.insert(0,'tools/addons'); import redwood_guides; redwood_guides.register(); redwood_guides.unregister(); print('ADDON OK')"
```
Expected: `ADDON OK` (registers and unregisters without error; the panel shows the "open a board file" hint when no project is found — that's correct headless).

- [ ] **Step 3: Manual acceptance (GUI, on the Blender machine)**

1. Blender ▸ Preferences ▸ Add-ons ▸ Install → pick `tools/addons/redwood_guides.py` → enable **Redwood Guides**. (Install-in-place: or add `tools/addons` to File Paths ▸ Scripts.)
2. One-time: Preferences ▸ File Paths ▸ Asset Libraries ▸ add the project `assets/` folder.
3. Open `boards/boards.blend`, switch to a board scene (e.g. `sq010_sh010`).
4. Sidebar (N) ▸ **Redwood** ▸ Add Guide → pick `boy` → **Add Guide**. A boy instance appears at `(0, 1.5, 0)` in the `sq010_sh010_guides` collection, selected, facing the camera.
5. Move/rotate/scale it; confirm it does **not** appear in a render: `F12` (or check the `guides` collection's camera toggle is off) → the render is blank white paper.
6. Confirm Asset-Browser drag-drop of `mom` (from the `guides/cast` catalog) into the guides collection also works.

Report results to the human. If any step fails, fix and rerun.

- [ ] **Step 4: Commit**

```bash
git add tools/addons/redwood_guides.py
git commit -m "feat: redwood_guides add-on — one-click guide dropper for boards

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Q5Hhdvq9TU6goE9exjCHyB"
```

---

## Task 6: Docs

**Files:**
- Create: `docs/boards.md`
- Modify: `docs/tools.md`
- Modify: `docs/treatment/site.md`

- [ ] **Step 1: Write `docs/boards.md`**

Create `docs/boards.md`:

```markdown
# Boards & drawing guides

`boards/boards.blend` holds one Grease Pencil scene per shotlist row (built by
`tools/make_boards.py`): a paper stage — GP plane at the origin, camera at
`(0,-10,0)` looking `+Y`, white paper world. You draw the animatic here; a board
graduates into the edit once its GP has any stroke (see `conform_edit`).

## Scale guides

Recognisable, correctly-scaled 3D stand-ins for the cast and hero props, to
draw over. They give truthful relative scale and composition and **never
render** into the animatic.

- **Cast** (`assets/chars/cast.blend`): `boy`, `mom`, `sheriff`.
- **Props** (`assets/props/props.blend`): `machine_gun`, `printer`,
  `action_figure`, `delivery_truck`, `cruiser`, `rosco`, `big_pistol`, `santa`,
  `scale_stick`.
- **Set** (`assets/envs/property/property.blend`): the whole `property`
  massing, for wide establishing boards.

All are catalogued Assets (`guides/cast`, `guides/props`, `guides/set`) via
`assets/blender_assets.cats.txt`. Regenerate cast/props with
`tools/guide_assets.py` (see `tools.md`).

### One-time setup

1. **Asset library:** Preferences ▸ File Paths ▸ Asset Libraries → add the
   project `assets/` folder. Every guide now shows in the Asset Browser.
2. **Add-on:** Preferences ▸ Add-ons ▸ Install → `tools/addons/redwood_guides.py`
   → enable **Redwood Guides**.

### Drawing with guides

Each board scene owns a non-rendering collection `<shotcode>_guides` (created by
`make_boards.py`; its render toggle is off and it is the active collection).

- **Add a guide:** Sidebar (N) ▸ **Redwood** ▸ Add Guide → pick one → it drops
  into the guides collection at `(0, 1.5, 0)` — just behind the paper — facing
  the camera. Or drag it from the Asset Browser (it lands in the active guides
  collection as a *linked* instance).
- **Position it:** move/rotate/scale as a single unit for the shot's framing.
  Guides are rigid; if you need a distinct pose (e.g. the boy aiming), ask for a
  variant collection rather than trying to deform the instance.
- **It won't render:** guides live in a `hide_render` collection, so `F12` and
  `conform_edit` only ever see your strokes.

Guides are throwaway references — delete or leave them; they never reach the
edit.
```

- [ ] **Step 2: Add a `guide_assets.py` section to `docs/tools.md`**

In `docs/tools.md`, immediately after the `### tools/make_boards.py …` section (which ends before `### tools/conform_edit.py`), insert:

```markdown
### `tools/guide_assets.py` — build the drawing-guide assets

```sh
"$BLENDER" --background --factory-startup --python-exit-code 1 \
    --python tools/guide_assets.py
# --force          overwrite the (now hand-maintained) asset files
# --out=<dir>       throwaway build into <dir>
# --previews=<dir>  render each guide to <dir>/<name>.png
# --check           build to a temp dir + assert invariants
# --mark-property   mark the `property` collection as a catalogued asset
```

Builds `assets/chars/cast.blend` and `assets/props/props.blend` — one
recognisable, real-scale, primitive-built collection per cast member and hero
prop — plus `assets/blender_assets.cats.txt`. Each collection is a catalogued
Asset (`guides/cast`, `guides/props`). These are drawing scale-guides for the
animatic: they link into board scenes and never render. See `docs/boards.md`.
Declarative registry lives in `tools/guides.py`; covered by
`tools/tests/test_guides.py` and the headless `tools/tests/test_blender_smoke.py`.
```

Also, in the existing `### tools/make_boards.py` section, append one sentence to
its description paragraph:

```markdown
Every board scene also gets a non-rendering `<shotcode>_guides` collection for
movable drawing guides (see `docs/boards.md`); reruns heal it into existing
scenes.
```

- [ ] **Step 3: Cross-link from `site.md`**

In `docs/treatment/site.md`, at the end of the `## Status` section, append:

```markdown

Movable, correctly-scaled drawing guides for the cast and hero props live in
`assets/chars/cast.blend` and `assets/props/props.blend`; the `property` set is
itself a linkable guide. See `docs/boards.md` for the drawing-guide workflow.
```

- [ ] **Step 4: Commit**

```bash
git add docs/boards.md docs/tools.md docs/treatment/site.md
git commit -m "docs: drawing-guide workflow (boards.md) + tool/site cross-links

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Q5Hhdvq9TU6goE9exjCHyB"
```

---

## Final verification

- [ ] `python3 -m pytest tools/tests/ -v` → all pass (smoke test PASS on the Blender machine, not skipped).
- [ ] Asset Browser shows all 12 guides + `property` under the `guides/*` catalogs.
- [ ] A board scene: Add Guide → position → `F12` renders blank paper (guide hidden).
- [ ] `git status` clean; `git log --oneline -6` shows the six task commits.
```
