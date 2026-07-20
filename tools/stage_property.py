#!/usr/bin/env python3
"""Stage the full cast + props into assets/envs/property/property.blend as
LINKED collection instances, in a separate `blocking` collection — for blocking
out shots inside the property file. The instances reference their guide source
files (cast.blend / props.blend), so this file stays light and edits to the
guides flow through.

The `property` collection stays the PURE set (environment + set-dressing) and
remains the linkable "set" guide — the blocking instances live OUTSIDE it, so
linking `property` into a board never drags the cast/props along. In boards you
instance cast/props individually via the Redwood Guides add-on.

Idempotent: re-running clears the `blocking` collection, rebuilds it, and
removes any leftover greybox standins. Never touches the property asset mark.

Run:
  "$BLENDER" --background --python-exit-code 1 \
      --python tools/stage_property.py
"""
import math
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import guides
import shotlib

BLOCKING = "blocking"

# Greybox standins in the `property` set that the linked guide instances replace.
STANDINS = ["mark_boy", "mark_sheriff_crash", "santa",
            "figure_0", "figure_1", "figure_2", "figure_3", "figure_4"]

# (instance name, guide collection, source file, (x, y, z), rot_z degrees).
# Guides are authored facing -Y; rot_z 180 faces +Y (into the yard), 90 faces +X.
STAGING = [
    # cast — face +Y, into the yard
    ("boy",     "boy",     guides.CAST_FILE, (-2.0, 8.5, 0.0), 180),
    ("mom",     "mom",     guides.CAST_FILE, (-2.5, 6.0, 0.0), 180),
    ("sheriff", "sheriff", guides.CAST_FILE, (9.0, -8.0, 0.0), 180),
    # firing squad — face -Y, at the boy
    ("action_figure_0", "action_figure", guides.PROPS_FILE, (-6.0, 20.0, 0.0), 0),
    ("action_figure_1", "action_figure", guides.PROPS_FILE, (-3.0, 20.0, 0.0), 0),
    ("action_figure_2", "action_figure", guides.PROPS_FILE, (0.0, 20.0, 0.0), 0),
    ("action_figure_3", "action_figure", guides.PROPS_FILE, (3.0, 20.0, 0.0), 0),
    ("action_figure_4", "action_figure", guides.PROPS_FILE, (6.0, 20.0, 0.0), 0),
    # props
    ("santa",          "santa",          guides.PROPS_FILE, (-9.25, 5.05, 0.0), 0),
    ("machine_gun",    "machine_gun",    guides.PROPS_FILE, (-1.3, 8.7, 1.0), 90),
    ("printer",        "printer",        guides.PROPS_FILE, (-10.0, 0.0, 0.0), 0),
    ("delivery_truck", "delivery_truck", guides.PROPS_FILE, (-8.0, -20.0, 0.0), 0),
    ("cruiser",        "cruiser",        guides.PROPS_FILE, (10.0, -15.5, 0.0), 40),
    ("rosco",          "rosco",          guides.PROPS_FILE, (-1.9, 6.0, 1.0), 180),
    ("big_pistol",     "big_pistol",     guides.PROPS_FILE, (9.3, -7.8, 0.8), 180),
]


def link_collection(root, rel_file, name, cache):
    """Return the linked collection `name` from rel_file, reusing if present."""
    key = (rel_file, name)
    if key in cache:
        return cache[key]
    basename = Path(rel_file).name
    existing = next((c for c in bpy.data.collections
                     if c.name == name and c.library
                     and Path(c.library.filepath).name == basename), None)
    if existing is None:
        filepath = str(root / rel_file)
        with bpy.data.libraries.load(filepath, link=True) as (src, dst):
            if name not in src.collections:
                sys.exit(f"error: collection {name!r} not in {rel_file}")
            dst.collections = [name]
        existing = dst.collections[0]
    cache[key] = existing
    return existing


def main():
    root = shotlib.project_root()
    path = root / guides.PROPERTY_FILE
    if not path.exists():
        sys.exit(f"error: {path} not found (run guide_assets.py first)")
    bpy.ops.wm.open_mainfile(filepath=str(path))
    scene = bpy.context.scene

    # drop the greybox standins wherever they live
    removed = 0
    for name in STANDINS:
        ob = bpy.data.objects.get(name)
        if ob is not None:
            bpy.data.objects.remove(ob, do_unlink=True)
            removed += 1

    # fresh `blocking` collection, linked at scene root (NOT under `property`)
    blocking = bpy.data.collections.get(BLOCKING)
    if blocking is None:
        blocking = bpy.data.collections.new(BLOCKING)
        scene.collection.children.link(blocking)
    else:
        for ob in list(blocking.objects):
            bpy.data.objects.remove(ob, do_unlink=True)

    cache = {}
    for inst_name, guide_name, rel_file, loc, rot_z in STAGING:
        linked = link_collection(root, rel_file, guide_name, cache)
        inst = bpy.data.objects.new(inst_name, None)
        inst.instance_type = "COLLECTION"
        inst.instance_collection = linked
        inst.location = loc
        inst.rotation_euler = (0.0, 0.0, math.radians(rot_z))
        blocking.objects.link(inst)

    prop = bpy.data.collections.get("property")
    if prop is None:
        sys.exit("error: no `property` collection")
    # the set guide must stay pure: blocking is never nested under property
    if BLOCKING in [c.name for c in prop.children]:
        sys.exit("error: `blocking` must not be a child of `property`")

    bpy.ops.wm.save_as_mainfile(filepath=str(path), relative_remap=True)
    print(f"stage_property: removed {removed} standin(s), staged "
          f"{len(STAGING)} instance(s) in `{BLOCKING}`; property set has "
          f"{len(prop.objects)} objects, asset="
          f"{'yes' if prop.asset_data else 'NO'}")


if __name__ == "__main__":
    main()
