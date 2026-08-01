#!/usr/bin/env python3
"""One-shot reset of boards.blend into the camera-driven layout model.

The old model changed framing by moving and ROTATING the property instance
with the camera pinned at (0,-10,0) — and had begun animating the set itself
to fake camera moves (sq010_sh010, sq010_sh045 both carry Actions on their
property instance). None of that survives the new invariants, and by decision
it is discarded rather than converted: the blocking took minutes to place.

What this does per scene:
  - deletes every collection instance (all blocking)
  - clears every object Action (all animation)
  - renames <code>_guides -> <code>_blocking
  - links the property at identity
  - parents the GP paper and the note to the camera, fits the paper
  - resets the camera

Two things survive because they are free:
  - Grease Pencil data is never touched, so sq010_sh010's 119 strokes remain.
  - That one scene's camera is solved statically as M^-1 * C, so the only
    drawn shot in the film keeps 3D standing behind it at the drawn angle.

Run ONCE, with Blender closed, AFTER `git mv boards/boards.blend
layout/layout.blend`:
  "$BLENDER" --background --python-exit-code 1 \
      --python tools/migrate_layout.py [-- --dry-run]
"""
import sys
from pathlib import Path

import bpy
from mathutils import Matrix

sys.path.insert(0, str(Path(__file__).resolve().parent))
import guides
import layoutlib
import make_layout
import shotlib

DRAWN_SCENE = "sq010_sh010"


def solve_camera(scene):
    """Camera transform that reproduces the old framing with a static set.

    Old: property at M, camera at C, both possibly animated.
    New: property at identity, camera at C' — and the picture is preserved
    when C'^-1 = C^-1 * M, i.e. C' = M^-1 * C.

    Evaluated at frame_start only: this is a static solve, deliberately. The
    animation is being discarded.
    """
    scene.frame_set(scene.frame_start)
    # matrix_world is identity in --background until something forces a
    # depsgraph evaluation. bpy.context.evaluated_depsgraph_get() is NOT
    # that something here: it evaluates the CONTEXT scene's depsgraph, and
    # in this file the context scene is whatever scene was current when
    # Blender opened it (sq010_sh045, not the DRAWN_SCENE we're solving) —
    # so prop/cam evaluated against it come back at identity, silently,
    # for scenes other than the context one. Use the target scene's own
    # depsgraph instead, which also folds in parenting and constraints that
    # a manual Matrix.LocRotScale composition would silently ignore.
    deps = scene.view_layers[0].depsgraph
    cam = scene.camera
    prop = next((o for o in scene.objects
                 if o.instance_collection is not None
                 and o.instance_collection.name == "property"), None)
    if cam is None or prop is None:
        return None
    m = prop.evaluated_get(deps).matrix_world.copy()
    c = cam.evaluated_get(deps).matrix_world.copy()
    # A wrong answer here is indistinguishable from a right one unless it's
    # checked: if the depsgraph handed back identity for BOTH sources (the
    # exact failure mode above, and anything equivalent to it), solving
    # would silently plant the camera at the world origin instead of
    # reproducing the old framing. Refuse and fall through to the neutral
    # default rather than write a result nobody could tell was wrong.
    if m.to_translation().length < 1e-6 and c.to_translation().length < 1e-6:
        print(f"warning: {scene.name}: depsgraph returned identity for both "
              f"property and camera — solve skipped, camera left at default")
        return None
    return m.inverted() @ c


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    dry_run = "--dry-run" in argv

    root = shotlib.project_root()
    out = root / "layout" / "layout.blend"
    if not out.exists():
        sys.exit(f"error: {out.relative_to(root)} not found — run "
                 "`git mv boards/boards.blend layout/layout.blend` first")
    bpy.ops.wm.open_mainfile(filepath=str(out))

    # State-derived, not a sentinel: this asks the migration's own defining
    # question — is the file still in the old shape? — so it cannot drift out
    # of sync with what the script does, and nothing is written into the
    # .blend. Measured: a second run deletes 46 objects, including every
    # staged blocking instance, and no tool restores them.
    if not any(s.collection.children.get(f"{s.name}_guides")
               for s in bpy.data.scenes):
        sys.exit("error: no <code>_guides collections found — layout.blend "
                 "has already been migrated. Re-running would delete every "
                 "staged blocking instance and clear every Action in all 39 "
                 "scenes. Refusing.")

    solved = {}
    if DRAWN_SCENE in bpy.data.scenes:
        m = solve_camera(bpy.data.scenes[DRAWN_SCENE])
        if m is not None:
            solved[DRAWN_SCENE] = m
            print(f"solved {DRAWN_SCENE} camera from its old framing")

    stats = {"scenes": 0, "instances": 0, "actions": 0, "renamed": 0}
    for scene in bpy.data.scenes:
        stats["scenes"] += 1
        cam = scene.camera

        for ob in list(scene.objects):
            # Count actions BEFORE the instance branch. Most animation in this
            # file lives on blocking instances, so checking after a `continue`
            # would tally 3 of 10 and under-report what this script destroyed.
            if ob.animation_data is not None:
                stats["actions"] += 1
                if not dry_run:
                    ob.animation_data_clear()
            if ob.instance_collection is not None:
                stats["instances"] += 1
                if not dry_run:
                    bpy.data.objects.remove(ob, do_unlink=True)

        old = scene.collection.children.get(f"{scene.name}_guides")
        if old is not None:
            stats["renamed"] += 1
            if not dry_run:
                old.name = guides.blocking_collection_name(scene.name)

        if dry_run:
            continue

        scene.world = make_layout.layout_world()
        layoutlib.apply_project_settings(scene, view_transform="Standard")
        make_layout.ensure_blocking_collection(scene)
        make_layout.link_property(scene)
        layoutlib.apply_hide_blocking(scene)

        if cam is not None:
            if scene.name in solved:
                cam.matrix_world = solved[scene.name]
            else:
                cam.matrix_basis = Matrix.Identity(4)
                cam.location = (0.0, -10.0, 1.6)
                cam.rotation_euler = (1.5707963, 0.0, 0.0)
            for ob in scene.objects:
                if ob.type in layoutlib.GP_TYPES:
                    layoutlib.fit_paper(ob, cam)
                elif ob.type == "FONT" and ob.name.endswith("_note"):
                    ob.parent = cam
                    ob.matrix_parent_inverse = Matrix.Identity(4)
                    ob.location = (-1.6, 0.9, -4.0)
                    ob.rotation_euler = (0.0, 0.0, 0.0)

    if dry_run:
        print(f"--dry-run: {stats}")
        return
    bpy.ops.wm.save_mainfile()
    print(f"migrated: {stats}")


if __name__ == "__main__":
    main()
