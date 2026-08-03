---
name: shot-surgery
description: Use when adding, inserting, splitting, retiming, deleting, or reframing a shot in the redwood_video pipeline — anything that changes docs/shotlist.csv or a layout scene. This is a mechanical tool-driven operation, NOT a design task; do not brainstorm or write a spec first.
---

# Shot surgery

Adding or changing a shot in this project is a **mechanical operation with
existing tooling**. The shotlist is the source of truth and the scripts
materialize it. Do not reach for brainstorming, writing-plans, or a design
doc — edit two text files, run three scripts, verify.

(Specs in `docs/superpowers/specs/` exist for *building the tools*. Using them
is not a design task.)

## The four invariants (constrain every choice — see `docs/layout.md`)

1. The property is linked at identity in every layout scene and **never moves**.
2. **The camera is the only framing authority.** A new angle = a new camera
   transform, never a moved set.
3. **Blocking is world-space.** A guide's transform is where that character or
   prop actually stands on the property. If a guide already appears in another
   scene, **reuse its exact position** — grep for it first.
4. Shot files under `shots/` are a derived export, not a stage. Don't create one.

## Recipe

Read `docs/tools.md` for what each script does. Then:

### 1. Pick the frames off the beat map

```sh
awk -F, 'NR==1 || ($4>=<START> && $4<=<END>)' docs/beatmap.csv
```

Cuts land on a beat. **`beatmap.csv` bars are 1-indexed; `script.md` counts one
lower** — beatmap bar 34 is script bar 33. Verify against both endpoints of the
shot you're touching.

**Inserting a shot means splitting a neighbour, not shifting the timeline.**
The shotlist is contiguous end-to-end and frames are song-global; pushing rows
downstream desyncs every later shot from the track. Take the new shot's frames
out of the neighbour whose beat it belongs to.

### 2. `docs/shotlist.csv`

Insert the row, fix the neighbour's `end_frame`/`duration`.

- **No commas in `description`** — unquoted CSV read by `csv.DictReader`; a
  comma shifts every later column and `read_shotlist` fails on `start_frame`.
  Use a dash or "and".
- `sq`/`sh` are 3-digit strings. Tens are the convention; the gaps exist so
  inserts (`044`, `045`) never renumber an existing shot.
- `duration` must equal `end - start + 1` (validated).
- `assets` is `;`-separated and validated against the `guides.py` registry — a
  typo fails at parse time.

Validate before going near Blender:

```sh
cd tools && python3 -c "
import shotlib
shots = shotlib.read_shotlist('../docs/shotlist.csv')
prev = None
for s in shots:
    assert prev is None or s.start_frame == prev.end_frame + 1, (prev.code, s.code)
    prev = s
print(len(shots), 'shots contiguous to', prev.end_frame)"
python3 -m unittest discover tests
```

### 3. `docs/treatment/script.md` — before running anything

Load-bearing, not just prose: `make_layout.read_script_prompts` parses these
tables and renders `cells[5]` as the scene's on-screen note. A missing row =
a scene with no note. Edit it **before** step 4 so the note is right on
creation, and so an edited neighbour's note gets healed in the same run.

### 4. Run the three scripts (Blender must be CLOSED)

```sh
pgrep -f "Blender.app/Contents/MacOS/Blender" || echo "safe to write"
B=/Applications/Blender.app/Contents/MacOS/Blender

$B --background --factory-startup --python-exit-code 1 --python tools/make_layout.py
$B --background --factory-startup --python-exit-code 1 --python tools/resync_layout.py
$B --background --factory-startup --python-exit-code 1 --python tools/stage_shots.py
```

- `make_layout.py` (**no `--force`** — that destroys all drawing and blocking)
  adds scenes for new rows and heals existing ones, including note text.
- `resync_layout.py` re-points existing scenes at their shotlist frame range.
  `make_layout` only ever *adds*, so this is what fixes the neighbour you
  retimed. `-- --dry-run` first.
- `stage_shots.py` needs a new entry in its `STAGING` table: a camera
  (`(loc, look_at, lens)`) and world-space blocking. It only frames a camera
  still at the default `(0, -10, 1.6)`, and only creates guides not already
  present — hand work is never reset.

An open Blender session will clobber these headless writes on its next save.

### 5. Framing math for the `STAGING` camera

1920×1080 on a 36 mm sensor → sensor height 20.25 mm.

```
vertical coverage = distance * 20.25 / lens
horizontal        = distance * 36    / lens
```

Size the frame around the subject's real geometry (guide builders are in
`tools/guide_assets.py` — heights, and where detail like a duct-tape patch
sits). Guides are authored facing **−Y**, so `rotZ 90` faces +X, `rotZ 180`
faces +Y. A guide's front detail is only visible from the side it faces.

Property bounds, measured (also in `stage_shots.py`'s header): house x −7..5,
y −4..5; garage x −13..−7, y −3..3 with the passthrough at x ≈ −10; driveway
x −12.5..−7.5, y −14..−3; road y −23..−17. **+Y = backyard, −Y = road.**

### 6. Verify — always render a frame

Framing math is not framing. Render the new scene and *look at it*:

```sh
$B --background layout/layout.blend --factory-startup --python-expr "
import bpy
sc = bpy.data.scenes['<code>']
bpy.context.window.scene = sc
sc.frame_set(sc.frame_start)
sc.render.filepath = '<scratchpad>/check_'
sc.render.resolution_percentage = 60
sc.render.use_sequencer = False   # 5.x: on render, not scene
bpy.ops.render.render(write_still=True, scene='<code>')"
```

A second render at `lens = 20` (don't save it) shows the surroundings, which is
how you confirm the subject is where the script says it is.

Then assert, headlessly: every scene's range matches its row; the new scene has
its camera / blocking / note / `<code>_blocking` collection and `property` at
identity; `layoutlib.shot_ready()` is True; and — the check that matters most —
**nothing pre-existing changed** (neighbouring blocking, hand-framed cameras,
Grease Pencil strokes).

## Don't

- Don't run `make_layout.py --force`, `conform_edit.py --force`, or
  `migrate_layout.py` at all. See the "which tools destroy work" table in
  `docs/handoff.md`.
- Don't move or re-instance the property to reframe — move the camera.
- Don't hand-edit `layout.blend` through the MCP bridge for structural work the
  scripts own; the scripts are re-runnable and the file is 227 KB of LFS binary.
- Don't pass `--force` to `conform_edit.py`. Its default run **updates in
  place** — safe, repeatable, and it preserves the file's UI, its markers and
  any hand-cut strips. `--force` is the from-scratch rebuild and throws all
  three away. After a retime, the default run is exactly what you want.
