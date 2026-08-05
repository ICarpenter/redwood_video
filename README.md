# redwood_video

An animated music video produced end-to-end in Blender — **Mid-Century Print**,
a flat-gouache poster look built on hand-painted tilt dabs (`MCM_Toon`), cut to
a finished track. Style locked 2026-08-05; see `docs/treatment/style.md`.

- **Start here:** `docs/handoff.md` — project state, conventions, next actions
- Design spec: `docs/superpowers/specs/2026-07-19-redwood-video-pipeline-design.md`
- Conventions: `docs/pipeline.md`
- Tools & production flow: `docs/tools.md`
- Layout & drawing guides: `docs/layout.md`
- Source of truth for shots: `docs/shotlist.csv`

## Directory layout

| Path | What lives there |
|---|---|
| `docs/` | ideation, treatment, shotlist.csv, beatmap.csv, pipeline docs |
| `refs/` | style references, palette |
| `audio/track/` | the final track (drop the WAV here) |
| `layout/` | `layout.blend` — one camera-driven scene per shot: camera, world-space blocking, optional Grease Pencil paper |
| `assets/` | chars/, props/, envs/, materials/ — linked libraries |
| `shots/` | on-demand per-shot exports (`sq010/sh010/sh010.blend`) — not every shot has one |
| `render/` | versioned frame sequences (gitignored) |
| `edit/` | VSE master edit |
| `delivery/` | final encodes (gitignored) |
| `tools/` | pipeline scripts + shot template |

## Phases

- [x] 1. Ideation — concept notes in `docs/ideation/`, refs into `refs/`
- [x] 2. Writing — treatment in `docs/treatment/`, beat map, first shotlist
- [ ] 3. Layout & animatic — `layout/` (camera + world-space blocking +
      optional Grease Pencil), durations → shotlist
      *(in progress: 39 layout scenes seeded, 1 shot drawn, 4 blocked out,
      slug animatic cut)*
- [ ] 4. Asset production — `assets/` registered in the Asset Browser
      *(started: property blockout — see `docs/treatment/site.md`)*
- [ ] 5. Animation — export a layout scene to `shots/` on demand with
      `tools/export_shot.py`, playblasts into edit
- [ ] 6. Rendering — `tools/render_shot.sh` per shot
- [ ] 7. Compositing — per-shot compositor (Uber Compositor)
- [ ] 8. Editing — `edit/edit.blend` against the track
- [ ] 9. Post & delivery — grade + `tools/encode_delivery.sh`

## Quickstart

```sh
# after dropping the track into audio/track/:
python3 tools/beatmap.py --bpm <BPM> --length <SECONDS>  # → docs/beatmap.csv
"$BLENDER" --background --factory-startup --python-exit-code 1 \
    --python tools/make_layout.py                        # seed layout/layout.blend
"$BLENDER" --background --python-exit-code 1 \
    --python tools/export_shot.py -- --shot sq010_sh010   # only once a shot earns its own file
tools/render_shot.sh 010 010                              # render that exported shot
```

Blender is expected at `/Applications/Blender.app/Contents/MacOS/Blender`;
override with `$BLENDER`.
