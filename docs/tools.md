# Pipeline tools & production flow

What each script in `tools/` does, what it reads and writes, and how the whole
thing runs from a finished song to a delivered video. Conventions (naming,
statuses, linking rules) live in `pipeline.md`; the layout invariants and the
drawing-guide workflow live in `layout.md`; this doc is the narrative.

## The big picture

The pipeline is built around one file: **`docs/shotlist.csv`**. Every shot in
the video is a row — its sequence/shot number, description, start/end frame in
the song's timeline, the assets it needs, and a status that walks from
`boarded` to `final`. Humans edit it; every tool reads it. Nothing downstream
invents structure: the tools just materialize what the shotlist says.

Two conventions make the math trivial everywhere:

- **Timeline frame 1 = song time 0, at 24 fps.** Shot frame ranges are
  *song-global* — shot `sq020_sh030` covering frames 481–528 is literally
  seconds 20–22 of the track. Any layout scene or render drops into the edit
  at its own frame numbers and is automatically in sync.
- **Settings live in one place.** Resolution, fps, color management, and
  output format are all applied through `tools/layoutlib.py`'s
  `apply_project_settings()` — `make_template.py` and `make_layout.py` both
  call it, so they cannot independently drift the way they once did (layout
  scenes pass `view_transform="Standard"` since they show greybox blocking
  and flat GP ink, which AgX only muddies; everything else stays AgX).

```mermaid
flowchart TD
    track["audio/track/*.wav<br/>(finished song)"] --> beatmap["tools/beatmap.py"]
    beatmap --> bcsv["docs/beatmap.csv<br/>(bar/beat → frame)"]
    bcsv -.timing for layout<br/>and shot boundaries.-> shotlist["docs/shotlist.csv<br/>(SOURCE OF TRUTH)"]
    shotlist --> makelayout["tools/make_layout.py"]
    assets["assets/&lt;kind&gt;/&lt;name&gt;/&lt;name&gt;.blend<br/>(linked, never appended)"] --> makelayout
    track -.per-scene scrub audio.-> makelayout
    makelayout --> layout["layout/layout.blend<br/>(one camera-driven scene per shot)"]
    stageshots["tools/stage_shots.py"] -.starting camera +<br/>world-space blocking.-> layout
    continueshot["tools/continue_shot.py"] -.copy camera + blocking<br/>shot to shot.-> layout
    layout --> conform["tools/conform_edit.py"]
    layout --> export["tools/export_shot.py<br/>(on demand)"]
    export --> shots["shots/sqXXX/shXXX/shXXX.blend<br/>(animate here)"]
    shots --> render["tools/render_shot.sh"]
    render --> frames["render/sqXXX_shXXX/vNNN/<br/>(versioned frame sequences)"]
    frames --> conform
    conform --> edit["edit/edit.blend<br/>(VSE: track + shot strips)"]
    edit -->|render the final edit| final["final frame sequence"]
    final --> encode["tools/encode_delivery.sh"]
    track --> encode
    encode --> delivery["delivery/&lt;name&gt;_prores.mov<br/>delivery/&lt;name&gt;_h264.mp4"]
```

## The tools, one by one

### `tools/shotlib.py` — the shared brain (not run directly)

A stdlib-only Python module the other tools import. It owns the project's
path math and data contracts so they exist in exactly one place:

- parses and *validates* `docs/shotlist.csv` (3-digit ids, sane frame ranges,
  duration consistency, known statuses, no duplicate shots, and every
  `assets` entry is a known guide name from `guides.py` — bad rows fail
  loudly with `file:line` errors instead of corrupting downstream work)
- converts musical beats to frames (`beat_to_frame`)
- derives canonical paths (`shots/sq010/sh010/sh010.blend`,
  `render/sq010_sh010/`) and the next render version (`v001` → `v002`)
- finds the Blender binary (`$BLENDER` env var → `PATH` → the standard
  `/Applications` install)

It runs under both system Python and Blender's bundled Python, which is what
lets the same logic serve CLI tools and in-Blender scripts. Covered by the
test suite in `tools/tests/`.

### `tools/guides.py` — the drawing-guide registry (not run directly)

Also stdlib-only, bpy-free (same rule `shotlib.py` follows — both import
under system Python for `guide_assets.py --check` and the test suite, and
under Blender's Python for the add-on and the layout tools). Declares:

- `GuideSpec` / `GUIDES` / `DROPPABLE` — the catalog of cast, prop, and set
  guides, each authored facing `-Y`, feet at `z=0`, centred on `x=0`
- `blocking_collection_name(scene_name)` → `<scene_name>_blocking` — the one
  place that owns the per-shot blocking collection's name
- `DROP_DISTANCE` — the fallback distance the Redwood Guides add-on drops a
  guide along the camera's view ray when it never meets the ground plane
- the asset-catalog UUIDs/paths and the `.cats.txt` file text

### `tools/layoutlib.py` — the shared bpy-aware brain (not run directly)

`shotlib.py` and `guides.py` are deliberately bpy-free so they import under
system Python; this is their counterpart for code that must touch Blender
data, shared by `make_layout.py`, `stage_shots.py`, `continue_shot.py`,
`export_shot.py`, and `conform_edit.py` — they all need to ask the same
questions about a shot, and the answers must agree:

- `has_strokes` / `blocking_instances` / `shot_ready` — whether a layout
  scene has real Grease Pencil ink, staged blocking, or either (which is
  what earns it a strip in the edit)
- `blocking_collection` — get-or-create the scene's `<code>_blocking`
  collection
- `apply_hide_blocking` — honours the hand-set `scene["hide_blocking"]`
  opt-out; blocking and paper both render by default, and **no tool ever
  writes this flag**
- `apply_project_settings` — the one place fps/resolution/color-management
  live (see "Settings live in one place" above)
- `fit_paper` — parents a Grease Pencil "paper" to a camera and sizes it to
  the frustum, so a stroke at the paper's edge lands exactly at frame edge
  for any lens or distance; `PAPER_DISTANCE` is a framing choice, not an
  occlusion trick (Grease Pencil composites over mesh geometry in EEVEE
  unconditionally — see `handoff.md`)

### `tools/beatmap.py` — turn BPM into frame numbers

```sh
python3 tools/beatmap.py --bpm 92 --length 214
```

Run once, right after the track lands in `audio/track/`. Writes
`docs/beatmap.csv`: every beat of the song as bar number, beat number,
seconds, and timeline frame. This is the timing reference for everything —
when writing the shotlist you pick shot boundaries off this table so cuts
land on beats, and while animating you can check exactly which frame the
downbeat of bar 17 hits.

### `tools/make_template.py` — (re)build the shot template

```sh
"$BLENDER" --background --factory-startup --python-exit-code 1 \
    --python tools/make_template.py
```

Generates `tools/shot_template.blend`: an empty stage with a camera, the
`cam`/`chars`/`env`/`fx` collection layout, and the locked project settings
(via `layoutlib.apply_project_settings`) — 1920×1080, 24 fps, EEVEE, AgX view
transform, PNG 16-bit output, audio-synced playback. Already generated and
committed; you only rerun this if the project settings themselves change.
Nothing downstream opens this file directly any more — layout scenes are
built by `make_layout.py`, not stamped from the template — but it is the
canonical reference for the locked settings, and sharing
`apply_project_settings` with `make_layout.py` is what keeps the two from
drifting the way they once did.

### `tools/env.sh` — shared shell plumbing (not run directly)

Sourced by the shell scripts. Resolves the project root and the Blender
binary (honoring `$BLENDER`) and fails with a clear message if Blender isn't
found, so the scripts that depend on it don't each reinvent discovery.

### `tools/render_shot.sh` — render one shot, versioned

```sh
tools/render_shot.sh 010 010          # → render/sq010_sh010/v001/
tools/render_shot.sh 010 010          # → v002 (auto-increments, v001 kept)
tools/render_shot.sh 010 010 v002     # explicit version = resume/re-render INTO v002
```

Headless-renders a shot as an image sequence. Requires the shot to already
exist under `shots/sqXXX/shXXX/shXXX.blend` — export it first with
`export_shot.py` if it hasn't been. The frame range is read from the shot's
`docs/shotlist.csv` row *at render time* — the shotlist governs at both ends
of the pipeline, so retiming a row re-renders correctly without recreating
the shot file (the blend's stored range only drives in-UI scrubbing and
playblasts). Every run gets a fresh `vNNN` directory by default, so old
renders are never lost — you can always A/B against the previous version.
Passing an explicit version is the crash-resume path: it re-renders into
that directory (overwriting those frames). Format and resolution come from
the shot file's own settings (PNG by default, switch a specific shot to EXR
for comp-heavy work and the script honors it). Frame sequences rather than
movie files because a crashed render resumes instead of starting over.

### `tools/make_layout.py` — seed the camera-driven layout file

```sh
"$BLENDER" --background --factory-startup --python-exit-code 1 \
    --python tools/make_layout.py
# `-- --force` rebuilds from scratch (DESTROYS all drawing and blocking)
```

Creates/extends `layout/layout.blend`: one scene per shotlist row, named by
shot code, holding the project's four layout invariants (see `layout.md`) —
the property linked at identity, a starting camera as the shot's sole
framing authority, a per-scene `<code>_blocking` collection for world-space
blocking, and a Grease Pencil "paper" fit to the camera's frustum for
animatic drawing — plus a script-prompt note parented to the camera and the
track on the scene's sequencer so drawing happens with audio scrubbing in
context.

The default run only ADDS scenes for new shotlist rows (safe after
drawing/blocking has begun) — inserting a cutaway later is one shotlist row +
one rerun. Reruns also heal anything an existing scene is missing or has
drifted from: world, project settings, the blocking collection, the linked
property (snapped back to identity if it has drifted off), the starter
Grease Pencil keyframe, the script note, or a paper unfit to its camera. A
camera-less scene can't be given a framing authority automatically, so it's
reported instead of silently skipped.

### `tools/guide_assets.py` — build the drawing-guide assets

```sh
"$BLENDER" --background --factory-startup --python-exit-code 1 \
    --python tools/guide_assets.py
# --force          overwrite the (now hand-maintained) asset files
# --out=<dir>       throwaway build into <dir>
# --previews=<dir>  render each guide to <dir>/<name>.png
# --check           build to a temp dir + assert invariants
# --mark-property   mark the `property` collection as a catalogued asset
# --add=<name>      append ONE new guide to its asset file, in place
```

`--add=<name>` is the non-destructive way to introduce a new guide once the
asset files are hand-maintained: it opens the file, appends just that
collection, marks and dimension-checks it, and saves. It refuses if the guide
already exists. Adding a guide is therefore two edits (a `GuideSpec` in
`guides.py`, a builder in `guide_assets.py`) plus one `--add` run — no `--force`,
nothing else touched.

Builds `assets/chars/cast.blend` and `assets/props/props.blend` — one
recognisable, real-scale, primitive-built collection per cast member and hero
prop — plus `assets/blender_assets.cats.txt`. Each collection is a catalogued
Asset (`guides/cast`, `guides/props`). These are scale guides for blocking out
and drawing a shot: they link into layout scenes as world-space blocking
instances or Asset-Browser drops (see `docs/layout.md`).
Declarative registry lives in `tools/guides.py`; covered by
`tools/tests/test_guides.py` and the headless `tools/tests/test_blender_smoke.py`.

### `tools/resync_layout.py` — re-point layout scenes at the shotlist's frame ranges

```sh
"$BLENDER" --background --factory-startup --python-exit-code 1 \
    --python tools/resync_layout.py
# `-- --dry-run` reports what would change without saving
```

`make_layout.py` only ever ADDS scenes, so re-timing a shot in `shotlist.csv`
leaves its layout scene on the old range. This resets `frame_start`/`frame_end`
on every existing layout scene to match its row. Frame ranges only — no scene
is created or removed, no Grease Pencil is touched, no camera or blocking
instance moves. Scenes with no shotlist row are reported and left alone.
Idempotent. Run it after any shotlist re-time, and after splitting a shot.

### `tools/stage_shots.py` — frame starting cameras and drop starting blocking

```sh
"$BLENDER" --background --factory-startup --python-exit-code 1 \
    --python tools/stage_shots.py
# `-- --dry-run` reports what would change without saving
```

Declarative `STAGING` table — scene code → a starting camera (an explicit
world-space location/look-at/lens, or a named preview camera appended from
`property.blend` and copied in) and the world-space blocking that shot
needs, all measured off the property's actual bounds. Scoped to
*composition*, on top of the scene structure `make_layout.py` already built.

Two additive, left-alone update rules, so re-running is always safe:

- **Camera:** only a camera still at the `make_layout.py` default
  `(0, -10, 1.6)` gets framed. A camera that has moved — by this script or by
  hand — is finished work and is never reset.
- **Blocking:** a guide already present in a scene (matched by
  instance-collection identity, not object name, since instance objects get
  auto-suffixed) is left untouched. Only missing ones are created.

Positions here are a starting point for framing and blocking, not final
composition — the artist takes it from there.

### `tools/continue_shot.py` — carry a shot's staging forward

```sh
"$BLENDER" --background --python-exit-code 1 \
    --python tools/continue_shot.py -- --from sq010_sh040 --to sq010_sh045 \
    [--at-frame 490] [--force] [--dry-run]
```

Because the property is linked at identity in *every* layout scene, two
scenes share one world origin — so continuing a shot is a direct world-matrix
copy of the camera and every blocking instance, read at a given frame (the
source's last frame by default) and written into the destination. Snapshot
semantics, not a live link: the destination is independent the moment it's
written, so re-blocking the source afterwards never disturbs it. A blocking
instance already present in the destination is left alone unless `--force`.
Refuses to copy a snapshot that evaluated to all-identity matrices (the
depsgraph trap described in `handoff.md`) rather than silently plant the
destination at the world origin.

### `tools/export_shot.py` — export one layout scene into its own shot file

```sh
"$BLENDER" --background --python-exit-code 1 \
    --python tools/export_shot.py -- --shot sq010_sh040 [--force]
```

Shot files are a **derived export, not a stage** — most shots never need
one, since a layout scene already carries the camera, the blocking, the
linked property, and the frame range. Export a shot when it earns its own
file: a per-shot compositor, a sim, a 4K re-render, lighting that must not
touch its neighbours.

Opens `layout/layout.blend`, marks the source scene `exported = True` (so
`conform_edit.py` can flag it as a possibly-stale reference) and saves that
back into `layout.blend`, then strips every other scene from an in-memory
copy, switches the surviving scene to AgX (layout scenes draw in Standard;
renders need AgX), turns off `use_sequencer` (the scene's scrub-audio track
would otherwise make `render_shot.sh` render the sequencer instead of the
camera — black frames), purges the orphaned datablocks the other 38 scenes
left behind, and saves `shots/sqXXX/shXXX/shXXX.blend`. One-way: refuses to
overwrite an existing shot file unless `--force`.

### `tools/migrate_layout.py` — one-shot migration (already run; do not rerun)

```sh
"$BLENDER" --background --python-exit-code 1 \
    --python tools/migrate_layout.py [-- --dry-run]
```

The script that reset `boards/boards.blend` (moved to `layout/layout.blend`)
into the camera-driven model: it deleted every blocking instance and cleared
every object's Action in every scene, renamed each `<code>_guides` collection
to `<code>_blocking`, linked the property at identity, and — for
`sq010_sh010` only — solved a static camera transform that reproduces the
old fixed-camera framing, so that shot's 119 drawn strokes keep 3D standing
behind them at the angle they were drawn at. Its own docstring explains why
the old animation was discarded rather than converted (the old model had
begun keyframing the property instance to fake camera moves — see
`handoff.md`'s "Blender gotchas" for the old model this replaced).

**This has already been run, once, against the pre-migration file. Do not
run it again** — see the "which tools destroy work" table in `handoff.md`.

### `tools/conform_edit.py` — build/rebuild the edit from what's rendered

```sh
"$BLENDER" --background --factory-startup --python-exit-code 1 \
    --python tools/conform_edit.py            # first build
# add `-- --force` to rebuild (DESTROYS manual edit work — it's a full regen)
```

Creates `edit/edit.blend`: the track as the spine on channel 1 (the scene's
frame range is derived from the actual audio length), and one strip per
`docs/shotlist.csv` row on channel 2 at its song-global frames, choosing the
best available tier per shot:

1. **render** — latest `render/<code>/vNNN/` as an image strip
2. **layout** — the scene named `<code>` in `layout/layout.blend`, linked in
   as a scene strip rendering its camera (its own sequencer, which only
   carries scrub audio, is excluded), once it has real Grease Pencil strokes
   **or** staged blocking — either makes a shot worth watching
3. **slug** — a text strip showing the shot code + description

So the animatic exists from day one as a slug cut and upgrades shot by shot
as blocking, drawing, and renders land — same cut throughout. If a layout
scene has already been exported to a shot file (`scene["exported"]`), a note
is printed: its blocking may now be stale relative to the exported file. If
`docs/sections.csv` exists, each song section also becomes a timeline marker
(intro, verse_1, chorus_1, …), so every scrub is oriented by song structure.

Two things to know: it's a **from-scratch regen**, so once you start hand-
cutting (cutaways on higher channels, trims, transitions) stop conforming and
maintain the edit manually — the `--force` guard exists to protect exactly
that work. And the edit scene deliberately uses the **Standard** view
transform: shot renders already have AgX baked in, and applying AgX again in
the edit visibly washes out every strip (verified: double-transformed frames
measure 25 dB PSNR against source vs. 102 dB when passed through untouched).

### `tools/encode_delivery.sh` — final masters

```sh
tools/encode_delivery.sh <frames_dir> <audio_file> <name>
```

The last step. Takes the final edit's rendered frame sequence plus the track
and produces two files in `delivery/`: a ProRes 422 HQ master
(`<name>_prores.mov`, archival/grading quality) and an H.264
(`<name>_h264.mp4`, CRF 18 + AAC 320k + faststart — upload-ready for
YouTube/Vimeo). Needs `ffmpeg` (installed via Homebrew).

## The flow, phase by phase

1. **Ideation / writing** — no tools yet. Notes in `docs/ideation/`, refs in
   `refs/`, treatment in `docs/treatment/`. Drop the track into
   `audio/track/` and run **`beatmap.py`**. Draft `docs/shotlist.csv` with
   shot boundaries picked off the beat map.
2. **Layout & animatic** — **`make_layout.py`** seeds `layout/layout.blend`,
   one camera-driven scene per shot. Frame starting cameras and block out
   cast/props in world space (`stage_shots.py`, the Redwood Guides add-on,
   or `continue_shot.py` to carry a beat forward), and draw Grease Pencil
   over it when a shot is ready for ink. Both tiers cut into the animatic
   immediately (see step 5). Statuses become `boarded` → `blocked`.
3. **Assets** — build characters/props/environments in `assets/`, one blend
   per asset, each exposing a root collection named after itself. Fill in
   each shot row's `assets` column (planning metadata, validated against
   `guides.py`, no longer a link instruction).
4. **Shot export & animation** — most shots stay in `layout.blend`
   indefinitely. Export one to its own file with **`export_shot.py`** only
   when it needs something a shared layout scene can't give it (a per-shot
   compositor, a sim, a 4K re-render, isolated lighting), then animate there.
   Viewport playblasts go into `shots/.../playblast/` and replace layout
   panels in `edit/edit.blend`, so the full video stays watchable while it's
   half-made. Statuses: `blocked` → `animated`.
5. **Rendering / comp** — **`render_shot.sh`** per exported shot (overnight
   batches: it's a loop in the shell away). Per-shot compositor tweaks
   re-render into the next version. Statuses: `rendered` → `comped`.
6. **Edit** — in `edit/edit.blend` (VSE), rebuilt or extended with
   **`conform_edit.py`**: render → layout → slug, same cut throughout as
   tiers upgrade.
7. **Delivery** — render the finished edit to a frame sequence, then
   **`encode_delivery.sh`** for the ProRes master and the upload encode.

The status column across all rows *is* the production dashboard: `grep -c
final docs/shotlist.csv` tells you how done the video is.
