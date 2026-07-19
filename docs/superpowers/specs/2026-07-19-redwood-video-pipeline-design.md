# Redwood Video — Project Pipeline Design

**Date:** 2026-07-19
**Status:** Approved decisions captured; pending user review of this spec.

## Context

`redwood_video` is an animated music video produced end-to-end in Blender. The track
is finished, the scope is ambitious (full song, 50+ shots, multiple characters and
environments), and the visual direction is a stylized clay look built on ClayPencil,
Clay Doh, and Grease Pencil. There is no prior project template to inherit — the one
earlier music video start (`music_videos/green_apple/`) only established a `refs/`
folder convention — so this project defines the template.

This document specifies the folder structure, the nine-phase workflow mapped onto it,
the Blender tools used at each phase, and the project conventions.

## Decisions

| Decision | Choice |
|---|---|
| Visual style | Clay/ClayPencil look (ClayPencil + Clay Doh + Grease Pencil, EEVEE) |
| Track status | Finished track; all timing derived from it |
| Scope | Full song, 50+ shots, multiple environments and characters |
| Edit & post | Entirely in Blender (VSE edit, compositor per-shot post) |
| Structure | Studio pipeline: organized by artifact type, phases live in docs |
| Versioning | git + git-LFS for `.blend`; renders and proxies ignored |
| Master render target | 1920×1080 @ 24 fps (per-shot 4K re-render possible later) |
| AI/library assets | Polyhaven freely; text-to-3D (Hyper3D/Hunyuan) and Sketchfab for blockout/draft geometry only — final geometry is resculpted into the clay style |

## Folder structure

```
redwood_video/
├── README.md                    # project map + phase checklist
├── docs/
│   ├── ideation/                # concept notes, influences, moodboard notes
│   ├── treatment/               # treatment.md, lyrics/structure breakdown
│   ├── shotlist.csv             # SOURCE OF TRUTH: sq, sh, description, start/end
│   │                            #   frame, duration, assets, status
│   ├── beatmap.csv              # generated: BPM → bar/beat → frame @ 24 fps
│   ├── pipeline.md              # conventions quick-reference
│   └── superpowers/specs/       # design docs (this file)
├── refs/                        # style refs, palette copy, video refs
├── audio/
│   ├── track/                   # final master (WAV)
│   └── stems/                   # optional stems for timing work
├── boards/
│   ├── boards.blend             # Grease Pencil storyboards (Storypencil scenes)
│   └── animatic/                # animatic VSE file + rendered animatic movies
├── assets/
│   ├── chars/<name>/<name>.blend    # one .blend per character
│   ├── props/<name>/<name>.blend
│   ├── envs/<name>/<name>.blend
│   ├── materials/clay_library.blend # Clay Doh-derived, palette-matched materials
│   └── blender_assets.cats.txt      # Asset Browser catalog
├── shots/
│   └── sq010/
│       └── sh010/
│           ├── sh010.blend      # links assets; anim + lighting + per-shot comp
│           └── playblast/       # viewport preview renders
├── render/
│   └── sq010_sh010/
│       └── v001/                # frame sequences (PNG; EXR for comp-heavy shots)
├── edit/
│   ├── edit.blend               # VSE master edit
│   └── proxies/
├── delivery/                    # ProRes master + H.264 encodes
└── tools/
    ├── shot_template.blend      # locked render settings, linked clay library
    ├── new_shot.py              # stamp out a shot from template + shotlist row
    ├── build_shots.py           # batch-generate shot files from shotlist.csv
    ├── render_shot.sh           # headless render of one shot / frame range
    ├── beatmap.py               # generate beatmap.csv from BPM + track length
    └── encode_delivery.sh       # FFmpeg presets for delivery/
```

## Phase workflow and tools

1. **Ideation → `docs/ideation/` + `refs/`.** Concept notes and image gathering.
   The shared Coolors palette (`../assets/colors/palette.scss`) is copied into
   `refs/` as the seed of the video's color script. No Blender work yet.

2. **Writing → `docs/treatment/`.** Treatment (what happens, section by section of
   the song), lyrics/structure breakdown, and the beat map: `tools/beatmap.py`
   converts BPM and track length into a bar/beat → frame table at 24 fps so shot
   boundaries snap to musical beats. `docs/shotlist.csv` is created here and is the
   machine-readable source of truth for everything downstream.

3. **Storyboarding → `boards/`.** Grease Pencil boards via **Storypencil**
   (Blender Studio's storyboard add-on; install from Blender Extensions if not
   bundled in the installed Blender version). Boards are GP scenes synced to a VSE
   edit cut against the real track — the storyboard *is* the animatic. Final shot
   durations flow from the animatic back into `shotlist.csv`.

4. **Asset production → `assets/`.** One `.blend` per asset, collections named to
   convention, registered in the Blender **Asset Browser** through the project
   catalog. Clay materials live in `materials/clay_library.blend`, built from
   **Clay Doh** and matched to the palette. **ClayPencil** for clay-styled GP
   characters/strokes; **World Blender Pro** for environment terrain;
   **Pro-Lighting Skies** HDRIs as lighting bases. Polyhaven (via MCP) for
   HDRIs/textures; text-to-3D and Sketchfab only for blockout meshes that get
   resculpted. Downstream files **link, never append**.

5. **Animation → `shots/`.** `tools/new_shot.py` creates `sqXXX/shXXX/shXXX.blend`
   from `shot_template.blend`: links the assets listed in the shotlist row, sets
   the frame range, loads the audio segment. Library overrides make linked
   characters animatable. The **gp_draw_transform** add-on assists GP animation.
   Playblasts go into the edit immediately, replacing animatic panels.

6. **Rendering → `render/`.** EEVEE, settings locked in `shot_template.blend` so
   all shots match: 1920×1080, 24 fps, AgX view transform (revisit during look-dev
   if the clay style wants Standard). Output as frame sequences (crash-safe,
   resumable), versioned `v001/`, `v002/`. Headless batch rendering via
   `tools/render_shot.sh`.

7. **Compositing →** per-shot compositor nodes inside each shot file (**Uber
   Compositor** toolkit), rendered into the same `render/<shot>/` versioning.
   Comp stays light for the clay/EEVEE look: glow, grade, vignette.

8. **Editing → `edit/edit.blend`.** VSE with the final track as the spine. Strips
   reference rendered frame sequences and are progressively upgraded: animatic
   panel → playblast → final render, one cut throughout production.

9. **Post → `delivery/`.** Final grade on the assembled edit (VSE modifiers or a
   final compositor pass), then `tools/encode_delivery.sh` produces a ProRes
   master and H.264/YouTube encodes via FFmpeg.

## Conventions

- **Naming:** `sq010`, `sh010`, increments of 10. Files and folders lowercase
  snake_case, no spaces.
- **Linking:** shots link collections from `assets/`; never append. Rig animation
  via library overrides.
- **Paths:** all blends use relative paths (`//../../assets/...`) so the project
  is portable.
- **Versioning:** git repo at project root. LFS tracks `*.blend`. Ignored:
  `render/`, `delivery/`, `edit/proxies/`, `shots/**/playblast/`, `*.blend1`,
  `*.blend@`. Prerequisite: `brew install git-lfs && git lfs install`
  (not yet installed as of this writing).
- **Status tracking:** `shotlist.csv` `status` column
  (`boarded → blocked → animated → rendered → comped → final`), mirrored by a
  phase checklist in `README.md`.
- **Review loop:** the edit is watchable end-to-end at every stage; playblasts and
  viewport screenshots (via the Blender MCP bridge) are the review medium between
  render versions.

## Claude/MCP integration

The Blender MCP bridge is already enabled for this project. Claude drives scene
setup, batch operations, Polyhaven/asset downloads, and visual review via viewport
screenshots. `tools/` scripts are runnable both headless (`blender --background
--python ...`) and via MCP. `shotlist.csv` is the interface Claude reads and edits
when creating shots or reporting status.

## Out of scope

- No external NLE or grading tool; if that changes, `render/` frame sequences are
  already the correct handoff format.
- No multi-user/collaboration conventions (solo project).
- Song production: the track is finished and treated as immutable input.

## Risks / notes

- **Storypencil availability:** moved to the Extensions platform in recent Blender
  versions; verify it installs on the project's Blender (4.4+ per Clay Doh
  requirement). Fallback: plain GP scenes + manual VSE animatic (same structure,
  slightly more manual syncing).
- **Blend file size under LFS:** environment files may grow large; keep heavy
  textures as external files (linked, not packed) to keep LFS churn reasonable.
- **50+ shot scale:** the per-shot ceremony (template, scripts, shotlist) is the
  mitigation, not the burden — resist hand-creating shot files.
