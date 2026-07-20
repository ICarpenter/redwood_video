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

**Drag-drop caveat:** the **Add Guide** button always targets the correct
`<shotcode>_guides` collection, but Asset-Browser drag-drop lands wherever the
*active* collection is — if you've clicked into a rendering collection, a
dragged instance can end up there too, so prefer the button (or re-select the
guides collection before dragging).
