# Layout & drawing guides

`layout/layout.blend` holds one camera-driven scene per shotlist row, built
by `tools/make_layout.py`. Every scene rests on four invariants:

1. **The property never moves.** It is linked at identity (world origin,
   ground at `z=0`) in every scene.
2. **The camera is the only framing authority.** A different angle means a
   different camera transform in that scene, never a moved or rotated set.
3. **Blocking is world-space.** A guide's transform says where that
   character or prop actually stands on the property — not where it looks
   good from one particular lens.
4. **Shot files are a derived export, not a stage.** A layout scene already
   carries everything a shot needs (camera, blocking, the linked property,
   the frame range). Nothing is required to pass through `shots/`; see
   `tools/export_shot.py` in `tools.md` for when a shot earns its own file.

A shot graduates into the edit once it has real Grease Pencil strokes **or**
world-space blocking — see `conform_edit` in `pipeline.md`.

## Scale guides

Recognisable, correctly-scaled 3D stand-ins for the cast and hero props, to
block out a shot or draw over. They give truthful relative scale and
composition.

- **Cast** (`assets/chars/cast.blend`): `boy`, `mom`, `sheriff`.
- **Props** (`assets/props/props.blend`): `machine_gun`, `printer`,
  `action_figure`, `delivery_truck`, `cruiser`, `rosco`, `big_pistol`, `santa`,
  `box`, `scale_stick`.
- **Set** (`assets/envs/property/property.blend`): the whole `property`
  massing. It is linked at identity in every layout scene already
  (invariant 1) — it is not a guide you drop; see below.

All are catalogued Assets (`guides/cast`, `guides/props`, `guides/set`) via
`assets/blender_assets.cats.txt`. Regenerate cast/props with
`tools/guide_assets.py` (see `tools.md`).

### One-time setup

1. **Asset library:** Preferences ▸ File Paths ▸ Asset Libraries → add the
   project `assets/` folder. Every guide now shows in the Asset Browser.
2. **Add-on:** Preferences ▸ Add-ons ▸ Install → `tools/addons/redwood_guides.py`
   → enable **Redwood Guides**.

### Blocking with guides

Each layout scene owns a collection `<shotcode>_blocking` (created by
`make_layout.py`, and set as the active collection so drops land there).

- **Add a guide:** Sidebar (N) ▸ **Redwood** ▸ Add Guide → pick one → it drops
  onto the ground **where the camera is looking**: the camera's view ray is
  cast onto the property's `z = 0` ground plane, feet at `z = 0`. If the
  camera is level or tilted up (the ray never meets the ground), it falls
  back to a fixed distance along the view ray, flattened to `z = 0`. Or drag
  it from the Asset Browser (it lands in the active blocking collection as a
  *linked* instance).
- **Position it:** the drop is a starting point — move/rotate as needed.
  These are world-space positions on the property, not camera-relative: a
  guide's transform says where that character actually stands. Guides are
  rigid; if you need a distinct pose (e.g. the boy aiming), ask for a
  variant collection rather than trying to deform the instance.
- **The property never moves.** It is already linked at identity in every
  layout scene (invariant 1), so it is not in the Add Guide dropdown and
  must never be instanced or transformed again — the Add Guide operator
  refuses it outright. To frame a wide establishing shot, pull the
  **camera** back instead: the camera is the only framing authority
  (invariant 2).
- **Rendering is not automatic.** Blocking and any Grease Pencil paper both
  render, always — the drawing is an overlay on top of blocked 3D, not a
  replacement for it. There is no tool-owned visibility rule left to
  re-sync. A shot that must go fully 2D opts out by hand:
  `scene["hide_blocking"] = True`. **No tool ever writes this** — it is a
  deliberate, hand-set per-scene flag, and is the only thing that turns
  blocking off.
- **Nothing occludes strokes.** Grease Pencil composites over mesh geometry
  in EEVEE unconditionally, regardless of distance or `stroke_depth_order`
  (measured: identical ink pixels at 0.11 m in front of an occluder and 10 m
  behind it). There is no X-ray caveat to remember — draw over blocking at
  any distance and the ink always wins.

This makes a guide blockout a real tier in the edit, between a slug and a
drawing: `conform_edit` cuts in any layout scene that has strokes **or**
blocking, so major story beats are watchable before a line is drawn.

### Continuing a shot

`tools/continue_shot.py --from <code> --to <code>` copies the source shot's
camera and blocking forward as a world-matrix snapshot (the property is
linked at identity in every scene, so both scenes share one world origin —
no relative-space conversion needed). It's a one-time copy, not a live link:
re-blocking the source afterwards never disturbs the destination. See
`tools.md` for flags (`--at-frame`, `--force`, `--dry-run`).

**Drag-drop caveat:** the **Add Guide** button always targets the correct
`<shotcode>_blocking` collection, but Asset-Browser drag-drop lands wherever
the *active* collection is — if you've clicked into a rendering collection, a
dragged instance can end up there too, so prefer the button (or re-select the
blocking collection before dragging). **Never drag in `property`:** it is
still a catalogued Asset (`guides/set`), so the browser keeps offering it,
but the Add Guide button's refusal cannot reach drag-drop. A dragged copy
instances the set a second time at a non-identity transform — indistinguishable
from ordinary blocking, so it survives every `make_layout` heal forever and
gets copied forward by `continue_shot` and baked by `export_shot`. The
property is already linked at identity in every layout scene; to frame
wider, move the **camera** instead (invariant 2).
