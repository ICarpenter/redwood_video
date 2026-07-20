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

# Guide asset files build, mark, catalog, and dimension-check.
guide_assets.run_check()

# make_boards ensures a non-rendering, idempotent per-scene guides collection.
sc = bpy.data.scenes.new("sq999_sh999")
created = make_boards.ensure_guides_collection(sc)
assert created is True, "guides collection should be created on first call"
gname = guides.guides_collection_name(sc.name)
gc = sc.collection.children.get(gname)
assert gc is not None, f"missing {gname}"
assert gc.hide_render is True, "guides collection must not render"
assert make_boards.ensure_guides_collection(sc) is False, "must be idempotent"

print("ALL CHECKS OK")
