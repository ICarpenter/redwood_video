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
layoutlib.apply_hide_blocking(sc)
assert bc.hide_render is False, "clearing the flag must restore rendering"

# --- THE PAPER DEPTH GATE ------------------------------------------------
# The whole design assumes a near-field camera-parented paper draws over
# close geometry. Prove it with an actual render before anything is built on
# it. If this fails, STOP: the fallback is rendering the GP on its own view
# layer composited over, which changes make_layout and conform_edit.
import os
import tempfile

# Use the CONTEXT scene, not a fresh one: bpy.ops.render.render has no
# `scene` argument and --background has no window to switch the active scene
# through, so a new scene would render the wrong thing or not at all.
depth = bpy.context.scene
depth.world = bpy.data.worlds.new("depth_world")
depth.world.use_nodes = True
depth.world.node_tree.nodes["Background"].inputs["Color"].default_value = (1, 1, 1, 1)
# EEVEE's engine id here is BLENDER_EEVEE (not _NEXT) — pick from the enum
# rather than hardcoding, so this survives a Blender bump.
_engines = depth.render.bl_rna.properties["engine"].enum_items.keys()
depth.render.engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in _engines else _engines[0]
depth.render.resolution_x = 64
depth.render.resolution_y = 64
depth.render.image_settings.file_format = "PNG"
depth.render.use_sequencer = False
depth.view_settings.view_transform = "Standard"
for _ob in list(depth.objects):
    bpy.data.objects.remove(_ob, do_unlink=True)

cam_data = bpy.data.cameras.new("depth_cam")
cam = bpy.data.objects.new("depth_cam", cam_data)
cam.location = (0.0, 0.0, 0.0)
depth.collection.objects.link(cam)
depth.camera = cam

# An obstruction 0.5m in front of camera, filling frame — far closer than
# any real foreground character, and 4x nearer than the old 10m paper.
bpy.ops.mesh.primitive_cube_add(size=4.0, location=(0.0, 0.0, -0.5))

gp_data = (bpy.data.grease_pencils_v3 if hasattr(bpy.data, "grease_pencils_v3")
           else bpy.data.grease_pencils).new("depth_paper")
gp_layer = gp_data.layers.new("lines")
gp_frame = gp_layer.frames.new(1)
gp_frame.drawing.add_strokes([4])
stroke_pts = gp_frame.drawing.strokes[0].points
# a fat X across the middle of the paper, in paper-local units
for pt, co in zip(stroke_pts, [(-2.0, 0.0, -2.0), (2.0, 0.0, 2.0),
                               (2.0, 0.0, -2.0), (-2.0, 0.0, 2.0)]):
    pt.position = co
    pt.radius = 0.35
gp = bpy.data.objects.new("depth_paper", gp_data)
depth.collection.objects.link(gp)
layoutlib.fit_paper(gp, cam)

out = os.path.join(tempfile.mkdtemp(), "depth.png")
depth.render.filepath = out
bpy.ops.render.render(write_still=True)
img = bpy.data.images.load(out)
px = list(img.pixels)
# The cube is grey (~0.8 default) and the world is white. Ink strokes are the
# only thing that can be dark, so dark pixels prove the paper beat the cube.
dark = sum(1 for i in range(0, len(px), 4) if px[i] < 0.25)
assert dark > 0, (
    f"PAPER DEPTH GATE FAILED: no ink pixels in {out} — the near-field paper "
    "did not render over geometry 0.5m from camera. Do not proceed; switch to "
    "the view-layer/compositor fallback in the spec."
)
print(f"paper depth gate: {dark} ink pixels over a 0.5m obstruction — OK")

print("ALL CHECKS OK")
