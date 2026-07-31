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
import boardlib  # noqa: E402

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

# Guides render while a board is blocked out, and stop once it is drawn, so the
# edit shows the best available tier without ever printing guides under artwork.
assert boardlib.has_strokes(sc) is False, "fresh scene has no strokes"
boardlib.sync_guide_visibility(sc)
assert gc.hide_render is False, "undrawn board must render its guides"
assert boardlib.sync_guide_visibility(sc) is False, "sync must be idempotent"

# an undrawn board with guides staged is edit-ready; an empty one is not
assert boardlib.board_ready(sc) is False, "no strokes and no guides = not ready"
inst = bpy.data.objects.new("guide_probe", None)
inst.instance_type = "COLLECTION"
inst.instance_collection = bpy.data.collections.new("probe_target")
gc.objects.link(inst)
assert boardlib.guide_instances(sc), "staged guide should be found"
assert boardlib.board_ready(sc) is True, "guides alone make a board edit-ready"

# now draw on it: guides must drop back out of the render
gp_data = make_boards.gp_data_collection().new("sq999_sh999_board")
layer = gp_data.layers.new("lines")
frame = layer.frames.new(1)
frame.drawing.add_strokes([3])
gp = bpy.data.objects.new("sq999_sh999_board", gp_data)
sc.collection.objects.link(gp)
assert boardlib.has_strokes(sc) is True, "stroke should be detected"
assert boardlib.sync_guide_visibility(sc) is True, "drawing must flip guides off"
assert gc.hide_render is True, "drawn board must hide its guides"

print("ALL CHECKS OK")
