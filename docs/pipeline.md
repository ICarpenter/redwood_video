# Pipeline conventions — quick reference

Full rationale: `superpowers/specs/2026-07-19-redwood-video-pipeline-design.md`
What each tool does and the end-to-end flow: `tools.md`

## Frames & timing
- 24 fps, 1920×1080, AgX view transform. Locked in `tools/shot_template.blend`.
- Timeline frame 1 = song time 0. All shot start/end frames are song-global.
- `docs/beatmap.csv` maps bar/beat → timeline frame
  (`python3 tools/beatmap.py --bpm <BPM> --length <SECONDS>`).
- `docs/sections.csv` maps song sections (intro/verse/chorus/…) to bars and
  frames; `conform_edit.py` turns them into timeline markers in the edit.
  NOTE: its bar columns count from 0 at song start (matching the written
  structure in `treatment/lyrics.md`); beatmap.csv's bar column is 1-indexed.

## Naming
- Sequences `sq010`, shots `sh010` — 3 digits, increments of 10.
- Lowercase snake_case everywhere; no spaces.

## Shotlist (`docs/shotlist.csv`) — source of truth
Columns: `sq,sh,description,start_frame,end_frame,duration,assets,status`
- `start_frame`/`end_frame` inclusive, song-global. `duration` = end−start+1
  (validated; may be left blank).
- `assets`: `;`-separated guide-registry names, validated against `guides.py`
  at parse time (e.g. `boy;box`) — planning metadata, not a link path; see
  "Assets" below.
- `status` flow: `scripted → boarded → blocked → animated → rendered → comped → final`.

## Assets
- **Single-asset files** (a character/prop built as a full asset) follow
  `assets/<kind>/<name>/<name>.blend`, exposing ONE root collection named
  `<name>` — that is what shots link. `property.blend` is the working
  example.
- **Guide libraries are the exception, deliberately:** `assets/chars/cast.blend`
  and `assets/props/props.blend` each hold many catalogued collections, one
  per guide, with no collection matching the filename — built by
  `guide_assets.py`, registered in `guides.py`. Nothing resolves a guide by
  path; `docs/shotlist.csv`'s `assets` column names guides from the
  registry and is validated against it at parse time. It's planning
  metadata — `export_shot.py` exports what a layout scene actually contains
  and never reads this column.
- Shots LINK, never append, either shape; rig animation via library overrides.
- Clay materials: `assets/materials/clay_library.blend` (Clay Doh-derived,
  palette-matched — built during look-dev).
- Polyhaven assets: fine. AI text-to-3D / Sketchfab: blockouts only, resculpt
  into the clay style before a shot renders.

## Layout
- The property is **linked at identity** (world origin, ground at `z=0`) in
  every layout scene, and never moves.
- The **camera is the only framing authority** — a different angle means a
  different camera transform, never a moved or rotated set.
- **Blocking is world-space** — a guide's transform says where that
  character or prop actually stands on the property.
- **Shot files are a derived export, not a stage** — nothing is required to
  pass through `shots/`. Most shots never need one.

Full detail, including drawing guides and the drop-on-ground rule for the
Redwood Guides add-on: `layout.md`.

## Shots
- Layout scenes already carry everything a shot needs (camera, blocking, the
  linked property, the frame range) — a `.blend` under `shots/` is an
  on-demand export, not a required stage.
- Export one when it earns its own file (a per-shot compositor, a sim, a 4K
  re-render, lighting that must not touch its neighbours):
  `"$BLENDER" --background --python-exit-code 1 \
      --python tools/export_shot.py -- --shot sq010_sh040 [--force]`
- Export is one-way: afterwards the shot file is authoritative and the
  layout scene is a stale reference (`conform_edit` flags it as such).
- Playblasts: viewport render into `shots/sqXXX/shXXX/playblast/` (gitignored).

## Render
- `tools/render_shot.sh <sq> <sh> [vNNN]` → `render/sqXXX_shXXX/vNNN/` PNGs.
- Frame range comes from `docs/shotlist.csv` at render time — retiming a row
  re-renders correctly; the blend's stored range is a creation-time default.
- Versions auto-increment by default. Pass an explicit vNNN only to resume or re-render into that version — it overwrites those frames.

## Edit & delivery
- `edit/edit.blend` (VSE): track on channel 1, shots as image-sequence strips,
  upgraded animatic → playblast → final render without changing the cut.
- Seed/rebuild it with `tools/conform_edit.py`. Per shotlist row it places the
  best available tier at the shot's song-global frames: rendered frames
  (latest vNNN) → layout scene from `layout/layout.blend` (scene named by
  shot code, linked) → slug (text strip). Refuses to overwrite a hand-cut edit
  without `--force`.
- The three tiers are **render → layout → slug**. A layout scene earns its
  strip once it has real Grease Pencil strokes **or** world-space blocking —
  either one makes a shot worth watching before the other is done. Seed/extend
  layout scenes with `tools/make_layout.py`, one scene per shot, named
  `sqXXX_shXXX`. (Storypencil does NOT work on Blender 5.x — rewrite pending
  upstream — so layout scenes are plain camera + Grease Pencil scenes; our
  conform does the assembly.)
- The edit scene uses the **Standard** view transform — shot renders already
  carry AgX baked in; AgX in the edit would apply twice and wash everything out.
- `tools/encode_delivery.sh <frames_dir> <audio> <name>` → `delivery/`
  ProRes master + H.264 (needs `brew install ffmpeg`).

## Git
- LFS: blends, audio, images, video (see `.gitattributes`).
- Ignored: `render/`, `delivery/`, playblasts, proxies, `*.blend1`.
- Commit explicit paths; never `git add -A`.
