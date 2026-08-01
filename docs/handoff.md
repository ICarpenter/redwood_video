# redwood_video — handoff

State of the project for anyone (or any future session) picking it up cold.
Written 2026-07-20, updated 2026-07-31.

## What this is

An animated music video for **`guns`** (`audio/track/guns.wav` — 4:15,
141 BPM, 150 bars), produced end-to-end in Blender 5.1.2 with a stylized
**claymation** look: bright colors, white-trash Americana, Spike & Mike
energy. A heartland kid 3D-prints a machine gun, and by sundown has
dragged his mom and the county sheriff into a three-way backyard war.
39 shots. Solo production.

Read next, in order: `treatment/story.md` (what happens),
`treatment/script.md` (shot by shot, frame-locked), `treatment/site.md`
(where everything is), `pipeline.md` (conventions), `tools.md` (the
machinery), `layout.md` (the layout & drawing workflow).

## Where we are

| Phase | Status |
|-------|--------|
| 1. Ideation | done |
| 2. Writing — story, script, lyrics, sections | done |
| 3. Layout / animatic | **in progress** — infrastructure done; 1 shot drawn, 4 blocked out in world space |
| 4. Asset production | started — property blockout + 13 scale guides + garage passthrough |
| 5–9. Animation → delivery | not started (pipeline built and validated end-to-end) |

The film is **watchable right now**: `edit/edit.blend` holds the track,
9 section markers, 5 layout strips and 34 slugs. It upgrades in place as
blocking, drawings, and renders land.

Layout state today:

| Shot | State |
|------|-------|
| sq010_sh010 | drawn (119 strokes) — camera solved statically from the old fixed-camera framing |
| sq010_sh020 | blocked out (camera + box — the package has landed, the truck's already gone) |
| sq010_sh030 | blocked out (camera + boy + box, at the screen door) |
| sq010_sh040 | blocked out (camera + boy + box, dragging up the driveway) |
| sq010_sh045 | blocked out (camera + boy + box, reverse through the garage passthrough) |
| the other 34 | empty layout scenes — slug tier in the edit |

## Nine conventions that will bite you if you forget them

**The layout model — this refactor's four invariants:**

1. **The property never moves.** It is linked at identity — world origin,
   ground at `z=0` — in every layout scene.
2. **The camera is the only framing authority.** A different angle means a
   different camera, never a moved or rotated set.
3. **Blocking is world-space.** A guide's transform says where that
   character actually stands on the property.
4. **Shot files are a derived export, not a stage.** Nothing is required to
   pass through `shots/`.

**Everything else:**

5. **Timeline: frame 1 = song time 0, 24 fps.** Every shot's frame range
   is song-global, so a shot's keyframes and its strip position are the
   same numbers. The song ends dead on the last chorus hit at **bar 111 /
   frame 4534**; frames 4535+ are audio tail only (shots currently run to
   4780, into the tail).
6. **Bars are counted from 0** in `sections.csv` and the treatment docs
   (matching how the song structure was written). `beatmap.csv`'s bar
   column is 1-indexed — its bar 1 is our bar 0. Concretely: script bar 10
   is beatmap bar 11 is frame 410. Get this backwards and cuts land a bar
   off.
7. **`docs/shotlist.csv` is the source of truth.** Tools read it; nothing
   invents structure. Render boundaries come from it *at render time*, so
   retiming a row re-renders correctly without recreating the shot file.
   It is **unquoted CSV — never put a comma in a description**, or the
   columns shift and `read_shotlist` dies on `int()`. The `assets` column
   is semicolon-separated for exactly this reason.
8. **Link, never append.** Single-asset files (a character/prop built as a
   full asset) live at `assets/<kind>/<name>/<name>.blend`, one root
   collection named `<name>` — `property.blend` is the working example.
   Guide libraries are the deliberate exception: `cast.blend`/`props.blend`
   each hold many catalogued collections, one per guide, none matching the
   filename — built by `guide_assets.py`, registered in `guides.py`, and
   never resolved by path (the shotlist's `assets` column names guides,
   validated against the registry; `export_shot.py` never reads it).
   Animate linked rigs via library overrides.
9. **The edit uses the Standard view transform, not AgX.** Shot renders
   already have AgX baked in; applying it again in the edit washes
   everything out (measured: 25 dB PSNR vs 102 dB when passed through).

Plus the compass, from `treatment/site.md`: **+Y = backyard, −Y = road,
sun rises east, sets west** — the final sprint runs west into the sunset,
mirroring the sunrise.

## Shot numbering

Shots step by tens (`010, 020, …`) so a cut can be inserted without
renumbering. `sq010_sh045` is the first use of that gap — the garage beat
split into a drag and a reverse. **Insert, don't renumber**: renaming a
layout scene orphans its drawings, notes, and blocking collection. The `sh`
field only has to be 3 digits.

## Layout scenes, and how blocking reaches the edit

Every layout scene owns a `<shotcode>_blocking` collection holding linked
world-space instances of cast/prop guides, plus a Grease Pencil "paper"
parented to the camera for drawing over it. **Both render by default,
always** — blocking is an overlay under a drawing, not something the
drawing replaces.

There is no automatic visibility rule left to re-sync. A shot that must go
fully 2D opts out by hand: `scene["hide_blocking"] = True`. **No tool ever
writes this flag** — that is exactly what distinguishes it from the
automatic rule it replaced.

`conform_edit` cuts in any layout scene with strokes **or** blocking, so
the tiers are: render → layout → slug.

Nothing occludes a stroke, at any distance: Grease Pencil composites over
mesh geometry in EEVEE unconditionally (see the gotchas below) — there is
no X-ray caveat to remember any more.

This replaced the old fixed-camera board model: boards used to pin the
camera at `(0, −10, 0)` and change framing by moving and rotating the
*property instance* — sh010 sat at rotZ −43.8°, sh030 at +90°, sh045 at
180° — and had begun keyframing that instance to fake camera moves
(`sq010_sh010` and `sq010_sh045` both carried Actions on it). That is
exactly why blocking used to be worthless downstream: nothing about a
board's framing said anything about where a character stood in the world.
`tools/migrate_layout.py`'s docstring has the mechanics of the one-time
reset off that model, including how `sq010_sh010`'s camera was solved to
reproduce its old framing statically so the 119 strokes already drawn
still line up.

## Blender 5.1.2 gotchas already paid for

- **Storypencil does not work on Blender 5.x** (upstream rewrite pending).
  Layout scenes are plain camera + Grease Pencil scenes; our conform does
  the assembly.
- `SequenceEditor.sequences` → **`.strips`** (use a `hasattr` fallback).
- `strips.new_effect()` takes **`length=`**, not `frame_end=`.
- `action.fcurves` is **gone** — actions are slotted. Note that
  `strip.channelbags` is a *collection* while `strip.channelbag(slot)` is
  a *function*; calling the former explodes with "not callable".
- **`matrix_world` is stale in `--background` until the scene is
  evaluated. `.location` and other RNA properties (rotation, scale, a
  camera's `.data.lens`) are always live**, no evaluation required — read
  those instead of `matrix_world` when you don't actually need a
  depsgraph. Two follow-on traps, both paid for the hard way this
  refactor:
  - **`scene.view_layers[0].depsgraph` is `None`** until something
    evaluates that scene, and **`scene.frame_set()` is what builds it.**
    A scene that has never had `frame_set()` (or an equivalent) called on
    it has no depsgraph to evaluate anything through yet.
  - **`bpy.context.evaluated_depsgraph_get()` returns the CONTEXT scene's
    depsgraph — not the scene you're holding a reference to.** Evaluating
    another scene's objects through it returns **identity, silently, with
    no error.** This is what planted a camera at the world origin during
    the `migrate_layout.py` migration (the context scene at file-open was
    never the scene being solved) and it passed every check until someone
    printed the value. Always fetch the *target* scene's own
    `scene.view_layers[0].depsgraph` (after calling `frame_set()` on that
    scene), never `bpy.context`'s.
- **Grease Pencil composites over mesh geometry in EEVEE
  unconditionally** — independent of distance and of `stroke_depth_order`
  (measured: identical ink pixels at 0.11 m in front of an occluder and
  10 m behind it, under both depth-order modes). Paper distance is
  therefore a framing choice, not an occlusion trick:
  `PAPER_DISTANCE = 10.0` gives a scale of exactly 1.0 at a 50 mm lens,
  matching `sq010_sh010`'s existing strokes 1:1.
- **Edits to linked datablocks do not persist.** Setting `hide_render` on
  a linked collection works in memory and reverts to the library value on
  reopen. Anything that must survive has to be written in the source file.
- Scenes created through the data API have **no world** → black viewport
  and black renders. Assign one.
- Viewport shading defaults to **Theme** background (grey) — set
  *Background → World* per viewport to see the layout scene's world.
- Aim cameras with `direction.to_track_quat("-Z", "Y")`; hand-rolled Euler
  math gets the yaw sign wrong.
- EEVEE's engine id here is `BLENDER_EEVEE` (not `_NEXT`) — pick from the
  enum rather than hardcoding.

## The toolchain

Everything is stdlib-only Python + bash, driven by the shotlist. Blender
is found via `$BLENDER`, defaulting to
`/Applications/Blender.app/Contents/MacOS/Blender`.

| Tool | What it does |
|------|--------------|
| `shotlib.py` | shared, bpy-free: validated shotlist/sections parsing, beat math, paths, versions, track/Blender discovery |
| `guides.py` | shared, bpy-free: declarative scale-guide registry (specs, catalogs, blocking-collection naming, drop distance) |
| `layoutlib.py` | shared, bpy-aware: stroke/blocking detection, the blocking collection, the `hide_blocking` opt-out, shared project settings, paper fitting |
| `beatmap.py` | BPM + length → `docs/beatmap.csv` (bar/beat → frame) |
| `make_template.py` | builds `shot_template.blend` (1080p24, EEVEE, AgX, PNG 16-bit) — the settings reference; no longer opened directly to create anything |
| `make_layout.py` | seeds `layout/layout.blend` — one camera-driven scene per shot; reruns add new rows and heal world/settings/blocking-collection/property-identity/paper/note drift |
| `resync_layout.py` | shotlist → existing layout scene frame ranges (the gap make_layout leaves, since it only adds) |
| `stage_shots.py` | declarative starting cameras + world-space blocking — **additive**, never resets framing set by hand |
| `continue_shot.py` | copies a shot's camera + blocking forward into another scene, as a one-time world-matrix snapshot |
| `guide_assets.py` | builds `cast.blend` / `props.blend`; `--add=<name>` appends one guide non-destructively |
| `blockout_property.py` | rebuilds the greybox property + preview cameras (the static set only — no cast/props) |
| `export_shot.py` | exports one layout scene to `shots/sqXXX/shXXX/shXXX.blend`, on demand — one-way |
| `migrate_layout.py` | **spent, one-shot.** Reset the old boards model into the layout model. Already run, once. Do not run again |
| `render_shot.sh` | headless render → `render/<code>/vNNN/`, auto-incrementing |
| `conform_edit.py` | rebuilds `edit/edit.blend`: track + markers + best tier per shot |
| `encode_delivery.sh` | ProRes HQ master + H.264 into `delivery/` |

Tests: `python3 -m unittest discover -s tools/tests -t tools/tests` (45
passing). Note the `-t` — `tools/tests` has no `__init__.py`, so plain
discovery from the repo root fails with "Start directory is not importable".

### Which tools destroy work

| Tool | Behaviour |
|------|-----------|
| `make_layout.py` | **safe** — adds and heals only. `--force` rebuilds and destroys all drawing and blocking |
| `stage_shots.py` | **safe** — leaves existing framing and blocking untouched, idempotent |
| `resync_layout.py` | **safe** — frame ranges only, idempotent |
| `continue_shot.py` | **safe** — skips a destination blocking instance already present unless `--force` |
| `export_shot.py` | **safe** — refuses to overwrite an existing shot file unless `--force` |
| `guide_assets.py --add=` | **safe** — appends one collection, refuses if it already exists |
| `guide_assets.py` (default) | wipes and rebuilds cast+props; guarded, needs `--force` |
| `blockout_property.py` | wipes and rebuilds property.blend; guarded, needs `--force`. Also destroys the asset mark — re-run `--mark-property` after. (property.blend has no `blocking` collection any more — per-shot blocking now lives in `layout.blend`.) |
| `migrate_layout.py` | **HAZARD — do not run.** It is a spent one-shot script with **no re-run guard**. Its per-object loop deletes every object carrying an `instance_collection`, which today means *all* staged world-space blocking across all 39 scenes, in every shot. Only its docstring's "Run ONCE" stands between it and destroying every bit of blocking staged since the migration it performed. It has already been run once, against the pre-migration file, and that is the only time it should ever run. |
| `conform_edit.py` | **destroys** `edit/edit.blend`; guarded, needs `--force` |

**Close Blender before running any of these.** They write `.blend` files
headlessly; an open session's later save will clobber the result.

Regenerable and gitignored: `render/`, `delivery/`, playblasts,
`edit/proxies/`.

**`edit/edit.blend` is tracked in LFS**, decided 2026-07-31. It is
regenerable (`conform_edit.py -- --force`), but committing it means the
current cut is reviewable in a PR and watchable without a Blender run.
The cost: it is a binary that re-serializes on every save, so expect
diffs with no semantic change, and never merge two branches that both
touched it — regenerate instead.

## Repo state

- Everything through PR #9 (`property-passthrough`: garage passthrough,
  `edit/edit.blend` tracked in LFS, first 5 shots blocked out) is merged.
  `main` is current.
- This branch, `camera-driven-layout`, implements the refactor this doc
  describes — property static at the origin, camera as the sole framing
  authority, blocking in world space, shot files an on-demand export — and
  has not yet been opened as a PR.
- Merged branches that can be deleted: `scaffold`, `track-and-beatmap`,
  `ideation`, `boards`, `envs`, `boards-guide-blockout`,
  `property-passthrough`. `board-sunrise` is kept deliberately — see "PRs
  so far" below.

## The garage passthrough

The garage opening is a **boolean**, not modelled geometry. `garage`
carries a `BOOLEAN DIFFERENCE` targeting `garage_door_rcutter`, which
punches front-to-back through the shell (y −3.58..+3.56) to make the
passthrough sq010_sh045 shoots along.

Two things keep it from leaking into shots:

- the cutter lives in a **`cutters` collection at scene root, deliberately
  outside `property`** — so linking the `property` set never drags it in
- it is `hide_render = True` at both object and collection level

It still resolves through the link: Blender pulls the modifier target in
as an *indirect* dependency, so `garage` evaluates 8 → 17 verts in
layout.blend exactly as it does in property.blend. Verified — but it is a
non-obvious dependency, so if the passthrough ever closes up in a layout
scene, check that `garage_door_rcutter` still came along.

Both garage doors are modelled **open** — retracted horizontal panels at
z 2.35..2.45, not slabs filling the opening.

## Open decisions

- **Backyard scale.** Currently ~22 m deep. Generous — good for
  firing-squad wides, but the three-way firefight may play funnier
  cramped. Cheap to change now, expensive after layout begins.
- **Front yard depth** — governs how long the cruiser is on screen before
  the tire blows.
- **Drawing fidelity** — one held drawing per shot, or 2–3 poses for the
  action beats. The blocking tier takes some pressure off this: a beat can
  read in the edit before it is drawn at all.
- **Verse 2 gag density** — the script flags it as the hottest section
  with an explicit cut-first order (hubcap skeet → package football →
  flowerbed arm). The animatic arbitrates; don't cut on taste beforehand.
- **Production design** — nothing designed yet beyond massing: siding,
  porch clutter, junk, terrain, and the clay look itself.

## Next actions

1. **Keep blocking out story beats.** Add a row to `STAGING` in
   `stage_shots.py` per shot, drop guides by hand with Sidebar ▸ Redwood ▸
   Add Guide, or carry a beat forward with `continue_shot.py`. Conform and
   watch — beats read before anything is drawn.
2. **Draw the film.** A rough scribble pass over all 39 layout scenes
   first, polish later — blocking and drawing both render together,
   always, so there is nothing to re-run afterward.
3. **Arbitrate verse 2** with the animatic, then firm durations and move
   statuses `scripted → boarded` (all 39 rows are still `scripted`).
4. **Design pass on the property** once the layout says what the camera
   actually needs.
5. Then asset production proper: clay material library, characters.

## Working notes

- The Blender MCP bridge is live on `127.0.0.1:9876` (configured in
  `~/blender/.mcp.json`, *not* in this repo — a session started from the
  project root will not have the tool unless it is added). It can inspect
  and fix the *open* Blender file directly, which is the right way to
  touch a file the artist has open. Note `bpy.data.is_dirty` is **not**
  set by script-driven RNA writes, so Blender may not prompt to save on
  quit — save explicitly after a bridge edit.
- Guides are authored in real metres, facing −Y, feet at Z=0, centred on
  X=0, and are dimension-checked on build (`guide_assets.py -- --check`).
  Adding one is: a `GuideSpec` in `guides.py`, a builder in
  `guide_assets.py`, run `--add=<name>`, then bump the counts in
  `tools/tests/test_guides.py` (they are hard-coded and will fail).
- GitHub LFS carries `.blend`, audio, images, video. GitHub's LFS
  endpoint has thrown 502s during incidents — retry rather than
  re-architect. Lock verification is disabled (solo repo).
- PRs so far: scaffold (#1), track+beatmap (#2), story/script (#3),
  boards infrastructure (#4), env blockout + scale guides (#6, #7),
  guide-blockout tier (#8), garage passthrough + edit LFS (#9). PR #5 (a
  test sunrise board) was scrapped — the strokes survive on the
  `board-sunrise` branch if ever wanted.
