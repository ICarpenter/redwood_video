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
import mathutils  # noqa: E402
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

# The property must NEVER be droppable: it is linked at identity in every
# layout scene already (invariant 1), and a second instance dropped as
# "just another guide" cannot be told apart from staged blocking by any
# later heal pass, so it would survive forever. Requesting it must refuse.
try:
    redwood_guides.add_guide_instance(scene, "property")
except RuntimeError as e:
    assert "property" in str(e).lower(), f"unexpected refusal message: {e}"
else:
    raise AssertionError("add_guide_instance must refuse to drop the property")

# ...and it must not even be offered in the Add Guide dropdown.
offered = [item[0] for item in redwood_guides._guide_items(None, None)]
assert "property" not in offered, \
    f"property must not be offered in the Add Guide dropdown, got {offered}"

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

# Pin the actual intersection, not just "on the ground, ahead of camera" —
# the fallback satisfies both of those too, so a wrong t formula (e.g. a
# flipped sign) would otherwise pass. Expected point derived independently
# from the camera's own transform.
fwd = cam.matrix_basis.to_quaternion() @ mathutils.Vector((0.0, 0.0, -1.0))
t = -cam.matrix_basis.translation.z / fwd.z
expect = cam.matrix_basis.translation + fwd * t
assert (mathutils.Vector(loc) - mathutils.Vector((expect.x, expect.y, 0.0))).length < 1e-5, \
    f"raycast landed at {loc}, expected {(expect.x, expect.y, 0.0)}"

# camera level with the horizon: the ray never meets z=0, so fall back
cam.rotation_euler = (math.radians(90), 0.0, 0.0)
loc = redwood_guides.ground_drop_location(sc)
assert abs(loc[2]) < 1e-6, "fallback still puts feet on the ground"
assert abs(loc[1] - (cam.location.y + guides.DROP_DISTANCE)) < 1e-4, \
    f"fallback should be DROP_DISTANCE along the view ray, got {loc}"
print("ground drop: OK")
