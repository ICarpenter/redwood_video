# Camera-Driven Layout Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the boards/shots split with one camera-driven layout file where the property is static at world origin, the camera is the sole framing authority, and blocking is world-space and reusable.

**Architecture:** `boards/boards.blend` becomes `layout/layout.blend` — one scene per shotlist row, each holding a shot camera, a `<code>_blocking` collection of linked cast/prop instances positioned in world space, the property linked at identity, and a Grease Pencil "paper" parented to the camera as an optional overlay. Shot `.blend` files stop being a mandatory stage and become an on-demand export.

**Tech Stack:** Blender 5.1.2 (`bpy`, `mathutils`), stdlib-only Python 3 for the bpy-free modules, `unittest`, bash.

**Spec:** `docs/superpowers/specs/2026-07-31-camera-driven-layout-design.md`

## Global Constraints

- **Blender is found via `shotlib.find_blender()`** (`$BLENDER` → `PATH` → `/Applications/Blender.app/Contents/MacOS/Blender`). Never hardcode the path.
- **`shotlib.py` and `guides.py` are bpy-free** — stdlib only, importable under system Python. `layoutlib.py` is the bpy-aware counterpart. Do not import `bpy` into the first two.
- **Test command:** `python3 -m unittest discover -s tools/tests -t tools/tests`. The `-t` is required — `tools/tests` has no `__init__.py` and plain discovery from the repo root fails with "Start directory is not importable".
- **Blender-side assertions live in `tools/tests/check_blender.py`**, run inside Blender and wrapped by `tools/tests/test_blender_smoke.py`, which asserts the string `ALL CHECKS OK` in stdout. Add-on assertions live in `check_addon.py` / `test_addon_smoke.py`. There is no `test_boardlib.py` and there will be no `test_layoutlib.py` — bpy-aware code is covered by `check_blender.py`. **This corrects the spec's Testing section**, which proposed a system-Python `test_layoutlib.py`; `shot_ready` needs `bpy` and cannot run there.
- **Blender must be closed** before running any tool that writes a `.blend` headlessly. An open session's later save clobbers the result.
- **`matrix_world` is identity in `--background`** until a depsgraph evaluation. Before reading any matrix: `scene.frame_set(f)`, then `ob.evaluated_get(depsgraph)`.
- **Slotted actions:** `action.fcurves` no longer exists. Traverse `action.layers[0].strips[0].channelbag(slot)`. Note `strip.channelbags` is a collection while `strip.channelbag(slot)` is a function.
- **Scenes created via the data API have no world** → black viewport and black renders. Always assign one.
- **Commit explicit paths, never `git add -A`.** End every commit message with:
  ```
  Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
  Claude-Session: https://claude.ai/code/session_01QWjoTLDghmnsCjTkDiBrGc
  ```
- **Branch:** all work lands on `camera-driven-layout`, already created and holding the spec commit.
- **`.blend` files are LFS-tracked.** Use `git mv` for path moves so LFS pointers follow.

---

## File Structure

**Created**
- `tools/layoutlib.py` — bpy-aware layout helpers (from `boardlib.py` via `git mv`)
- `tools/make_layout.py` — builds/heals `layout/layout.blend` (from `make_boards.py`)
- `tools/stage_shots.py` — declarative world-space staging (from `stage_boards.py`)
- `tools/resync_layout.py` — frame-range resync (from `resync_boards.py`)
- `tools/migrate_layout.py` — one-shot reset of the existing file
- `tools/continue_shot.py` — snapshot copy-forward between scenes
- `tools/export_shot.py` — layout scene → shot `.blend` (from `new_shot.py`)
- `layout/layout.blend` — from `boards/boards.blend` via `git mv`
- `docs/layout.md` — from `docs/boards.md`

**Modified**
- `tools/guides.py` — vocabulary rename, drop-location constants
- `tools/conform_edit.py` — layout path, simplified tiers
- `tools/make_template.py` — delegates settings to the shared function
- `tools/addons/redwood_guides.py` — ground-plane drop, blocking collection
- `tools/shotlib.py` — validate the `assets` column against the guide registry
- `tools/tests/check_blender.py`, `check_addon.py`, `test_guides.py`, `test_shotlist.py`
- `docs/pipeline.md`, `docs/tools.md`, `docs/handoff.md`, `README.md`

**Deleted**
- `tools/build_shots.py`, `tools/tests/test_build_shots.py`
- `tools/stage_property.py`
- `tools/new_shot.py` (becomes `export_shot.py`)
- `boardlib.sync_guide_visibility`

---

### Task 1: Blocking vocabulary in `guides.py`

The bpy-free registry renames first so every later task imports stable names.

**Files:**
- Modify: `tools/guides.py:8-25` (docstring + suffix + helper), `tools/guides.py:18` (`DROP_LOCATION`)
- Test: `tools/tests/test_guides.py:49-52`

**Interfaces:**
- Consumes: nothing.
- Produces: `guides.BLOCKING_SUFFIX = "_blocking"`, `guides.blocking_collection_name(scene_name: str) -> str`, `guides.DROP_DISTANCE: float = 8.0`. `DROP_LOCATION` and `guides_collection_name` are removed.

- [ ] **Step 1: Write the failing test**

Replace `test_collection_name` in `tools/tests/test_guides.py` (currently at line 49):

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest discover -s tools/tests -t tools/tests -k guides -v`
Expected: FAIL — `AttributeError: module 'guides' has no attribute 'blocking_collection_name'`

- [ ] **Step 3: Implement**

In `tools/guides.py`, replace the module docstring's second paragraph (lines 8-12) and lines 18-25 with:

```python
"""Declarative registry of animatic scale-guides.

Stdlib only — imported by guide_assets.py, make_layout.py, and the
redwood_guides add-on inside Blender, and by the test suite under system
Python. No bpy here (same rule shotlib.py follows).

Layout scenes hold the property linked at identity (world origin, ground at
z=0) and change framing by moving the camera, never the set. Guides are
authored facing -Y, feet at Z=0, centred on X=0; they are dropped in WORLD
space onto the property, so a guide's transform says where that character
stands. They live in a per-scene `<code>_blocking` collection.
"""
from __future__ import annotations

from dataclasses import dataclass

# Fallback distance along the camera's view ray when it never meets the
# z=0 ground plane (camera level or tilted up). Metres.
DROP_DISTANCE = 8.0

BLOCKING_SUFFIX = "_blocking"


def blocking_collection_name(scene_name: str) -> str:
    """Per-scene blocking collection name (globally unique, one per shot)."""
    return f"{scene_name}{BLOCKING_SUFFIX}"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest discover -s tools/tests -t tools/tests -k guides -v`
Expected: PASS (the 13-guide counts are unchanged)

- [ ] **Step 5: Commit**

```bash
git add tools/guides.py tools/tests/test_guides.py
git commit -m "refactor: guides registry speaks blocking, not board guides"
```

Note: the repo is temporarily broken — `boardlib.py`, `make_boards.py`, `stage_boards.py` and the add-on still call `guides.guides_collection_name`. Task 2 fixes `boardlib`; Tasks 4, 7 and 10 fix the rest. Run the full suite only at the end of Task 4.

---

### Task 2: `layoutlib.py` and the paper-depth verification

Builds the shared bpy-aware helper module. **Amended 2026-07-31:** this task originally gated on proving a near-field paper wins the depth test. Measurement showed GP strokes composite over meshes unconditionally in EEVEE, so the gate could not fail and was deleted, and the paper sits at 10 m (scale 1.0 at 50 mm, matching `sq010_sh010`'s strokes 1:1) rather than at the near clip. See the spec's "Paper depth" section.

**Files:**
- Create: `tools/layoutlib.py` (via `git mv tools/boardlib.py tools/layoutlib.py`)
- Modify: `tools/tests/check_blender.py`
- Delete: `boardlib.sync_guide_visibility`

**Interfaces:**
- Consumes: `guides.blocking_collection_name` (Task 1).
- Produces:
  - `layoutlib.has_strokes(scene) -> bool` (unchanged behaviour)
  - `layoutlib.blocking_collection(scene, create=False)`
  - `layoutlib.blocking_instances(scene) -> list`
  - `layoutlib.shot_ready(scene) -> bool`
  - `layoutlib.apply_hide_blocking(scene) -> bool`
  - `layoutlib.PAPER_HALF_WIDTH = 3.6`
  - `layoutlib.paper_distance(cam) -> float`
  - `layoutlib.fit_paper(gp, cam, distance=None) -> None`

- [ ] **Step 1: Move the file and rename its symbols**

```bash
git mv tools/boardlib.py tools/layoutlib.py
```

Then in `tools/layoutlib.py`: rename `guides_collection` → `blocking_collection`, `guide_instances` → `blocking_instances`, `board_ready` → `shot_ready`, and **delete `sync_guide_visibility` entirely**. Update the docstring and the `guides.guides_collection_name` call. The file becomes:

```python
#!/usr/bin/env python3
"""Shared bpy helpers for layout scenes.

shotlib.py and guides.py are deliberately bpy-free so they import under system
Python. This is their counterpart for code that must touch Blender data, shared
by make_layout.py, stage_shots.py, continue_shot.py, export_shot.py, and
conform_edit.py — they all need to ask the same questions about a shot, and the
answers must agree.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix

sys.path.insert(0, str(Path(__file__).resolve().parent))
import guides

GP_TYPES = {"GREASEPENCIL", "GPENCIL"}

# Frame half-width in paper-local units. Every paper is scaled so the camera
# frame spans +/- this at the paper's plane, whatever the lens or distance.
# 3.6 preserves the historical 10m/50mm board scale, which is what keeps
# sq010_sh010's existing 119 strokes framed exactly as drawn.
PAPER_HALF_WIDTH = 3.6


def has_strokes(scene) -> bool:
    """True once the shot's Grease Pencil holds actual strokes.

    Scenes ship with an empty starter keyframe, so keyframe existence is not
    enough — look inside the frames (GPv3: frame.drawing.strokes; legacy:
    frame.strokes).
    """
    for ob in scene.objects:
        if ob.type not in GP_TYPES:
            continue
        for layer in ob.data.layers:
            for fr in layer.frames:
                strokes = getattr(fr, "strokes", None)
                if strokes is None:
                    drawing = getattr(fr, "drawing", None)
                    strokes = getattr(drawing, "strokes", ()) if drawing else ()
                if len(strokes):
                    return True
    return False


def blocking_collection(scene, create=False):
    """The scene's blocking collection, or None. Created and linked if asked."""
    name = guides.blocking_collection_name(scene.name)
    coll = scene.collection.children.get(name)
    if coll is not None or not create:
        return coll
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
    scene.collection.children.link(coll)
    return coll


def blocking_instances(scene) -> list:
    """Collection-instance empties staged in this shot's blocking collection."""
    coll = blocking_collection(scene)
    if coll is None:
        return []
    return [o for o in coll.objects if o.instance_collection is not None]


def shot_ready(scene) -> bool:
    """True if this shot has something worth cutting into the edit.

    Either real strokes, or blocking staged. Deliberately NOT stroke-only:
    blocking major story beats is a stage the edit should be watchable at,
    same as slugs and renders.
    """
    return has_strokes(scene) or bool(blocking_instances(scene))


def apply_hide_blocking(scene) -> bool:
    """Honour the hand-set `hide_blocking` scene property. True if changed.

    Blocking and paper both render by default — the drawing is an overlay on
    top of blocked 3D, not a replacement for it. A shot taken fully 2D sets
    scene["hide_blocking"] = True by hand. NO TOOL EVER WRITES IT; that is
    exactly what distinguishes it from the automatic rule it replaces.
    """
    coll = blocking_collection(scene)
    if coll is None:
        return False
    hide = bool(scene.get("hide_blocking", False))
    if coll.hide_render == hide:
        return False
    coll.hide_render = hide
    return True


# Distance from camera to paper, in metres. Chosen for framing, NOT for
# occlusion: Grease Pencil strokes composite over mesh geometry in EEVEE
# unconditionally — measured in Blender 5.1.2, identical results at 0.11m in
# front of a wall and 10m behind it, under both stroke_depth_order modes. So
# nothing can hide the paper and the distance is free. 10m makes the scale
# below exactly 1.0 at a 50mm lens, which matches sq010_sh010's existing
# strokes 1:1.
PAPER_DISTANCE = 10.0


def paper_distance(cam) -> float:
    """Distance from camera to paper. Framing choice, not a depth trick."""
    return PAPER_DISTANCE


def fit_paper(gp, cam, distance=None) -> None:
    """Park the GP paper in front of the camera, sized to the frustum.

    Parents `gp` to `cam` and sets its local transform so a stroke at paper
    coordinate x=PAPER_HALF_WIDTH lands exactly on the right edge of frame,
    for any lens or distance. Local rotation is -90 deg about X: the paper's
    XZ drawing plane maps onto the camera's XY screen plane, which is the
    relationship the original boards had (GP unrotated at the origin, camera
    rotated +90 deg about X). Preserving it is what keeps existing strokes
    framed as drawn.

    The paper does not need to be near the camera to stay visible — see
    PAPER_DISTANCE. It is in front purely so drawing happens in camera space.
    """
    d = paper_distance(cam) if distance is None else distance
    half_w = d * (cam.data.sensor_width / 2.0) / cam.data.lens
    s = half_w / PAPER_HALF_WIDTH
    gp.parent = cam
    gp.matrix_parent_inverse = Matrix.Identity(4)
    gp.location = (0.0, 0.0, -d)
    gp.rotation_euler = (math.radians(-90), 0.0, 0.0)
    gp.scale = (s, s, s)
```

- [ ] **Step 2: Write the failing Blender check**

In `tools/tests/check_blender.py`, replace the `import boardlib` line with `import layoutlib`, delete the whole `sync_guide_visibility` block (the four asserts about `hide_render` flipping), and replace the board-readiness block with this. Leave `guide_assets.run_check()` and the `make_boards` block alone — Task 4 rewrites those.

```python
# --- blocking collection + readiness -------------------------------------
sc = bpy.data.scenes.new("sq999_sh999")
sc.world = bpy.data.worlds.new("check_world")
bc = layoutlib.blocking_collection(sc, create=True)
assert bc is not None, "blocking collection should be created"
assert bc.name == "sq999_sh999_blocking", f"unexpected name {bc.name}"
assert layoutlib.shot_ready(sc) is False, "no strokes and no blocking = not ready"

inst = bpy.data.objects.new("blocking_probe", None)
inst.instance_type = "COLLECTION"
inst.instance_collection = bpy.data.collections.new("probe_target")
bc.objects.link(inst)
assert layoutlib.blocking_instances(sc), "staged blocking should be found"
assert layoutlib.shot_ready(sc) is True, "blocking alone makes a shot edit-ready"

# --- hide_blocking is opt-in and hand-set only ---------------------------
assert bc.hide_render is False, "blocking renders by default"
assert layoutlib.apply_hide_blocking(sc) is False, "no property = no change"
sc["hide_blocking"] = True
assert layoutlib.apply_hide_blocking(sc) is True, "flag must take effect"
assert bc.hide_render is True, "hide_blocking must hide the collection"
assert layoutlib.apply_hide_blocking(sc) is False, "must be idempotent"
del sc["hide_blocking"]
layoutlib.apply_hide_blocking(sc)
assert bc.hide_render is False, "clearing the flag must restore rendering"

# --- NOTE: the paper-depth gate was removed ------------------------------
# This plan originally gated here on a render proving a near-field paper
# draws over close geometry. Measured in Blender 5.1.2 during Task 2: GP
# strokes composite over meshes UNCONDITIONALLY — same 488 ink pixels at
# 0.11m in front of a wall and at 10m behind it, under both
# stroke_depth_order modes. The assertion could not fail, so it is deleted
# rather than kept as false assurance. See the spec's "Paper depth" section.
```

- [ ] **Step 3: Run the check to verify it fails**

Run: `"${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}" --background --factory-startup --python-exit-code 1 --python tools/tests/check_blender.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'boardlib'` from `make_boards.py`, which Task 4 rewrites.

To see the new assertions run before Task 4 lands, temporarily comment out the `import make_boards` line and its block, run, then restore. The paper-depth gate must print its OK line.

- [ ] **Step 4: Verify the gate passes**

Expected: the blocking, `hide_blocking`, and `fit_paper` assertions all pass. There is no depth gate to satisfy.

- [ ] **Step 5: Commit**

```bash
git add tools/layoutlib.py tools/tests/check_blender.py
git commit -m "feat: layoutlib with camera-locked paper at a fixed framing distance"
```

---

### Task 3: One owner for project render settings

`make_template.py` and `make_boards.py` each set fps/resolution/colour independently and have already drifted (the template is AgX + PNG 16-bit, boards are Standard). One function ends that.

**Files:**
- Modify: `tools/layoutlib.py` (add `apply_project_settings`), `tools/make_template.py`
- Modify: `tools/tests/check_blender.py`

**Interfaces:**
- Consumes: Task 2's `layoutlib`.
- Produces: `layoutlib.apply_project_settings(scene, view_transform="AgX") -> None`.

- [ ] **Step 1: Write the failing check**

Append to `tools/tests/check_blender.py`, after the paper-depth gate:

```python
# --- project settings live in exactly one place --------------------------
ps = bpy.data.scenes.new("settings_probe")
layoutlib.apply_project_settings(ps)
assert ps.render.fps == 24, f"fps {ps.render.fps}"
assert (ps.render.resolution_x, ps.render.resolution_y) == (1920, 1080)
assert ps.render.image_settings.file_format == "PNG"
assert ps.render.image_settings.color_depth == "16"
assert ps.view_settings.view_transform == "AgX", ps.view_settings.view_transform
assert ps.sync_mode == "AUDIO_SYNC"
# layout scenes draw against greybox, so they opt out of AgX explicitly
ps2 = bpy.data.scenes.new("settings_probe_std")
layoutlib.apply_project_settings(ps2, view_transform="Standard")
assert ps2.view_settings.view_transform == "Standard"
assert ps2.render.fps == 24, "everything else must still apply"
print("project settings: OK")
```

- [ ] **Step 2: Run to verify it fails**

Run: `"${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}" --background --factory-startup --python-exit-code 1 --python tools/tests/check_blender.py`
Expected: FAIL — `AttributeError: module 'layoutlib' has no attribute 'apply_project_settings'`

- [ ] **Step 3: Implement**

Add to `tools/layoutlib.py`:

```python
def apply_project_settings(scene, view_transform="AgX") -> None:
    """The project's locked render settings, in one place.

    Applied to shot_template.blend and to every layout scene, so the two can
    never drift. Layout scenes pass view_transform="Standard" — they show
    greybox blocking and flat GP ink, which AgX only muddies. Renders keep
    AgX, and the edit passes them through with Standard so it is not applied
    twice.
    """
    scene.render.fps = 24
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "16"
    scene.view_settings.view_transform = view_transform
    # the block this replaces set `look` too; dropping it would make "one
    # place" a lie the moment a scene carries a non-default look
    scene.view_settings.look = "None"
    scene.sync_mode = "AUDIO_SYNC"
```

Then in `tools/make_template.py`, delete the inline settings block and call `layoutlib.apply_project_settings(scene)` instead. Add the import alongside the existing ones:

```python
import layoutlib
```

- [ ] **Step 4: Run to verify it passes**

Run: `"${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}" --background --factory-startup --python-exit-code 1 --python tools/tests/check_blender.py`
Expected: `project settings: OK`

Then rebuild and confirm the template is unchanged in substance:
Run: `"${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}" --background --factory-startup --python-exit-code 1 --python tools/make_template.py`
Expected: exit 0.

- [ ] **Step 5: Commit**

```bash
git add tools/layoutlib.py tools/make_template.py tools/shot_template.blend tools/tests/check_blender.py
git commit -m "refactor: project render settings get a single owner"
```

---

### Task 4: `make_layout.py`

Builds the new scene anatomy. This is where the invariants become real.

**Files:**
- Create: `tools/make_layout.py` (via `git mv tools/make_boards.py tools/make_layout.py`)
- Modify: `tools/tests/check_blender.py`

**Interfaces:**
- Consumes: `layoutlib.{apply_project_settings, fit_paper, blocking_collection, apply_hide_blocking}`, `guides.{blocking_collection_name, PROPERTY_FILE}`.
- Produces: `make_layout.ensure_blocking_collection(scene) -> bool`, `make_layout.link_property(scene) -> object`, `make_layout.gp_data_collection()`, `make_layout.build_scene(shot, track, ink, prompt)`.

- [ ] **Step 1: Move and rewrite**

```bash
git mv tools/make_boards.py tools/make_layout.py
```

In `tools/make_layout.py`:

Update the docstring, the import (`import boardlib` → `import layoutlib`), and the output path (`root / "boards" / "boards.blend"` → `root / "layout" / "layout.blend"`).

Replace `paper_world()` — layout scenes look at greybox in a world, not white paper:

```python
def layout_world():
    """Neutral grey so greybox blocking reads. Scenes made via the data API
    have NO world at all, which renders black."""
    w = bpy.data.worlds.get("layout")
    if w is None:
        w = bpy.data.worlds.new("layout")
        w.use_nodes = True
        bg = w.node_tree.nodes.get("Background")
        if bg is not None:
            bg.inputs["Color"].default_value = (0.55, 0.6, 0.65, 1.0)
            bg.inputs["Strength"].default_value = 1.0
    return w
```

Replace `ensure_guides_collection` with:

```python
def ensure_blocking_collection(scene):
    """Per-scene collection for world-space blocking instances.

    Names are globally unique in Blender, so each shot owns `<code>_blocking`.
    Set active so Asset-Browser drops land here. Returns True if newly created.

    Render visibility is NOT set here — blocking renders by default and only
    the hand-set `hide_blocking` scene property turns it off
    (layoutlib.apply_hide_blocking).
    """
    name = guides.blocking_collection_name(scene.name)
    created = scene.collection.children.get(name) is None
    coll = layoutlib.blocking_collection(scene, create=True)
    vl = scene.view_layers[0]
    lc = vl.layer_collection.children.get(coll.name)
    if lc is not None:
        vl.active_layer_collection = lc
    return created
```

Add property linking:

```python
def link_property(scene):
    """Link the property set at IDENTITY — the pipeline's first invariant.

    The set never moves. Framing changes by moving the camera. Returns the
    instance object, or None if the property file is missing.
    """
    name = "property"
    existing = next((o for o in scene.objects
                     if o.instance_collection is not None
                     and o.instance_collection.name == name), None)
    if existing is not None:
        return existing

    root = shotlib.project_root()
    path = root / guides.PROPERTY_FILE
    if not path.exists():
        print(f"warning: {guides.PROPERTY_FILE} missing — scene has no set")
        return None

    linked = next((c for c in bpy.data.collections
                   if c.name == name and c.library
                   and Path(c.library.filepath).name == path.name), None)
    if linked is None:
        with bpy.data.libraries.load(str(path), link=True) as (src, dst):
            if name not in src.collections:
                sys.exit(f"error: no collection {name!r} in {path}")
            dst.collections = [name]
        linked = dst.collections[0]

    inst = bpy.data.objects.new(name, None)
    inst.instance_type = "COLLECTION"
    inst.instance_collection = linked
    inst.location = (0.0, 0.0, 0.0)
    inst.rotation_euler = (0.0, 0.0, 0.0)
    inst.scale = (1.0, 1.0, 1.0)
    inst.hide_select = True   # you cannot nudge the set by accident
    scene.collection.objects.link(inst)
    return inst
```

Rewrite `build_scene` (replacing lines 130-168) — the camera keeps the default `(0,-10,0)` placement only as a starting point now, and the note joins the paper as a camera child:

```python
def build_scene(shot, track, ink, prompt):
    scene = bpy.data.scenes.new(shot.code)
    scene.world = layout_world()
    layoutlib.apply_project_settings(scene, view_transform="Standard")
    scene.frame_start = shot.start_frame
    scene.frame_end = shot.end_frame

    cam_data = bpy.data.cameras.new(f"{shot.code}_cam")
    cam = bpy.data.objects.new(f"{shot.code}_cam", cam_data)
    # A starting point only — stage_shots.py and hand framing move it. The
    # set never moves, so this is the one thing that decides the shot.
    cam.location = (0.0, -10.0, 1.6)
    cam.rotation_euler = (math.radians(90), 0.0, 0.0)
    scene.collection.objects.link(cam)
    scene.camera = cam

    gp_data = gp_data_collection().new(f"{shot.code}_board")
    if hasattr(gp_data, "materials") and ink is not None:
        gp_data.materials.append(ink)
    layer = gp_data.layers.new("lines")
    # starter keyframe so drawing works immediately; layoutlib.has_strokes
    # looks inside the frame, so an empty one does not count as drawn
    layer.frames.new(shot.start_frame)
    gp = bpy.data.objects.new(f"{shot.code}_board", gp_data)
    scene.collection.objects.link(gp)
    layoutlib.fit_paper(gp, cam)

    note = build_note(scene, shot.code, prompt)
    note.parent = cam
    note.matrix_parent_inverse = Matrix.Identity(4)
    note.location = (-1.6, 0.9, -4.0)
    note.rotation_euler = (0.0, 0.0, 0.0)

    if track is not None:
        se = scene.sequence_editor_create()
        strips = se.strips if hasattr(se, "strips") else se.sequences
        strips.new_sound(name="track", filepath=str(track), channel=1,
                         frame_start=1)

    ensure_blocking_collection(scene)
    link_property(scene)
    layoutlib.apply_hide_blocking(scene)
    return scene
```

Add `from mathutils import Matrix` to the imports.

In `main()`, update the healing loop: `ensure_guides_collection` → `ensure_blocking_collection`, `boardlib.sync_guide_visibility` → `layoutlib.apply_hide_blocking`, `paper_world()` → `layout_world()`, and add property/paper healing inside the per-scene loop:

```python
            if link_property(sc) is not None and sc.get("_property_healed") is None:
                sc["_property_healed"] = True
                healed += 1
            cam = sc.camera
            for ob in sc.objects:
                if ob.type in GP_TYPES_LOCAL and ob.parent is not cam and cam:
                    layoutlib.fit_paper(ob, cam)
                    healed += 1
```

with `GP_TYPES_LOCAL = layoutlib.GP_TYPES` defined at module level.

- [ ] **Step 2: Update the Blender check**

In `tools/tests/check_blender.py`, replace `import make_boards` with `import make_layout` and replace the old `ensure_guides_collection` block with:

```python
# --- make_layout builds the invariants into every scene ------------------
ml = bpy.data.scenes.new("sq998_sh998")
assert make_layout.ensure_blocking_collection(ml) is True, "created on first call"
assert make_layout.ensure_blocking_collection(ml) is False, "must be idempotent"

ml_cam_data = bpy.data.cameras.new("sq998_sh998_cam")
ml_cam = bpy.data.objects.new("sq998_sh998_cam", ml_cam_data)
ml.collection.objects.link(ml_cam)
ml.camera = ml_cam
ml_gp = bpy.data.objects.new(
    "sq998_sh998_board", make_layout.gp_data_collection().new("sq998_sh998_board"))
ml.collection.objects.link(ml_gp)
layoutlib.fit_paper(ml_gp, ml_cam)
assert ml_gp.parent is ml_cam, "paper must be a camera child"
assert abs(ml_gp.location.z + layoutlib.paper_distance(ml_cam)) < 1e-6
# a stroke at the paper's half-width must land on the frame edge
half_w = layoutlib.paper_distance(ml_cam) * (ml_cam_data.sensor_width / 2.0) / ml_cam_data.lens
assert abs(ml_gp.scale.x * layoutlib.PAPER_HALF_WIDTH - half_w) < 1e-9, "paper misfit"

# the property links at identity and nowhere else
prop = make_layout.link_property(ml)
if prop is not None:
    assert tuple(prop.location) == (0.0, 0.0, 0.0), f"property moved: {prop.location}"
    assert tuple(prop.rotation_euler) == (0.0, 0.0, 0.0), "property rotated"
    assert tuple(prop.scale) == (1.0, 1.0, 1.0), "property scaled"
    assert make_layout.link_property(ml) is prop, "link_property must be idempotent"
print("make_layout: OK")
```

- [ ] **Step 3: Run to verify it fails, then passes**

Run: `"${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}" --background --factory-startup --python-exit-code 1 --python tools/tests/check_blender.py`
Expected first: FAIL on `make_layout` attribute errors. After implementing: `make_layout: OK` then `ALL CHECKS OK`.

- [ ] **Step 4: Run the full suite**

Run: `python3 -m unittest discover -s tools/tests -t tools/tests`
Expected: PASS except `test_build_shots.py` (deleted in Task 9) and any test importing `boardlib`. If `test_build_shots` fails on the missing `boards.blend` path, leave it — Task 9 deletes it.

- [ ] **Step 5: Commit**

```bash
git add tools/make_layout.py tools/tests/check_blender.py
git commit -m "feat: make_layout builds camera-driven scenes with a static property"
```

---

### Task 5: `conform_edit.py` reads the layout file

Done before migration so the edit can be regenerated the moment the blend moves.

**Files:**
- Modify: `tools/conform_edit.py:1-30` (docstring, import), `:71-84` (scene loading), `:100-108` (tier), `:85`, `:129-131` (counts)

**Interfaces:**
- Consumes: `layoutlib.shot_ready`.
- Produces: no new API.

- [ ] **Step 1: Implement**

In `tools/conform_edit.py`:

Change `import boardlib` → `import layoutlib`. Update the docstring's tier list to say `layout scene named <code> in layout/layout.blend`.

Replace lines 71-84 with:

```python
    # link all available layout scenes (named by shot code) in one pass
    layout_scenes = {}
    layout_blend = root / "layout" / "layout.blend"
    if layout_blend.exists():
        codes = {s.code for s in shots}
        with bpy.data.libraries.load(str(layout_blend), link=True) as (src, dst):
            dst.scenes = [name for name in src.scenes if name in codes]
        # a shot earns its strip once it is drawn OR blocked out. Blocking and
        # paper both render, so the strip shows blocking, a drawing, or a
        # drawing over blocking — whatever the scene actually holds.
        layout_scenes = {sc.name: sc for sc in bpy.data.scenes
                         if sc.library is not None and layoutlib.shot_ready(sc)}
        stale = sorted(name for name, sc in layout_scenes.items()
                       if sc.get("exported"))
        if stale:
            print(f"note: {len(stale)} layout scene(s) already exported to "
                  f"shot files — their blocking may be stale: {', '.join(stale)}")
```

Rename the counter key `"board"` → `"layout"` at line 85 and in the print at line 130, and replace the `elif` branch (lines 100-108) with:

```python
        elif shot.code in layout_scenes:
            strip = strips.new_scene(name=f"{shot.code}_layout",
                                     scene=layout_scenes[shot.code],
                                     channel=2, frame_start=shot.start_frame)
            strip.frame_final_duration = shot.duration
            # render the layout scene's camera view; its own sequencer (the
            # scrub-audio strip) must not feed the edit
            strip.scene_input = "CAMERA"
            counts["layout"] += 1
```

- [ ] **Step 2: Verify it does not crash on the not-yet-moved file**

Run: `"${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}" --background --factory-startup --python-exit-code 1 --python tools/conform_edit.py -- --force`
Expected: exit 0, reporting `0 render / 0 layout / 39 slug strip(s)` — `layout/layout.blend` does not exist yet, so every shot correctly falls back to a slug. This proves the fallback path works before migration depends on it.

- [ ] **Step 3: Restore the edit**

The step above overwrote `edit/edit.blend` with an all-slug cut. That is expected and temporary — Task 6 regenerates it properly. Do not commit the blend yet.

```bash
git checkout -- edit/edit.blend
```

- [ ] **Step 4: Commit**

```bash
git add tools/conform_edit.py
git commit -m "refactor: conform_edit cuts layout scenes, reports stale exports"
```

---

### Task 6: `migrate_layout.py` — the reset

Existing blocking and animation are discarded by decision. Only `sq010_sh010`'s 119 strokes and a static solve for its camera survive.

**Files:**
- Create: `tools/migrate_layout.py`
- Move: `boards/boards.blend` → `layout/layout.blend`

**Interfaces:**
- Consumes: `layoutlib`, `make_layout`, `guides`, `shotlib`.
- Produces: a one-shot script, not imported by anything.

**Deviation from the spec:** the spec proposed reseeding every migrated camera
from `cam_intro`. That would put all 39 shots at the same angle, which is no
more informative than a plain default and costs a library read per scene. The
migration uses a neutral `(0, -10, 1.6)` placeholder instead, and seed cameras
earn their keep in Task 7 where a *specific* seed matches a *specific* shot
(`sq010_sh045` ← `cam_sidecorridor`). Same intent, applied where it pays.

- [ ] **Step 1: Write the migration**

Create `tools/migrate_layout.py`:

```python
#!/usr/bin/env python3
"""One-shot reset of boards.blend into the camera-driven layout model.

The old model changed framing by moving and ROTATING the property instance
with the camera pinned at (0,-10,0) — and had begun animating the set itself
to fake camera moves (sq010_sh010, sq010_sh045 both carry Actions on their
property instance). None of that survives the new invariants, and by decision
it is discarded rather than converted: the blocking took minutes to place.

What this does per scene:
  - deletes every collection instance (all blocking)
  - clears every object Action (all animation)
  - renames <code>_guides -> <code>_blocking
  - links the property at identity
  - parents the GP paper and the note to the camera, fits the paper
  - resets the camera

Two things survive because they are free:
  - Grease Pencil data is never touched, so sq010_sh010's 119 strokes remain.
  - That one scene's camera is solved statically as M^-1 * C, so the only
    drawn shot in the film keeps 3D standing behind it at the drawn angle.

Run ONCE, with Blender closed, AFTER `git mv boards/boards.blend
layout/layout.blend`:
  "$BLENDER" --background --python-exit-code 1 \
      --python tools/migrate_layout.py [-- --dry-run]
"""
import sys
from pathlib import Path

import bpy
from mathutils import Matrix

sys.path.insert(0, str(Path(__file__).resolve().parent))
import guides
import layoutlib
import make_layout
import shotlib

DRAWN_SCENE = "sq010_sh010"


def solve_camera(scene):
    """Camera transform that reproduces the old framing with a static set.

    Old: property at M, camera at C, both possibly animated.
    New: property at identity, camera at C' — and the picture is preserved
    when C'^-1 = C^-1 * M, i.e. C' = M^-1 * C.

    Evaluated at frame_start only: this is a static solve, deliberately. The
    animation is being discarded.
    """
    scene.frame_set(scene.frame_start)
    deps = bpy.context.evaluated_depsgraph_get()
    cam = scene.camera
    prop = next((o for o in scene.objects
                 if o.instance_collection is not None
                 and o.instance_collection.name == "property"), None)
    if cam is None or prop is None:
        return None
    # matrix_world is identity in --background until something forces a
    # depsgraph evaluation; evaluated_get is that something.
    m = prop.evaluated_get(deps).matrix_world.copy()
    c = cam.evaluated_get(deps).matrix_world.copy()
    return m.inverted() @ c


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    dry_run = "--dry-run" in argv

    root = shotlib.project_root()
    out = root / "layout" / "layout.blend"
    if not out.exists():
        sys.exit(f"error: {out.relative_to(root)} not found — run "
                 "`git mv boards/boards.blend layout/layout.blend` first")
    bpy.ops.wm.open_mainfile(filepath=str(out))

    solved = {}
    if DRAWN_SCENE in bpy.data.scenes:
        m = solve_camera(bpy.data.scenes[DRAWN_SCENE])
        if m is not None:
            solved[DRAWN_SCENE] = m
            print(f"solved {DRAWN_SCENE} camera from its old framing")

    stats = {"scenes": 0, "instances": 0, "actions": 0, "renamed": 0}
    for scene in bpy.data.scenes:
        stats["scenes"] += 1
        cam = scene.camera

        for ob in list(scene.objects):
            # Count actions BEFORE the instance branch. Most animation in this
            # file lives on blocking instances, so checking after a `continue`
            # would tally 3 of 10 and under-report what this script destroyed.
            if ob.animation_data is not None:
                stats["actions"] += 1
                if not dry_run:
                    ob.animation_data_clear()
            if ob.instance_collection is not None:
                stats["instances"] += 1
                if not dry_run:
                    bpy.data.objects.remove(ob, do_unlink=True)

        old = scene.collection.children.get(f"{scene.name}_guides")
        if old is not None:
            stats["renamed"] += 1
            if not dry_run:
                old.name = guides.blocking_collection_name(scene.name)

        if dry_run:
            continue

        scene.world = make_layout.layout_world()
        layoutlib.apply_project_settings(scene, view_transform="Standard")
        make_layout.ensure_blocking_collection(scene)
        make_layout.link_property(scene)
        layoutlib.apply_hide_blocking(scene)

        if cam is not None:
            if scene.name in solved:
                cam.matrix_world = solved[scene.name]
            else:
                cam.matrix_basis = Matrix.Identity(4)
                cam.location = (0.0, -10.0, 1.6)
                cam.rotation_euler = (1.5707963, 0.0, 0.0)
            for ob in scene.objects:
                if ob.type in layoutlib.GP_TYPES:
                    layoutlib.fit_paper(ob, cam)
                elif ob.type == "FONT" and ob.name.endswith("_note"):
                    ob.parent = cam
                    ob.matrix_parent_inverse = Matrix.Identity(4)
                    ob.location = (-1.6, 0.9, -4.0)
                    ob.rotation_euler = (0.0, 0.0, 0.0)

    if dry_run:
        print(f"--dry-run: {stats}")
        return
    bpy.ops.wm.save_mainfile()
    print(f"migrated: {stats}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Move the file and dry-run**

```bash
mkdir -p layout
git mv boards/boards.blend layout/layout.blend
git rm --cached boards/boards.blend1 2>/dev/null || true
rm -f boards/boards.blend1
"${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}" --background --python-exit-code 1 \
    --python tools/migrate_layout.py -- --dry-run
```

Expected: `--dry-run: {'scenes': 39, 'instances': 11, 'actions': 10, 'renamed': 39}`
(11 instances and 10 actions, distributed 1/2/2/3/3 and 1/2/2/2/3 across
`sq010_sh010`, `sh020`, `sh030`, `sh040`, `sh045` — from the pre-spec audit.)

- [ ] **Step 3: Migrate for real, then verify**

```bash
"${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}" --background --python-exit-code 1 \
    --python tools/migrate_layout.py
```

Then verify the invariants with a throwaway script:

```bash
cat > /tmp/verify_migration.py <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "tools"))
import bpy, layoutlib
bad = []
strokes = 0
for sc in bpy.data.scenes:
    for ob in sc.objects:
        if ob.instance_collection and ob.instance_collection.name != "property":
            bad.append(f"{sc.name}: leftover blocking {ob.name}")
        if ob.instance_collection and ob.instance_collection.name == "property":
            if tuple(ob.location) != (0.0, 0.0, 0.0) or tuple(ob.scale) != (1.0, 1.0, 1.0):
                bad.append(f"{sc.name}: property not at identity")
        if ob.animation_data and ob.animation_data.action:
            bad.append(f"{sc.name}: leftover action on {ob.name}")
        if ob.type in layoutlib.GP_TYPES:
            if ob.parent is not sc.camera:
                bad.append(f"{sc.name}: paper not parented to camera")
            if sc.name == "sq010_sh010":
                strokes = sum(
                    len(getattr(f, "strokes", None) or f.drawing.strokes)
                    for l in ob.data.layers for f in l.frames)
assert strokes == 119, f"sq010_sh010 strokes: {strokes}, expected 119"
assert not bad, "\n".join(bad)
print(f"migration verified: 39 scenes, {strokes} strokes preserved")
PY
"${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}" --background layout/layout.blend \
    --python-exit-code 1 --python /tmp/verify_migration.py
```

Expected: `migration verified: 39 scenes, 119 strokes preserved`

- [ ] **Step 4: Regenerate the edit and watch it**

```bash
"${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}" --background --factory-startup \
    --python-exit-code 1 --python tools/conform_edit.py -- --force
```

Expected: `0 render / 1 layout / 38 slug strip(s)` — only `sq010_sh010` has strokes now that all blocking is gone, so it is the only non-slug. That is correct and expected; Task 7 re-stages the rest.

- [ ] **Step 5: Commit**

```bash
git add tools/migrate_layout.py layout/layout.blend edit/edit.blend
git add -u boards/
git commit -m "feat!: migrate boards.blend to the camera-driven layout model

Blocking and animation discarded by decision. sq010_sh010's 119 strokes
survive, and its camera is solved statically from the old framing so the
one drawn shot keeps matching 3D behind it."
```

---

### Task 7: `stage_shots.py` — world-space staging

**Files:**
- Create: `tools/stage_shots.py` (via `git mv tools/stage_boards.py tools/stage_shots.py`)

**Interfaces:**
- Consumes: `layoutlib.{blocking_collection, fit_paper, GP_TYPES}`, `guides.{CAST_FILE, PROPS_FILE, PROPERTY_FILE}`.
- Produces: `stage_shots.STAGING: dict[str, dict]`, `stage_shots.link_collection(root, rel_file, name, cache)`, `stage_shots.aim_camera(scene, loc, look_at, lens) -> bool`, `stage_shots.seed_camera(root, name) -> tuple[tuple, tuple, float]`.

- [ ] **Step 1: Move and rewrite**

```bash
git mv tools/stage_boards.py tools/stage_shots.py
```

In `tools/stage_shots.py`: change `import boardlib` → `import layoutlib`, `boardlib.guides_collection` → `layoutlib.blocking_collection`, the output path to `layout/layout.blend`, and delete the `boardlib.sync_guide_visibility(scene)` call (blocking renders by default now).

`STAGING` gains a camera per shot and its positions become world-space. The old paper-space numbers are meaningless under the new invariants — replace the table wholesale:

```python
# scene code -> {"camera": (loc, look_at, lens), "blocking": [(guide, file, loc, rot_z)]}
#
# ALL POSITIONS ARE WORLD SPACE ON THE PROPERTY. The set sits at the origin
# with ground at z=0 and never moves; the camera is what frames the shot.
# Compass, from treatment/site.md: +Y = backyard, -Y = road.
#
# These are a starting point for framing, not final composition. A guide
# already present in a scene is LEFT ALONE, so re-running never disturbs work.
STAGING = {
    "sq010_sh020": {
        "camera": ((-6.0, -14.0, 2.2), (0.0, -2.0, 1.0), 40),
        "blocking": [
            ("delivery_truck", guides.PROPS_FILE, (-14.0, -8.0, 0.0), 90),
            ("box", guides.PROPS_FILE, (0.5, -3.0, 0.0), 0),
        ],
    },
    "sq010_sh030": {
        "camera": ((2.5, -8.0, 1.5), (0.0, -1.0, 1.2), 50),
        "blocking": [
            ("boy", guides.CAST_FILE, (0.0, -1.5, 0.0), 180),
            ("box", guides.PROPS_FILE, (0.5, -3.0, 0.0), 0),
        ],
    },
    "sq010_sh040": {
        "camera": ((4.0, -9.0, 1.4), (7.0, -1.0, 1.0), 35),
        "blocking": [
            ("boy", guides.CAST_FILE, (6.5, -5.0, 0.0), 0),
            ("box", guides.PROPS_FILE, (6.5, -6.2, 0.0), 0),
        ],
    },
    # The reverse: shooting down the side corridor through the garage
    # passthrough (the boolean cut) out to the driveway. Seeded from the
    # property file's own cam_sidecorridor, which already looks down that axis.
    "sq010_sh045": {
        "camera": "cam_sidecorridor",
        "blocking": [
            ("boy", guides.CAST_FILE, (7.5, 0.0, 0.0), 180),
            ("box", guides.PROPS_FILE, (7.5, -1.2, 0.0), 0),
        ],
    },
}
```

A `"camera"` value may be either an explicit `(loc, look_at, lens)` tuple or the **name of a seed camera** in `property.blend`. The property file already carries six framed cameras — `cam_site`, `cam_intro`, `cam_backyard`, `cam_kitchen`, `cam_road`, `cam_sidecorridor` — and under a camera-driven model those stop being previews and become the starting vocabulary for shots. Reading one is a plain append, not a link, because we want its transform copied and then owned by the scene:

```python
def seed_camera(root, name):
    """(location, rotation_euler, lens) of a named camera in property.blend.

    Appended, not linked: we want the transform copied into the layout scene
    and owned there, so framing it afterwards is a normal edit. The temporary
    object is removed once its numbers are read.
    """
    filepath = str(root / guides.PROPERTY_FILE)
    with bpy.data.libraries.load(filepath, link=False) as (src, dst):
        if name not in src.objects:
            sys.exit(f"error: no camera {name!r} in {guides.PROPERTY_FILE}")
        dst.objects = [name]
    ob = dst.objects[0]
    result = (tuple(ob.location), tuple(ob.rotation_euler),
              ob.data.lens if ob.type == "CAMERA" else 50.0)
    bpy.data.objects.remove(ob, do_unlink=True)
    return result
```

Add camera aiming — hand-rolled Euler math gets the yaw sign wrong, so use `to_track_quat`:

```python
def aim_camera(scene, loc, look_at, lens):
    """Place and aim the shot camera. Returns True if it moved anything."""
    cam = scene.camera
    if cam is None:
        return False
    direction = Vector(look_at) - Vector(loc)
    cam.location = loc
    # -Z forward, Y up: hand-rolled Euler math gets the yaw sign wrong
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lens
    return True
```

Import `from mathutils import Vector` and `import layoutlib`.

In `main()`, iterate the new table shape. Camera staging is additive in the same spirit — only place a camera the migration reset, never one that was framed by hand:

```python
    for scene_name, entry in STAGING.items():
        scene = bpy.data.scenes.get(scene_name)
        if scene is None:
            sys.exit(f"error: no scene {scene_name!r} in layout.blend; "
                     "run tools/make_layout.py first")
        coll = layoutlib.blocking_collection(scene, create=True)

        # Only frame a camera that is still at the migration default. A camera
        # moved by hand is finished work and must not be reset.
        cam = scene.camera
        if cam is not None and not dry_run:
            default = (abs(cam.location.x) < 1e-6
                       and abs(cam.location.y + 10.0) < 1e-6
                       and abs(cam.location.z - 1.6) < 1e-6)
            if default:
                spec_cam = entry["camera"]
                if isinstance(spec_cam, str):
                    loc, rot, lens = seed_camera(root, spec_cam)
                    cam.location = loc
                    cam.rotation_euler = rot
                    cam.data.lens = lens
                    print(f"  {scene_name}: camera seeded from {spec_cam}")
                else:
                    loc, look_at, lens = spec_cam
                    aim_camera(scene, loc, look_at, lens)
                    print(f"  {scene_name}: camera framed at {loc} -> {look_at}")
                # the paper's fit depends on the lens, so refit after aiming
                for ob in scene.objects:
                    if ob.type in layoutlib.GP_TYPES:
                        layoutlib.fit_paper(ob, cam)
            else:
                print(f"  {scene_name}: camera framed by hand, left alone")

        for guide_name, rel_file, loc, rot_z in entry["blocking"]:
            linked = link_collection(root, rel_file, guide_name, cache)
            # identity match, not name match: instance OBJECTS are auto-suffixed
            # (boy.001, box.002), so comparing object names misses them and
            # would silently stack duplicates on every run.
            if any(o.instance_collection is linked for o in coll.objects):
                print(f"  {scene_name}: {guide_name} already staged, left alone")
                skipped += 1
                continue
            print(f"  {scene_name}: staging {guide_name} at {loc} rotZ={rot_z}")
            created += 1
            if dry_run:
                continue
            inst = bpy.data.objects.new(guide_name, None)
            inst.instance_type = "COLLECTION"
            inst.instance_collection = linked
            inst.location = loc
            inst.rotation_euler = (0.0, 0.0, math.radians(rot_z))
            coll.objects.link(inst)
```

- [ ] **Step 2: Dry-run, then stage**

```bash
"${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}" --background --factory-startup \
    --python-exit-code 1 --python tools/stage_shots.py -- --dry-run
```
Expected: `would create 8, skip 0`

```bash
"${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}" --background --factory-startup \
    --python-exit-code 1 --python tools/stage_shots.py
```
Expected: `stage_shots: created 8, skipped 0`

- [ ] **Step 3: Verify idempotence**

Run the same command again.
Expected: `stage_shots: created 0, skipped 8`, and every scene reports `camera framed by hand, left alone`.

- [ ] **Step 4: Regenerate the edit and confirm the beats read**

```bash
"${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}" --background --factory-startup \
    --python-exit-code 1 --python tools/conform_edit.py -- --force
```
Expected: `0 render / 5 layout / 34 slug strip(s)`

- [ ] **Step 5: Commit**

```bash
git add tools/stage_shots.py layout/layout.blend edit/edit.blend
git commit -m "feat: stage_shots frames cameras and blocks in world space"
```

---

### Task 8: `continue_shot.py` — snapshot copy-forward

Because the property is at identity in every scene, both scenes share a world origin — so this is a direct world-matrix copy with no transform math at all.

**Files:**
- Create: `tools/continue_shot.py`
- Modify: `tools/tests/check_blender.py`

**Interfaces:**
- Consumes: `layoutlib.{blocking_collection, blocking_instances, fit_paper}`.
- Produces: `continue_shot.snapshot(scene, frame) -> dict[str, tuple]` mapping instance-collection name → (4×4 world matrix as a tuple of tuples, camera lens or None); `continue_shot.apply_snapshot(scene, snap, force=False) -> tuple[int, int]` returning (created, skipped).

- [ ] **Step 1: Write the failing check**

Append to `tools/tests/check_blender.py`:

```python
# --- continue_shot copies state forward ----------------------------------
import continue_shot  # noqa: E402

src = bpy.data.scenes.new("sq997_sh010")
src.world = bpy.data.worlds.new("cs_world")
src_cam = bpy.data.objects.new("sq997_sh010_cam", bpy.data.cameras.new("sq997_sh010_cam"))
src_cam.location = (3.0, -4.0, 1.5)
src_cam.data.lens = 42.0
src.collection.objects.link(src_cam)
src.camera = src_cam
src_bc = layoutlib.blocking_collection(src, create=True)
target = bpy.data.collections.new("cs_probe_boy")
probe = bpy.data.objects.new("boy", None)
probe.instance_type = "COLLECTION"
probe.instance_collection = target
probe.location = (1.25, 2.5, 0.0)
src_bc.objects.link(probe)

dst = bpy.data.scenes.new("sq997_sh020")
dst.world = bpy.data.worlds.new("cs_world2")
dst_cam = bpy.data.objects.new("sq997_sh020_cam", bpy.data.cameras.new("sq997_sh020_cam"))
dst.collection.objects.link(dst_cam)
dst.camera = dst_cam
layoutlib.blocking_collection(dst, create=True)

snap = continue_shot.snapshot(src, src.frame_start)
assert "boy" in snap, f"snapshot missing blocking: {list(snap)}"
created, skipped = continue_shot.apply_snapshot(dst, snap)
assert created == 1, f"expected 1 created, got {created}"

moved = next(o for o in layoutlib.blocking_instances(dst)
             if o.instance_collection is target)
assert (moved.matrix_world.translation - probe.matrix_world.translation).length < 1e-6, \
    "blocking must land at the SAME world position — both scenes share an origin"
assert abs(dst_cam.location.x - 3.0) < 1e-6, "camera location must copy"
assert abs(dst_cam.data.lens - 42.0) < 1e-6, "camera lens must copy"

# re-running must not stack duplicates
created2, skipped2 = continue_shot.apply_snapshot(dst, snap)
assert created2 == 0 and skipped2 == 1, f"not idempotent: {created2}, {skipped2}"
print("continue_shot: OK")
```

- [ ] **Step 2: Run to verify it fails**

Run: `"${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}" --background --factory-startup --python-exit-code 1 --python tools/tests/check_blender.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'continue_shot'`

- [ ] **Step 3: Implement**

Create `tools/continue_shot.py`:

```python
#!/usr/bin/env python3
"""Continue one shot from another: snapshot copy-forward of camera + blocking.

Because the property is linked at identity in EVERY layout scene, both scenes
share a world origin — so continuing a shot is a direct world-matrix copy. No
transform math, no relative-space conversion. That is the invariant paying for
itself.

Snapshot semantics, not a live link: the destination is independent from the
moment it is written, so re-blocking the source later never disturbs it.

Run (Blender closed — this writes layout/layout.blend):
  "$BLENDER" --background --python-exit-code 1 \
      --python tools/continue_shot.py -- --from sq010_sh040 --to sq010_sh045 \
      [--at-frame 490] [--force] [--dry-run]
"""
import argparse
import sys
from pathlib import Path

import bpy
from mathutils import Matrix

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layoutlib
import shotlib


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--from", dest="src", required=True, help="source shot code")
    p.add_argument("--to", dest="dst", required=True, help="destination shot code")
    p.add_argument("--at-frame", type=int, default=None,
                   help="frame to read the source at (default: its last frame)")
    p.add_argument("--force", action="store_true",
                   help="also overwrite blocking already present in the destination")
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args(argv)


def snapshot(scene, frame):
    """World matrices of the camera and every blocking instance at `frame`.

    Keyed by instance-collection name, which is stable: instance OBJECTS get
    auto-suffixed (boy.001, box.002) but the collection they instance does not.
    """
    scene.frame_set(frame)
    # matrix_world is identity in --background until a depsgraph evaluation,
    # and camera.matrix_world silently returns garbage rather than erroring.
    deps = bpy.context.evaluated_depsgraph_get()
    snap = {}
    for ob in layoutlib.blocking_instances(scene):
        m = ob.evaluated_get(deps).matrix_world.copy()
        snap[ob.instance_collection.name] = (tuple(tuple(r) for r in m), None)
    cam = scene.camera
    if cam is not None:
        m = cam.evaluated_get(deps).matrix_world.copy()
        snap["__camera__"] = (tuple(tuple(r) for r in m), cam.data.lens)
    return snap


def apply_snapshot(scene, snap, force=False):
    """Write a snapshot into `scene`. Returns (created, skipped)."""
    coll = layoutlib.blocking_collection(scene, create=True)
    present = {o.instance_collection.name: o
               for o in layoutlib.blocking_instances(scene)}
    created = skipped = 0

    for name, (rows, _lens) in snap.items():
        if name == "__camera__":
            continue
        m = Matrix(rows)
        existing = present.get(name)
        if existing is not None and not force:
            skipped += 1
            continue
        if existing is not None:
            existing.matrix_world = m
            continue
        linked = next((c for c in bpy.data.collections if c.name == name), None)
        if linked is None:
            print(f"warning: collection {name!r} not linked in this file, skipped")
            continue
        inst = bpy.data.objects.new(name, None)
        inst.instance_type = "COLLECTION"
        inst.instance_collection = linked
        coll.objects.link(inst)
        inst.matrix_world = m
        created += 1

    cam_entry = snap.get("__camera__")
    if cam_entry is not None and scene.camera is not None:
        rows, lens = cam_entry
        scene.camera.matrix_world = Matrix(rows)
        if lens is not None:
            scene.camera.data.lens = lens
        # the paper's fit depends on the lens
        for ob in scene.objects:
            if ob.type in layoutlib.GP_TYPES:
                layoutlib.fit_paper(ob, scene.camera)
    return created, skipped


def main():
    args = parse_args()
    root = shotlib.project_root()
    out = root / "layout" / "layout.blend"
    if not out.exists():
        sys.exit(f"error: {out.relative_to(root)} does not exist; "
                 "run tools/make_layout.py first")
    bpy.ops.wm.open_mainfile(filepath=str(out))

    src = bpy.data.scenes.get(args.src)
    dst = bpy.data.scenes.get(args.dst)
    if src is None:
        sys.exit(f"error: no scene {args.src!r} in layout.blend")
    if dst is None:
        sys.exit(f"error: no scene {args.dst!r} in layout.blend")

    frame = args.at_frame if args.at_frame is not None else src.frame_end
    if not (src.frame_start <= frame <= src.frame_end):
        sys.exit(f"error: frame {frame} outside {args.src} "
                 f"[{src.frame_start}-{src.frame_end}]")

    snap = snapshot(src, frame)
    names = sorted(k for k in snap if k != "__camera__")
    print(f"{args.src} @ {frame}: camera + {len(names)} blocking "
          f"({', '.join(names) or 'none'})")

    if args.dry_run:
        print(f"--dry-run: would continue {args.dst} from this state")
        return

    created, skipped = apply_snapshot(dst, snap, force=args.force)
    bpy.ops.wm.save_mainfile()
    print(f"continue_shot: {args.dst} created {created}, skipped {skipped}"
          f"{' (use --force to overwrite)' if skipped else ''}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run to verify it passes**

Run: `"${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}" --background --factory-startup --python-exit-code 1 --python tools/tests/check_blender.py`
Expected: `continue_shot: OK` then `ALL CHECKS OK`

Then a real run against the migrated file:
```bash
"${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}" --background --python-exit-code 1 \
    --python tools/continue_shot.py -- --from sq010_sh040 --to sq010_sh050 --dry-run
```
Expected: `sq010_sh040 @ 490: camera + 2 blocking (box, boy)`

- [ ] **Step 5: Commit**

```bash
git add tools/continue_shot.py tools/tests/check_blender.py
git commit -m "feat: continue_shot copies camera and blocking forward"
```

---

### Task 9: `export_shot.py`, and deleting the mandatory shot stage

**Files:**
- Create: `tools/export_shot.py` (via `git mv tools/new_shot.py tools/export_shot.py`)
- Delete: `tools/build_shots.py`, `tools/tests/test_build_shots.py`, `tools/stage_property.py`

**Interfaces:**
- Consumes: `layoutlib.apply_project_settings`, `shotlib.shot_blend`.
- Produces: `export_shot.export(code, force=False) -> Path`.

- [ ] **Step 1: Delete what the design retires**

```bash
git rm tools/build_shots.py tools/tests/test_build_shots.py tools/stage_property.py
```

`stage_property.py` also owns a `blocking` collection of 15 objects inside `property.blend`. Remove it, since layout scenes now hold blocking natively:

```bash
cat > /tmp/drop_blocking.py <<'PY'
import bpy
coll = bpy.data.collections.get("blocking")
assert coll is not None, "no blocking collection — already removed?"
n = len(coll.objects)
for ob in list(coll.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
bpy.data.collections.remove(coll)
bpy.ops.wm.save_mainfile()
print(f"removed blocking collection ({n} objects) from property.blend")
PY
"${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}" --background \
    assets/envs/property/property.blend --python-exit-code 1 --python /tmp/drop_blocking.py
```
Expected: `removed blocking collection (15 objects) from property.blend`

- [ ] **Step 2: Write export_shot**

```bash
git mv tools/new_shot.py tools/export_shot.py
```

Replace the contents of `tools/export_shot.py` with:

```python
#!/usr/bin/env python3
"""Export one layout scene into its own shot .blend, on demand.

Shot files are a DERIVED EXPORT, not a stage. Most shots never need one: a
layout scene already carries the camera, the blocking, the property, and the
frame range. Export a shot when it earns its own file — a per-shot compositor,
a sim, a 4K re-render, lighting that must not touch its neighbours.

One-way. After export the shot file is authoritative and the layout scene is a
stale reference; this stamps `exported = True` on it so conform_edit says so
instead of silently cutting old blocking.

Run (Blender closed):
  "$BLENDER" --background --python-exit-code 1 \
      --python tools/export_shot.py -- --shot sq010_sh040 [--force]
"""
import argparse
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layoutlib
import shotlib


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--shot", required=True, help="shot code, e.g. sq010_sh040")
    p.add_argument("--force", action="store_true",
                   help="overwrite an existing shot file")
    return p.parse_args(argv)


def export(code, force=False):
    root = shotlib.project_root()
    layout = root / "layout" / "layout.blend"
    if not layout.exists():
        sys.exit(f"error: {layout.relative_to(root)} does not exist")

    shots = {s.code: s for s in shotlib.read_shotlist(root / "docs" / "shotlist.csv")}
    if code not in shots:
        sys.exit(f"error: {code} not found in docs/shotlist.csv")
    shot = shots[code]

    blend = shotlib.shot_blend(shot.sq, shot.sh, root)
    if blend.exists() and not force:
        sys.exit(f"error: {blend.relative_to(root)} exists (use --force)")

    bpy.ops.wm.open_mainfile(filepath=str(layout))
    scene = bpy.data.scenes.get(code)
    if scene is None:
        sys.exit(f"error: no layout scene {code!r}")

    # mark the source BEFORE stripping, so layout.blend keeps the record
    scene["exported"] = True
    bpy.ops.wm.save_mainfile()

    for other in list(bpy.data.scenes):
        if other is not scene:
            bpy.data.scenes.remove(other)

    # renders carry AgX; the layout scene deliberately used Standard
    layoutlib.apply_project_settings(scene, view_transform="AgX")
    # The scene carries a track strip for scrubbing. conform_edit never sees
    # it because it sets scene_input="CAMERA", but render_shot.sh renders the
    # scene directly — and a scene whose sequencer holds only a sound strip
    # renders the SEQUENCER, not the camera, i.e. black frames. Turn it off.
    scene.render.use_sequencer = False
    scene.frame_start = shot.start_frame
    scene.frame_end = shot.end_frame

    blend.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(blend), relative_remap=True)
    print(f"exported {blend.relative_to(root)} "
          f"[{shot.start_frame}-{shot.end_frame}], "
          f"{len(layoutlib.blocking_instances(scene))} blocking instance(s)")
    return blend


def main():
    args = parse_args()
    export(args.shot, force=args.force)


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Export a shot and verify it round-trips**

```bash
"${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}" --background --python-exit-code 1 \
    --python tools/export_shot.py -- --shot sq010_sh040
```
Expected: `exported shots/sq010/sh040/sh040.blend [410-490], 2 blocking instance(s)`

```bash
cat > /tmp/verify_export.py <<'PY'
import bpy
sc = bpy.data.scenes["sq010_sh040"]
assert len(bpy.data.scenes) == 1, f"{len(bpy.data.scenes)} scenes, expected 1"
assert sc.camera is not None, "no camera"
assert (sc.frame_start, sc.frame_end) == (410, 490), (sc.frame_start, sc.frame_end)
assert sc.view_settings.view_transform == "AgX", sc.view_settings.view_transform
# a scene whose sequencer holds only the scrub-audio strip would render the
# sequencer instead of the camera — i.e. black frames
assert sc.render.use_sequencer is False, "sequencer must be off in a shot file"
print("export verified")
PY
"${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}" --background \
    shots/sq010/sh040/sh040.blend --python-exit-code 1 --python /tmp/verify_export.py
```
Expected: `export verified`

- [ ] **Step 4: Confirm conform reports the stale scene, then clean up**

```bash
"${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}" --background --factory-startup \
    --python-exit-code 1 --python tools/conform_edit.py -- --force
```
Expected: a line reading `note: 1 layout scene(s) already exported to shot files — their blocking may be stale: sq010_sh040`

The export was a smoke test, not real work. Remove it so `shots/` starts empty as designed, and clear the marker:

```bash
rm -rf shots/sq010
cat > /tmp/unmark.py <<'PY'
import bpy
sc = bpy.data.scenes["sq010_sh040"]
del sc["exported"]
bpy.ops.wm.save_mainfile()
print("cleared exported marker")
PY
"${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}" --background layout/layout.blend \
    --python-exit-code 1 --python /tmp/unmark.py
"${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}" --background --factory-startup \
    --python-exit-code 1 --python tools/conform_edit.py -- --force
```

- [ ] **Step 5: Commit**

```bash
git add tools/export_shot.py assets/envs/property/property.blend layout/layout.blend edit/edit.blend
git add -u tools/
git commit -m "feat!: shot files become an on-demand export

Deletes build_shots.py, stage_property.py and the property file's blocking
collection — all three existed only because boards could not hold real
blocking."
```

---

### Task 10: Add-on drops guides on the ground

**Files:**
- Modify: `tools/addons/redwood_guides.py`
- Modify: `tools/tests/check_addon.py`

**Interfaces:**
- Consumes: `guides.{blocking_collection_name, DROP_DISTANCE, guide_by_name}`, `make_layout.ensure_blocking_collection`.
- Produces: `redwood_guides.ground_drop_location(scene) -> tuple[float, float, float]`, `redwood_guides.add_guide_instance(scene, name)` (unchanged signature).

- [ ] **Step 1: Write the failing check**

Add to `tools/tests/check_addon.py` (match its existing style — read it first; it drives the add-on headlessly):

```python
# A guide drops onto the ground plane in front of the camera, feet at z=0 —
# a real place on the property, not a spot in a picture.
sc = bpy.data.scenes.new("sq996_sh010")
cam = bpy.data.objects.new("sq996_sh010_cam", bpy.data.cameras.new("sq996_sh010_cam"))
cam.location = (0.0, -10.0, 2.0)
cam.rotation_euler = (math.radians(80), 0.0, 0.0)  # tilted down toward the ground
sc.collection.objects.link(cam)
sc.camera = cam

loc = redwood_guides.ground_drop_location(sc)
assert abs(loc[2]) < 1e-6, f"guides drop with feet on the ground, got z={loc[2]}"
assert loc[1] > cam.location.y, "drop must be IN FRONT of the camera"

# camera level with the horizon: the ray never meets z=0, so fall back
cam.rotation_euler = (math.radians(90), 0.0, 0.0)
loc = redwood_guides.ground_drop_location(sc)
assert abs(loc[2]) < 1e-6, "fallback still puts feet on the ground"
assert abs(loc[1] - (cam.location.y + guides.DROP_DISTANCE)) < 1e-4, \
    f"fallback should be DROP_DISTANCE along the view ray, got {loc}"
print("ground drop: OK")
```

- [ ] **Step 2: Run to verify it fails**

Run: `"${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}" --background --factory-startup --python-exit-code 1 --python tools/tests/check_addon.py`
Expected: FAIL — `AttributeError: module 'redwood_guides' has no attribute 'ground_drop_location'`

- [ ] **Step 3: Implement**

In `tools/addons/redwood_guides.py`, update the docstring, change `import make_boards` → `import make_layout` (and the tuple it returns), then replace `add_guide_instance`'s collection resolution and drop location:

```python
def ground_drop_location(scene):
    """Where the camera is looking, on the ground.

    Guides are authored feet-at-z=0, and the property's ground IS z=0, so
    intersecting the camera's view ray with that plane drops a character
    exactly where they would stand. If the camera is level or tilted up the
    ray never meets the ground — fall back to DROP_DISTANCE along the view
    ray, flattened to z=0.
    """
    root, mods = _load_guides()
    guides_mod = mods[0] if mods else None
    distance = guides_mod.DROP_DISTANCE if guides_mod else 8.0

    cam = scene.camera
    if cam is None:
        return (0.0, 0.0, 0.0)
    origin = cam.matrix_world.translation
    forward = (cam.matrix_world.to_quaternion()
               @ mathutils.Vector((0.0, 0.0, -1.0)))
    if forward.z < -1e-4:
        t = -origin.z / forward.z
        if 0.0 < t < 1000.0:
            hit = origin + forward * t
            return (hit.x, hit.y, 0.0)
    flat = mathutils.Vector((forward.x, forward.y, 0.0))
    if flat.length < 1e-6:
        return (origin.x, origin.y, 0.0)
    hit = origin + flat.normalized() * distance
    return (hit.x, hit.y, 0.0)
```

Add `import mathutils` at the top. In `add_guide_instance`, replace lines 61-65 and line 82:

```python
    make_layout.ensure_blocking_collection(scene)
    gname = guides_mod.blocking_collection_name(scene.name)
    gcoll = scene.collection.children.get(gname)
    if gcoll is None:
        raise RuntimeError(f"could not resolve blocking collection {gname}")
```

```python
    inst.location = ground_drop_location(scene)
```

Also update `_load_guides` to import `make_layout`, the panel's error text (`"Open layout.blend from the project"`), and `add_guide_instance`'s "Open boards.blend" message.

- [ ] **Step 4: Run to verify it passes**

Run: `"${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}" --background --factory-startup --python-exit-code 1 --python tools/tests/check_addon.py`
Expected: `ground drop: OK`

Run: `python3 -m unittest discover -s tools/tests -t tools/tests`
Expected: all PASS

- [ ] **Step 5: Commit**

```bash
git add tools/addons/redwood_guides.py tools/tests/check_addon.py
git commit -m "feat: Add Guide drops onto the ground where the camera looks"
```

---

### Task 11: The `assets` column becomes validated metadata

`sq010_sh040` and `sq010_sh045` carry `assets = boy;box`, which `new_shot.py` resolved to `assets/boy/boy.blend` and silently warned-and-skipped. Nothing links from this column any more — `export_shot.py` exports what the scene contains — so it becomes planning metadata that fails loudly on a typo.

**Files:**
- Modify: `tools/shotlib.py:62-112`
- Modify: `tools/tests/test_shotlist.py`

**Interfaces:**
- Consumes: `guides.DROPPABLE` (Task 1).
- Produces: `read_shotlist` raises `ValueError` on an unknown asset name.

- [ ] **Step 1: Write the failing test**

Add to `tools/tests/test_shotlist.py` (follow the existing tmp-CSV pattern in that file):

```python
    def test_unknown_asset_name_is_rejected(self):
        path = self._write(
            "sq,sh,description,start_frame,end_frame,duration,assets,status\n"
            "010,010,a shot,1,10,10,boy;nonesuch,scripted\n"
        )
        with self.assertRaises(ValueError) as ctx:
            shotlib.read_shotlist(path)
        self.assertIn("nonesuch", str(ctx.exception))

    def test_known_guide_names_are_accepted(self):
        path = self._write(
            "sq,sh,description,start_frame,end_frame,duration,assets,status\n"
            "010,040,drags the box,410,490,81,boy;box,scripted\n"
        )
        shots = shotlib.read_shotlist(path)
        self.assertEqual(shots[0].assets, ["boy", "box"])
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m unittest discover -s tools/tests -t tools/tests -k shotlist -v`
Expected: FAIL — `ValueError not raised`

- [ ] **Step 3: Implement**

In `tools/shotlib.py`, add the import at the top (both modules are bpy-free, so this is safe):

```python
import guides
```

Replace line 109 with:

```python
            assets = [a.strip() for a in row["assets"].split(";") if a.strip()]
            # Planning metadata, NOT a link instruction: blocking lives in the
            # layout scene and export_shot exports what the scene holds. It is
            # still validated, so a typo fails here instead of warning into
            # the void the way new_shot.py used to.
            known = {g.name for g in guides.DROPPABLE}
            for a in assets:
                if a not in known:
                    raise ValueError(
                        f"{path}:{lineno}: unknown asset {a!r}; "
                        f"expected one of {', '.join(sorted(known))}"
                    )
```

- [ ] **Step 4: Run to verify it passes**

Run: `python3 -m unittest discover -s tools/tests -t tools/tests`
Expected: all PASS, including the real `docs/shotlist.csv` parse (`boy;box` are both registry names).

- [ ] **Step 5: Commit**

```bash
git add tools/shotlib.py tools/tests/test_shotlist.py
git commit -m "feat: validate the shotlist assets column against the guide registry"
```

---

### Task 12: `resync_layout.py` and the docs

The docs are the deliverable here — every convention this plan changed is currently written down wrong in four places.

**Files:**
- Create: `tools/resync_layout.py` (via `git mv tools/resync_boards.py`)
- Create: `docs/layout.md` (via `git mv docs/boards.md`)
- Modify: `docs/pipeline.md`, `docs/tools.md`, `docs/handoff.md`, `README.md`

- [ ] **Step 1: Move the last two files**

```bash
git mv tools/resync_boards.py tools/resync_layout.py
git mv docs/boards.md docs/layout.md
```

In `tools/resync_layout.py`, change the path `boards/boards.blend` → `layout/layout.blend` and update the docstring's references to boards. Behaviour is unchanged — frame ranges only, idempotent.

- [ ] **Step 2: Rewrite `docs/layout.md`**

It currently describes the paper-at-origin model in full. Replace its "Scale guides" preamble and "Drawing with guides" sections so they state:

- The four invariants (property static at origin with ground at z=0; the camera is the only framing authority; blocking is world-space; shot files are a derived export).
- **Add Guide** drops onto the ground where the camera is looking, feet at z=0.
- Blocking and paper both render; `scene["hide_blocking"] = True` is the hand-set opt-out and no tool writes it.
- The X-ray caveat is **gone** — Grease Pencil composites over mesh geometry in EEVEE regardless of depth, so nothing occludes strokes.
- The "re-run `make_boards.py` after a drawing session" rule is **gone** — there is no automatic visibility rule left to re-sync.
- Continuing a shot: `continue_shot.py --from <code> --to <code>`.

- [ ] **Step 3: Update the other three docs**

`docs/pipeline.md`: rewrite the **Shots** section — shot files are a derived export via `export_shot.py`, not `build_shots.py`. Update the **Edit & delivery** section's board paragraph to describe layout scenes and the render → layout → slug tiers. Add the four invariants under a new **Layout** heading.

`docs/tools.md`: rename every tool entry, delete the `build_shots.py`, `new_shot.py` and `stage_property.py` entries, add `export_shot.py`, `continue_shot.py`, and `migrate_layout.py`. Update the mermaid flowchart: `shotlist → make_layout → layout.blend → {conform_edit, export_shot}` and `export_shot → shots/ → render_shot.sh`. Update the phase list — phase 4 is no longer "Shot creation: fifty shot files appear."

`docs/handoff.md`: this is the cold-start doc and is now wrong in its most load-bearing parts. Update the board-state table, replace the "The boards, and how guides reach the edit" section (the fixed-camera rule, the auto-hide rule, and the X-ray caveat are all obsolete), update the tool table and the "Which tools destroy work" table (`stage_property.py` is gone; `migrate_layout.py` is one-shot and already run), and add the four invariants to "Five conventions that will bite you."

`README.md`: update the phase checklist and any path references to `boards/`.

- [ ] **Step 4: Full verification**

```bash
python3 -m unittest discover -s tools/tests -t tools/tests
grep -rn "boardlib\|make_boards\|stage_boards\|resync_boards\|boards\.blend\|build_shots\|stage_property\|new_shot\|guides_collection_name\|sync_guide_visibility" \
    tools/ docs/ README.md --include="*.py" --include="*.md" --include="*.sh"
```
Expected: all tests PASS, and the grep returns only historical references inside `docs/superpowers/specs/` and `docs/superpowers/plans/` (which describe the old model on purpose). Any hit in `tools/`, `README.md`, `docs/pipeline.md`, `docs/tools.md`, `docs/handoff.md` or `docs/layout.md` is a miss — fix it.

- [ ] **Step 5: Commit and open the PR**

```bash
git add tools/resync_layout.py docs/layout.md docs/pipeline.md docs/tools.md docs/handoff.md README.md
git add -u
git commit -m "docs: rewrite the pipeline docs for the camera-driven model"
git push -u origin camera-driven-layout
gh pr create --title "Camera-driven layout pipeline" --body "$(cat <<'EOF'
Property static at world origin, camera as the sole framing authority,
blocking in world space, Grease Pencil as an optional camera-locked overlay.

`boards/boards.blend` becomes `layout/layout.blend`; shot `.blend` files stop
being a mandatory stage and become an on-demand export.

Existing blocking and animation were discarded rather than migrated, by
decision — the staged boards had begun animating the property instance itself
to fake camera moves, which the new invariants make unnecessary.
`sq010_sh010`'s 119 strokes survive, and its camera was solved statically from
the old framing.

Spec: `docs/superpowers/specs/2026-07-31-camera-driven-layout-design.md`
Plan: `docs/superpowers/plans/2026-07-31-camera-driven-layout.md`

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01QWjoTLDghmnsCjTkDiBrGc
EOF
)"
```

---

## Verification Checklist

After Task 12, all of these must hold:

- [ ] `python3 -m unittest discover -s tools/tests -t tools/tests` passes
- [ ] `check_blender.py` prints `ALL CHECKS OK`
- [ ] `check_addon.py` prints `ground drop: OK`
- [ ] Every property instance in `layout/layout.blend` is at identity
- [ ] `sq010_sh010` still has 119 strokes
- [ ] `edit/edit.blend` conforms to `0 render / 5 layout / 34 slug`
- [ ] `shots/` contains no `.blend` files
- [ ] `boards/` no longer exists; `git log --follow layout/layout.blend` shows the history
