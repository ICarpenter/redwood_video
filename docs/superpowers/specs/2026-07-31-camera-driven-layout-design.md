# Camera-driven layout pipeline — design

**Date:** 2026-07-31
**Status:** Approved in brainstorming; pending user review of this spec.
**Supersedes:** the boards/shots split described in
`2026-07-19-redwood-video-pipeline-design.md` §3 and §5.

## Why

The current model pins the board camera at `(0, −10, 0)` and changes framing by
moving and rotating the **property instance** — `sq010_sh010` at rotZ −43.8°,
`sq010_sh030` at +90°, `sq010_sh045` at 180°. Three consequences:

1. **Blocking is worthless downstream.** A guide's transform describes a
   position in a picture, not a place on the property. `sq010_sh045` stages the
   boy at `(−0.80, 5.00, −1.22)` against a property spun 180° — those numbers
   mean nothing once the set stops moving.
2. **Continuity between shots is unreasonable.** Two shots of the same corner of
   the yard have no relationship a human or a script can see.
3. **The set is being animated to fake camera moves.** Verified 2026-07-31:
   `sq010_sh010`'s `property` instance and `sq010_sh045`'s `property.004` both
   carry Actions. Every staged camera and guide is keyframed too.

Meanwhile `shots/` is **empty** — no shot blend has ever been built — so the
shot-file layer is entirely theoretical and free to redefine.

## Decisions

| Decision | Choice |
|---|---|
| Property placement | Static at world origin, ground at `z = 0`, linked at identity, never transformed |
| Framing authority | The shot camera, exclusively |
| Grease Pencil | Optional per-shot overlay on top of 3D blocking, not a replacement for it |
| Blocking space | World space, on the property |
| Shot continuity | Snapshot copy-forward (explicit operation), not a shared timeline |
| Shot .blend files | Derived export, on demand — never a mandatory stage |
| Existing blocking + animation | Discarded, not migrated (user decision: "those took zero effort") |
| Naming | `boards` → `layout` across files, tools, and docs |

## Invariants

Every tool enforces these; every doc states them.

1. **The property never moves.** Linked at identity — location `(0,0,0)`,
   rotation `0`, scale `1`. Ground is `z = 0`.
2. **The camera is the only framing authority.** A different angle means a
   different camera, never a different set position.
3. **Blocking is world-space.** A guide's transform says where that character
   stands on the property.
4. **Shot files are a derived export, not a stage.** Nothing is required to
   pass through `shots/`.

Invariant 1 is what makes copy-forward a plain world-matrix copy between
scenes: both scenes share a world origin, so no transform math is involved.

## Topology

One layout file, `layout/layout.blend`, holds one scene per `docs/shotlist.csv`
row. The property links in once and is shared by all 39 scenes.

`shots/` stays in the tree, starts empty, and fills only when a shot earns its
own file.

### Why not per-shot files

Per-shot files save no memory: linked datablocks are shared, so 39 scenes
referencing one property cost one property in RAM plus a few empties per scene,
and Blender evaluates only the active scene's depsgraph — viewport speed is
governed by the shot you are looking at, not the file's scene count.

The real costs of a single file are git-LFS churn (a full binary re-serialize
per save of one growing file), corruption blast radius, and no parallel
headless renders without each process loading everything. All three are late
problems. If churn becomes painful, splitting to one file per sequence is a
cheap later migration that this design does not foreclose.

## Scene anatomy

Each scene is named by shot code (`sq010_sh010`) and holds:

| Element | Notes |
|---|---|
| `<code>_cam` | The shot camera. Keyable within the shot. Carries all framing. |
| `<code>_blocking` | Linked collection instances of cast/props at current fidelity, positioned in world space. Grows from greybox guides into real assets without changing shape. |
| the property | Linked at identity, shared across all scenes. |
| `<code>_paper` | GP object parented to `<code>_cam`, parked just past the near clip and sized to the frustum for that camera's lens. Screen-space stroke thickness. |
| `<code>_note` | Existing text label, also camera-parented. |

Frame range comes from the shotlist row; the track sits on the scene sequencer
for scrubbing; render settings come from **one shared function** so the layout
file and `tools/shot_template.blend` cannot drift.

### Paper depth

The paper must render in front of everything, including close foreground
objects. The mechanism is geometric rather than flag-based: park it just past
`clip_start` (~0.11 m at the default 0.1) and size it to the frustum there.
Nothing can be in front of it without being clipped. Screen-space stroke
thickness means an 11 cm plane draws and reads identically to a 10 m one.

**Verify in Blender before building on it.** If near-field drawing feels bad in
practice, the fallback is rendering the GP on its own view layer composited
over — which also frees the paper from near-field placement.

### Visibility rule (inverted)

Today guides render until a board has strokes, then auto-hide: the drawing
*replaces* the blockout. Grease Pencil is now an overlay, so:

**Blocking and paper both render, always.** A scribble reads on top of blocked
3D. Shots taken fully 2D set `scene["hide_blocking"] = True` — a scene custom
property, read by `layoutlib` and applied to the `<code>_blocking` collection's
`hide_render`. Absent means false. It is set by hand, per shot, and no tool
ever writes it; that is what makes it different from the automatic rule it
replaces.

Three things fall out:

- `boardlib.sync_guide_visibility` is deleted, and with it the "re-run
  `make_boards.py` after every drawing session or the edit lies" footgun.
- The "guides at negative Y occlude your strokes, use X-ray" caveat disappears —
  the paper is camera-locked in front.
- `conform_edit`'s tiers simplify to: render → layout scene (has blocking *or*
  strokes) → slug.

### Seed cameras

`property.blend` already carries `cam_site`, `cam_intro`, `cam_backyard`,
`cam_kitchen`, `cam_road`, `cam_sidecorridor`. Under a camera-driven model these
stop being previews and become seed cameras: a shot camera can be initialized
from a named one.

## Toolchain

### New

| Tool | Behaviour |
|---|---|
| `continue_shot.py` | Copy-forward. `--from sq010_sh040 --to sq010_sh045 [--at-frame N]`; default frame is the source's `frame_end`. Copies the source camera and every blocking world matrix into the destination. Creates missing instances; leaves existing ones alone without `--force`. |
| `export_shot.py` | Was `new_shot.py`. Layout scene → `shots/sqXXX/shXXX/shXXX.blend` with camera, blocking, property link, track, and project settings. One-way, on demand. |
| `migrate_layout.py` | One-shot reset (below). |

`continue_shot.py` must handle the documented `matrix_world`-is-identity-in-
`--background` trap: `frame_set` then `evaluated_get(depsgraph)` before reading
any matrix.

### Renamed / changed

| Now | Becomes |
|---|---|
| `boards/boards.blend` | `layout/layout.blend` |
| `<code>_guides` collection | `<code>_blocking` |
| `tools/boardlib.py` | `tools/layoutlib.py` |
| `tools/make_boards.py` | `tools/make_layout.py` |
| `tools/stage_boards.py` | `tools/stage_shots.py` |
| `tools/resync_boards.py` | `tools/resync_layout.py` |
| `docs/boards.md` | `docs/layout.md` |

- **`layoutlib.py`** gains `apply_project_settings`, `fit_paper`,
  `parent_paper_to_camera`; renames `guides_collection` → `blocking_collection`,
  `guide_instances` → `blocking_instances`, `board_ready` → `shot_ready`; loses
  `sync_guide_visibility`.
- **`make_layout.py`** builds each scene per the anatomy above. Still additive
  and healing; `--force` still destroys.
- **`stage_shots.py`** `STAGING` gains a camera per shot (explicit transform or
  `from=<seed camera>`); blocking positions become world-space. Still additive —
  never touches an element that already exists.
- **`resync_layout.py`** unchanged in behaviour.
- **`conform_edit.py`** points at `layout/layout.blend`; tiers simplified.
- **`make_template.py`** delegates settings to the shared function.
- **`guides.py`** `guides_collection_name` → `blocking_collection_name`.
- **`redwood_guides.py` add-on** targets `<code>_blocking`, and Add Guide
  raycasts the camera's view direction to `z = 0` and drops there — feet on the
  ground at a real place on the property, instead of `(0, 1.5, 0)` "just behind
  the paper."

### Deleted

- **`stage_property.py`** and the `blocking` collection it owns inside
  `property.blend` (15 objects). It exists only because boards could not hold
  real blocking, so it built a sandbox in the property file instead. Layout
  scenes now do that natively. Also removes one of the four documented
  work-destroying tools.
- **`build_shots.py`** and `tools/tests/test_build_shots.py`. Batch-stamping 39
  empty shot files is exactly the stage this design makes optional.
- **`boardlib.sync_guide_visibility`**.

### Staleness honesty

Once a shot is exported and animated, its layout scene is stale and
`conform_edit` would keep cutting the old blocking. `export_shot.py` stamps
`exported = True` on the layout scene and `conform_edit` reports it. No
behaviour change — just no silent lying about what you are watching.

## Migration

Existing blocking and animation are **discarded**, by decision. Migration is a
reset, not a conversion.

`migrate_layout.py`:

1. `git mv boards/boards.blend layout/layout.blend` (LFS path move).
2. Per scene: delete every instance object, clear every object Action, rename
   `<code>_guides` → `<code>_blocking`, link the property at identity, parent
   the GP and `_note` to `<code>_cam`, fit the paper to the near field, and
   reset the camera by seeding it from `cam_intro` in `property.blend` (an
   existing preview camera — no invented default numbers).
3. Re-stage fresh through `stage_shots.py`.

Two things survive because they are free:

- **`sq010_sh010`'s 119 strokes.** GP data is never touched by any step above.
- **That shot's camera**, solved once and statically as `M(1)⁻¹ · C(1)` with
  `mathutils` — one matrix multiply, no baking — so the only drawn shot in the
  film keeps 3D standing behind its drawing at the angle it was drawn for.

Expected breakage: `edit/edit.blend` holds scene strips pointing at
`boards/boards.blend`. The path move breaks them; regenerate with
`conform_edit.py -- --force`, the sanctioned recovery path.

## Testing

Blender smoke tests carry the real coverage, because every claim worth checking
is about Blender state:

- Migration leaves `sq010_sh010` with 119 strokes, zero instance objects in any
  scene, and the GP parented to its camera.
- The near-field paper renders strokes over geometry placed close to camera.
  (This is also the verification gate for the paper-depth mechanism.)
- `continue_shot` round-trip: copy A→B at frame F, then assert B's blocking
  world matrices equal A's evaluated matrices at F.
- `export_shot` produces a file that opens with its camera, blocking, and frame
  range intact.

Under system Python, `test_layoutlib.py` covers `shot_ready` and collection
naming. `test_guides.py` keeps its 13-guide counts but needs updating for the
renamed `blocking_collection_name` (asserted at `test_collection_name`) and the
changed drop location. `test_build_shots.py` is deleted with its tool.

## The `assets` column

`docs/shotlist.csv` rows `sq010_sh040` and `sq010_sh045` carry
`assets = boy;box`, which `new_shot.py` resolves to `assets/boy/boy.blend` and
silently warns-and-skips. The convention never fit the guide files anyway:
`pipeline.md` promises `<kind>/<name>/<name>.blend` exposing one collection
named `<name>`, but `cast.blend` and `props.blend` each hold many collections
(`boy`, `mom`, `sheriff`; `box`, `cruiser`, …) and no collection named `cast` or
`props`.

Resolution: **the column becomes planning metadata and stops driving linking.**
Blocking in the layout scene is authoritative — `export_shot.py` exports what
the scene actually contains and never reads this column. Values are guide names
from the `guides.py` registry, validated by `shotlib.read_shotlist` so a typo
fails loudly instead of warning into the void. `boy;box` is then already
correct, and the silent-skip path is gone rather than papered over.

## Out of scope

- Per-sequence file splitting. Deferred; this design does not foreclose it.
- Look development, clay materials, lighting. The layout world only needs to
  show greybox legibly.
- Any change to `docs/shotlist.csv` as source of truth, the song-global frame
  convention, or the Standard-view-transform rule in the edit.
