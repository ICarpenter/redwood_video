#!/usr/bin/env python3
"""Build or update edit/edit.blend: track on channel 1, one strip per
docs/shotlist.csv row on channel 2 at its song-global position, choosing the
best available tier per shot:

  1. rendered frames (latest render/<code>/vNNN/) -> image strip
  2. layout scene named <code> in layout/layout.blend -> linked scene strip
  3. otherwise -> slug (text strip: shot code + description)

So the edit is watchable at every stage: slugs -> layout -> renders, same
cut throughout.

Two modes:

* **update in place (default when the file exists)** — opens edit.blend and
  reconciles channel 2 against the shotlist: retimes strips whose frames
  moved, replaces those whose tier changed, adds missing ones, drops strips
  for shots that left the shotlist. Everything else is left alone — the
  file's UI, the sound strip, and anything you have hand-cut on channels 3+.
  Markers are only ADDED, never moved (see sync_markers).

* **build from scratch (--force, or no file yet)** — DESTRUCTIVE. Replaces
  the whole edit, including the file's UI: the rebuild is saved out of a
  --factory-startup session, so workspaces and screens go too. The stock
  Video Editing workspace is appended back (see
  ensure_video_editing_workspace) but customised panel layouts are not
  preserved. Once you have hand-cut work, stay out of this mode.

Project render settings (resolution, fps, colour management) are re-applied
in BOTH modes: they are meant to live in exactly one place
(layoutlib.apply_project_settings), so drift there is a bug, not a
preference.

Run:
  "$BLENDER" --background --factory-startup --python-exit-code 1 \
      --python tools/conform_edit.py [-- --force] [-- --dry-run]
"""
import re
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shotlib
import layoutlib


VIDEO_EDITING_TEMPLATE = ("startup", "bl_app_templates_system",
                          "Video_Editing", "startup.blend")

TIER_RENDER, TIER_LAYOUT, TIER_SLUG = "render", "layout", "slug"

_STRIP_RE = re.compile(r"^(sq\d{3}_sh\d{3})_(.+)$")


def ensure_video_editing_workspace():
    """Append Blender's stock Video Editing workspace.

    A from-scratch build runs under --factory-startup, whose 11 workspaces do
    NOT include Video Editing (it is normally added by hand via the workspace
    "+" menu). Saving that session wrote factory UI over the edit file on
    every regen, so the VSE workspace had to be re-added after each run.

    Appending the stock template gives exactly what the "+" menu would:
    screen areas FILE_BROWSER / SEQUENCE_EDITOR / PROPERTIES /
    SEQUENCE_EDITOR. Non-fatal — a missing or renamed template must not fail
    a conform, since the edit itself is still correct without it.

    Two things this deliberately does NOT do, both verified rather than
    assumed:

    - It cannot make the file OPEN in that workspace. `window.workspace = ws`
      is silently ignored under --background (it reads back as "Layout"), so
      the file still opens on Layout and the VSE tab needs one click.
    - It restores the *stock* workspace, not a customised one. Panel sizes
      and editor tweaks inside it are still lost on a from-scratch build.
      Update-in-place is what preserves those, by never touching the UI.
    """
    if any(w.name == "Video Editing" for w in bpy.data.workspaces):
        return True
    template = Path(bpy.utils.system_resource("SCRIPTS")).joinpath(
        *VIDEO_EDITING_TEMPLATE)
    if not template.exists():
        print(f"warning: no Video Editing template at {template}; "
              "add the workspace by hand")
        return False
    with bpy.data.libraries.load(str(template), link=False) as (src, dst):
        if "Video Editing" not in src.workspaces:
            print("warning: template has no 'Video Editing' workspace")
            return False
        dst.workspaces = ["Video Editing"]
    return True


# --------------------------------------------------------------------------
# tier selection — shared by both modes so they cannot disagree
# --------------------------------------------------------------------------

def link_layout_scenes(root, codes):
    """Link layout scenes for `codes`, returning {code: scene} for ready ones.

    Safe to call on an already-open edit.blend: scenes already linked from a
    previous run are reused rather than linked twice. Readiness is evaluated
    against layout.blend as it is on disk right now, so a shot that has since
    been blocked out is picked up, and one that lost its blocking falls back
    to a slug.
    """
    layout_blend = root / "layout" / "layout.blend"
    if not layout_blend.exists():
        return {}
    have = {sc.name for sc in bpy.data.scenes if sc.library is not None}
    want = [c for c in codes if c not in have]
    if want:
        with bpy.data.libraries.load(str(layout_blend), link=True) as (src, dst):
            dst.scenes = [name for name in src.scenes if name in want]
    ready = {sc.name: sc for sc in bpy.data.scenes
             if sc.library is not None and sc.name in codes
             and layoutlib.shot_ready(sc)}
    stale = sorted(name for name, sc in ready.items() if sc.get("exported"))
    if stale:
        print(f"note: {len(stale)} layout scene(s) already exported to "
              f"shot files — their blocking may be stale: {', '.join(stale)}")
    return ready


def latest_render(shot, root):
    """(version_name, [frame paths]) for the newest render, or (None, [])."""
    rdir = shotlib.render_dir(shot.sq, shot.sh, root)
    if not rdir.is_dir():
        return None, []
    versions = sorted(d for d in rdir.iterdir()
                      if d.is_dir() and d.name.startswith("v"))
    if not versions:
        return None, []
    frames = sorted(versions[-1].glob("*.png"))
    return (versions[-1].name, frames) if frames else (None, [])


def desired_tier(shot, root, layout_scenes):
    """(tier, key, payload). `key` is the strip-name suffix and the identity
    used to decide whether an existing strip is still current — so a render
    version bump (v001 -> v002) reads as a tier change and rebuilds."""
    version, frames = latest_render(shot, root)
    if frames:
        return TIER_RENDER, version, frames
    if shot.code in layout_scenes:
        return TIER_LAYOUT, TIER_LAYOUT, layout_scenes[shot.code]
    return TIER_SLUG, TIER_SLUG, None


def create_strip(strips, shot, tier, key, payload, channel=2):
    """Create the strip for one shot at its shotlist frames, on `channel`."""
    name = f"{shot.code}_{key}"
    if tier == TIER_RENDER:
        strip = strips.new_image(name=name, filepath=str(payload[0]),
                                 channel=channel, frame_start=shot.start_frame)
        for f in payload[1:]:
            strip.elements.append(f.name)
        if len(payload) != shot.duration:
            print(f"warning: {shot.code} has {len(payload)} rendered frame(s) "
                  f"but the shotlist says {shot.duration}")
    elif tier == TIER_LAYOUT:
        strip = strips.new_scene(name=name, scene=payload, channel=channel,
                                 frame_start=shot.start_frame)
        # render the layout scene's camera view; its own sequencer (the
        # scrub-audio strip) must not feed the edit
        strip.scene_input = "CAMERA"
    else:
        strip = strips.new_effect(name=name, type="TEXT", channel=channel,
                                  frame_start=shot.start_frame,
                                  length=shot.duration)
        strip.text = f"{shot.code}\n{shot.description}"
        strip.font_size = 56
        strip.wrap_width = 0.8
    place_strip(strip, shot, channel)
    return strip


def needs_move(strip, shot):
    return (int(strip.frame_final_start) != shot.start_frame
            or int(strip.frame_final_duration) != shot.duration
            or strip.channel != 2)


def place_strip(strip, shot, channel=2):
    """Move/trim a strip onto the shot's frames, on `channel`."""
    strip.channel = channel
    strip.frame_start = shot.start_frame
    strip.frame_final_duration = shot.duration
    # a hand-trimmed strip has frame_final_start offset from frame_start;
    # compensate so the CUT lands on the shotlist frame either way
    drift = shot.start_frame - int(strip.frame_final_start)
    if drift:
        strip.frame_start = int(strip.frame_start) + drift


def split_strip_name(name):
    """('sq010_sh010', 'v001') for 'sq010_sh010_v001', else (None, None).

    Matches the shot-code SHAPE rather than the current shotlist, so a strip
    left behind by a shot that has since been deleted is still recognised as
    ours and can be removed. Matching against the live code list instead
    would make orphans invisible.
    """
    base = name.split(".")[0]          # drop Blender's auto-suffix
    match = _STRIP_RE.match(base)
    return (match.group(1), match.group(2)) if match else (None, None)


def sync_markers(scene, sections_csv):
    """Add missing section markers. Never moves one that already exists.

    The hand-placed markers in edit.blend are the measured truth about the
    recording — docs/sections.csv is downstream of them, not the other way
    round. Resetting them here would destroy exactly the work this file is
    the source of. Drift is reported so it can be pulled back into the CSV
    deliberately.
    """
    if not sections_csv.exists():
        return 0, []
    existing = {m.name: m for m in scene.timeline_markers}
    added, drift = 0, []
    for sec in shotlib.read_sections(sections_csv):
        marker = existing.get(sec.name)
        if marker is None:
            scene.timeline_markers.new(sec.name, frame=sec.start_frame)
            added += 1
        elif int(marker.frame) != sec.start_frame:
            drift.append((sec.name, int(marker.frame), sec.start_frame))
    return added, drift


# --------------------------------------------------------------------------
# modes
# --------------------------------------------------------------------------

def build_from_scratch(root, out, shots, track):
    scene = bpy.context.scene
    scene.name = "edit"
    # Standard, NOT AgX: shot renders already carry AgX baked in — the edit
    # must pass them through untouched or the transform applies twice
    layoutlib.apply_project_settings(scene, view_transform="Standard")

    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    se = scene.sequence_editor_create()
    strips = se.strips if hasattr(se, "strips") else se.sequences

    snd = strips.new_sound(name="track", filepath=str(track), channel=1,
                           frame_start=1)
    scene.frame_start = 1
    scene.frame_end = int(snd.frame_final_end) - 1

    layout_scenes = link_layout_scenes(root, {s.code for s in shots})

    counts = {TIER_RENDER: 0, TIER_LAYOUT: 0, TIER_SLUG: 0}
    for shot in shots:
        tier, key, payload = desired_tier(shot, root, layout_scenes)
        create_strip(strips, shot, tier, key, payload)
        counts[tier] += 1

    scene.timeline_markers.clear()
    marked, _ = sync_markers(scene, root / "docs" / "sections.csv")
    workspace = ensure_video_editing_workspace()

    out.parent.mkdir(exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out), relative_remap=True)
    print(f"conformed edit/edit.blend: track [1-{scene.frame_end}], "
          f"{counts[TIER_RENDER]} render / {counts[TIER_LAYOUT]} layout / "
          f"{counts[TIER_SLUG]} slug strip(s), {marked} section marker(s)"
          f"{', Video Editing workspace' if workspace else ''}")


def update_in_place(root, out, shots, dry_run):
    bpy.ops.wm.open_mainfile(filepath=str(out))
    scene = bpy.data.scenes.get("edit")
    if scene is None:
        sys.exit(f"error: {out} has no scene named 'edit'; "
                 "rebuild it with -- --force")
    se = scene.sequence_editor
    if se is None:
        sys.exit(f"error: {out} has no sequence editor; "
                 "rebuild it with -- --force")
    strips = se.strips if hasattr(se, "strips") else se.sequences

    layoutlib.apply_project_settings(scene, view_transform="Standard")
    layout_scenes = link_layout_scenes(root, {s.code for s in shots})

    # Match on NAME, across every channel — not "whatever is on channel 2".
    # A strip Blender bumped off channel 2 to dodge an overlap is still ours;
    # skipping it would silently duplicate that shot on the next run. Strips
    # that do not carry a shot code (hand-cut work, colour mattes, titles) are
    # never touched, whatever channel they sit on.
    known = {s.code for s in shots}
    existing = {}
    for strip in list(strips):
        code, key = split_strip_name(strip.name)
        if code is not None:
            existing[code] = (strip, key)

    # Two-pass placement. Strips are positioned on a scratch channel first and
    # only dropped to channel 2 once EVERY frame range is final. Placing them
    # one at a time on channel 2 makes a strip briefly overlap a neighbour that
    # has not been moved yet — Blender resolves that by bumping one of them to
    # another channel, which silently scattered the edit and produced bogus
    # "rows overlap" warnings on a shotlist that is perfectly contiguous.
    scratch = max((s.channel for s in strips), default=2) + 1

    added = retimed = replaced = removed = unchanged = 0
    parked = []
    for shot in shots:
        tier, key, payload = desired_tier(shot, root, layout_scenes)
        found = existing.get(shot.code)
        if found is not None:
            strip, old_key = found
            if old_key == key:
                if not needs_move(strip, shot):
                    unchanged += 1
                    continue
                print(f"  retimed  {shot.code} -> "
                      f"{shot.start_frame}-{shot.end_frame}")
                retimed += 1
                if not dry_run:
                    place_strip(strip, shot, scratch)
                    parked.append((strip, shot))
                continue
            print(f"  replaced {shot.code}: {old_key} -> {key}")
            replaced += 1
            if not dry_run:
                strips.remove(strip)
        else:
            print(f"  added    {shot.code} ({key}) at "
                  f"{shot.start_frame}-{shot.end_frame}")
            added += 1
        if not dry_run:
            parked.append((create_strip(strips, shot, tier, key, payload,
                                        scratch), shot))

    for strip, shot in parked:
        strip.channel = 2
        # now that every range is final, a bump really does mean two shotlist
        # rows overlap — the shotlist is meant to be contiguous
        if strip.channel != 2:
            print(f"warning: {shot.code} was pushed to channel "
                  f"{strip.channel} — its shotlist row overlaps a neighbour")

    for code, (strip, _) in existing.items():
        if code not in known:
            print(f"  removed  {code} (no longer in the shotlist)")
            removed += 1
            if not dry_run:
                strips.remove(strip)

    marker_added, drift = sync_markers(scene, root / "docs" / "sections.csv")
    for name, have, want in drift:
        print(f"  marker   {name} is at {have}, sections.csv says {want} "
              f"— left alone")

    summary = (f"{added} added, {replaced} replaced, {retimed} retimed, "
               f"{removed} removed, {unchanged} unchanged; "
               f"{marker_added} marker(s) added, {len(drift)} drifted")
    if dry_run:
        print(f"--dry-run: would be {summary}")
        return
    if added or replaced or retimed or removed or marker_added:
        bpy.ops.wm.save_mainfile()
    print(f"updated edit/edit.blend: {summary}")


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    force = "--force" in argv
    dry_run = "--dry-run" in argv

    root = shotlib.project_root()
    out = root / "edit" / "edit.blend"

    track = shotlib.find_track(root)
    if track is None:
        sys.exit("error: no track in audio/track/ — the edit needs its spine")

    shots = shotlib.read_shotlist(root / "docs" / "shotlist.csv")

    if out.exists() and not force:
        update_in_place(root, out, shots, dry_run)
        return
    if dry_run:
        sys.exit("error: --dry-run only applies to an update; a from-scratch "
                 "build has nothing to compare against")
    build_from_scratch(root, out, shots, track)


if __name__ == "__main__":
    main()
