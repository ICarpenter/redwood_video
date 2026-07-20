"""Run INSIDE Blender to integration-test the redwood_guides add-on against
the real boards.blend file and the real linked cast/props assets. Exits
non-zero on failure (via --python-exit-code 1). Invoked by
test_addon_smoke.py and runnable by hand:

  "$BLENDER" --background --factory-startup --python-exit-code 1 \
      --python tools/tests/check_addon.py

Never saves boards.blend — opens it in memory only.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent  # repo root (parent of tools/)
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "addons"))

import bpy  # noqa: E402
import guides  # noqa: E402
import redwood_guides  # noqa: E402

bpy.ops.wm.open_mainfile(filepath=str(ROOT / "boards" / "boards.blend"))

redwood_guides.register()

scene = next(s for s in bpy.data.scenes if s.name.startswith("sq"))
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
assert tuple(round(v, 3) for v in inst.location) == guides.DROP_LOCATION, \
    f"expected location {guides.DROP_LOCATION}, got {tuple(inst.location)}"

gcoll = scene.collection.children[guides.guides_collection_name(scene.name)]
assert inst.name in gcoll.objects, \
    f"{inst.name} not linked into {gcoll.name}.objects"

# Second drop of the same guide: reuse the already-linked library collection
# rather than double-linking it (no `boy.001`), and reuse the same instance
# transform contract.
inst2 = redwood_guides.add_guide_instance(scene, "boy")

boy_collections = [c for c in bpy.data.collections if c.name == "boy"]
assert len(boy_collections) == 1, \
    f"expected exactly one 'boy' collection, got {[c.name for c in boy_collections]}"
assert inst2.instance_collection is inst.instance_collection, \
    "second drop should reuse the same linked collection, not relink it"

guide_instances = [ob for ob in gcoll.objects
                    if ob.instance_collection is inst.instance_collection]
assert len(guide_instances) == 2, \
    f"expected 2 instances of the linked 'boy' collection in {gcoll.name}, " \
    f"got {len(guide_instances)}"

redwood_guides.unregister()

print("ADDON CHECK OK")
