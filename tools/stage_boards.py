#!/usr/bin/env python3
"""Drop starting guide instances into board scenes — additively.

Declarative counterpart to stage_property.py, but with the opposite update
rule. stage_property.py owns its `blocking` collection outright and clears it
on every run; that is safe there and would be destructive here, because board
guides get positioned by hand as each shot is framed (sq010_sh010's property
sits at rotZ -43.8, sh030's at +90, sh040's boy in front of the paper).

So: a guide already present in a scene is LEFT ALONE — transform untouched.
Only missing ones are created, at the STAGING position. Re-running is a no-op
once a shot is staged, which makes it safe to leave in the pipeline as new
shots arrive.

Positions here are a sane starting point for drawing, not final framing.

Run (Blender must be closed — this writes boards/boards.blend):
  "$BLENDER" --background --factory-startup --python-exit-code 1 \
      --python tools/stage_boards.py [-- --dry-run]
"""
import math
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import guides
import shotlib

# scene code -> [(guide collection, source file, (x, y, z), rot_z degrees)]
# Guides are authored facing -Y (toward the board camera at (0,-10,0)).
STAGING = {
    # The box joins the boy already staged in front of the paper plane.
    "sq010_sh040": [
        ("box", guides.PROPS_FILE, (1.20, -4.60, -1.20), 0),
    ],
    # Reverse through the garage: the property set spun 180 so we look in at
    # the rear door, through the passthrough, to the driveway beyond.
    "sq010_sh045": [
        ("property", guides.PROPERTY_FILE, (-10.00, 6.00, -1.22), 180),
        ("boy", guides.CAST_FILE, (-0.80, 5.00, -1.22), 0),
        ("box", guides.PROPS_FILE, (0.60, 4.60, -1.22), 0),
    ],
}


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


def guides_collection(scene):
    """The scene's non-rendering guides collection, created if absent."""
    name = guides.guides_collection_name(scene.name)
    coll = scene.collection.children.get(name)
    if coll is None:
        coll = bpy.data.collections.get(name)
        if coll is None:
            coll = bpy.data.collections.new(name)
        scene.collection.children.link(coll)
    coll.hide_render = True
    return coll


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    dry_run = "--dry-run" in argv

    root = shotlib.project_root()
    out = root / "boards" / "boards.blend"
    if not out.exists():
        sys.exit(f"error: {out.relative_to(root)} does not exist; "
                 "run tools/make_boards.py first")
    bpy.ops.wm.open_mainfile(filepath=str(out))

    cache = {}
    created = skipped = 0
    for scene_name, entries in STAGING.items():
        scene = bpy.data.scenes.get(scene_name)
        if scene is None:
            sys.exit(f"error: no scene {scene_name!r} in boards.blend; "
                     "run tools/make_boards.py first")
        coll = guides_collection(scene)
        for guide_name, rel_file, loc, rot_z in entries:
            linked = link_collection(root, rel_file, guide_name, cache)
            # identity match, not name match: instance OBJECTS are auto-suffixed
            # (property.003, boy.001), so comparing object names misses them
            # and would silently stack duplicates on every run.
            if any(o.instance_collection is linked for o in coll.objects):
                print(f"  {scene_name}: {guide_name} already staged, left alone")
                skipped += 1
                continue
            print(f"  {scene_name}: staging {guide_name} at {loc} rotZ={rot_z}")
            created += 1
            if dry_run:
                continue
            inst = bpy.data.objects.new(guide_name, None)
            inst.instance_type = "COLLECTION"
            inst.instance_collection = linked
            inst.location = loc
            inst.rotation_euler = (0.0, 0.0, math.radians(rot_z))
            coll.objects.link(inst)

    if dry_run:
        print(f"--dry-run: would create {created}, skip {skipped}")
        return
    if created:
        bpy.ops.wm.save_mainfile()
    print(f"stage_boards: created {created}, skipped {skipped}")


if __name__ == "__main__":
    main()
