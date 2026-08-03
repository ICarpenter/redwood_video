# redwood_video

A Blender music-video pipeline. **`docs/shotlist.csv` is the source of truth**;
everything else is materialized from it by scripts in `tools/`.

## This repo is tool-driven — read before improvising

Most requests here ("add a shot", "retime", "block out X", "reframe", "rebuild
the animatic") are **already implemented as a script**. Read the docs and run
the tool. Do not design a solution, write a spec, or hand-edit `layout.blend`
for something a script owns.

| Read this | For |
|---|---|
| `docs/tools.md` | what every script does, its flags, and the end-to-end flow |
| `docs/pipeline.md` | naming, frames, statuses, linking rules |
| `docs/layout.md` | the four layout invariants + the guide/blocking workflow |
| `docs/handoff.md` | Blender gotchas and the **which tools destroy work** table |
| `.claude/skills/shot-surgery/` | adding, splitting, retiming, or reframing a shot |

`docs/superpowers/specs/` are specs for *building the tools*. Using a tool is
not a design task and does not need one.

## Non-negotiables

- **Blender must be closed** before any headless script writes
  `layout/layout.blend` — an open session clobbers it on its next save. Check
  with `pgrep -f "Blender.app/Contents/MacOS/Blender"`.
- The property is linked at identity in every layout scene and never moves.
  **The camera is the only framing authority.** Blocking is world-space.
- Never run `migrate_layout.py`. Never pass `--force` to `make_layout.py` or
  `conform_edit.py` unless the user explicitly asks — see `docs/handoff.md`.
  Both tools' *default* runs are the safe, additive ones: `make_layout.py`
  adds and heals, `conform_edit.py` updates the edit in place.
- No commas in `docs/shotlist.csv` descriptions (unquoted CSV).
- Verify by **rendering a frame and looking at it**, not by trusting the math.
- Blends are git-LFS. Commit explicit paths; never `git add -A`.
