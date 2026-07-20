# Scale guides for the animatic drawing binge — design

**Date:** 2026-07-20 · **Branch:** boards (phase 3) · **Status:** approved, ready to plan

## Problem

The 38 board scenes in `boards/boards.blend` are blank paper stages: a Grease
Pencil plane at the origin, a camera at `(0,-10,0)` looking `+Y`, a white paper
world. Before the animatic drawing binge we want recognisable, movable 3D
stand-ins for the cast and hero props to draw over, so every board has truthful
*relative scale* and composition. The greybox `property.blend` gives us the set
massing but only abstract markers for characters and props (a cylinder for
"boy", boxes for "figure_0..4", etc.) — not recognisable enough to draw from.

The guides are **throwaway tracing references**. They must be visible in the
viewport but must **never render** into a board — `conform_edit` builds the
animatic from GP strokes on a clean white page.

## Goals

- A small cast of recognisable-by-silhouette, correctly-scaled guides, linkable
  into any board scene and movable relative to the drawing plane.
- Guides never appear in a board render.
- Low-friction to place during a long drawing session.
- Regenerable, version-controlled, on-style with the existing script-driven
  greybox pipeline. Nothing hand-built that a script can own.

## Non-goals

- No rigging or animation. Guides are rigid; a distinct pose becomes a separate
  variant collection only if a shot needs it.
- No clay look, materials polish, or detail modelling. Silhouette only.
- Not the future `clay_library.blend` production-asset catalog — though this
  reuses the same Asset Browser mechanism and is a stepping stone toward it.
- No changes to how boards render or how `conform_edit` promotes them.

## Conventions (the load-bearing decisions)

**Units.** Every guide is modelled in real-world metres so relative scale is
honest. Boy ≈ 1.3 m, Mom ≈ 1.7 m, Sheriff ≈ 1.8 m; props to match.

**Facing.** The board camera sits at `(0,-10,0)` rotated `+90°` about X, looking
`+Y`; in the image, right = `+X`, up = `+Z`, into-screen = `+Y`. Every guide is
authored with its **front facing −Y** (toward camera), **feet at Z = 0**,
**centred on X = 0**. Dropped at the origin it therefore presents a clean
front elevation to draw over.

**Drawing-plane depth.** GP strokes land on the plane through the GP object
origin (Y = 0). Guides default to **Y = +1.5** — just *behind* the paper — so
strokes overlay the guide in the viewport.

**Render-hiding.** Guides live in a per-scene collection (named `<shotcode>_guides`
— Blender collection names are global, so the shot code disambiguates them; see
Components below) whose render toggle is off (`hide_render = True`). Visible in
the viewport, invisible to the render and therefore to `conform_edit`. The
collection is also set as the scene's **active collection**, so Asset-Browser
drops land in it by default.

## Architecture

Three linkable asset files. Each guide is one collection, marked as an asset and
assigned to a catalog. Catalogs are defined in a committed
`assets/blender_assets.cats.txt` with **hard-coded UUIDs** so regeneration never
churns the file.

| File | Collections (one asset each) | Catalog |
|------|------------------------------|---------|
| `assets/chars/cast.blend` *(new)* | `boy`, `mom`, `sheriff` | `guides/cast` |
| `assets/props/props.blend` *(new)* | `machine_gun`, `printer`, `action_figure`, `delivery_truck`, `cruiser`, `rosco`, `big_pistol`, `santa`, `scale_stick` | `guides/props` |
| `assets/envs/property/property.blend` *(exists)* | existing `property` collection, marked as an asset | `guides/set` |

The `scale_stick` is a 2 m pole ticked every 0.5 m — a bare height reference.
Marking the `property` set as an asset lets wide establishing boards (e.g.
sq010-sh010) drop in the whole house massing.

**One-time user setup:** register the project `assets/` folder as an asset
library in Blender Preferences. After that every guide appears in the Asset
Browser. Documented in `docs/boards.md`.

## Components

### 1. `tools/guide_assets.py` (new)

Builds `cast.blend` and `props.blend`, modelled on `blockout_property.py`:

- Primitive helpers (`box`, `cyl`, sphere) + a small palette.
- One builder function per guide; assembles stacked primitives into a
  recognisable silhouette (see recipes below). Applies the facing convention.
- Each guide goes in its own collection; the collection is `asset_mark()`-ed and
  its `asset_data.catalog_id` set to the right hard-coded catalog UUID.
- Writes/refreshes `assets/blender_assets.cats.txt`.
- `--force` guard: refuses to overwrite an existing (now hand-maintained) asset
  file without `--force`; `--out=<path>` builds a throwaway copy.
- `--previews=<dir>`: renders each guide from a board-style camera (front, `−Y`
  looking `+Y`) so silhouettes can be eyeballed.
- `--mark-property`: opens `property.blend`, marks its `property` collection as
  an asset in the `guides/set` catalog, saves. Separate path because
  `property.blend` is otherwise `--force`-guarded and hand-maintained.

**Silhouette recipes (primitive stacks):**
- `boy`: small sphere head, tapered box torso, stubby limb boxes; short.
- `mom`: adult torso, ring of small curler bumps on the head, apron wedge.
- `sheriff`: adult torso, brim disc + crown (hat), belly sphere.
- `machine_gun`: barrel cylinder + box receiver + magazine + stock.
- `printer`: open box frame + horizontal gantry bar.
- `action_figure`: blocky humanoid, human-sized (the firing-squad target).
- `delivery_truck`: body box + cab box + wheel cylinders.
- `cruiser`: sedan body + cab + wheels + rooftop lightbar.
- `rosco`: small handgun silhouette.
- `big_pistol`: comically oversized handgun.
- `santa`: cone hat + body + arms; a duct-tape stripe accent.
- `scale_stick`: 2 m pole with 0.5 m tick discs.

### 2. `tools/make_boards.py` (extend)

Add one heal case to the existing heal loop: for every board scene, ensure a
`guides` collection exists, `hide_render = True`, linked under the scene
collection, and set as the scene's active collection. Runs on the normal
(non-`--force`) path so all 38 existing scenes gain it without a rebuild, and
new shots get it at creation. Idempotent; counts toward the `healed` tally.

### 3. `tools/addons/redwood_guides.py` (new add-on)

A lightweight add-on the user enables once in Preferences. Adds an **"Add
Guide"** panel to the 3D-view N-panel (shown for board scenes):

- A dropdown of available guides (name → source file + collection).
- On invoke: links the chosen collection from its asset file (creating the
  library link on first use), creates a collection **instance** in the scene's
  `guides` collection at the default drop transform (origin, facing camera,
  Y = +1.5), and selects it for immediate positioning.
- Asset-Browser drag-drop remains the equivalent manual path; the add-on just
  makes it one click and guarantees the correct collection and facing.

### 4. Docs — `docs/boards.md` (new)

The guide workflow end to end: the one-time asset-library registration, enabling
the add-on, dropping and positioning guides, the `guides`-collection /
never-renders contract, and how to regenerate the asset files. Cross-linked from
`docs/treatment/site.md`.

## Data flow

```
guide_assets.py ──build──> cast.blend / props.blend   (collections marked as assets)
guide_assets.py --mark-property ──> property.blend     (property collection marked)
        │
        ├── assets/blender_assets.cats.txt (catalogs)
        ▼
Blender Asset Browser (assets/ registered as a library)
        │
   drag-drop  ── or ──  "Add Guide" add-on
        ▼
board scene `<shotcode>_guides` collection  (hide_render=True, active)
        │  artist positions instances, draws GP over them
        ▼
conform_edit  ── sees only GP strokes; guides never render ──> animatic
```

## Testing

`tools/tests/` currently holds pure-Python pytest modules. Add:

- **Headless Blender smoke test** (invoked via `$BLENDER`, guarded/skipped when
  Blender is absent): build the asset files to a temp path and assert — expected
  collections exist; each is marked as an asset with the right catalog; each
  guide's world-space bounds put feet at Z ≈ 0, centre at X ≈ 0, and overall
  height within tolerance of the target metres. Facing (front toward −Y) is
  verified by the rendered previews, not asserted — a symmetric bounding box
  can't reveal orientation.
- **`make_boards` guides-collection test**: after a run, every board scene has a
  `guides` collection with `hide_render == True`.
- **Rendered previews** (`--previews`) for the human eyeball check of
  recognisability — not an automated assertion.

## Risks / open questions

- **Recognisability is subjective.** Mitigated by `--previews` and cheap
  iteration — the script owns the geometry, so tweaks are fast.
- **Asset-library registration is a manual, per-machine Preferences step.**
  Documented; unavoidable with Blender's asset system. The add-on can detect and
  warn if the library isn't registered.
- **Poses.** Rigid guides may not suit every shot (e.g. boy aiming). Accepted:
  add a variant collection (`boy_aim`) on demand rather than rigging now.
- **Board camera lens/framing** is unchanged; the artist adjusts the per-scene
  camera as today. Guides are sized in true metres regardless.

## Deliverables checklist

- [ ] `tools/guide_assets.py` builds `cast.blend` + `props.blend`, marks/catalogs
      assets, writes cats file, `--force`/`--out`/`--previews`/`--mark-property`.
- [ ] `assets/blender_assets.cats.txt` committed with hard-coded UUIDs.
- [ ] `property` collection marked as an asset (`--mark-property`).
- [ ] `make_boards.py` `guides`-collection heal case.
- [ ] `tools/addons/redwood_guides.py` "Add Guide" add-on.
- [ ] Tests: asset smoke test + `make_boards` guides test.
- [ ] `docs/boards.md` workflow + setup, cross-linked from `site.md`.
