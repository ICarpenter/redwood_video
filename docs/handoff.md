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
machinery), `boards.md` (the drawing workflow).

## Where we are

| Phase | Status |
|-------|--------|
| 1. Ideation | done |
| 2. Writing — story, script, lyrics, sections | done |
| 3. Storyboards / animatic | **in progress** — infrastructure done; 1 board drawn, 4 blocked out with guides |
| 4. Asset production | started — property blockout + 13 scale guides + garage passthrough |
| 5–9. Animation → delivery | not started (pipeline built and validated end-to-end) |

The film is **watchable right now**: `edit/edit.blend` holds the track,
9 section markers, 5 board strips and 34 slugs. It upgrades in place as
boards and renders land.

Board state today:

| Shot | State |
|------|-------|
| sq010_sh010 | drawn (119 strokes) — guides auto-hidden |
| sq010_sh020 | blocked out (property + delivery_truck, truck animated across X) |
| sq010_sh030 | blocked out (property + boy) |
| sq010_sh040 | blocked out (property + boy + box) |
| sq010_sh045 | blocked out (property rotated 180° + boy + box) |
| the other 34 | slugs |

## Five conventions that will bite you if you forget them

1. **Timeline: frame 1 = song time 0, 24 fps.** Every shot's frame range
   is song-global, so a shot's keyframes and its strip position are the
   same numbers. The song ends dead on the last chorus hit at **bar 111 /
   frame 4534**; frames 4535+ are audio tail only (shots currently run to
   4780, into the tail).
2. **Bars are counted from 0** in `sections.csv` and the treatment docs
   (matching how the song structure was written). `beatmap.csv`'s bar
   column is 1-indexed — its bar 1 is our bar 0. Concretely: script bar 10
   is beatmap bar 11 is frame 410. Get this backwards and cuts land a bar
   off.
3. **`docs/shotlist.csv` is the source of truth.** Tools read it; nothing
   invents structure. Render boundaries come from it *at render time*, so
   retiming a row re-renders correctly without recreating the shot file.
   It is **unquoted CSV — never put a comma in a description**, or the
   columns shift and `read_shotlist` dies on `int()`. The `assets` column
   is semicolon-separated for exactly this reason.
4. **Link, never append.** Assets live at
   `assets/<kind>/<name>/<name>.blend` exposing one root collection named
   `<name>`. Animate linked rigs via library overrides.
5. **The edit uses the Standard view transform, not AgX.** Shot renders
   already have AgX baked in; applying it again in the edit washes
   everything out (measured: 25 dB PSNR vs 102 dB when passed through).

Plus the compass, from `treatment/site.md`: **+Y = backyard, −Y = road,
sun rises east, sets west** — the final sprint runs west into the sunset,
mirroring the sunrise.

## Shot numbering

Shots step by tens (`010, 020, …`) so a cut can be inserted without
renumbering. `sq010_sh045` is the first use of that gap — the garage beat
split into a drag and a reverse. **Insert, don't renumber**: renaming a
board scene orphans its drawings, notes, and guides collection. The `sh`
field only has to be 3 digits.

## The boards, and how guides reach the edit

Every board scene owns a `<shotcode>_guides` collection holding linked
scale-guide instances. Guide **render visibility is automatic**: guides
render while a board is undrawn, and stop the moment it has real strokes,
so a guide never prints under artwork. `boardlib.sync_guide_visibility`
owns the rule; `make_boards.py` applies it to every board on each run.

**Re-run `make_boards.py` after a drawing session** — otherwise newly
drawn boards keep showing their guides in the edit.

`conform_edit` cuts in any board with strokes **or** guides, so the tiers
are: render → drawn board → guide blockout → slug.

Boards use a **fixed camera** at `(0, −10, 0)` looking +Y at a Grease
Pencil paper plane on the origin. You change the angle by moving and
rotating the *property instance*, not the camera — sh010 sits at rotZ
−43.8°, sh030 at +90°, sh045 at 180°. Moving the camera after drawing
skews the strokes already on the paper.

Guides at negative Y sit in *front* of the paper and will occlude your
strokes (sh040 stages its boy and box there deliberately, as foreground).
Use X-ray on those boards.

## Blender 5.1.2 gotchas already paid for

- **Storypencil does not work on Blender 5.x** (upstream rewrite pending).
  Boards are plain Grease Pencil scenes; our conform does the assembly.
- `SequenceEditor.sequences` → **`.strips`** (use a `hasattr` fallback).
- `strips.new_effect()` takes **`length=`**, not `frame_end=`.
- `action.fcurves` is **gone** — actions are slotted. Note that
  `strip.channelbags` is a *collection* while `strip.channelbag(slot)` is
  a *function*; calling the former explodes with "not callable".
- **`matrix_world` is identity in `--background`** until something forces
  a depsgraph evaluation — including `camera.matrix_world`, which makes
  `world_to_camera_view` silently return garbage rather than error. Either
  evaluate (`obj.evaluated_get(depsgraph)` after `frame_set`) or compose
  the transform yourself from stored location/rotation.
- **Edits to linked datablocks do not persist.** Setting `hide_render` on
  a linked collection works in memory and reverts to the library value on
  reopen. Anything that must survive has to be written in the source file.
- Scenes created through the data API have **no world** → black viewport
  and black renders. Assign one.
- Viewport shading defaults to **Theme** background (grey) — set
  *Background → World* per viewport to see white paper.
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
| `guides.py` | shared, bpy-free: declarative scale-guide registry (specs, catalogs, drop location) |
| `boardlib.py` | shared, bpy-aware: board stroke detection, guides collection, visibility rule, edit-readiness |
| `beatmap.py` | BPM + length → `docs/beatmap.csv` (bar/beat → frame) |
| `make_template.py` | builds `shot_template.blend` (1080p24, EEVEE, AgX, PNG 16-bit) |
| `make_boards.py` | seeds `boards/boards.blend` — one GP scene per shot; reruns add new rows, heal notes/worlds, and re-sync guide visibility |
| `resync_boards.py` | shotlist → existing board frame ranges (the gap make_boards leaves, since it only adds) |
| `stage_boards.py` | declarative guide staging into boards — **additive**, never resets framing set by hand |
| `guide_assets.py` | builds `cast.blend` / `props.blend`; `--add=<name>` appends one guide non-destructively |
| `blockout_property.py` | rebuilds the greybox property + preview cameras |
| `stage_property.py` | stages cast/props as linked instances in property.blend's `blocking` collection |
| `new_shot.py` / `build_shots.py` | stamp shot blends from the template |
| `render_shot.sh` | headless render → `render/<code>/vNNN/`, auto-incrementing |
| `conform_edit.py` | rebuilds `edit/edit.blend`: track + markers + best tier per shot |
| `encode_delivery.sh` | ProRes HQ master + H.264 into `delivery/` |

Tests: `python3 -m unittest discover -s tools/tests -t tools/tests` (42
passing). Note the `-t` — `tools/tests` has no `__init__.py`, so plain
discovery from the repo root fails with "Start directory is not importable".

### Which tools destroy work

| Tool | Behaviour |
|------|-----------|
| `make_boards.py` | **safe** — adds and heals only. `--force` rebuilds and destroys all drawings |
| `stage_boards.py` | **safe** — skips guides already present, idempotent |
| `resync_boards.py` | **safe** — frame ranges only, idempotent |
| `guide_assets.py --add=` | **safe** — appends one collection, refuses if it already exists |
| `guide_assets.py` (default) | wipes and rebuilds cast+props; guarded, needs `--force` |
| `blockout_property.py` | wipes and rebuilds property.blend; guarded, needs `--force`. Also destroys the asset mark and the `blocking` collection — re-run `--mark-property` and `stage_property.py` after |
| `stage_property.py` | **clears and rebuilds** its `blocking` collection every run; hand-placed blocking instances are reset |
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

- Everything through PR #8 (sh040 split, box guide, guide blockout tier)
  is merged. `main` is current.
- Branch names describe the work; `envs` and `boards-guide-blockout` are
  merged and can be deleted.

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
boards.blend exactly as it does in property.blend. Verified — but it is a
non-obvious dependency, so if the passthrough ever closes up in a board,
check that `garage_door_rcutter` still came along.

Both garage doors are modelled **open** — retracted horizontal panels at
z 2.35..2.45, not slabs filling the opening.

## Open decisions

- **Backyard scale.** Currently ~22 m deep. Generous — good for
  firing-squad wides, but the three-way firefight may play funnier
  cramped. Cheap to change now, expensive after boards.
- **Front yard depth** — governs how long the cruiser is on screen before
  the tire blows.
- **Board fidelity** — one held drawing per shot, or 2–3 poses for the
  action beats. The guide-blockout tier takes some pressure off this: a
  beat can read in the edit before it is drawn at all.
- **Verse 2 gag density** — the script flags it as the hottest section
  with an explicit cut-first order (hubcap skeet → package football →
  flowerbed arm). The animatic arbitrates; don't cut on taste beforehand.
- **Production design** — nothing designed yet beyond massing: siding,
  porch clutter, junk, terrain, and the clay look itself.

## Next actions

1. **Keep blocking out story beats with guides.** Add a row to `STAGING`
   in `stage_boards.py` per shot, or drop guides by hand with Sidebar ▸
   Redwood ▸ Add Guide. Conform and watch — beats read before anything is
   drawn.
2. **Board the film.** A rough scribble pass over all 39 first, polish
   later. Re-run `make_boards.py` afterwards so drawn boards drop their
   guides out of the edit.
3. **Arbitrate verse 2** with the animatic, then firm durations and move
   statuses `scripted → boarded` (all 39 rows are still `scripted`).
4. **Design pass on the property** once the boards say what the camera
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
  boards infrastructure (#4), env blockout + scale guides (#7). PR #5 (a
  test sunrise board) was scrapped — the strokes survive on the
  `board-sunrise` branch if ever wanted.
