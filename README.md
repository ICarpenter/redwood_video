# redwood_video

An animated music video produced end-to-end in Blender — stylized clay look
(ClayPencil + Clay Doh + Grease Pencil), cut to a finished track.

- Design spec: `docs/superpowers/specs/2026-07-19-redwood-video-pipeline-design.md`
- Conventions: `docs/pipeline.md`
- Source of truth for shots: `docs/shotlist.csv`

## Layout

| Path | What lives there |
|---|---|
| `docs/` | ideation, treatment, shotlist.csv, beatmap.csv, pipeline docs |
| `refs/` | style references, palette |
| `audio/track/` | the final track (drop the WAV here) |
| `boards/` | Grease Pencil storyboards + animatic |
| `assets/` | chars/, props/, envs/, materials/ — linked libraries |
| `shots/` | per-shot .blends (`sq010/sh010/sh010.blend`) |
| `render/` | versioned frame sequences (gitignored) |
| `edit/` | VSE master edit |
| `delivery/` | final encodes (gitignored) |
| `tools/` | pipeline scripts + shot template |

## Phases

- [ ] 1. Ideation — concept notes in `docs/ideation/`, refs into `refs/`
- [ ] 2. Writing — treatment in `docs/treatment/`, beat map, first shotlist
- [ ] 3. Storyboards & animatic — `boards/` (Storypencil), durations → shotlist
- [ ] 4. Asset production — `assets/` registered in the Asset Browser
- [ ] 5. Animation — `shots/` via `tools/build_shots.py`, playblasts into edit
- [ ] 6. Rendering — `tools/render_shot.sh` per shot
- [ ] 7. Compositing — per-shot compositor (Uber Compositor)
- [ ] 8. Editing — `edit/edit.blend` against the track
- [ ] 9. Post & delivery — grade + `tools/encode_delivery.sh`

## Quickstart

```sh
# after dropping the track into audio/track/:
python3 tools/beatmap.py --bpm <BPM> --length <SECONDS>  # → docs/beatmap.csv
python3 tools/build_shots.py --dry-run                   # what would be created
python3 tools/build_shots.py                             # create missing shots
tools/render_shot.sh 010 010                             # render one shot
```

Blender is expected at `/Applications/Blender.app/Contents/MacOS/Blender`;
override with `$BLENDER`.
