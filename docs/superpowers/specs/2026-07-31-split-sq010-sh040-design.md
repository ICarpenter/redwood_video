# Split sq010_sh040 + add the box guide — Design

**Date:** 2026-07-31
**Status:** Approved decisions captured; pending user review of this spec.

## Context

`sq010_sh040` ("garage unbox — NOT A TOY sticker pocketed", frames 410–572) is
carrying two distinct beats. The script row already says so out loud:

> Garage unbox frenzy — he's dragged the box in the FRONT, the rear door open onto
> the backyard (**establish the passthrough**). Packing peanuts everywhere. He peels
> the big "NOT A TOY" sticker off the box and pockets it — deliberately.

Splitting it gives each beat its own shot: the boy dragging the box up the drive into
the garage, then a reverse from the back yard looking in through the open rear door,
where he unpacks it. The reverse is what actually establishes the passthrough.

The box itself has never existed as a guide. It is referenced from sq010_sh020 (the
truck throws it) onward, so it is overdue regardless of this split.

Blocking is early: only `sq010_sh010` has strokes (119). Every other board is empty,
so this is the cheapest possible moment to restructure sq010.

## Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Cut point | Frame 491 | Beatmap bar 13 beat 1. Yields even 2-bar halves (81f + 82f), matching sh050 which is already an 82-frame 2-bar shot |
| Numbering | Insert `sh045` | Standard film practice; the tens gaps exist for this. Zero existing scenes renamed |
| Total span | Unchanged (410–572) | No downstream shot shifts; 34 later rows untouched |
| Box size | 1.10 × 0.90 × 1.20 m | Chest-to-eye on the 1.3 m boy — reads as a two-arm drag. Printer (0.9 × 0.9 × 1.4) ships on its side |
| Guide build path | New `--add=<name>` flag | Non-destructive; `--force` would rebuild all 9 prop guides. Reusable for every guide still to be authored |
| Reverse angle | Rotate the property instance 180°, camera fixed | Follows the established convention (sh010 rotZ −43.8°, sh030 rotZ +90°). Keeps the GP paper plane identical on every board |
| Board fix-ups | Two reusable tools, not a one-off script | `resync_boards.py` + `stage_boards.py`; 34 shots still to stage and re-time |

### Bar-numbering caveat

`script.md` counts bars one lower than `beatmap.csv` — script bar 10 ↔ beatmap bar 11
(frame 410). Verified against both endpoints of sh040. The cut at beatmap bar 13 is
therefore **script bar 12**. The script table uses exclusive bar ends (`010` is `0–4`,
`020` is `4–7`), so the new rows read `10–12` and `12–14`.

## 1. Shotlist and script

`docs/shotlist.csv` — row 040 edited, row 045 inserted after it:

```
010,040,boy drags the box up the drive into the garage,410,490,81,boy;box,scripted
010,045,reverse through garage from back yard - unbox and pocket the sticker,491,572,82,boy;box,scripted
```

`duration` is validated by `shotlib.read_shotlist` as `end - start + 1`:
490−410+1 = 81, 572−491+1 = 82. Both correct.

**Descriptions must contain no commas.** The file is unquoted CSV read by
`csv.DictReader`, so a comma inside `description` shifts every later column — `start_frame`
would receive a text fragment and `read_shotlist` would fail with
"start_frame/end_frame must be integers". Use a dash or "and" instead. The `assets`
column is semicolon-separated precisely to avoid this.

Both rows above were dry-run through `shotlib.read_shotlist` against a copy of the real
file before this spec was committed: 39 shots parse, durations validate, and the whole
timeline stays contiguous end-to-end with no gaps or overlaps. The comma variant was
confirmed to fail with the error described.

The `assets` column is blank on every existing row. Populating it here (`boy;box`) is a
deliberate small break with that precedent — it is the column's documented purpose and
these are the first two shots whose guide set is fully pinned down.

`docs/treatment/script.md` — the sq010 table row `040` becomes two rows. This is load
bearing, not just documentation: `make_boards.read_script_prompts` parses this table and
`make_boards.build_note` renders `cells[5]` as the board's on-screen note. A missing 045
row means a board with no note.

```
| 040 | 10–12 | 410–490 | 3.4s | Boy drags the big box up the drive and in through the garage FRONT door. Packing peanuts already trailing. |
| 045 | 12–14 | 491–572 | 3.4s | REVERSE — from the back yard, looking in through the open rear door: the passthrough established, road beyond. He tears the box open and peels the big "NOT A TOY" sticker off, pocketing it — deliberately. |
```

Note text is run through `make_boards.normalize`, which strips `**`, `♪`, and em/en
dashes for Blender's default font. Plain hyphens and straight quotes are safest.

## 2. The box guide

### Spec

`tools/guides.py` — one entry in `GUIDES`, inserted after `santa`:

```python
GuideSpec("box", PROPS_FILE, "props", 1.2),
```

### Builder

`tools/guide_assets.py` — uses only the existing `box()` primitive helper, so it makes no
`bpy.ops` calls and is safe to run against an already-open file:

```python
def build_box(c):
    # Shipping box for the printer. Flaps + a tape stripe give the silhouette a
    # definite top so it reads as a carton rather than a crate.
    box(c, "bx_body",   0.00, 0, 0.60, 1.10, 0.90, 1.20, "wood")
    box(c, "bx_tape",   0.00, 0, 1.20, 1.12, 0.10, 0.02, "white")
    box(c, "bx_flap_l", -0.28, 0, 1.21, 0.54, 0.88, 0.02, "wood")
    box(c, "bx_flap_r",  0.28, 0, 1.21, 0.54, 0.88, 0.02, "wood")
```

Registered as `BUILDERS["box"] = build_box`.

Invariants, checked against the existing tolerances:

| Check | Tolerance | Actual |
|---|---|---|
| `FEET_TOL` — min Z at floor | 0.03 | 0.00 (`bx_body` spans 0.00–1.20) |
| `CENTRE_TOL` — centre X on axis | 0.12 | 0.00 (widest part `bx_tape`, −0.56..+0.56) |
| `HEIGHT_TOL` — vs spec height | ±25% of 1.2 | 1.22 (flap tops) |

### The `--add=<name>` path

New non-destructive entry point in `guide_assets.py`, dispatched in `main()` alongside
`--check` and `--mark-property`:

```
"$BLENDER" --background --factory-startup --python-exit-code 1 \
    --python tools/guide_assets.py -- --add=box
```

Behaviour:

1. Resolve the name via `guides.guide_by_name`; exit non-zero if unknown, or if it
   resolves to `property` (marked in place by `--mark-property`, never built).
2. Open the spec's `.blend`.
3. **Exit non-zero if the collection already exists** — never silently overwrite.
4. Build into a new collection linked to the scene collection, matching
   `build_guide_file`'s structure.
5. `asset_mark()` and set `catalog_id` from `guides.CATALOGS`.
   (`catalog_simple_name` is read-only on Blender 5.1.2 — setting `catalog_id` alone
   satisfies the asset contract, per the existing comment in `build_guide_file`.)
6. Run `check_structural` and `check_dimensions` on just that spec.
7. Save in place with `relative_remap=True`.

The nine existing prop collections are never touched.

### Test updates

`tools/tests/test_guides.py` hard-codes counts that this change invalidates:

| Assertion | From | To |
|---|---|---|
| `len(guides.GUIDES)` | 12 | 13 |
| `len(guides_for_file(PROPS_FILE))` | 9 | 10 |
| `len(guides.DROPPABLE)` | 13 | 14 |

Add a case asserting `guide_by_name("box")` resolves to `PROPS_FILE` / catalog `props`.

## 3. Boards staging

### Scene creation

`make_boards.py` with **no** `--force` adds scenes for new shotlist rows and leaves
existing scenes untouched, so it creates `sq010_sh045` (camera, GP board, note, empty
`sq010_sh045_guides` collection) without risking the 119 strokes on sh010.

Two things it will not do:

- **It will not correct sh040's frame range.** That scene already exists, so it is
  skipped entirely; `frame_end` stays 572 and must be set to 490.
- **It will not stage guides.** Those are dropped per shot.

Both gaps are closed by two new headless tools, run after `make_boards.py`.

### `tools/resync_boards.py`

Reads `docs/shotlist.csv` as the source of truth and, for every board scene that already
exists, resets `frame_start` / `frame_end` to match its row. It fixes sh040 today and any
future re-time without knowing about this split specifically. Frame ranges only: no scene
creation, no deletion, no GP data, no guide changes. Reports each scene it changed.

### `tools/stage_boards.py`

Mirrors the shape of `stage_property.py` — a declarative table, linked collection
instances, safe to re-run:

```python
STAGING = {
    "sq010_sh040": [
        ("box", guides.PROPS_FILE, (1.20, -4.60, -1.20), 0),
    ],
    "sq010_sh045": [
        ("property", guides.PROPERTY_FILE, (-10.00, 6.00, -1.22), 180),
        ("boy",      guides.CAST_FILE,     (-0.80,  5.00, -1.22),   0),
        ("box",      guides.PROPS_FILE,    ( 0.60,  4.60, -1.22),   0),
    ],
}
```

**It must be additive, not idempotent-by-rebuild.** This is the one place this design can
destroy existing work. `stage_property.py` is idempotent by clearing and rebuilding its
`blocking` collection, and copying that behaviour here would be wrong: sh010, sh020,
sh030 and sh040 all hold guides the user has already positioned by hand (sh010's property
at rotZ −43.8°, sh030's at +90°, sh040's `boy.001` at y −5.14). Clearing and rebuilding
would reset every one of those to a table value.

Required semantics:

- For each `(scene, guide)` pair, **skip entirely if an instance of that collection is
  already present** in the scene's guides collection. Leave its transform untouched.
- Only create instances that are missing, at the table's transform.
- Match by `instance_collection.name`, **not** by object name — Blender auto-suffixes
  instance objects, so the existing ones are called `property.003`, `boy.001`, and a
  name comparison would miss them and produce duplicates.
- Link into the scene's `<scene>_guides` collection, creating it via
  `guides.guides_collection_name` if absent.
- Report created vs. skipped per scene.

Re-running is therefore a no-op once a shot is staged, which makes it safe to leave in
the pipeline as new shots get added. Framing is still finished by eye in the UI; the
table only provides a sane starting position.

### Guide placement

Starting transforms — values to nudge by eye, not final framing:

| Shot | Instance | Location | rotZ |
|---|---|---|---|
| sh040 | `box` (new) | (+1.20, −4.60, −1.20) | 0° |
| sh045 | `property` | (−10.00, +6.00, −1.22) | **180°** |
| sh045 | `boy` | (−0.80, +5.00, −1.22) | 0° |
| sh045 | `box` | (+0.60, +4.60, −1.22) | 0° |

sh040 already has `property.003` (rotZ 0°, x +9.91) and `boy.001` staged; only the box
is added.

### Why those numbers work

Property-local geometry: garage x −13..−7 (centre −10), rear door y +1.50..+3.80, front
door y −3.80..−1.50, driveway y −14..−3 running out to the road.

At rotZ 180° with offset (−10.0, +6.0, −1.22), world space becomes:

| Element | World Y | Reads as |
|---|---|---|
| Rear door | +2.20..+4.50 | nearest camera, the opening we look through |
| Garage interior | +3.00..+9.00 | boy and box live here |
| Front door | +7.50..+9.80 | far opening |
| Driveway | +9.00..+20.00 | running away toward the road |

(The garage shell is local y −3..+3, symmetric about its centre, so the 180° rotation
leaves its span unchanged before the +6.0 offset. The doors sit proud of those faces at
local ±1.50..±3.80, which is why they land asymmetrically.)

Garage centre lands at world x 0.00. Camera sits at (0, −10, 0), so the rear door is
12.2 m out; a 50 mm lens on a 36 mm sensor covers 12.2 × 0.36 × 2 = 8.8 m of width there
against the garage's 6 m, framing with margin. Vertical half-height is 2.47 m: floor at
−1.22 and garage top at +1.68 sit inside frame, roof ridge at +2.88 clips off the top,
which reads as interior.

All three sh045 guides land at y > 0, i.e. behind the GP paper plane at the origin, so
strokes overlay them rather than being occluded.

sh040 is different and deliberately so: its existing `boy.001` is staged at y −5.14, in
*front* of the paper, as a foreground figure. The new box is placed at y −4.60 to sit at
that same depth beside him. Guides in front of the paper will occlude strokes drawn on
it, so this shot wants X-ray or wireframe display while drawing.

## Verification

1. `python3 -m unittest discover tools/tests` — guide counts and shotlist parsing.
2. `shotlib.read_shotlist(docs/shotlist.csv)` parses clean — this validates 3-digit
   codes, `duration == end - start + 1`, and duplicate shot codes.
3. `guide_assets.py -- --check` — builds cast + props to a temp dir and asserts
   dimensions on all 13 guides including the box.
4. Headless assertions against `boards/boards.blend`:
   - `sq010_sh040` range is 410–490
   - `sq010_sh045` exists, range 491–572, has `_board` / `_note` / `_guides`
   - `sq010_sh045_guides` contains property (rotZ 180°), boy, box
   - `sq010_sh040_guides` now also contains a box instance
5. **Nothing pre-existing was clobbered** — the check that matters most:
   - `sq010_sh010` still has 119 strokes; total across all scenes still 119
   - `sq010_sh010` property still at rotZ −43.8°, `sq010_sh030` still at +90°
   - `sq010_sh040`'s `boy.001` still at y −5.14
   - every other shot's `frame_start` / `frame_end` unchanged
6. Re-run `stage_boards.py` and confirm it reports 0 created / all skipped, and that no
   duplicate instances appeared.
7. `box` appears in the Asset Browser under `guides/props` and drops via the
   `redwood_guides` add-on.

## Run order

Blender closed throughout:

```
1. edit docs/shotlist.csv + docs/treatment/script.md
2. edit tools/guides.py, tools/guide_assets.py, tools/tests/test_guides.py
3. guide_assets.py -- --check          # box passes dimension checks
4. guide_assets.py -- --add=box        # writes assets/props/props.blend
5. make_boards.py                      # no --force; creates sq010_sh045 only
6. resync_boards.py                    # sh040 -> 410-490
7. stage_boards.py                     # additive guide placement
8. verification pass
```

Steps 4 and 5 write `.blend` files tracked by git-LFS; commit after verification.

## Operational constraint

`make_boards.py` writes `boards/boards.blend` headlessly. Blender must be **closed**
for the whole run or an open session's save will clobber it. Confirmed closed before
this spec was written; `boards.blend` last saved 2026-07-31 10:29.

## Out of scope

- Drawing any strokes on either board.
- Re-timing anything outside 410–572; every other shot keeps its frames.
- The sq010_sh020 truck animation (retimed by hand since; untouched here).
- Packing-peanut guides — drawn, not staged.
