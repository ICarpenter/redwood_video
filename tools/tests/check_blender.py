"""Run INSIDE Blender to assert guide-asset build invariants. Exits non-zero
on failure (via --python-exit-code 1). Invoked by test_blender_smoke.py and
runnable by hand:

  "$BLENDER" --background --factory-startup --python-exit-code 1 \
      --python tools/tests/check_blender.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # tools/

import bpy  # noqa: E402,F401
from mathutils import Vector  # noqa: E402

import guides  # noqa: E402,F401
import guide_assets  # noqa: E402
import make_layout  # noqa: E402
import layoutlib  # noqa: E402
import shotlib  # noqa: E402
import stage_shots  # noqa: E402
import continue_shot  # noqa: E402

# Guide asset files build, mark, catalog, and dimension-check.
guide_assets.run_check()

# --- make_layout builds the invariants into every scene ------------------
ml = bpy.data.scenes.new("sq998_sh998")
assert make_layout.ensure_blocking_collection(ml) is True, "created on first call"
assert make_layout.ensure_blocking_collection(ml) is False, "must be idempotent"

ml_cam_data = bpy.data.cameras.new("sq998_sh998_cam")
ml_cam = bpy.data.objects.new("sq998_sh998_cam", ml_cam_data)
ml.collection.objects.link(ml_cam)
ml.camera = ml_cam
ml_gp = bpy.data.objects.new(
    "sq998_sh998_board", make_layout.gp_data_collection().new("sq998_sh998_board"))
ml.collection.objects.link(ml_gp)
layoutlib.fit_paper(ml_gp, ml_cam)
assert ml_gp.parent is ml_cam, "paper must be a camera child"
assert abs(ml_gp.location.z + layoutlib.paper_distance(ml_cam)) < 1e-6
# a stroke at the paper's half-width must land on the frame edge
half_w = layoutlib.paper_distance(ml_cam) * (ml_cam_data.sensor_width / 2.0) / ml_cam_data.lens
assert abs(ml_gp.scale.x * layoutlib.PAPER_HALF_WIDTH - half_w) < 1e-9, "paper misfit"

# an unparented note is exactly the drift the heal loop must repair — build
# and heal share one helper (park_note) so they cannot disagree on the pose
ml_note = make_layout.build_note(ml, "sq998_sh998_note_probe", "prompt")
assert ml_note.parent is None, "sanity: build_note alone leaves the note unparented"
make_layout.park_note(ml_note, ml_cam)
assert ml_note.parent is ml_cam, "park_note must parent an existing note to the camera"
# object transforms round-trip through single-precision RNA floats, so
# compare with tolerance rather than exact equality (as the paper-fit
# assertions above already do)
assert all(abs(a - b) < 1e-5 for a, b in zip(ml_note.location, (-1.6, 0.9, -4.0))), \
    "park_note must set the fixed offset"

# the property links at identity and nowhere else
prop = make_layout.link_property(ml)
if prop is not None:
    assert tuple(prop.location) == (0.0, 0.0, 0.0), f"property moved: {prop.location}"
    assert tuple(prop.rotation_euler) == (0.0, 0.0, 0.0), "property rotated"
    assert tuple(prop.scale) == (1.0, 1.0, 1.0), "property scaled"
    assert make_layout.link_property(ml) is prop, "link_property must be idempotent"

    # a drifted instance must be repaired, not trusted — this is exactly the
    # drift the old stage_boards.py used to bake into the property transform
    prop.location = (5.0, -2.0, 1.0)
    prop.rotation_euler = (0.0, 0.0, 0.3)
    prop.scale = (2.0, 2.0, 2.0)
    healed_prop = make_layout.link_property(ml)
    assert healed_prop is prop, "link_property must still return the existing instance"
    assert tuple(healed_prop.location) == (0.0, 0.0, 0.0), "drifted location must reset"
    assert tuple(healed_prop.rotation_euler) == (0.0, 0.0, 0.0), "drifted rotation must reset"
    assert tuple(healed_prop.scale) == (1.0, 1.0, 1.0), "drifted scale must reset"
print("make_layout: OK")

# --- blocking collection + readiness -------------------------------------
sc = bpy.data.scenes.new("sq999_sh999")
sc.world = bpy.data.worlds.new("check_world")
bc = layoutlib.blocking_collection(sc, create=True)
assert bc is not None, "blocking collection should be created"
assert bc.name == "sq999_sh999_blocking", f"unexpected name {bc.name}"
assert layoutlib.shot_ready(sc) is False, "no strokes and no blocking = not ready"

inst = bpy.data.objects.new("blocking_probe", None)
inst.instance_type = "COLLECTION"
inst.instance_collection = bpy.data.collections.new("probe_target")
bc.objects.link(inst)
assert layoutlib.blocking_instances(sc), "staged blocking should be found"
assert layoutlib.shot_ready(sc) is True, "blocking alone makes a shot edit-ready"

# --- hide_blocking is opt-in and hand-set only ---------------------------
assert bc.hide_render is False, "blocking renders by default"
assert layoutlib.apply_hide_blocking(sc) is False, "no property = no change"
sc["hide_blocking"] = True
assert layoutlib.apply_hide_blocking(sc) is True, "flag must take effect"
assert bc.hide_render is True, "hide_blocking must hide the collection"
assert layoutlib.apply_hide_blocking(sc) is False, "must be idempotent"
del sc["hide_blocking"]
assert layoutlib.apply_hide_blocking(sc) is True, "clearing the flag must change state"
assert bc.hide_render is False, "clearing the flag must restore rendering"

# The paper-depth gate that used to live here was deleted 2026-07-31: it
# asserted ink pixels survive over close geometry, which is true
# unconditionally (GP composites over meshes in EEVEE regardless of distance
# or stroke_depth_order — measured), so it could not fail. See the spec's
# "Paper depth" section.

# --- project settings live in exactly one place --------------------------
# Seed wrong values first: nearly every project setting matches Blender's
# factory default, so asserting the post-state alone proves nothing — the
# assertions passed even with the function gutted.
ps = bpy.data.scenes.new("settings_probe")
ps.render.fps = 12
ps.render.resolution_x, ps.render.resolution_y = 640, 480
ps.render.resolution_percentage = 50
ps.render.image_settings.file_format = "JPEG"
ps.render.image_settings.color_mode = "BW"
ps.render.image_settings.color_depth = "8"
ps.view_settings.view_transform = "Standard"
ps.view_settings.look = "Very High Contrast"
ps.sync_mode = "NONE"
layoutlib.apply_project_settings(ps)
assert ps.render.fps == 24, f"fps {ps.render.fps}"
assert (ps.render.resolution_x, ps.render.resolution_y) == (1920, 1080)
assert ps.render.resolution_percentage == 100
assert ps.render.image_settings.file_format == "PNG"
assert ps.render.image_settings.color_mode == "RGB"
assert ps.render.image_settings.color_depth == "16"
assert ps.view_settings.view_transform == "AgX", ps.view_settings.view_transform
assert ps.view_settings.look == "None", ps.view_settings.look
assert ps.sync_mode == "AUDIO_SYNC"
# layout scenes draw against greybox, so they opt out of AgX explicitly —
# seeded to AgX here so the Standard override below has to actually change it
ps2 = bpy.data.scenes.new("settings_probe_std")
ps2.render.fps = 12
ps2.render.resolution_x, ps2.render.resolution_y = 640, 480
ps2.render.resolution_percentage = 50
ps2.render.image_settings.file_format = "JPEG"
ps2.render.image_settings.color_mode = "BW"
ps2.render.image_settings.color_depth = "8"
ps2.view_settings.view_transform = "AgX"
ps2.view_settings.look = "AgX - Very High Contrast"
ps2.sync_mode = "NONE"
layoutlib.apply_project_settings(ps2, view_transform="Standard")
assert ps2.view_settings.view_transform == "Standard"
# everything else must still apply
assert ps2.render.fps == 24, f"fps {ps2.render.fps}"
assert (ps2.render.resolution_x, ps2.render.resolution_y) == (1920, 1080)
assert ps2.render.resolution_percentage == 100
assert ps2.render.image_settings.file_format == "PNG"
assert ps2.render.image_settings.color_mode == "RGB"
assert ps2.render.image_settings.color_depth == "16"
assert ps2.view_settings.look == "None", ps2.view_settings.look
assert ps2.sync_mode == "AUDIO_SYNC"
print("project settings: OK")

# --- stage_shots: seed_camera + aim_camera --------------------------------
# seed_camera is deliberately unused by STAGING in stage_shots.py — none of
# property.blend's six preview cameras frames the four beats staged there,
# they were composed to show off the property, not to shoot those actions.
# It stays implemented (and covered here) because it is the natural way to
# start a shot from cam_backyard or cam_road later; nothing else exercises
# it, so assert its contract directly.
root = shotlib.project_root()
before = len(bpy.data.objects)
loc, rot, lens = stage_shots.seed_camera(root, "cam_backyard")
assert len(bpy.data.objects) == before, \
    "seed_camera must remove its temporary appended object"
assert len(loc) == 3 and len(rot) == 3, "seed_camera must return (loc, rot, lens)"
assert isinstance(lens, float) and lens > 0.0, f"bad lens {lens!r}"
# cam_backyard's position and lens are authored in tools/blockout_property.py
# at (-4.5, 6.4, 2.5), lens=32 — check the real numbers came back, not just
# plausible-looking ones.
assert all(abs(a - b) < 1e-4 for a, b in zip(loc, (-4.5, 6.4, 2.5))), loc
assert abs(lens - 32.0) < 1e-4, lens
# Its *aim* is deliberately not pinned. The preview cameras get re-tilted by
# hand in property.blend as the set changes — cam_backyard was tilted up ~12°
# to put the basin ridgeline in frame — and pinning the pitch to the tool's
# authored aim only makes this test fail every time the framing is adjusted.
# loc and lens already prove seed_camera read the blend rather than guessing.
assert all(isinstance(a, float) for a in rot), rot
try:
    stage_shots.seed_camera(root, "not_a_real_camera")
except SystemExit:
    pass
else:
    raise AssertionError("seed_camera must sys.exit on an unknown camera name")
print("stage_shots.seed_camera: OK")

# aim_camera: place and aim a scene's camera with the same to_track_quat
# construction used above (hand-rolled Euler math gets the yaw sign wrong,
# which is exactly what to_track_quat avoids).
ss_scene = bpy.data.scenes.new("sq997_sh997")
ss_cam_data = bpy.data.cameras.new("sq997_sh997_cam")
ss_cam = bpy.data.objects.new("sq997_sh997_cam", ss_cam_data)
ss_scene.collection.objects.link(ss_cam)
ss_scene.camera = ss_cam
assert stage_shots.aim_camera(ss_scene, (5.0, -10.0, 2.0), (0.0, 0.0, 1.0), 40) is True
assert tuple(ss_cam.location) == (5.0, -10.0, 2.0)
assert ss_cam.data.lens == 40
aim_expected = (Vector((0.0, 0.0, 1.0)) - Vector((5.0, -10.0, 2.0))
               ).to_track_quat("-Z", "Y")
aim_got = ss_cam.rotation_euler.to_quaternion()
assert aim_expected.rotation_difference(aim_got).angle < 1e-6, \
    "aim_camera must aim with to_track_quat, not hand-rolled Euler math"

ss_scene.camera = None
assert stage_shots.aim_camera(ss_scene, (0, 0, 0), (0, 1, 0), 50) is False, \
    "a scene with no camera has nothing to aim"
print("stage_shots.aim_camera: OK")

# --- continue_shot: apply_snapshot writes world matrices -----------------
# apply_snapshot only writes, so it is tested directly against a hand-built
# snapshot dict rather than one produced by snapshot() — that round-trip is
# covered separately below.
cs_target = bpy.data.collections.new("cs_probe_boy")
cs_dst = bpy.data.scenes.new("sq997_sh020")
cs_dst_cam = bpy.data.objects.new("sq997_sh020_cam", bpy.data.cameras.new("sq997_sh020_cam"))
cs_dst.collection.objects.link(cs_dst_cam)
cs_dst.camera = cs_dst_cam
layoutlib.blocking_collection(cs_dst, create=True)

# translation-only matrices (identity rotation) — rotation round-trips
# through Euler decomposition can land on an equivalent-but-different-
# looking angle (e.g. -180 vs 180), which is a distraction from what this
# check is actually verifying.
cs_snap = {
    "cs_probe_boy": (
        ((1.0, 0.0, 0.0, 1.25),
         (0.0, 1.0, 0.0, 2.5),
         (0.0, 0.0, 1.0, 0.0),
         (0.0, 0.0, 0.0, 1.0)),
        None,
    ),
    "__camera__": (
        ((1.0, 0.0, 0.0, 3.0),
         (0.0, 1.0, 0.0, -4.0),
         (0.0, 0.0, 1.0, 1.5),
         (0.0, 0.0, 0.0, 1.0)),
        42.0,
    ),
}

created, skipped, updated = continue_shot.apply_snapshot(cs_dst, cs_snap)
assert created == 1, f"expected 1 created, got {created}"
assert updated == 0, f"expected 0 updated, got {updated}"

moved = next(o for o in layoutlib.blocking_instances(cs_dst)
             if o.instance_collection is cs_target)
# .location, not .matrix_world: matrix_world stays stale until a depsgraph
# evaluation, but apply_snapshot's `inst.matrix_world = m` assignment
# decomposes into .location/.rotation_euler/.scale immediately, which is
# what makes this readable without one.
assert all(abs(a - b) < 1e-6 for a, b in zip(moved.location, (1.25, 2.5, 0.0))), \
    f"blocking must land at the snapshot's world position, got {tuple(moved.location)}"
assert abs(cs_dst_cam.location.x - 3.0) < 1e-6, "camera location must copy"
assert abs(cs_dst_cam.location.y + 4.0) < 1e-6, "camera location must copy"
assert abs(cs_dst_cam.location.z - 1.5) < 1e-6, "camera location must copy"
assert abs(cs_dst_cam.data.lens - 42.0) < 1e-6, "camera lens must copy"

# re-running must not stack duplicates
created2, skipped2, updated2 = continue_shot.apply_snapshot(cs_dst, cs_snap)
assert created2 == 0 and skipped2 == 1 and updated2 == 0, \
    f"not idempotent: {created2}, {skipped2}, {updated2}"
print("continue_shot.apply_snapshot: OK")

# --- continue_shot: snapshot() + apply_snapshot round-trip ---------------
# snapshot()'s first statement is scene.frame_set(frame), which is what
# builds the scene's depsgraph — scene.view_layers[0].depsgraph is None
# before that (for a scene that has never been evaluated) and populated
# after, so an in-memory scene built via bpy.data.scenes.new() CAN be
# snapshotted here, same as a scene loaded from a file. The actual lesson
# from this: .matrix_world stays stale in --background until something
# evaluates the scene, but .location (and camera.data.lens) is always
# live — assert on those, never on .matrix_world, for both the source
# fixture and the snapshotted result.
rt_src = bpy.data.scenes.new("sq996_sh010")
rt_src.world = bpy.data.worlds.new("cs_world_rt_src")
rt_src_cam = bpy.data.objects.new("sq996_sh010_cam", bpy.data.cameras.new("sq996_sh010_cam"))
rt_src_cam.location = (3.0, -4.0, 1.5)
rt_src_cam.data.lens = 42.0
rt_src.collection.objects.link(rt_src_cam)
rt_src.camera = rt_src_cam
rt_src_bc = layoutlib.blocking_collection(rt_src, create=True)
# named distinctly from any real guide collection (guide_assets.run_check()
# above leaves guide collections behind in bpy.data) and from the
# "cs_probe_boy" collection used above, so this fixture cannot collide with
# — or be mistaken for — either
rt_target = bpy.data.collections.new("rt_probe_boy")
rt_probe = bpy.data.objects.new("boy", None)
rt_probe.instance_type = "COLLECTION"
rt_probe.instance_collection = rt_target
rt_probe.location = (1.25, 2.5, 0.0)
rt_src_bc.objects.link(rt_probe)

rt_dst = bpy.data.scenes.new("sq996_sh020")
rt_dst.world = bpy.data.worlds.new("cs_world_rt_dst")
rt_dst_cam = bpy.data.objects.new("sq996_sh020_cam", bpy.data.cameras.new("sq996_sh020_cam"))
rt_dst.collection.objects.link(rt_dst_cam)
rt_dst.camera = rt_dst_cam
layoutlib.blocking_collection(rt_dst, create=True)

rt_snap = continue_shot.snapshot(rt_src, rt_src.frame_start)
# snapshot() keys by instance-collection name (see its docstring), which is
# "rt_probe_boy" here — the probe OBJECT is named "boy" to mirror real
# staged instances, but that name is never the key.
assert "rt_probe_boy" in rt_snap, f"snapshot missing blocking: {list(rt_snap)}"
rt_created, rt_skipped, rt_updated = continue_shot.apply_snapshot(rt_dst, rt_snap)
assert rt_created == 1, f"expected 1 created, got {rt_created}"
assert rt_updated == 0, f"expected 0 updated, got {rt_updated}"

rt_moved = next(o for o in layoutlib.blocking_instances(rt_dst)
                if o.instance_collection is rt_target)
assert (rt_moved.location - Vector((1.25, 2.5, 0.0))).length < 1e-5, \
    f"blocking landed at {tuple(rt_moved.location)}, expected (1.25, 2.5, 0.0)"
assert abs(rt_dst.camera.location.x - 3.0) < 1e-5, "camera location must copy"
assert abs(rt_dst.camera.location.y + 4.0) < 1e-5, "camera location must copy"
assert abs(rt_dst.camera.location.z - 1.5) < 1e-5, "camera location must copy"
assert abs(rt_dst.camera.data.lens - 42.0) < 1e-5, "camera lens must copy"

# re-running must not stack duplicates
rt_created2, rt_skipped2, rt_updated2 = continue_shot.apply_snapshot(rt_dst, rt_snap)
assert rt_created2 == 0 and rt_skipped2 == 1 and rt_updated2 == 0, \
    f"not idempotent: {rt_created2}, {rt_skipped2}, {rt_updated2}"
print("continue_shot: OK")

print("ALL CHECKS OK")
