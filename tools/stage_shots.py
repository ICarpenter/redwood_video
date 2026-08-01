#!/usr/bin/env python3
"""Frame starting cameras and drop starting guide instances — additively.

Declarative counterpart to make_layout.py, but scoped to composition rather
than scene structure: make_layout.py builds every scene's invariants (world,
camera, paper, blocking collection, linked property); this script is where a
handful of early story beats get their first camera framing and world-space
blocking, on top of that.

ALL POSITIONS ARE WORLD SPACE ON THE PROPERTY. The set sits at the origin
with ground at z=0 and never moves (make_layout.link_property enforces
that); the camera is what frames the shot. A guide's transform says where
that character actually stands.

Two additive, LEFT-ALONE update rules, so re-running is always safe:
  - Blocking: a guide already present in a scene is left untouched. Only
    missing ones are created, at the STAGING position. Once a shot is
    staged, re-running is a no-op for its guides.
  - Camera: only a camera still at the migration default (0, -10, 1.6) gets
    framed. A camera that has moved — by this script or by hand — is
    finished work and is never reset.

Positions here are a starting point for framing and blocking, not final
composition.

Run (Blender must be closed — this writes layout/layout.blend):
  "$BLENDER" --background --factory-startup --python-exit-code 1 \
      --python tools/stage_shots.py [-- --dry-run]
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import guides
import shotlib
import layoutlib

# scene code -> {"camera": (loc, look_at, lens) or "seed camera name",
#                "blocking": [(guide, file, loc, rot_z)]}
#
# ALL POSITIONS ARE WORLD SPACE ON THE PROPERTY. The set sits at the origin
# with ground at z=0 and never moves; the camera is what frames the shot.
# Compass, from treatment/site.md: +Y = backyard, -Y = road.
#
# These are a starting point for framing, not final composition. A guide
# already present in a scene is LEFT ALONE, so re-running never disturbs work.
#
# All coordinates were measured off property.blend's actual world bounds on
# 2026-07-31, not guessed: house x -7..5, y -4..5; porch x -5..1,
# y -6.4..-4 at deck height z 0.5; garage x -13..-7, y -3..3 with its
# boolean passthrough running front-to-back along Y at x ~= -10; driveway
# x -12.5..-7.5, y -14..-3; road y -23..-17; back stoop y 5..6.2.
# Guides are authored facing -Y, so rotZ 180 faces +Y (into the backyard)
# and rotZ 90 faces +X (east).
STAGING = {
    # "package sticks the landing on the porch" — camera on the front lawn,
    # three-quarter onto the porch. The package is already down; the truck
    # has gone (and could not be framed from here anyway — see below).
    "sq010_sh020": {
        "camera": ((4.0, -13.0, 1.8), (-2.0, -5.2, 1.0), 40),
        # No truck: at 40mm from y=-13 the road (y=-19) is BEHIND the
        # camera. The beat is the package landing, not the delivery — the
        # truck has gone. Verified by render, 2026-07-31.
        "blocking": [
            ("box", guides.PROPS_FILE, (-1.5, -5.0, 0.5), 0),
        ],
    },
    # "boy at the screen door clocks the package" — he is ON the porch deck
    # (z=0.5) at the front door, facing -Y out toward the road.
    "sq010_sh030": {
        "camera": ((1.5, -10.0, 1.5), (-1.9, -4.6, 1.2), 50),
        "blocking": [
            ("boy", guides.CAST_FILE, (-1.9, -4.6, 0.5), 0),
            # off the camera axis and screen-left: on the axis it eclipsed
            # the boy completely (verified by render, 2026-07-31)
            ("box", guides.PROPS_FILE, (-3.4, -5.4, 0.5), 0),
        ],
    },
    # "boy drags the box up the drive into the garage" — driveway runs
    # y -14..-3 at x -12.5..-7.5, into the garage front door. He walks +Y
    # (rotZ 180) with the box trailing behind him at lower Y.
    "sq010_sh040": {
        "camera": ((-7.0, -15.0, 1.4), (-10.0, -3.0, 1.0), 35),
        "blocking": [
            # Side by side, not in depth: from a camera looking down the
            # driveway these are nearly collinear, and 1.1m of lateral
            # offset bought only ~3 deg of angular separation — the box
            # still ate the boy. 2m apart gives 12 deg inside a 27 deg
            # half-FOV, so both read clearly. Verified by render.
            ("boy", guides.CAST_FILE, (-11.2, -8.0, 0.0), 180),
            ("box", guides.PROPS_FILE, (-9.2, -8.6, 0.0), 170),
        ],
    },
    # "reverse through garage from back yard" — camera in the BACKYARD at
    # +Y looking -Y straight down the garage axis (x=-10) and out through
    # the boolean passthrough to the driveway beyond. The boy faces the
    # camera (+Y, rotZ 180) crouched over the box.
    "sq010_sh045": {
        "camera": ((-10.0, 9.0, 1.4), (-10.0, -6.0, 1.0), 35),
        "blocking": [
            ("boy", guides.CAST_FILE, (-10.0, 0.0, 0.0), 180),
            ("box", guides.PROPS_FILE, (-10.0, -1.0, 0.0), 0),
        ],
    },
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


def aim_camera(scene, loc, look_at, lens):
    """Place and aim the shot camera. Returns True if it moved anything."""
    cam = scene.camera
    if cam is None:
        return False
    direction = Vector(look_at) - Vector(loc)
    cam.location = loc
    # -Z forward, Y up: hand-rolled Euler math gets the yaw sign wrong
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lens
    return True


def seed_camera(root, name):
    """(location, rotation_euler, lens) of a named camera in property.blend.

    Appended, not linked: we want the transform copied into the layout scene
    and owned there, so framing it afterwards is a normal edit. The temporary
    object is removed once its numbers are read.

    Deliberately unused by STAGING above: none of property.blend's six
    preview cameras (cam_site, cam_intro, cam_backyard, cam_kitchen,
    cam_road, cam_sidecorridor) frames any of these four beats — they were
    composed to show off the property, not to shoot these actions. Forcing
    one in would produce worse staging than an explicit transform. Kept, and
    covered by an assertion in tools/tests/check_blender.py, because it is
    the natural way to start a shot from cam_backyard or cam_road later.
    """
    filepath = str(root / guides.PROPERTY_FILE)
    with bpy.data.libraries.load(filepath, link=False) as (src, dst):
        if name not in src.objects:
            sys.exit(f"error: no camera {name!r} in {guides.PROPERTY_FILE}")
        dst.objects = [name]
    ob = dst.objects[0]
    result = (tuple(ob.location), tuple(ob.rotation_euler),
              ob.data.lens if ob.type == "CAMERA" else 50.0)
    bpy.data.objects.remove(ob, do_unlink=True)
    return result


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    dry_run = "--dry-run" in argv

    root = shotlib.project_root()
    out = root / "layout" / "layout.blend"
    if not out.exists():
        sys.exit(f"error: {out.relative_to(root)} does not exist; "
                 "run tools/make_layout.py first")
    bpy.ops.wm.open_mainfile(filepath=str(out))

    cache = {}
    created = skipped = 0
    changed = False
    for scene_name, entry in STAGING.items():
        scene = bpy.data.scenes.get(scene_name)
        if scene is None:
            sys.exit(f"error: no scene {scene_name!r} in layout.blend; "
                     "run tools/make_layout.py first")
        coll = layoutlib.blocking_collection(scene, create=True)

        # Only frame a camera that is still at the migration default. A camera
        # moved by hand is finished work and must not be reset.
        cam = scene.camera
        if cam is not None and not dry_run:
            default = (abs(cam.location.x) < 1e-6
                       and abs(cam.location.y + 10.0) < 1e-6
                       and abs(cam.location.z - 1.6) < 1e-6)
            if default:
                spec_cam = entry["camera"]
                if isinstance(spec_cam, str):
                    loc, rot, lens = seed_camera(root, spec_cam)
                    cam.location = loc
                    cam.rotation_euler = rot
                    cam.data.lens = lens
                    print(f"  {scene_name}: camera seeded from {spec_cam}")
                else:
                    loc, look_at, lens = spec_cam
                    aim_camera(scene, loc, look_at, lens)
                    print(f"  {scene_name}: camera framed at {loc} -> {look_at}")
                changed = True
                # the paper's fit depends on the lens, so refit after aiming
                for ob in scene.objects:
                    if ob.type in layoutlib.GP_TYPES:
                        layoutlib.fit_paper(ob, cam)
            else:
                print(f"  {scene_name}: camera framed by hand, left alone")

        for guide_name, rel_file, loc, rot_z in entry["blocking"]:
            linked = link_collection(root, rel_file, guide_name, cache)
            # identity match, not name match: instance OBJECTS are auto-suffixed
            # (boy.001, box.002), so comparing object names misses them and
            # would silently stack duplicates on every run.
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
    # A STAGING row can move only a camera (blocking already present, or its
    # "blocking" list simply empty) — created/skipped alone would miss that
    # and this would print success while saving nothing.
    if created or changed:
        bpy.ops.wm.save_mainfile()
    print(f"stage_shots: created {created}, skipped {skipped}"
          f"{', camera(s) framed' if changed else ''}")


if __name__ == "__main__":
    main()
