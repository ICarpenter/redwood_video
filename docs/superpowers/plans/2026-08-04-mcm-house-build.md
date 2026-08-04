# MCM House Build Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the greybox house/garage in `assets/envs/property/property.blend` with the flat-roof MCM build specced in `docs/treatment/house.md`, without any layout scene ever seeing work in progress.

**Architecture:** A new script `tools/build_house.py` (mirroring `tools/blockout_property.py`'s idiom) builds the whole house into a **`house_v2` staging collection + `house_modeling` workspace scene inside `property.blend`**. Layout scenes link ONLY the `property` root collection (`docs/pipeline.md`), so staging is invisible to them until an explicit `--swap` moves the finished objects into `property` and parks the greybox in a `_greybox` collection (reversible with `--revert`, deleted only after the final re-render check). The three animatable leaves (screen door, casement sash, back-door leaf) are props, added to `props.blend` via the sanctioned `guides.py`/`guide_assets.py --add` flow.

**Tech Stack:** Blender 5.1.2 headless (`$BLENDER=/Applications/Blender.app/Contents/MacOS/Blender`), bpy + mathutils, pytest (system python) for `tools/tests/test_guides.py`, git-LFS blends.

## Global Constraints

- **Blender must be CLOSED before any step that writes a `.blend`.** Check: `pgrep -f "Blender.app/Contents/MacOS/Blender"` must print nothing. (CLAUDE.md non-negotiable.)
- Never `git add -A`; blends are git-LFS — commit by explicit path only. `assets/chars/cast.blend` and `layout/layout.blend` currently carry unrelated uncommitted animatic work: **never stage or commit them in this plan.**
- Never run `migrate_layout.py`; never pass `--force` to `make_layout.py`/`conform_edit.py`/`guide_assets.py` (this plan needs none of them beyond `guide_assets.py --add`, which is the non-destructive path).
- The `property` collection is linked at identity in every layout scene: nothing in this plan may move, rename, or instance that collection itself, and preview/modeling cameras stay **outside** it.
- All spec dimensions come from `docs/treatment/house.md` and are **frozen**: house `x −7…5, y −4…5`, garage `x −13…−7, y −3…3`, wall thickness 0.25, every opening's plan position/sill/head as tabled below. New openings: the clerestory only.
- Verify by rendering and looking, never by trusting the numbers (CLAUDE.md).
- Renders go to `<scratchpad>/house_renders/` (your session scratchpad), never into the repo.
- Commit cadence: the **script** commits on every task; **`property.blend`** commits only at three milestones (staging complete after Task 8, swap after Task 10, cleanup after Task 13); **`props.blend`** commits in Task 11.

## File structure

- Create: `tools/build_house.py` — one file, all build/check/swap logic (the repo's pattern: one tool per job, `blockout_property.py` is the template).
- Modify: `tools/guides.py` — 3 new `GuideSpec` rows + `SCENERY` additions.
- Modify: `tools/guide_assets.py` — 3 new leaf builders.
- Modify: `tools/tests/test_guides.py:10-13` — guide counts 34→37, props 25→28.
- Modify: `docs/treatment/site.md` — flat-roof + stale-porch-note fixes.
- Data (via tools, explicit-path commits): `assets/envs/property/property.blend`, `assets/props/props.blend`.

---

### Task 1: `tools/build_house.py` scaffold — staging collection, modeling scene, materials, check/save plumbing

**Files:**
- Create: `tools/build_house.py`

**Interfaces:**
- Produces (used by every later task): constants `HOUSE`, `WALL_T=0.25`, `MATS`; helpers `mat(name)`, `box(name,x0,x1,y0,y1,z0,z1,mat_name)`, `multi_box(name,specs,mat_name)`, `_wall(face)`, `wall_spec(face,a0,a1,n0,n1,z0,z1)`, `camera(name,loc,look_at,lens)`, `stage()` (get-or-create `house_v2`), `staging_meshes()`; CLI flags `--rebuild`, `--check`, `--previews=<dir>`; `CHECKS` list each task appends assert functions to.

- [ ] **Step 1: Write the scaffold**

```python
#!/usr/bin/env python3
"""Build the MCM house (docs/treatment/house.md) into property.blend.

Everything stages in a `house_v2` collection shown in a `house_modeling`
workspace scene. Layout scenes link ONLY the `property` root collection
(docs/pipeline.md), so staging is invisible to the film until --swap
(Task 10) moves it in and parks the greybox in `_greybox` (--revert undoes).
Same-file staging (not a second .blend) means shared datablocks: no append
step, no material duplication, no name collisions at swap time. Precedent:
the boy_modeling workspace scene in cast.blend.

Run (Blender must be CLOSED — CLAUDE.md):
  "$BLENDER" --background assets/envs/property/property.blend \
      --python-exit-code 1 --python tools/build_house.py -- [flags]
Flags:
  --rebuild         delete + rebuild the house_v2 staging collection
  --check           run cumulative invariant asserts, then exit non-zero on fail
  --previews=<dir>  render every cam_model_* camera to <dir>/<name>.png
  --swap / --revert (Task 10) move staging into `property` / undo it
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

HOUSE = (-7.0, 5.0, -4.0, 5.0, 0.0, 3.2)      # x0 x1 y0 y1 z0 z1 (FROZEN)
WALL_T = 0.25
FRAME_T = 0.05                                  # thin MCM window profile
STAGE = "house_v2"
GREYBOX_COLL = "_greybox"

# zone -> (r, g, b, alpha). Starter animatic colors per docs/treatment/house.md
# ("Surfaces & material zones") — both style candidates rebind these later.
MATS = {
    "MAT_siding":       (0.86, 0.83, 0.72, 1.0),
    "MAT_fascia":       (0.92, 0.90, 0.86, 1.0),
    "MAT_block":        (0.80, 0.76, 0.68, 1.0),
    "MAT_roof_gravel":  (0.55, 0.52, 0.47, 1.0),
    "MAT_glass":        (0.45, 0.62, 0.72, 0.25),
    "MAT_frames":       (0.93, 0.92, 0.88, 1.0),
    "MAT_door_accent":  (0.69, 0.46, 0.29, 1.0),
    "MAT_deck":         (0.70, 0.66, 0.58, 1.0),
    "MAT_interior":     (0.90, 0.89, 0.85, 1.0),   # light — a dark interior
    "MAT_kitchen_tile": (0.85, 0.66, 0.66, 1.0),   # renders sq050_sh040 black
    "MAT_kitchen_cab":  (0.92, 0.92, 0.90, 1.0),
    "MAT_terrazzo":     (0.88, 0.86, 0.80, 1.0),
    "MAT_metal_93":     (0.26, 0.25, 0.23, 1.0),
    "MAT_plywood":      (0.72, 0.60, 0.40, 1.0),
}

CHECKS = []   # each build section appends f() -> list[str] of failures


def mat(name):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        r, g, b, a = MATS[name]
        bsdf = m.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (r, g, b, 1.0)
            bsdf.inputs["Roughness"].default_value = 0.85
            bsdf.inputs["Alpha"].default_value = a
        if a < 1.0:
            if hasattr(m, "surface_render_method"):
                m.surface_render_method = "BLENDED"
            elif hasattr(m, "blend_method"):
                m.blend_method = "BLEND"
            m.show_transparent_back = False
        m.diffuse_color = (r, g, b, a)
    return m


def stage():
    coll = bpy.data.collections.get(STAGE)
    if coll is None:
        coll = bpy.data.collections.new(STAGE)
        bpy.context.scene.collection.children.link(coll)
    return coll


def staging_meshes():
    return [ob for ob in stage().all_objects if ob.type == "MESH"]


def _box_data(x0, x1, y0, y1, z0, z1, base=0):
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
         (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    f = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1),
         (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    return v, [tuple(i + base for i in face) for face in f]


def _fix_normals(me):
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    me.update()


def multi_box(name, specs, mat_name):
    verts, faces = [], []
    for spec in specs:
        v, f = _box_data(*spec, base=len(verts))
        verts += v
        faces += f
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    _fix_normals(me)
    me.materials.append(mat(mat_name))
    ob = bpy.data.objects.new(name, me)
    stage().objects.link(ob)
    return ob


def box(name, x0, x1, y0, y1, z0, z1, mat_name):
    return multi_box(name, [(x0, x1, y0, y1, z0, z1)], mat_name)


def _wall(face):
    """(wall plane coord, outward sign, along-axis) — blockout convention."""
    x0, x1, y0, y1, _z0, _z1 = HOUSE
    return {"+Y": (y1, 1.0, "X"), "-Y": (y0, -1.0, "X"),
            "+X": (x1, 1.0, "Y"), "-X": (x0, -1.0, "Y")}[face]


def wall_spec(face, a0, a1, n0, n1, z0, z1):
    """Box spec against a house wall; n measured from the OUTER face
    (n<0 into the reveal, n>0 proud of it). Copied from blockout_property."""
    w, s, axis = _wall(face)
    p, q = sorted((w + s * n0, w + s * n1))
    return (a0, a1, p, q, z0, z1) if axis == "X" else (p, q, a0, a1, z0, z1)


def camera(name, loc, look_at, lens=35):
    data = bpy.data.cameras.new(name)
    data.lens = lens
    cam = bpy.data.objects.new(name, data)
    cam.location = loc
    direction = Vector(look_at) - Vector(loc)
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    return cam


def modeling_scene():
    sc = bpy.data.scenes.get("house_modeling")
    if sc is not None:
        return sc
    sc = bpy.data.scenes.new("house_modeling")
    sc.collection.children.link(stage())
    # context: existing set pieces the house must sit against. Objects can
    # live in many collections — this LINKS them, property is untouched.
    ctx = bpy.data.collections.new("hv2_context")
    sc.collection.children.link(ctx)
    for nm in ("ground_yard", "ground_roadside", "road", "driveway",
               "culvert", "bbq", "propane_tank", "truck_body", "truck_cab",
               "mailbox", "mailbox_post"):
        ob = bpy.data.objects.get(nm)
        if ob is not None:
            ctx.objects.link(ob)
    sun = bpy.data.objects.get("sun")
    if sun is not None:
        sc.collection.objects.link(sun)
    sc.world = bpy.data.worlds.get("sky")
    sc.render.engine = bpy.context.scene.render.engine
    sc.render.resolution_x, sc.render.resolution_y = 1280, 720
    sc.view_settings.view_transform = "AgX"
    for nm, loc, look, lens in (
        ("cam_model_front",  (16, -22, 4.5), (-2, 0, 2), 40),
        ("cam_model_rear",   (-2, 26, 5.0),  (-3, 2, 2), 40),
        ("cam_model_corner", (16, -16, 5.5), (-1, 0, 2), 35),
        ("cam_model_tunnel", (-10, -12, 1.4), (-10, 3, 1.2), 30),
        ("cam_model_kitchen", (-5.0, 1.2, 1.7), (5, 3, 1.5), 24),
        ("cam_model_porch",  (4, -9, 1.8), (-2, -4.5, 1.5), 32),
    ):
        cam = camera(nm, loc, look, lens)
        sc.collection.objects.link(cam)
    sc.camera = bpy.data.objects["cam_model_front"]
    return sc


def clear_stage():
    coll = bpy.data.collections.get(STAGE)
    if coll is None:
        return
    for ob in list(coll.all_objects):
        bpy.data.objects.remove(ob, do_unlink=True)


def build():
    clear_stage()
    stage()
    modeling_scene()
    # Tasks 2-8 append build calls here.


def run_checks():
    failures = []
    for fn in CHECKS:
        failures += fn()
    if failures:
        for f in failures:
            print("CHECK FAIL:", f)
        sys.exit(1)
    print(f"all {len(CHECKS)} check groups passed")


def _bounds(ob):
    pts = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    xs, ys, zs = zip(*[(p.x, p.y, p.z) for p in pts])
    return min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)


# Seven staged objects reuse a greybox name (house_roof, garage_roof,
# front_door, porch_deck, porch_post_0/1, back_stoop). While both live in
# this file, Blender would silently .001-suffix the new one — so those are
# BUILT as <name>_v2 and renamed at swap time (Task 10's RENAME_AT_SWAP).
# _ob() resolves either state; checks always use it.
def _ob(nm):
    return bpy.data.objects.get(nm + "_v2") or bpy.data.objects.get(nm)


def check_foundation():
    out = []
    prop = bpy.data.collections.get("property")
    if prop is None:
        return ["property collection missing"]
    names = {ob.name for ob in prop.objects}
    swapped = "house_wall_e" in names        # new shell present == swapped
    if not swapped and len(prop.objects) != 94:
        out.append(f"pre-swap property has {len(prop.objects)}, want 94")
    if any(n.startswith("_gb_") for n in names):
        out.append("greybox objects leaked into property")
    for ob in staging_meshes():
        for slot in ob.data.materials:
            if not slot.name.startswith("MAT_"):
                out.append(f"{ob.name}: non-zone material {slot.name}")
    return out


CHECKS.append(check_foundation)


def render_previews(outdir: Path):
    sc = bpy.data.scenes.get("house_modeling")
    outdir.mkdir(parents=True, exist_ok=True)
    for cam in [o for o in sc.collection.objects if o.type == "CAMERA"]:
        sc.camera = cam
        sc.render.filepath = str(outdir / f"{cam.name}.png")
        bpy.ops.render.render(write_still=True, scene=sc.name)
        print("rendered", cam.name)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--rebuild" in argv:
        build()
        bpy.ops.wm.save_mainfile()
        print("staging rebuilt + saved")
    if "--check" in argv:
        run_checks()
    for arg in argv:
        if arg.startswith("--previews="):
            render_previews(Path(arg.split("=", 1)[1]))
```

- [ ] **Step 2: Verify Blender is closed**

Run: `pgrep -f "Blender.app/Contents/MacOS/Blender"`
Expected: no output (exit 1). If it prints a PID, stop and close Blender.

- [ ] **Step 3: Run it, expect a clean save + passing checks**

```bash
cd /Users/icarpenter/blender/redwood_video
export BLENDER=/Applications/Blender.app/Contents/MacOS/Blender
"$BLENDER" --background assets/envs/property/property.blend \
    --python-exit-code 1 --python tools/build_house.py -- --rebuild --check
```
Expected: `staging rebuilt + saved` then `all 1 check groups passed`. The
`property` count guard (94) proves staging touched nothing the film links.

- [ ] **Step 4: Commit the script only**

```bash
git add tools/build_house.py
git commit -m "feat: build_house scaffold — house_v2 staging + house_modeling scene"
```

---

### Task 2: House shell — segmented walls, floor, no booleans

**Files:**
- Modify: `tools/build_house.py` (extend `build()`)

**Interfaces:**
- Consumes: `wall_spec`, `multi_box`, `box`, `CHECKS` from Task 1.
- Produces: `wall_run(name, face, a_lo, a_hi, z_lo, z_hi, openings, mat_name)`; opening tables `E_OPENINGS`, `N_OPENINGS`, `W_OPENINGS`, `S_OPENINGS` (consumed again by Task 4's window units); objects `house_wall_e/n/w/s`, `house_floor`, `hv2 partition` comes later (Task 7).

- [ ] **Step 1: Add the wall generator and the frozen opening tables**

```python
# openings per wall: (a0, a1, sill, head) along the wall's axis.
# FROZEN — docs/treatment/house.md "Elevations". Clerestory is the one NEW cut.
E_OPENINGS = [                       # -Y wall, a = x
    (-6.00, -4.20, 1.20, 2.40),      # front_south
    (-2.40, -1.40, 0.50, 2.50),      # front door
    ( 1.99,  3.79, 1.20, 2.40),      # front_north
    ( 1.40,  4.60, 2.60, 3.05),      # clerestory (stacks over front_north)
]
N_OPENINGS = [                       # +X wall, a = y
    (-2.80, -1.40, 1.20, 2.40),      # north_east
    ( 1.60,  4.20, 1.20, 2.40),      # kitchen_north casement pair
]
W_OPENINGS = [                       # +Y wall, a = x
    (-3.40, -2.20, 0.45, 2.55),      # back door
    (-6.40, -5.20, 1.50, 2.40),      # west_south
    ( 1.40,  4.20, 1.20, 2.40),      # kitchen_west casement pair
]
S_OPENINGS = [                       # -X wall, a = y
    ( 3.40,  4.60, 1.20, 2.40),      # south_west
]


def wall_run(name, face, a_lo, a_hi, z_lo, z_hi, openings, mat_name):
    """One wall as clean segment boxes: slice into vertical bands at every
    opening edge, fill the z-gaps per band. Quads only, handles stacked
    openings (the clerestory over front_north), no booleans to go stale."""
    edges = sorted({a_lo, a_hi, *[a for o in openings for a in o[:2]]})
    specs = []
    for b_lo, b_hi in zip(edges, edges[1:]):
        mid = (b_lo + b_hi) / 2
        cuts = sorted((o[2], o[3]) for o in openings if o[0] < mid < o[1])
        z = z_lo
        for c_lo, c_hi in cuts:
            if c_lo > z:
                specs.append(wall_spec(face, b_lo, b_hi, -WALL_T, 0.0, z, c_lo))
            z = max(z, c_hi)
        if z < z_hi:
            specs.append(wall_spec(face, b_lo, b_hi, -WALL_T, 0.0, z, z_hi))
    return multi_box(name, specs, mat_name)


def build_house_shell():
    # ±Y walls own the corners (full 12 m); ±X walls butt between them.
    wall_run("house_wall_e", "-Y", -7.00, 5.00, 0.0, 3.2, E_OPENINGS, "MAT_siding")
    wall_run("house_wall_w", "+Y", -7.00, 5.00, 0.0, 3.2, W_OPENINGS, "MAT_siding")
    wall_run("house_wall_n", "+X", -3.75, 4.75, 0.0, 3.2, N_OPENINGS, "MAT_siding")
    wall_run("house_wall_s", "-X", -3.75, 4.75, 0.0, 3.2, S_OPENINGS, "MAT_siding")
    box("house_floor", -7.0, 5.0, -4.0, 5.0, 0.0, 0.25, "MAT_interior")
    # concrete plinth course proud of the siding at grade; the -X run skips
    # the garage attachment (y -3..3), the others overhang corners 0.04
    multi_box("house_plinth", [
        wall_spec("-Y", -7.04, 5.04, 0.0, 0.04, 0.0, 0.18),
        wall_spec("+Y", -7.04, 5.04, 0.0, 0.04, 0.0, 0.18),
        wall_spec("+X", -4.04, 5.04, 0.0, 0.04, 0.0, 0.18),
        wall_spec("-X", 3.0, 5.04, 0.0, 0.04, 0.0, 0.18),
    ], "MAT_block")


def check_shell():
    out = []
    for nm in ("house_wall_e", "house_wall_n", "house_wall_w", "house_wall_s",
               "house_floor", "house_plinth"):
        ob = bpy.data.objects.get(nm)
        if ob is None:
            out.append(f"{nm} missing")
            continue
        b = _bounds(ob)
        if not (-7.05 <= b[0] and b[1] <= 5.05 and -4.05 <= b[2]
                and b[3] <= 5.05 and b[5] <= 3.21):
            out.append(f"{nm} outside house envelope: {b}")
    return out


CHECKS.append(check_shell)
```
Call `build_house_shell()` from `build()`.

- [ ] **Step 2: Rebuild + check** (same command as Task 1 Step 3, after the pgrep guard). Expected: `all 2 check groups passed`.

- [ ] **Step 3: Render and look**

```bash
"$BLENDER" --background assets/envs/property/property.blend \
    --python-exit-code 1 --python tools/build_house.py \
    -- --rebuild --check --previews=<scratchpad>/house_renders/t2
```
Read the PNGs. Expect: four walls with real holes where every opening
belongs (front door hole reads at porch height, clerestory hole above
front_north), light interior visible through them, plinth line at grade.
Greybox house still standing alongside in context renders is EXPECTED —
it's still what the film links; ignore it (staging renders show both).

- [ ] **Step 4: Commit**

```bash
git add tools/build_house.py
git commit -m "feat: house shell — segmented walls with frozen openings, plinth"
```

---

### Task 3: Roof, fascia, beams, porch canopy

**Files:**
- Modify: `tools/build_house.py`

**Interfaces:**
- Consumes: `box`, `multi_box`, `CHECKS`.
- Produces: `build_house_roof()`; `CANOPY_XS`/`BEAM_XS` constants; objects `house_roof`, `house_fascia`, `house_ceiling`, `beam_*`.

- [ ] **Step 1: Add roof geometry**

```python
# beam module 1.35 lands on both porch posts (x -4.7, 0.7) — spec "Massing".
CANOPY_XS = (-4.70, -3.35, -2.00, -0.65, 0.70)
BEAM_XS = (-6.05, *CANOPY_XS, 2.05, 3.40, 4.75)

ROOF_SLABS = [  # z 3.2..3.35, tar-and-gravel. Stepped south edge: the 0.75
    (-7.00, 5.75, -4.75, 5.75),   # main (garage abuts x=-7 across y -3..3)
    (-7.75, -7.00, -4.75, -3.00), # south overhang, road corner
    (-7.75, -7.00,  3.00, 5.75),  # south overhang, backyard corner
    (-5.20, 1.20, -6.60, -4.75),  # porch canopy tongue (old porch_roof span)
]

FASCIA = [  # z 3.2..3.6 band, 0.08 thick, following the roof perimeter
    ( 5.67,  5.75, -4.75,  5.75),   # north edge (x = 5.75 face)
    (-7.75,  5.75,  5.67,  5.75),   # west edge
    (-7.75, -7.67,  3.00,  5.67),   # south-back (x = -7.75 face)
    (-7.75, -7.00,  3.00,  3.08),   # jog toward the garage joint
    (-7.75, -7.67, -4.75, -3.00),   # south-front
    (-7.75, -7.00, -3.08, -3.00),   # jog
    ( 1.20,  5.75, -4.75, -4.67),   # east edge, north of the canopy
    (-7.75, -5.20, -4.75, -4.67),   # east edge, south of the canopy
    (-5.20, -5.12, -6.60, -4.75),   # canopy west cheek
    (-5.20,  1.20, -6.60, -6.52),   # canopy east face (over the steps)
    ( 1.12,  1.20, -6.60, -4.75),   # canopy east cheek
]


def build_house_roof():
    # _v2 suffix: the greybox still owns the plain name (see Task 1 note)
    multi_box("house_roof_v2", [(x0, x1, y0, y1, 3.20, 3.35)
                             for x0, x1, y0, y1 in ROOF_SLABS], "MAT_roof_gravel")
    multi_box("house_fascia", [(x0, x1, y0, y1, 3.20, 3.60)
                               for x0, x1, y0, y1 in FASCIA], "MAT_fascia")
    # light soffit board over the shot interior (kitchen) so up-angles read
    box("house_ceiling", -6.75, 4.75, 0.25, 4.75, 3.18, 3.20, "MAT_interior")
    for i, bx in enumerate(BEAM_XS):
        y1 = 5.90                                   # punches west fascia 0.15
        y0 = -6.75 if bx in CANOPY_XS else -4.90    # and east/canopy fascia
        box(f"beam_{i}", bx - 0.05, bx + 0.05, y0, y1, 2.95, 3.20, "MAT_fascia")
    # the one replaced fascia board — dilapidation-as-content (spec, Roofscape)
    box("fascia_patch", 2.60, 3.90, -4.755, -4.745, 3.22, 3.58, "MAT_plywood")


def check_roof():
    out = []
    beams = [ob for ob in staging_meshes() if ob.name.startswith("beam_")]
    if len(beams) != 9:
        out.append(f"{len(beams)} beams, want 9")
    roof = _ob("house_roof")
    if roof is None or abs(_bounds(roof)[5] - 3.35) > 0.01:
        out.append("house_roof missing or wrong height (want top 3.35)")
    if _ob("house_fascia") is None:
        out.append("house_fascia missing")
    return out


CHECKS.append(check_roof)
```
Call `build_house_roof()` from `build()`.

- [ ] **Step 2: Rebuild + check + render** (commands as Task 2). Expect in
`cam_model_front`/`cam_model_corner`: flat slab, deep fascia band, beam ends
dotting the east/west fascia on a regular module, canopy running out over
the porch zone, plywood patch board visibly warmer on the east fascia.
- [ ] **Step 3: Commit** — `git add tools/build_house.py && git commit -m "feat: flat roof, fascia band, exposed beams, canopy"`

---

### Task 4: Window and door units

**Files:**
- Modify: `tools/build_house.py`

**Interfaces:**
- Consumes: `wall_spec`, `_wall`, `multi_box`, opening tables from Task 2.
- Produces: `_sash_matrix(hinge,u,n,deg)`, `fixed_lite(tag,face,a0,a1,z0,z1,mullions)`, `casement_pair(tag,face,a0,a1,z0,z1,open_deg)`, `hinged_door(name,face,a0,a1,z0,z1,open_deg,mat_name,lites)`; objects `win_*`, `front_door`, `back_door`.

- [ ] **Step 1: Add unit builders**

```python
def _sash_matrix(hinge, u, n, swing_deg):
    """Blockout_property's sash placement, verbatim: local x = hinge->free
    edge, y = outward normal; the second leaf's closed basis is a reflection,
    which no Euler produces — write matrix_world directly. Positive swing
    moves the free edge outward."""
    sign = 1.0 if (Vector((0, 0, 1)).cross(u) - n).length < 1e-6 else -1.0
    t = math.radians(swing_deg) * sign
    c, s = math.cos(t), math.sin(t)
    rz = Matrix(((c, -s, 0.0), (s, c, 0.0), (0.0, 0.0, 1.0)))
    uu, nn = rz @ u, rz @ n
    return Matrix(((uu.x, nn.x, 0.0, hinge.x),
                   (uu.y, nn.y, 0.0, hinge.y),
                   (uu.z, nn.z, 1.0, hinge.z),
                   (0.0, 0.0, 0.0, 1.0)))


def _leaf_frames(face):
    w, s, axis = _wall(face)
    n = Vector((0, s, 0)) if axis == "X" else Vector((s, 0, 0))
    return w, axis, n


def fixed_lite(tag, face, a0, a1, z0, z1, mullions=0):
    specs = [
        wall_spec(face, a0, a1, -0.10, -0.05, z1 - FRAME_T, z1),
        wall_spec(face, a0, a1, -0.10, -0.05, z0, z0 + FRAME_T),
        wall_spec(face, a0, a0 + FRAME_T, -0.10, -0.05, z0, z1),
        wall_spec(face, a1 - FRAME_T, a1, -0.10, -0.05, z0, z1),
    ]
    for i in range(mullions):
        m = a0 + (a1 - a0) * (i + 1) / (mullions + 1)
        specs.append(wall_spec(face, m - 0.02, m + 0.02, -0.10, -0.05, z0, z1))
    multi_box(f"win_{tag}_frame", specs, "MAT_frames")
    multi_box(f"win_{tag}_glass",
              [wall_spec(face, a0, a1, -0.085, -0.065, z0, z1)], "MAT_glass")
    multi_box(f"win_{tag}_sill",
              [wall_spec(face, a0 - 0.03, a1 + 0.03, -WALL_T, 0.06,
                         z0 - 0.04, z0)], "MAT_frames")


def casement_pair(tag, face, a0, a1, z0, z1, open_deg=62.0):
    """Static baked-open pair — matches today's set and the spec's default
    state; per-shot closed/animated states are the casement_leaf PROP."""
    multi_box(f"win_{tag}_frame", [
        wall_spec(face, a0, a1, -0.10, -0.05, z1 - FRAME_T, z1),
        wall_spec(face, a0, a1, -0.10, -0.05, z0, z0 + FRAME_T),
        wall_spec(face, a0, a0 + FRAME_T, -0.10, -0.05, z0, z1),
        wall_spec(face, a1 - FRAME_T, a1, -0.10, -0.05, z0, z1),
    ], "MAT_frames")
    multi_box(f"win_{tag}_sill",
              [wall_spec(face, a0 - 0.03, a1 + 0.03, -WALL_T, 0.06,
                         z0 - 0.04, z0)], "MAT_frames")
    w, axis, n = _leaf_frames(face)
    half, height = (a1 - a0) / 2, z1 - z0
    for leaf, (a_h, along) in enumerate(((a0, 1.0), (a1, -1.0))):
        u = Vector((along, 0, 0)) if axis == "X" else Vector((0, along, 0))
        hinge = (Vector((a_h, w, z0)) if axis == "X"
                 else Vector((w, a_h, z0)))
        m = _sash_matrix(hinge, u, n, open_deg)
        r = 0.07
        stile = multi_box(f"win_{tag}_sash{leaf}", [
            (0, half, 0, 0.05, 0, r),
            (0, half, 0, 0.05, height - r, height),
            (0, r, 0, 0.05, 0, height),
            (half - r, half, 0, 0.05, 0, height)], "MAT_frames")
        pane = multi_box(f"win_{tag}_sash{leaf}_glass",
                         [(r, half - r, 0.012, 0.038, r, height - r)],
                         "MAT_glass")
        for ob in (stile, pane):
            ob.matrix_world = m


def hinged_door(name, face, a0, a1, z0, z1, open_deg, mat_name, lites=()):
    """Slab door hinged at the a0 jamb. open_deg > 0 swings OUTWARD,
    negative swings into the house. Lites are leaf-local (x from hinge)."""
    w, axis, n = _leaf_frames(face)
    width, height = a1 - a0, z1 - z0
    u = Vector((1, 0, 0)) if axis == "X" else Vector((0, 1, 0))
    hinge = Vector((a0, w, z0)) if axis == "X" else Vector((w, a0, z0))
    m = _sash_matrix(hinge, u, n, open_deg)
    door = multi_box(name, [(0, width, -0.15, -0.10, 0, height)], mat_name)
    door.matrix_world = m
    for i, (lx0, lx1, lz0, lz1) in enumerate(lites):
        g = multi_box(f"{name}_lite{i}",
                      [(lx0, lx1, -0.155, -0.095, lz0, lz1)], "MAT_glass")
        g.matrix_world = m
    return door


def build_house_windows():
    fixed_lite("front_south", "-Y", -6.00, -4.20, 1.20, 2.40)
    fixed_lite("front_north", "-Y", 1.99, 3.79, 1.20, 2.40)
    fixed_lite("clerestory", "-Y", 1.40, 4.60, 2.60, 3.05, mullions=2)
    fixed_lite("north_east", "+X", -2.80, -1.40, 1.20, 2.40)
    fixed_lite("west_south", "+Y", -6.40, -5.20, 1.50, 2.40)
    fixed_lite("south_west", "-X", 3.40, 4.60, 1.20, 2.40)
    casement_pair("kitchen_north", "+X", 1.60, 4.20, 1.20, 2.40)
    casement_pair("kitchen_west", "+Y", 1.40, 4.20, 1.20, 2.40)
    # front door: accent slab, three staggered lites, baked open INTO the
    # house ~80 (dark doorway read; the screen door is a PROP).
    # _v2: greybox owns "front_door" until the swap (Task 1 note).
    hinged_door("front_door_v2", "-Y", -2.40, -1.40, 0.50, 2.50, -80.0,
                "MAT_door_accent",
                lites=((0.15, 0.35, 1.55, 1.75),
                       (0.40, 0.60, 1.30, 1.50),
                       (0.65, 0.85, 1.05, 1.25)))
    # back door: baked closed, half-glass (upper pane), painted not accent
    hinged_door("back_door", "+Y", -3.40, -2.20, 0.45, 2.55, 0.0,
                "MAT_frames", lites=((0.10, 1.10, 1.25, 2.00),))
    # window box on the SOUTH leaf's half of the kitchen_west sill only —
    # the north half is the sill Mom vaults in sq070_sh010 (spec, West)
    box("window_box", 1.50, 2.70, 5.06, 5.30, 0.95, 1.18, "MAT_metal_93")


def check_windows():
    out = []
    want = ["win_front_south_glass", "win_front_north_glass",
            "win_clerestory_glass", "win_north_east_glass",
            "win_west_south_glass", "win_south_west_glass",
            "win_kitchen_north_sash0", "win_kitchen_north_sash1",
            "win_kitchen_west_sash0", "win_kitchen_west_sash1",
            "front_door", "back_door", "window_box"]
    out += [f"{nm} missing" for nm in want if _ob(nm) is None]
    return out


CHECKS.append(check_windows)
```
Call `build_house_windows()` from `build()`.

- [ ] **Step 2: Rebuild + check + render.** Expect: casements swung open on
both kitchen windows exactly like the greybox's, thin frames everywhere,
the accent front door visible ajar through its opening from
`cam_model_porch`, clerestory as a 3-lite ribbon, window box hanging on the
south half of the kitchen_west sill only.
- [ ] **Step 3: Commit** — `git commit -m "feat: window units, doors — casements baked open, accent front door"` (add `tools/build_house.py`).

---

### Task 5: Garage — shell, passthrough, parked sectional doors

**Files:**
- Modify: `tools/build_house.py`

**Interfaces:**
- Consumes: `box`, `multi_box`.
- Produces: `build_garage()`; objects `garage_wall_*`, `garage_roof`, `garage_fascia`, `garage_floor`, `garage_sect_front/rear`, `garage_tracks`.

- [ ] **Step 1: Add the garage** (its own box helpers — the `wall_spec`
helpers are house-anchored, so garage walls are written as plain boxes):

```python
def build_garage():
    # ±Y walls carry the passthrough: jambs + header + 0.1 curb. FROZEN
    # opening x -12.4..-7.6, z 0.1..2.4, both faces (site.md passthrough).
    for tag, y0, y1 in (("front", -3.0, -2.75), ("rear", 2.75, 3.0)):
        multi_box(f"garage_wall_{tag}", [
            (-13.0, -12.4, y0, y1, 0.0, 2.9),      # west jamb
            (-7.6, -7.0, y0, y1, 0.0, 2.9),        # east jamb
            (-12.4, -7.6, y0, y1, 2.4, 2.9),       # header
            (-12.4, -7.6, y0, y1, 0.0, 0.1),       # curb
        ], "MAT_siding")
    box("garage_wall_s", -13.0, -12.75, -2.75, 2.75, 0.0, 2.9, "MAT_siding")
    box("garage_floor", -13.0, -7.0, -3.0, 3.0, 0.0, 0.1, "MAT_deck")
    # _v2: greybox owns "garage_roof" until the swap (Task 1 note)
    box("garage_roof_v2", -13.6, -7.0, -3.6, 3.6, 2.90, 3.00, "MAT_roof_gravel")
    box("garage_ceiling", -12.75, -7.0, -2.75, 2.75, 2.88, 2.90, "MAT_interior")
    multi_box("garage_fascia", [                    # z 2.9..3.25, 0.08 thick
        (-13.60, -7.00, -3.60, -3.52, 2.90, 3.25),  # east (road) edge
        (-13.60, -13.52, -3.60, 3.60, 2.90, 3.25),  # south edge
        (-13.60, -7.00, 3.52, 3.60, 2.90, 3.25),    # west (backyard) edge
    ], "MAT_fascia")
    # sectional doors PARKED OPEN under the ceiling — never rigged, never
    # closed (the script never closes them; spec, Garage). Glass-panel
    # style per the mustard-ranch ref: rails accent, panes glass.
    for tag, y0, y1 in (("front", -2.90, -1.10), ("rear", 1.10, 2.90)):
        rails, panes = [], []
        step = (y1 - y0) / 4
        for i in range(5):
            ry = y0 + step * i
            rails.append((-12.35, -7.65, ry - 0.025, ry + 0.025, 2.44, 2.56))
        for i in range(4):
            p0 = y0 + step * i + 0.025
            p1 = y0 + step * (i + 1) - 0.025
            panes.append((-12.30, -7.70, p0, p1, 2.47, 2.53))
        multi_box(f"garage_sect_{tag}_rails", rails, "MAT_door_accent")
        multi_box(f"garage_sect_{tag}_glass", panes, "MAT_glass")
    multi_box("garage_tracks", [
        (-12.45, -12.38, -2.9, -1.0, 2.42, 2.46),
        (-7.62, -7.55, -2.9, -1.0, 2.42, 2.46),
        (-12.45, -12.38, 1.0, 2.9, 2.42, 2.46),
        (-7.62, -7.55, 1.0, 2.9, 2.42, 2.46),
    ], "MAT_metal_93")


def check_garage():
    out = []
    for nm in ("garage_wall_front", "garage_wall_rear", "garage_roof",
               "garage_fascia", "garage_sect_front_rails",
               "garage_sect_rear_glass", "garage_tracks"):
        if _ob(nm) is None:
            out.append(f"{nm} missing")
    roof = _ob("garage_roof")
    if roof is not None and abs(_bounds(roof)[5] - 3.0) > 0.01:
        out.append("garage_roof top should be 3.0")
    return out


CHECKS.append(check_garage)
```
Call `build_garage()` from `build()`.

- [ ] **Step 2: Rebuild + check + render.** `cam_model_tunnel` must show the
road→garage→backyard sightline wide open with glassy door panels parked
overhead; `cam_model_corner` shows the fascia stepping down 0.35 at the
house joint.
- [ ] **Step 3: Commit** — `git commit -m "feat: garage — passthrough shell, parked glass sectionals, stepped fascia"`.

---

### Task 6: Porch, steps, stoop, breeze-block, roofscape junk

**Files:**
- Modify: `tools/build_house.py`

**Interfaces:**
- Consumes: `box`, `multi_box`, `camera` helpers.
- Produces: `build_porch_and_roofscape()`; objects `porch_deck`, `porch_step`, `porch_post_0/1`, `porch_mat`, `breeze_screen`, `back_stoop`, `swamp_cooler`, `tv_aerial`, `downspout_n/s`.

- [ ] **Step 1: Add it**

```python
def build_porch_and_roofscape():
    # _v2 on deck/posts/stoop: greybox owns the plain names (Task 1 note)
    box("porch_deck_v2", -5.0, 1.0, -6.4, -4.0, 0.0, 0.5, "MAT_deck")  # FROZEN
    # one intermediate tread: grade -> 0.25 -> deck 0.5. Full run x -3..0,
    # projecting south of the deck — sq010_sh030's one-jump steps.
    box("porch_step", -3.0, 0.0, -7.0, -6.7, 0.0, 0.25, "MAT_deck")
    for i, px in enumerate((-4.7, 0.7)):            # FROZEN positions
        box(f"porch_post_{i}_v2", px - 0.06, px + 0.06, -6.24, -6.12,
            0.5, 3.2, "MAT_frames")                 # slim steel, meets canopy
    box("porch_mat", -2.5, -1.3, -4.9, -4.1, 0.5, 0.52, "MAT_metal_93")
    # breeze-block screen closing the porch's south end (x = -5 plane).
    # Real holes: outer frame + bar grid, 6 x 8 cells.
    bars = [(-5.12, -5.00, -6.40, -4.40, 0.50, 0.56),
            (-5.12, -5.00, -6.40, -4.40, 2.84, 2.90)]
    for i in range(7):                               # verticals every ~0.33
        by = -6.40 + i * (2.00 / 6)
        bars.append((-5.12, -5.00, by - 0.02, by + 0.02, 0.50, 2.90))
    for j in range(8):                               # horizontals every 0.30
        bz = 0.56 + j * 0.285
        bars.append((-5.12, -5.00, -6.40, -4.40, bz - 0.02, bz + 0.02))
    multi_box("breeze_screen", bars, "MAT_block")
    box("back_stoop_v2", -4.0, -1.0, 5.0, 6.2, 0.0, 0.45, "MAT_deck")  # FROZEN
    # roofscape (spec, Roofscape): the 1993 layer
    box("swamp_cooler_curb", -4.5, -3.5, 2.5, 3.5, 3.35, 3.45, "MAT_metal_93")
    box("swamp_cooler", -4.45, -3.55, 2.55, 3.45, 3.45, 4.15, "MAT_metal_93")
    box("tv_aerial_mast", 4.48, 4.52, -4.22, -4.18, 3.35, 5.15, "MAT_metal_93")
    for i, az in enumerate((4.75, 4.95)):
        box(f"tv_aerial_bar_{i}", 4.50 - 0.45 - i * 0.1, 4.50 + 0.45 + i * 0.1,
            -4.21, -4.19, az - 0.015, az + 0.015, "MAT_metal_93")
    box("downspout_n", 5.70, 5.78, 5.25, 5.33, 0.0, 3.42, "MAT_metal_93")
    box("downspout_s", -7.78, -7.70, -4.40, -4.32, 0.0, 3.42, "MAT_metal_93")


def check_porch():
    out = []
    for nm in ("porch_deck", "porch_step", "porch_post_0", "porch_post_1",
               "breeze_screen", "back_stoop", "swamp_cooler", "tv_aerial_mast",
               "downspout_n", "downspout_s"):
        if _ob(nm) is None:
            out.append(f"{nm} missing")
    deck = _ob("porch_deck")
    if deck is not None and any(
            abs(a - b) > 1e-4 for a, b in
            zip(_bounds(deck), (-5.0, 1.0, -6.4, -4.0, 0.0, 0.5))):
        out.append("porch_deck moved off its frozen footprint")
    return out


CHECKS.append(check_porch)
```
Call `build_porch_and_roofscape()` from `build()`.

- [ ] **Step 2: Rebuild + check + render.** `cam_model_porch`: deck, step,
mat, breeze screen at frame edge, slim posts to the canopy. `cam_model_rear`:
swamp cooler and aerial breaking the flat roofline.
- [ ] **Step 3: Commit** — `git commit -m "feat: porch, steps, breeze screen, stoop, 1993 roofscape"`.

---

### Task 7: Kitchen interior + partition opening

**Files:**
- Modify: `tools/build_house.py`

**Interfaces:**
- Consumes: `box`, `multi_box`.
- Produces: `build_kitchen()`; objects `partition_e`, `kitchen_floor`, `kitchen_counter_w/n`, `kitchen_tile_*`, `kitchen_sink`, `kitchen_faucet`.

- [ ] **Step 1: Add the kitchen** (1962 bones only — 1993 clutter is set
dressing later, per spec "Interior scope"; NO upper cabinets, keeps
sq050_sh040's sightlines and the gun-cabinet wall `y 0.25…1.6` clear):

```python
def build_kitchen():
    # partition at y 0..0.25 with a cased 1.2 m opening centred x -0.5
    multi_box("partition_e", [
        (-6.75, -1.10, 0.0, 0.25, 0.0, 3.18),
        (0.10, 4.75, 0.0, 0.25, 0.0, 3.18),
        (-1.10, 0.10, 0.0, 0.25, 2.10, 3.18),
    ], "MAT_interior")
    multi_box("partition_casing", [
        (-1.14, -1.10, -0.02, 0.27, 0.0, 2.14),
        (0.10, 0.14, -0.02, 0.27, 0.0, 2.14),
        (-1.14, 0.14, -0.02, 0.27, 2.10, 2.14),
    ], "MAT_frames")
    box("kitchen_floor", -6.75, 4.75, 0.25, 4.75, 0.25, 0.265, "MAT_terrazzo")
    # counter L: along west wall (sink centred under kitchen_west) and
    # around the NW corner along the north wall
    box("kitchen_counter_w", 0.90, 4.70, 4.10, 4.75, 0.265, 0.85, "MAT_kitchen_cab")
    box("kitchen_counter_n", 4.10, 4.75, 1.00, 4.10, 0.265, 0.85, "MAT_kitchen_cab")
    box("kitchen_tile_top_w", 0.90, 4.70, 4.08, 4.75, 0.85, 0.90, "MAT_kitchen_tile")
    box("kitchen_tile_top_n", 4.08, 4.75, 1.00, 4.10, 0.85, 0.90, "MAT_kitchen_tile")
    multi_box("kitchen_tile_splash", [
        (0.90, 4.70, 4.70, 4.745, 0.90, 1.20),      # west wall, up to sill
        (4.70, 4.745, 1.00, 4.70, 0.90, 1.20),      # north wall
    ], "MAT_kitchen_tile")
    box("kitchen_sink", 2.30, 3.30, 4.25, 4.65, 0.86, 0.905, "MAT_metal_93")
    box("kitchen_faucet", 2.76, 2.84, 4.66, 4.72, 0.90, 1.14, "MAT_metal_93")


def check_kitchen():
    out = []
    for nm in ("partition_e", "kitchen_floor", "kitchen_counter_w",
               "kitchen_counter_n", "kitchen_tile_splash", "kitchen_sink"):
        if bpy.data.objects.get(nm) is None:
            out.append(f"{nm} missing")
    return out


CHECKS.append(check_kitchen)
```
Call `build_kitchen()` from `build()`.

- [ ] **Step 2: Rebuild + check + render.** `cam_model_kitchen`: pink-tiled
L-counter with the sink under the west casements, terrazzo floor, cased
opening in the partition, bare wall beside the north window where the
`gun_cabinet` prop stands.
- [ ] **Step 3: Commit** — `git commit -m "feat: kitchen — 1962 bones, pink tile, partition opening"`.

---

### Task 8: UVs + full check; staging milestone commit

**Files:**
- Modify: `tools/build_house.py`

**Interfaces:**
- Consumes: `staging_meshes()`.
- Produces: `unwrap_stage()` — world-space axis-aligned box projection at 1 UV tile = 12 m (≈3.4 px/cm on a 4K map, spec "UV & painting prep"); check `check_uvs`.

- [ ] **Step 1: Add deterministic unwrap** (no `bpy.ops.uv.*` — context-free,
axis-aligned by construction, exactly the orientation rule the tilt-dab
painting needs):

```python
def unwrap_stage(scale=1.0 / 12.0):
    for ob in staging_meshes():
        me = ob.data
        uv = me.uv_layers[0] if me.uv_layers else me.uv_layers.new(name="UVMap")
        mw = ob.matrix_world
        for poly in me.polygons:
            n = (mw.to_3x3() @ poly.normal)
            ax = max(range(3), key=lambda i: abs(n[i]))
            for li in poly.loop_indices:
                co = mw @ me.vertices[me.loops[li].vertex_index].co
                u, v = ((co.y, co.z), (co.x, co.z), (co.x, co.y))[ax]
                uv.data[li].uv = (u * scale, v * scale)


def check_uvs():
    return [f"{ob.name} has no UVs" for ob in staging_meshes()
            if not ob.data.uv_layers]


CHECKS.append(check_uvs)
```
Call `unwrap_stage()` at the end of `build()`. Known limits, accepted at
this stage (note them in the module docstring): opposite-facing faces get
mirrored dab direction, and world-space projection means paint continues
across objects — both fine for zone-flat starter materials; hero-asset UV
touch-up happens at look-dev with the style locked.

- [ ] **Step 2: Rebuild + full check.** Expected: `all 8 check groups passed`.
- [ ] **Step 3: Render the full preview set** to `<scratchpad>/house_renders/staging_final/` and read every PNG against the spec's elevation section.
- [ ] **Step 4: Milestone commit — script AND blend:**

```bash
git add tools/build_house.py assets/envs/property/property.blend
git commit -m "feat: MCM house staged complete in house_v2 — not yet swapped into property"
```

---

### Task 9: CHECKPOINT — present staging renders to Ian

- [ ] **Step 1:** Assemble the `staging_final` renders and present them to
Ian with the two calls he flagged as worth a second look at spec time
(casements-baked-open default; clerestory placement) plus anything that
looks off in the renders. **Do not proceed to Task 10 until Ian approves
the staging renders.** This is the cheap moment to change geometry — the
greybox is still what the film sees.

---

### Task 10: The swap — `--swap` / `--revert`, then preview-cam re-render

**Files:**
- Modify: `tools/build_house.py`

**Interfaces:**
- Consumes: `stage()`, `GREYBOX_COLL`.
- Produces: `swap()`, `revert()`; post-swap `property` contains the new build; greybox parked in `_greybox` renamed `_gb_*`.

- [ ] **Step 1: Add the swap** (the greybox list is exact — 46 objects, from
the pre-build dump of `property.blend`; the 48 keepers are grounds, road,
ditch, driveway, fences, trees, truck, BBQ, mailbox):

```python
GREYBOX_SWAP = [
    "house", "house_roof", "garage", "garage_roof", "garage_door_front",
    "garage_door_rear", "porch_deck", "porch_post_0", "porch_post_1",
    "porch_roof", "front_door", "back_door_casing", "back_stoop",
    "wall_kitchen_east",
    "win_front_north_casing", "win_front_north_glass",
    "win_front_north_mullion", "win_front_north_sill",
    "win_front_south_casing", "win_front_south_glass",
    "win_front_south_mullion", "win_front_south_sill",
    "win_kitchen_north_casing", "win_kitchen_north_sash0",
    "win_kitchen_north_sash0_glass", "win_kitchen_north_sash1",
    "win_kitchen_north_sash1_glass", "win_kitchen_north_sill",
    "win_kitchen_west_casing", "win_kitchen_west_sash0",
    "win_kitchen_west_sash0_glass", "win_kitchen_west_sash1",
    "win_kitchen_west_sash1_glass", "win_kitchen_west_sill",
    "win_north_east_casing", "win_north_east_glass",
    "win_north_east_mullion", "win_north_east_sill",
    "win_south_west_casing", "win_south_west_glass",
    "win_south_west_mullion", "win_south_west_sill",
    "win_west_south_casing", "win_west_south_glass",
    "win_west_south_mullion", "win_west_south_sill",
]
# the seven staged _v2 objects take the plain name once _gb_* frees it
RENAME_AT_SWAP = {
    "house_roof_v2": "house_roof",
    "garage_roof_v2": "garage_roof",
    "front_door_v2": "front_door",
    "porch_deck_v2": "porch_deck",
    "porch_post_0_v2": "porch_post_0",
    "porch_post_1_v2": "porch_post_1",
    "back_stoop_v2": "back_stoop",
}


def swap():
    prop = bpy.data.collections["property"]
    if bpy.data.collections.get(GREYBOX_COLL):
        sys.exit("already swapped — use --revert first to re-run")
    gb = bpy.data.collections.new(GREYBOX_COLL)
    bpy.context.scene.collection.children.link(gb)
    for nm in GREYBOX_SWAP:
        ob = bpy.data.objects.get(nm)
        if ob is None:
            sys.exit(f"greybox object missing: {nm} — wrong file state?")
        prop.objects.unlink(ob)
        gb.objects.link(ob)
        ob.name = f"_gb_{nm}"
    gb.hide_render = True
    gb.hide_viewport = True
    for ob in list(stage().objects):
        stage().objects.unlink(ob)
        prop.objects.link(ob)
        ob.name = RENAME_AT_SWAP.get(ob.name, ob.name)
    print(f"swapped: property now {len(prop.objects)} objects "
          f"(48 keepers + new build), greybox parked in {GREYBOX_COLL}")


def revert():
    prop = bpy.data.collections["property"]
    gb = bpy.data.collections.get(GREYBOX_COLL)
    if gb is None:
        sys.exit("nothing to revert")
    back_to_v2 = {v: k for k, v in RENAME_AT_SWAP.items()}
    for ob in [o for o in prop.objects if o.name not in KEEPERS]:
        prop.objects.unlink(ob)
        stage().objects.link(ob)
        ob.name = back_to_v2.get(ob.name, ob.name)
    for ob in list(gb.objects):
        gb.objects.unlink(ob)
        prop.objects.link(ob)
        ob.name = ob.name.removeprefix("_gb_")
    bpy.data.collections.remove(gb)
    print("reverted: greybox restored into property")


KEEPERS = {
    "ground_far", "ground_yard", "ground_roadside", "road", "ditch_floor",
    "ditch_wall_e", "ditch_wall_w", "culvert", "driveway", "mailbox",
    "mailbox_post", "bbq", "propane_tank", "truck_body", "truck_cab",
    "fence_rail_hi", "fence_rail_lo",
    *[f"fence_post_{i}" for i in range(15)],
    *[f"trunk_{i}" for i in range(8)],
    *[f"canopy_{i}" for i in range(8)],
}
```
Wire `--swap` / `--revert` into `__main__` (each followed by
`bpy.ops.wm.save_mainfile()`). Note `KEEPERS` counts 48 exactly — assert
`len(KEEPERS) == 48` at module import time.

- [ ] **Step 2: pgrep guard, then swap:**

```bash
"$BLENDER" --background assets/envs/property/property.blend \
    --python-exit-code 1 --python tools/build_house.py -- --swap --check
```
Expected: swap message, then checks pass with the post-swap `property`
count (48 + staged object count; `check_foundation` already branches on
`_greybox` existing).

- [ ] **Step 3: Re-render the six existing preview cams** — they live at the
scene level of `property.blend` (`cam_site`, `cam_intro`, `cam_backyard`,
`cam_kitchen`, `cam_road`, `cam_sidecorridor`). Reuse the `render_previews`
pattern on the main scene: set `scene.camera` to each in turn,
`bpy.ops.render.render(write_still=True)`, filepaths under
`<scratchpad>/house_renders/postswap/`, and do NOT save the blend
afterwards. Read all six: the new house should now be the only house, at
the greybox's exact station points, and `cam_kitchen`/`cam_backyard` should
show the casements, stoop, and BBQ relationship intact.
- [ ] **Step 4: Milestone commit:**

```bash
git add tools/build_house.py assets/envs/property/property.blend
git commit -m "feat: swap MCM house into property — greybox parked in _greybox"
```

---

### Task 11: The three prop leaves — guides registry, builders, `--add`

**Files:**
- Modify: `tools/guides.py` (three `GuideSpec` rows + `SCENERY`)
- Modify: `tools/guide_assets.py` (three builders)
- Modify: `tools/tests/test_guides.py:10-13`
- Data: `assets/props/props.blend` via `--add`

**Interfaces:**
- Consumes: `guide_assets.py` helpers `box(coll,name,cx,cy,cz,sx,sy,sz,color)` (CENTER-based, unlike build_house's corner-based `box`) and the `GuideSpec` dataclass.
- Produces: guides `screen_door` (h 2.0), `casement_leaf` (h 1.2), `back_door_leaf` (h 2.1), all in `SCENERY` (staging one must not make an empty shot "ready" — same reasoning as `clothesline`, `tools/guides.py:137-140`).

- [ ] **Step 1: `tools/guides.py`** — append to `GUIDES` (after `boy_aim`):

```python
    # House door/sash leaves. The property is linked at identity and cannot
    # change state per shot (the clothesline precedent) — so the openable
    # leaves are props, staged only in shots that need a state the baked
    # set doesn't show: the screen door's sq010 slap, a CLOSED kitchen
    # casement for sq050's through-the-glass beat, the back door open
    # behind Mom on the stoop. Authored CENTRED like every guide
    # (CENTRE_TOL forbids hinge-at-origin) — to swing one, parent the
    # instance to an Empty at the hinge edge and rotate the Empty.
    GuideSpec("screen_door", PROPS_FILE, "props", 2.0),
    GuideSpec("casement_leaf", PROPS_FILE, "props", 1.2),
    GuideSpec("back_door_leaf", PROPS_FILE, "props", 2.1),
```

and change `SCENERY`:

```python
SCENERY: frozenset[str] = frozenset(
    {"clothesline", "screen_door", "casement_leaf", "back_door_leaf"})
```

- [ ] **Step 2: `tools/tests/test_guides.py`** — counts 34→37 and 25→28:

```python
    def test_counts(self):
        self.assertEqual(len(guides.GUIDES), 37)
        self.assertEqual(len(guides.guides_for_file(guides.CAST_FILE)), 9)
        self.assertEqual(len(guides.guides_for_file(guides.PROPS_FILE)), 28)
```

- [ ] **Step 3: Run the registry tests** — `python3 -m pytest tools/tests/test_guides.py -q`. Expected: pass.

- [ ] **Step 4: `tools/guide_assets.py`** — three builders (near
`build_clothesline`; `box` here is center+size):

```python
def build_screen_door(c):
    """sq010_sh030's door-slap. Faces -Y, centred on X (CENTRE_TOL forbids
    hinge-at-origin) — swing it by parenting the instance to an Empty at
    the hinge edge (x -0.49 in guide space) and rotating the Empty."""
    w, h, t = 0.98, 2.00, 0.04
    box(c, "sd_stile_l", -(w / 2 - 0.045), 0, h / 2, 0.09, t, h, "wood")
    box(c, "sd_stile_r", (w / 2 - 0.045), 0, h / 2, 0.09, t, h, "wood")
    box(c, "sd_rail_top", 0, 0, h - 0.045, w - 0.18, t, 0.09, "wood")
    box(c, "sd_rail_mid", 0, 0, 0.75, w - 0.18, t, 0.09, "wood")
    box(c, "sd_rail_bot", 0, 0, 0.14, w - 0.18, t, 0.28, "wood")
    box(c, "sd_mesh_hi", 0, 0, (0.795 + h - 0.09) / 2,
        w - 0.18, 0.01, h - 0.09 - 0.795, "glass")
    box(c, "sd_mesh_lo", 0, 0, (0.28 + 0.705) / 2,
        w - 0.18, 0.01, 0.705 - 0.28, "glass")


def build_casement_leaf(c):
    """One kitchen-casement sash, matching the set's baked-open leaves
    (win_kitchen_*_sash*: 1.4 x 1.2, stiles 0.07). Staged closed-ish over
    the opening for sq050_sh035's through-the-glass beat."""
    w, h, r, t = 1.40, 1.20, 0.07, 0.05
    box(c, "cl_rail_bot", 0, 0, r / 2, w, t, r, "wood")
    box(c, "cl_rail_top", 0, 0, h - r / 2, w, t, r, "wood")
    box(c, "cl_stile_l", -(w - r) / 2, 0, h / 2, r, t, h, "wood")
    box(c, "cl_stile_r", (w - r) / 2, 0, h / 2, r, t, h, "wood")
    box(c, "cl_pane", 0, 0.005, h / 2, w - 2 * r, 0.026, h - 2 * r, "glass")


def build_back_door_leaf(c):
    """The half-glass back door, openable behind Mom on the stoop
    (sq060_sh012). Set's back_door is baked closed; this leaf overlays it
    open. 1.2 x 2.1 like the opening (z 0.45..2.55 world, feet-at-0 here)."""
    w, h = 1.20, 2.10
    box(c, "bd_slab", 0, 0, h / 2, w, 0.05, h, "wood")
    box(c, "bd_pane", 0, -0.028, 1.475, w - 0.20, 0.012, 0.75, "glass")
```

- [ ] **Step 5: Build-check headless** (no files written):

```bash
pgrep -f "Blender.app/Contents/MacOS/Blender"   # expect nothing
"$BLENDER" --background --factory-startup --python-exit-code 1 \
    --python tools/guide_assets.py -- --check
```
Expected: builds all guides to a temp dir, dimension asserts pass (heights
2.0 / 1.2 / 2.1 within tolerance, feet at z=0, centred).

- [ ] **Step 6: Add each guide to props.blend in place** (the sanctioned
non-destructive path — never `--force`):

```bash
"$BLENDER" --background --factory-startup --python-exit-code 1 \
    --python tools/guide_assets.py -- --add=screen_door
"$BLENDER" --background --factory-startup --python-exit-code 1 \
    --python tools/guide_assets.py -- --add=casement_leaf
"$BLENDER" --background --factory-startup --python-exit-code 1 \
    --python tools/guide_assets.py -- --add=back_door_leaf
```

- [ ] **Step 7: Commit**

```bash
git add tools/guides.py tools/guide_assets.py tools/tests/test_guides.py \
    assets/props/props.blend
git commit -m "feat: screen_door, casement_leaf, back_door_leaf prop guides (scenery)"
```

---

### Task 12: CHECKPOINT — layout-scene re-render check

**Files:**
- Create (scratchpad, NOT repo): `<scratchpad>/render_layout_checks.py`

- [ ] **Step 1: Write the read-only layout render script** (opens
`layout/layout.blend`, renders mid-frame of each checklist scene, never
saves — the spec's "What changes on screen" list, scene names use
underscores per `make_layout.py` convention):

```python
import sys
from pathlib import Path
import bpy

OUT = Path(sys.argv[sys.argv.index("--") + 1])
SCENES = [
    "sq010_sh010", "sq010_sh030", "sq010_sh045",
    "sq020_sh030", "sq020_sh040", "sq020_sh044",
    "sq040_sh020",
    "sq050_sh030", "sq050_sh035", "sq050_sh040",
    "sq060_sh012", "sq060_sh014",
    "sq070_sh010", "sq070_sh040", "sq070_sh050",
    "sq080_sh040",
]
OUT.mkdir(parents=True, exist_ok=True)
for name in SCENES:
    sc = bpy.data.scenes.get(name)
    if sc is None:
        print("MISSING SCENE:", name)
        continue
    sc.frame_set((sc.frame_start + sc.frame_end) // 2)
    sc.render.filepath = str(OUT / f"{name}.png")
    bpy.ops.render.render(write_still=True, scene=name)
    print("rendered", name)
```

- [ ] **Step 2: Run it** (read-only — it never saves, but keep Blender
closed anyway per the global rule):

```bash
"$BLENDER" --background layout/layout.blend --python-exit-code 1 \
    --python <scratchpad>/render_layout_checks.py \
    -- <scratchpad>/house_renders/layout_check
```
Missing scenes are reported, not fatal (not every checklist shot may have
a layout scene yet).

- [ ] **Step 3: Read every render.** What you are checking, per the spec:
openings still land where cameras expect (blocking framed against windows/
doors must still compose), the passthrough sightline in sq010_sh045, the
kitchen interior reads in sq050_sh040 (not black, gun-cabinet wall clear),
muzzle-flash window open in sq060_sh014's framing, and — the known,
deliberate change — the flat roofline in sq010_sh010 and sq070_sh010.
- [ ] **Step 4: Present the render grid to Ian.** The one likely decision:
whether sq010_sh010's sunrise wide wants a camera reframe against the
lower silhouette (camera-only change, made in `layout/layout.blend` by
hand later — NOT part of this plan, and layout.blend has uncommitted work).
**Do not proceed to Task 13 until Ian approves.** If something is broken
structurally, fix in `build_house.py`, `--revert`, `--rebuild`, `--swap`,
re-render, re-present.

---

### Task 13: Cleanup + docs

**Files:**
- Modify: `tools/build_house.py` (add `--purge-greybox`)
- Modify: `docs/treatment/site.md`
- Data: `assets/envs/property/property.blend`

- [ ] **Step 1: Add `--purge-greybox`** to `build_house.py` `__main__`:

```python
def purge_greybox():
    gb = bpy.data.collections.get(GREYBOX_COLL)
    if gb is None:
        sys.exit("no _greybox to purge")
    for ob in list(gb.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.collections.remove(gb)
    for _ in range(3):
        bpy.ops.outliner.orphans_purge(do_recursive=True)
    print("greybox purged")
```
(Keep the `house_modeling` scene and `house_v2`/`hv2_context` collections —
they are the workspace for future house edits, the `boy_modeling`
precedent.)

- [ ] **Step 2: Run it** (pgrep guard first):

```bash
"$BLENDER" --background assets/envs/property/property.blend \
    --python-exit-code 1 --python tools/build_house.py -- --purge-greybox --check
```
Expected: purge message + all checks pass. (`check_foundation` keys its
pre-swap branch on `house_wall_e` being absent from `property`, so the
purged file correctly takes the swapped branch — no check edits needed.)

- [ ] **Step 3: `docs/treatment/site.md` edits** — three exact replacements:

1. `"House 12×9 m, gable roof, front porch facing`
   → `"House 12×9 m, flat roof with deep fascia (see house.md), front porch facing`
2. `| House | x −7…5, y −4…5 | walls 3.2, ridge 5.2 |`
   → `| House | x −7…5, y −4…5 | walls 3.2, flat roof, fascia to 3.6 |`
3. `| Front porch | x −5…1, y −6.4…−4 | Mom's firing position, final shot |`
   → `| Front porch | x −5…1, y −6.4…−4 | the delivery lands here; sq010's door-slap and step-jump |`
   (the final-shot firing position moved mid-yard with the 2026-08-03
   west-sunset ending revision — sq080 has her centred in the backyard)

Also update the Status paragraph's "Not yet designed: architectural
character" sentence to point at `house.md` as designed/built.

- [ ] **Step 4: Final commits**

```bash
git add tools/build_house.py assets/envs/property/property.blend
git commit -m "feat: purge greybox house — the MCM build is the set now"
git add docs/treatment/site.md
git commit -m "docs: site.md catches up to the flat roof and the mid-yard finale"
```

---

## Self-review notes (already applied)

- Spec coverage: every spec section maps to a task — massing/roof (2-3),
  elevations/units (4), garage (5), porch/roofscape (6), interior (7),
  UV (8), state law/props (11), re-render check (10, 12), site.md stale
  notes (13). Material zones land in Task 1's `MATS` and are consumed
  everywhere. The spec's "keep greybox names on 1:1 replacements" is
  deliberately relaxed: the shell is no longer 1:1 (one hollowed box →
  four segmented walls), so names are descriptive instead; nothing in
  `tools/` resolves property internals by object name (verified: only the
  `property` collection name matters, plus `SCENERY`/guide names).
- The spec's "window units as in-file collections, instanced" became
  shared-mesh builders emitting plain objects: same shared-paint goal,
  zero risk to tools that dislike nested instancing inside the linked set.
- Checkpoint gates (9, 12) are where Ian's eyes are required; everything
  else is autonomous.
