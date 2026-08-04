# redwood_video — handoff

State of the project for anyone (or any future session) picking it up cold.
Written 2026-07-20, updated 2026-08-03.

## What this is

An animated music video for **`guns`** (`audio/track/guns.wav` — 4:15,
141 BPM, 150 bars), produced end-to-end in Blender 5.1.2 with a stylized
**claymation** look: bright colors, white-trash Americana, Spike & Mike
energy. A heartland kid 3D-prints a machine gun, and by sundown has
dragged his mom and the county sheriff into a three-way backyard war.
50 shots. Solo production.

Read next, in order: `treatment/story.md` (what happens),
`treatment/script.md` (shot by shot, frame-locked), `treatment/site.md`
(where everything is), `pipeline.md` (conventions), `tools.md` (the
machinery), `layout.md` (the layout & drawing workflow).

## Where we are

Written 2026-07-20, status updated 2026-08-03.

| Phase | Status |
|-------|--------|
| 1. Ideation | done |
| 2. Writing — story, script, lyrics, sections | done |
| 3. Layout / animatic | **BLOCKED END TO END — all 50 shots, frames 1–4780. Undrawn.** |
| 4. Asset production | greybox — property shell, 34 guides, 2 mini-sets, squib FX |
| 5–9. Animation → delivery | not started (pipeline built and validated end-to-end) |

The film is watchable now: `edit/edit.blend` cuts the track, 9 section
markers and 50 live layout strips — no slugs left. Nothing is rendered yet, so
every strip is a **linked scene strip** — the edit previews `layout.blend`
directly, and you must **reload libraries** after a headless run to see
changes.

### What is left

Nothing structural. Every shot is blocked and animated at guide tier and cuts
as layout; the film plays start to finish. It has not been drawn — 50 empty
Grease Pencil papers — and it has never been watched end to end at CORRECT
timing, because of the bug in the next section.

Blocked 2026-08-03 in this order: `sq070`–`sq090` (the aftermath, the ending
and the title card), then a performance pass over seven `sq010`/`sq020` shots,
then the sheriff's introduction and crash (`sq040_sh030`–`sh066`).

---

## THE KEYFRAME RETIME BUG — read this before animating anything

**`resync_layout.py` moves a scene's frame RANGE to match the shotlist. Nothing
moves the KEYS.** So every shot animated before the 2026-08-02 retime — which
pulled each section a bar (~41 frames) earlier — is still keyed where the old
chart put it, and the shot plays the wrong slice of its own move.

This is not cosmetic. `sq010_sh030` ran 246–368 with keys at 287–409: the first
41 frames were a held pose and the jump, keyed at 372–379, happened four frames
AFTER the shot ended. It had never been on screen once. Several "the animation
is weak" notes turned out to be this and nothing else.

**24 of 50 scenes were affected. 13 still are:**

    sq010_sh020   sq020_sh010  sq020_sh030  sq020_sh040  sq020_sh044
    sq020_sh050   sq030_sh030  sq040_sh010  sq040_sh020  sq040_sh050
    sq050_sh010   sq050_sh020  sq060_sh010

Worst offenders: `sq040_sh030`'s cruiser was keyed across 291 frames for a
41-frame shot (fixed); `sq030_sh030`'s heads-popping run is compressed into
half its shot; `sq040_sh050`'s hubcap skeet leads its shot by 358 frames.

**It is NOT a blanket −41.** Actions were duplicated forward between shots as
blocking was carried, so many carry inherited keys from earlier shots as well
as their own — a scene can legitimately have keys 200 frames before its start
(a settled value) while its own move is 41 frames late. Each one wants looking
at. The audit that finds them is described in "Working notes".

Suggested order, densest comedy first: `sq030_sh030` and `sq040_sh010/020/050`
(chorus 1 and the verse-2 gags), then `sq020_*`, then `sq010_sh020`,
`sq050_sh010/020`, `sq060_sh010`.

## Constraints that shape the late sequences

- **The sheriff is 10.8 m north of the boy** after the blast. No frame holds
  him, the boy and the back door at a readable size, which is why
  `sq070_sh010`'s aerial drops him and `sh020` is a long-lens OTS.
- **The Santa stands INSIDE the garage tunnel**, 0.24 m off its north wall at
  `(-7.839, 2.198)` — its world position since `sq010`. `sq070_sh050` shoots
  out through the rear passthrough, and the sweet-tea table's position is
  dictated by that sight-line, not by taste.
- **`ground_far` is not flat.** It runs z 0..42 and rises out past the road,
  which ate the bottom third of `sq090`'s title card. The card is parked
  FLOATING at `(0, -60, 5)`.
- **Six shots carry armed guns** — `sq060_sh012/sh014`, `sq080_sh030/sh040`,
  plus `sq030_sh030` and `sq040_sh010/sh050`'s `mg_ctrl`s. See the two traps
  under the gunfire chain.

## The gunfire chain, if you have not met it

Four tools, in this order. Each is documented in `tools.md`.

    fire_rig.py --arm   →  a gun that can fire      (["fire"] on a control)
    aim_gun.py          →  where it points per shot (TRACK_TO on an empty)
    gunfire.py --bake   →  raycast → damage         (squibs where rounds land)
    squib.py --apply    →  a hand-placed impact     (no shooter needed)

`gunfire.py --dry-run` prints every shot and what it hit, and doubles as an
aim audit of the blocking — it is how most of the staging errors in the solo
were caught, and how Mom's rounds were found going into the sheriff's belly in
`sq060_sh014` when he is not hit in this story.

**Two traps around armed guns, both paid for:**

- **Never `animation_data_clear()` a `<p>_ctrl`.** Its action is where
  `fire_rig` keyed `["fire"]`, and wiping it silently disarms the gun — the
  bake comes back "0 shots fired" and nothing warns you. `--arm` cannot put
  the keys back either, because it is keyed on the gun INSTANCE that arming
  itself deleted. Transform the control in place. To re-key a burst on an
  already-armed control, call `fire_rig._burst_keys(ctrl, start, end, period)`
  directly so the shape matches.
- **A blocking script that re-adds a gun to an armed shot leaves TWO guns** —
  one armed and static, one animated and dead. Arm AFTER blocking, and give
  any re-runnable pass an `only=` filter so you can re-run one step without
  touching the armed shots.

## The parent-inverse trap — this one has bitten three times

When Blender parents A to B it stores `matrix_parent_inverse` = B's world
matrix at that moment, so `A.location` keeps meaning what it meant. That makes
a child's numbers meaningless on their own: **world = parent · inverse · local,
and nothing in the file records what pose the parent was in when it happened.**

It has cost three real bugs: the boy's machine gun pointing 83 degrees off the
Santa in `sq020_sh030`; the sheriff and his sandwich sitting at coordinates
that only made sense against a car pose nobody had; and blocking that looked
correct in the outliner and wrong in the render.

Two ways out, both used in the file now:

- **Unparent and key in world space** when the child needs to AIM at something.
  A heading is then just `atan2(dy, dx)` — and a gun fires along local +X, so
  that heading IS its rotZ.
- **Re-parent with an identity inverse** when the child should ride the parent:
  `ob.parent = p; ob.matrix_parent_inverse = Matrix.Identity(4); ob.location =
  <plain parent-space offset>`. Then the numbers mean what they look like.

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

### Pose variants are how a rigid guide performs

Guides are rigid and `guide_assets.box()` is axis-aligned, so there is no way
to straight-arm a door, shove a carton, shoulder a rifle or sit in a car by
transforming a standing figure. The answer — and it is the same thing
stop-motion calls replacement animation — is a variant collection, about ten
lines in `guide_assets.py`:

    sheriff_war  sheriff_seated       boy_run  boy_push  boy_peer  boy_aim

Two rules learned building them:

- **Every mass must share volume with its neighbour.** `boy_run` and
  `boy_push` shipped with the trailing leg (local +X, which facing -Y is his
  LEFT) sharing no volume with the torso at all, so his left leg was a
  detached block floating behind him. A hip mass bridges them now. Check the
  numbers, not the front-orthographic preview — a detached limb is invisible
  head-on.
- **Swap variants with keyed `hide_viewport`/`hide_render` set to CONSTANT
  interpolation**, both guides keyed identically through the swap frame, so the
  cut reads as the pose changing rather than as a cut. That is how the Santa
  loses its head, how the sheriff gets out of his chair, and how the boy
  shoulders the gun.

`--add=` refuses to touch a guide that already exists, so fixing a builder
needs the collection removed first; there is a `rebuild_guide.py` pattern in
"Working notes".

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

- **The Redwood Guides add-on exists in TWO copies and they silently
  desync.** Blender's Install *copies* `tools/addons/redwood_guides.py` to
  `~/Library/Application Support/Blender/5.1/scripts/addons/`. Editing the
  repo file changes nothing in Blender until you reinstall, and
  `check_addon.py` imports the *repo* copy — so the suite can be fully
  green while the artist's Add Guide dropdown is empty. That is exactly
  what happened after this refactor: the installed copy still imported the
  renamed `make_boards`, `_load_guides()` raised inside the EnumProperty
  items callback, and the dropdown came up blank with no error shown.
  Symlink instead of installing (see `layout.md`), and restart Blender
  after any add-on change.

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
| `conform_edit.py` | **safe by default** — updates `edit/edit.blend` in place, preserving UI, markers and hand-cut strips. `--force` is the destructive full rebuild (replaces the edit AND the file's workspaces/screens) |

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

## Reverted deliberately — do not redo without asking

**`sheriff_eating` and the sq040 sandwich re-cut (commit `d9e0b69`, reverted
in `b0466ba`).** The diagnosis stands and is worth keeping: the sandwich was
bolted at `(0, -0.30, 0.98)` and `sheriff_seated`'s belly ball — centre
`(0, -0.10, 0.84)`, r 0.26 — reaches y -0.32 at that height, so it was 2 cm
inside him and below his hands. A pose variant with both arms forward was
built to fix it and the gag was re-cut around a lean-in bite.

**Ian did not like the new animation and wants to fix the original.** The
geometry finding above is still true; the performance replacement is what was
rejected. Fix the old animation rather than re-introducing `sheriff_eating`.

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
- **Rigged characters — DEFERRED, decided 2026-08-03.** Rigging faces, limbs
  and fingers before a full-animation sweep was considered and put off, for
  three reasons: the style is not locked (a claymation look wants REPLACEMENT
  animation — swappable heads and hands, no face rig at all; a print or gouache
  look wants something else again); the animatic has not finished its job while
  13 scenes still play the wrong slice of themselves; and at animatic scale the
  boy's whole head is about thirty pixels, so fingers cannot read yet.
  The agreed order is: finish the timing sweep and the storytelling details →
  watch it end to end and cut → lock the style and design the characters →
  THEN rig against locked designs and do the full sweep.
  If one thing gets pulled forward, make it **heads that turn independently of
  the body** — a head guide on a neck empty, no rig. That is the biggest
  readability win going (recognition beats, eyelines, the "Danny?" shudder)
  and it is cheap. Before faces, before fingers.

## Next actions

1. **Sweep the 13 remaining retimed scenes.** Until that is done the film
   cannot be honestly watched — a third of the gags are playing the wrong
   frames. See "THE KEYFRAME RETIME BUG" above for the list and the order.
2. **Fix `sq040_sh035`/`sh042`'s sandwich.** It sits inside the sheriff's
   belly and below his hands (numbers in "Reverted deliberately"). The
   geometry finding is good; the replacement performance was rejected, so
   repair the existing animation.
3. **Watch it end to end** and cut for time. The blocking tier is complete, so
   for the first time the whole film is arbitrable: verse 2's gag density, the
   `[IF TIME]` shots, and whether any beat is holding too long.
4. **Draw the film.** A rough scribble pass over all 50 layout scenes first,
   polish later — blocking and drawing both render together, always, so there
   is nothing to re-run afterward. This is the long pole.
5. **Firm durations after the watch**, then move statuses `scripted →
   boarded` (all 50 rows still say `scripted`, including the blocked ones —
   the column has never been maintained, so do it in one pass or not at all).
6. **Lock the style, then design pass** on the property and the characters.
7. **Then rig** — against locked designs — and do the full-animation sweep.
   See "Open decisions" for why that order and not the other one.

## How a blocking pass is actually done

There is no committed tool for animating a shot and there should not be one —
`stage_shots.py`'s STAGING table cannot express animation, multiple instances
of one guide, or a variant swap, and a one-shot script in `tools/` is the
`migrate_layout.py` hazard all over again. **`layout.blend` is the record.**
Every sequence from `sq050` on was authored this way.

The shape that worked, repeatedly:

1. **Audit before touching anything.** Two read-only scripts earn their keep:
   - *key-range audit* — for each scene, min/max keyframe across every
     animated object vs `frame_start`/`frame_end`. This is what found the
     retime bug. Anything with lead > 2 or tail > 2 is playing the wrong
     slice of itself.
   - *cast audit* — who is staged in shot N-1 and N+1 but not N. Found Mom
     missing from `sq080_sh020` and from `sq060_sh020`, whose own script line
     reads "All three freeze".
2. **Read the continuity basis out of the file, never off the docs.**
   `site.md` and the blocking disagree in at least two places (the Santa, the
   BBQ). The blocking wins — invariant 3.
3. **Write ONE idempotent script per pass**: clear each object's action and
   re-key; match instances by a `rw_tag` custom property so a shot can hold
   three tea glasses; give it an `only=<step>` filter.
4. **Render frames and look at them.** Framing math is not framing. The aerial
   and the OTS in `sq070` each took three passes; the arithmetic was right
   every time and the frame was wrong anyway.
5. **Diff every scene against the committed file** before committing, to prove
   nothing else moved. Pull `HEAD`'s `layout.blend` straight out of
   `.git/lfs/objects/<oid[0:2]>/<oid[2:4]>/<oid>`.
   **Caveat, learned the hard way:** a fingerprint of static transforms plus
   "does it have an action" CANNOT see an animation-only change, and will
   report a clean diff for a pass that only re-keyed. Read the fcurves back
   for those.

`--add=` refuses an existing guide, so a builder fix needs the collection
removed and rebuilt: open the asset file, remove the collection and its
objects, re-run `guide_assets.BUILDERS[name](coll)`, re-mark the asset,
re-run `check_structural` + `check_dimensions`, save.

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
