# Pipeline conventions — quick reference

Full rationale: `superpowers/specs/2026-07-19-redwood-video-pipeline-design.md`
What each tool does and the end-to-end flow: `tools.md`

## Frames & timing
- 24 fps, 1920×1080, AgX view transform. Locked in `tools/shot_template.blend`.
- Timeline frame 1 = song time 0. All shot start/end frames are song-global.
- `docs/beatmap.csv` maps bar/beat → timeline frame
  (`python3 tools/beatmap.py --bpm <BPM> --length <SECONDS>`).

## Naming
- Sequences `sq010`, shots `sh010` — 3 digits, increments of 10.
- Lowercase snake_case everywhere; no spaces.

## Shotlist (`docs/shotlist.csv`) — source of truth
Columns: `sq,sh,description,start_frame,end_frame,duration,assets,status`
- `start_frame`/`end_frame` inclusive, song-global. `duration` = end−start+1
  (validated; may be left blank).
- `assets`: `;`-separated paths under `assets/`, e.g. `chars/redwood;envs/forest`.
- `status` flow: `boarded → blocked → animated → rendered → comped → final`.

## Assets
- One .blend per asset at `assets/<kind>/<name>/<name>.blend`.
- Each asset blend exposes ONE root collection named `<name>` — that is what
  shots link. Shots LINK, never append; rig animation via library overrides.
- Clay materials: `assets/materials/clay_library.blend` (Clay Doh-derived,
  palette-matched — built during look-dev).
- Polyhaven assets: fine. AI text-to-3D / Sketchfab: blockouts only, resculpt
  into the clay style before a shot renders.

## Shots
- All missing shots: `python3 tools/build_shots.py`
- `--force` rebuilds existing shots from the empty template — it OVERWRITES animation work and asks for confirmation.
- One shot:
  `"$BLENDER" --background tools/shot_template.blend --python-exit-code 1 \
      --python tools/new_shot.py -- --sq 010 --sh 010`
- Playblasts: viewport render into `shots/sqXXX/shXXX/playblast/` (gitignored).

## Render
- `tools/render_shot.sh <sq> <sh> [vNNN]` → `render/sqXXX_shXXX/vNNN/` PNGs.
- Frame range comes from `docs/shotlist.csv` at render time — retiming a row
  re-renders correctly; the blend's stored range is a creation-time default.
- Versions auto-increment by default. Pass an explicit vNNN only to resume or re-render into that version — it overwrites those frames.

## Edit & delivery
- `edit/edit.blend` (VSE): track on channel 1, shots as image-sequence strips,
  upgraded animatic → playblast → final render without changing the cut.
- Seed/rebuild it with `tools/conform_edit.py` (places every rendered shot's
  latest version at its song-global frames; refuses to overwrite a hand-cut
  edit without `--force`).
- The edit scene uses the **Standard** view transform — shot renders already
  carry AgX baked in; AgX in the edit would apply twice and wash everything out.
- `tools/encode_delivery.sh <frames_dir> <audio> <name>` → `delivery/`
  ProRes master + H.264 (needs `brew install ffmpeg`).

## Git
- LFS: blends, audio, images, video (see `.gitattributes`).
- Ignored: `render/`, `delivery/`, playblasts, proxies, `*.blend1`.
- Commit explicit paths; never `git add -A`.
