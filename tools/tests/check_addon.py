"""Run INSIDE Blender to integration-test the redwood_guides add-on against
the real layout.blend file and the real linked cast/props/property assets.
Exits non-zero on failure (via --python-exit-code 1). Invoked by
test_addon_smoke.py and runnable by hand:

  "$BLENDER" --background --factory-startup --python-exit-code 1 \
      --python tools/tests/check_addon.py

Never saves layout.blend — opens it in memory only.
"""
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent  # repo root (parent of tools/)
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "addons"))

import bpy  # noqa: E402
import guides  # noqa: E402
import redwood_guides  # noqa: E402

bpy.ops.wm.open_mainfile(filepath=str(ROOT / "layout" / "layout.blend"))

redwood_guides.register()

scene = next(s for s in bpy.data.scenes if s.name.startswith("sq"))
assert scene.camera is not None, f"{scene.name} has no camera to drop guides against"

inst = redwood_guides.add_guide_instance(scene, "boy")

assert inst.instance_type == "COLLECTION", \
    f"expected COLLECTION instance_type, got {inst.instance_type}"
assert inst.instance_collection is not None, "instance_collection not set"
assert inst.instance_collection.name == "boy", \
    f"expected linked collection named 'boy', got {inst.instance_collection.name!r}"
assert inst.instance_collection.library is not None, \
    "linked collection should come from a library (LIBRARY link)"
assert Path(inst.instance_collection.library.filepath).name == "cast.blend", \
    f"expected library file cast.blend, got {inst.instance_collection.library.filepath!r}"

# Dropped feet-on-the-ground, at the point add_guide_instance's own
# ground_drop_location call would produce for this scene's camera.
expected_loc = redwood_guides.ground_drop_location(scene)
assert tuple(round(v, 3) for v in inst.location) == tuple(round(v, 3) for v in expected_loc), \
    f"expected location {expected_loc}, got {tuple(inst.location)}"
assert abs(inst.location[2]) < 1e-6, \
    f"guide should drop with feet on the ground, got z={inst.location[2]}"

bcoll = scene.collection.children[guides.blocking_collection_name(scene.name)]
assert inst.name in bcoll.objects, \
    f"{inst.name} not linked into {bcoll.name}.objects"

# Second drop of the same guide: reuse the already-linked library collection
# rather than double-linking it (no `boy.001`), and reuse the same instance
# transform contract.
inst2 = redwood_guides.add_guide_instance(scene, "boy")

boy_collections = [c for c in bpy.data.collections if c.name == "boy"]
assert len(boy_collections) == 1, \
    f"expected exactly one 'boy' collection, got {[c.name for c in boy_collections]}"
assert inst2.instance_collection is inst.instance_collection, \
    "second drop should reuse the same linked collection, not relink it"

guide_instances = [ob for ob in bcoll.objects
                    if ob.instance_collection is inst.instance_collection]
assert len(guide_instances) == 2, \
    f"expected 2 instances of the linked 'boy' collection in {bcoll.name}, " \
    f"got {len(guide_instances)}"

# The whole property SET is droppable too (LIBRARY link from property.blend).
prop_inst = redwood_guides.add_guide_instance(scene, "property")
assert prop_inst.instance_collection is not None, "property instance_collection not set"
assert prop_inst.instance_collection.name == "property", \
    f"expected linked collection 'property', got {prop_inst.instance_collection.name!r}"
assert prop_inst.instance_collection.library is not None, \
    "property collection should be a LIBRARY link"
assert Path(prop_inst.instance_collection.library.filepath).name == "property.blend", \
    f"expected library property.blend, got {prop_inst.instance_collection.library.filepath!r}"
assert prop_inst.name in bcoll.objects, \
    f"{prop_inst.name} not linked into {bcoll.name}.objects"

redwood_guides.unregister()

print("ADDON CHECK OK")

# A guide drops onto the ground plane in front of the camera, feet at z=0 —
# a real place on the property, not a spot in a picture.
sc = bpy.data.scenes.new("sq996_sh010")
cam = bpy.data.objects.new("sq996_sh010_cam", bpy.data.cameras.new("sq996_sh010_cam"))
cam.location = (0.0, -10.0, 2.0)
cam.rotation_euler = (math.radians(80), 0.0, 0.0)  # tilted down toward the ground
sc.collection.objects.link(cam)
sc.camera = cam

loc = redwood_guides.ground_drop_location(sc)
assert abs(loc[2]) < 1e-6, f"guides drop with feet on the ground, got z={loc[2]}"
assert loc[1] > cam.location.y, "drop must be IN FRONT of the camera"

# camera level with the horizon: the ray never meets z=0, so fall back
cam.rotation_euler = (math.radians(90), 0.0, 0.0)
loc = redwood_guides.ground_drop_location(sc)
assert abs(loc[2]) < 1e-6, "fallback still puts feet on the ground"
assert abs(loc[1] - (cam.location.y + guides.DROP_DISTANCE)) < 1e-4, \
    f"fallback should be DROP_DISTANCE along the view ray, got {loc}"
print("ground drop: OK")
