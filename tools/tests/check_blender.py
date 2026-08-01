"""Run INSIDE Blender to assert guide-asset build invariants. Exits non-zero
on failure (via --python-exit-code 1). Invoked by test_blender_smoke.py and
runnable by hand:

  "$BLENDER" --background --factory-startup --python-exit-code 1 \
      --python tools/tests/check_blender.py

# Task 4 extends this with make_boards guides-collection assertions.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # tools/

import bpy  # noqa: E402,F401
import guides  # noqa: E402,F401
import guide_assets  # noqa: E402
import make_boards  # noqa: E402
import layoutlib  # noqa: E402

# Guide asset files build, mark, catalog, and dimension-check.
guide_assets.run_check()

# make_boards ensures an idempotent per-scene guides collection.
sc = bpy.data.scenes.new("sq999_sh999")
created = make_boards.ensure_guides_collection(sc)
assert created is True, "guides collection should be created on first call"
gname = guides.guides_collection_name(sc.name)
gc = sc.collection.children.get(gname)
assert gc is not None, f"missing {gname}"
assert make_boards.ensure_guides_collection(sc) is False, "must be idempotent"

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
