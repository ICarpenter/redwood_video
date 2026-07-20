# redwood_video — handoff

State of the project for anyone (or any future session) picking it up cold.
Written 2026-07-20.

## What this is

An animated music video for **`guns`** (`audio/track/guns.wav` — 4:15,
141 BPM, 150 bars), produced end-to-end in Blender 5.1.2 with a stylized
**claymation** look: bright colors, white-trash Americana, Spike & Mike
energy. A heartland kid 3D-prints a machine gun, and by sundown has
dragged his mom and the county sheriff into a three-way backyard war.
38 shots. Solo production.

Read next, in order: `treatment/story.md` (what happens),
`treatment/script.md` (shot by shot, frame-locked), `treatment/site.md`
(where everything is), `pipeline.md` (conventions), `tools.md` (the
machinery).

## Where we are

| Phase | Status |
|-------|--------|
| 1. Ideation | done |
| 2. Writing — story, script, lyrics, sections | done |
| 3. Storyboards / animatic | **in progress** — infrastructure built, drawing not started |
| 4. Asset production | started — property blockout only |
| 5–9. Animation → delivery | not started (pipeline built and validated end-to-end) |

The whole film is **watchable right now** as a slug animatic:
`edit/edit.blend` holds the track, 9 section markers, and 38 titled text
strips cut to the music. It upgrades in place as boards and renders land.

## Five conventions that will bite you if you forget them

1. **Timeline: frame 1 = song time 0, 24 fps.** Every shot's frame range
   is song-global, so a shot's keyframes and its strip position are the
   same numbers. The song ends dead on the last chorus hit at **bar 111 /
   frame 4534**; frames 4535+ are audio tail only.
2. **Bars are counted from 0** in `sections.csv` and the treatment docs
   (matching how the song structure was written). `beatmap.csv`'s bar
   column is 1-indexed — its bar 1 is our bar 0.
3. **`docs/shotlist.csv` is the source of truth.** Tools read it; nothing
   invents structure. Render boundaries come from it *at render time*, so
   retiming a row re-renders correctly without recreating the shot file.
4. **Link, never append.** Assets live at
   `assets/<kind>/<name>/<name>.blend` exposing one root collection named
   `<name>`. Animate linked rigs via library overrides.
5. **The edit uses the Standard view transform, not AgX.** Shot renders
   already have AgX baked in; applying it again in the edit washes
   everything out (measured: 25 dB PSNR vs 102 dB when passed through).

Plus the compass, from `treatment/site.md`: **+Y = backyard, −Y = road,
sun rises east, sets west** — the final sprint runs west into the sunset,
mirroring the sunrise.

## Blender 5.1.2 gotchas already paid for

- **Storypencil does not work on Blender 5.x** (upstream rewrite pending).
  Boards are plain Grease Pencil scenes; our conform does the assembly.
- `SequenceEditor.sequences` → **`.strips`** (use a `hasattr` fallback).
- `strips.new_effect()` takes **`length=`**, not `frame_end=`.
- `action.fcurves` is **gone** — actions are slotted
  (`action.layers[0].strips[0].channelbag(slot).fcurves`).
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
| `shotlib.py` | shared: validated shotlist/sections parsing, beat math, paths, versions, track/Blender discovery. Imported by everything, incl. in-Blender scripts |
| `beatmap.py` | BPM + length → `docs/beatmap.csv` (bar/beat → frame) |
| `make_template.py` | builds `shot_template.blend` (1080p24, EEVEE, AgX, PNG 16-bit) |
| `make_boards.py` | seeds `boards/boards.blend` — one GP scene per shot, white world, starter keyframe, script prompt as an in-scene note, track for scrubbing |
| `new_shot.py` / `build_shots.py` | stamp shot blends from the template: frame range, audio, linked assets. `--force` confirms before overwriting |
| `render_shot.sh` | headless render → `render/<code>/vNNN/`, auto-incrementing |
| `conform_edit.py` | rebuilds `edit/edit.blend`: track + section markers + best tier per shot (render → board → slug) |
| `encode_delivery.sh` | ProRes HQ master + H.264 into `delivery/` |
| `blockout_property.py` | rebuilds the greybox property + 6 preview cameras |

Tests: `python3 -m unittest discover -s tools/tests -v` (29 passing).

Regenerable, therefore gitignored: `render/`, `delivery/`, playblasts,
proxies, **and `edit/edit.blend`** (rebuild with `conform_edit.py`).

## Open decisions

- **Backyard scale.** Currently ~22 m deep. Generous — good for
  firing-squad wides, but the three-way firefight may play funnier
  cramped. Cheap to change now, expensive after boards.
- **Front yard depth** — governs how long the cruiser is on screen before
  the tire blows.
- **Board fidelity** — one held drawing per shot, or 2–3 poses for the
  action beats (obliteration, sandwich-save, firefight, sprint).
- **Verse 2 gag density** — the script flags it as the hottest section
  with an explicit cut-first order (hubcap skeet → package football →
  flowerbed arm). The animatic arbitrates; don't cut on taste beforehand.
- **Production design** — nothing designed yet beyond massing: siding,
  porch clutter, junk, terrain, and the clay look itself.

## Next actions

1. **Board the film.** Open `boards/boards.blend`, pick a scene by shot
   code, draw. A rough scribble pass over all 38 first — polish later.
2. **Conform and watch** (`conform_edit.py -- --force`). Boards graduate
   from slugs automatically once a scene has real strokes.
3. **Arbitrate verse 2** with the animatic, then firm durations and move
   statuses `scripted → boarded`.
4. **Design pass on the property** once the boards say what the camera
   actually needs.
5. Then asset production proper: clay material library, characters.

## Working notes

- The Blender MCP bridge is live: a session can inspect and fix the
  *open* Blender file directly. Prefer that over writing to a file the
  artist has open. Save in Blender before asking for a conform or commit.
- GitHub LFS carries `.blend`, audio, images, video. GitHub's LFS
  endpoint has thrown 502s during incidents — retry rather than
  re-architect. Lock verification is disabled (solo repo).
- Work happens on branches with PRs: scaffold (#1), track+beatmap (#2),
  story/script (#3), boards infrastructure (#4), env blockout (this one).
  PR #5 (a test sunrise board) was scrapped — the strokes survive on the
  `board-sunrise` branch if ever wanted.
