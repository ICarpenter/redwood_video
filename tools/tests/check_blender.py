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
import guides  # noqa: E402,F401
import guide_assets  # noqa: E402
import make_layout  # noqa: E402
import layoutlib  # noqa: E402

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
ps = bpy.data.scenes.new("settings_probe")
layoutlib.apply_project_settings(ps)
assert ps.render.fps == 24, f"fps {ps.render.fps}"
assert (ps.render.resolution_x, ps.render.resolution_y) == (1920, 1080)
assert ps.render.image_settings.file_format == "PNG"
assert ps.render.image_settings.color_depth == "16"
assert ps.view_settings.view_transform == "AgX", ps.view_settings.view_transform
assert ps.view_settings.look == "None", ps.view_settings.look
assert ps.sync_mode == "AUDIO_SYNC"
# layout scenes draw against greybox, so they opt out of AgX explicitly
ps2 = bpy.data.scenes.new("settings_probe_std")
layoutlib.apply_project_settings(ps2, view_transform="Standard")
assert ps2.view_settings.view_transform == "Standard"
# everything else must still apply
assert ps2.render.fps == 24, f"fps {ps2.render.fps}"
assert (ps2.render.resolution_x, ps2.render.resolution_y) == (1920, 1080)
assert ps2.render.image_settings.file_format == "PNG"
assert ps2.render.image_settings.color_depth == "16"
assert ps2.view_settings.look == "None", ps2.view_settings.look
assert ps2.sync_mode == "AUDIO_SYNC"
print("project settings: OK")

print("ALL CHECKS OK")
