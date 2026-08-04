#!/usr/bin/env python3
"""Build the MCM house (docs/treatment/house.md) into property.blend.

Everything stages in a `house_v2` collection shown in a `house_modeling`
workspace scene. Layout scenes link ONLY the `property` root collection
(docs/pipeline.md), so staging is invisible to the film until --swap
(Task 10) moves it in and parks the greybox in `_greybox` (--revert undoes).
Same-file staging (not a second .blend) means shared datablocks: no append
step, no material duplication, no name collisions at swap time. Precedent:
the boy_modeling workspace scene in cast.blend.

Run (Blender must be CLOSED — CLAUDE.md):
  "$BLENDER" --background assets/envs/property/property.blend \
      --python-exit-code 1 --python tools/build_house.py -- [flags]
Flags:
  --rebuild         delete + rebuild the house_v2 staging collection
  --check           run cumulative invariant asserts, then exit non-zero on fail
  --previews=<dir>  render every cam_model_* camera to <dir>/<name>.png
  --swap / --revert (Task 10) move staging into `property` / undo it
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

HOUSE = (-7.0, 5.0, -4.0, 5.0, 0.0, 3.2)      # x0 x1 y0 y1 z0 z1 (FROZEN)
WALL_T = 0.25
FRAME_T = 0.05                                  # thin MCM window profile
STAGE = "house_v2"
GREYBOX_COLL = "_greybox"

# zone -> (r, g, b, alpha). Starter animatic colors per docs/treatment/house.md
# ("Surfaces & material zones") — both style candidates rebind these later.
MATS = {
    "MAT_siding":       (0.86, 0.83, 0.72, 1.0),
    "MAT_fascia":       (0.92, 0.90, 0.86, 1.0),
    "MAT_block":        (0.80, 0.76, 0.68, 1.0),
    "MAT_roof_gravel":  (0.55, 0.52, 0.47, 1.0),
    "MAT_glass":        (0.45, 0.62, 0.72, 0.25),
    "MAT_frames":       (0.93, 0.92, 0.88, 1.0),
    "MAT_door_accent":  (0.69, 0.46, 0.29, 1.0),
    "MAT_deck":         (0.70, 0.66, 0.58, 1.0),
    "MAT_interior":     (0.90, 0.89, 0.85, 1.0),   # light — a dark interior
    "MAT_kitchen_tile": (0.85, 0.66, 0.66, 1.0),   # renders sq050_sh040 black
    "MAT_kitchen_cab":  (0.92, 0.92, 0.90, 1.0),
    "MAT_terrazzo":     (0.88, 0.86, 0.80, 1.0),
    "MAT_metal_93":     (0.26, 0.25, 0.23, 1.0),
    "MAT_plywood":      (0.72, 0.60, 0.40, 1.0),
}

CHECKS = []   # each build section appends f() -> list[str] of failures


def mat(name):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        r, g, b, a = MATS[name]
        bsdf = m.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (r, g, b, 1.0)
            bsdf.inputs["Roughness"].default_value = 0.85
            bsdf.inputs["Alpha"].default_value = a
        if a < 1.0:
            if hasattr(m, "surface_render_method"):
                m.surface_render_method = "BLENDED"
            elif hasattr(m, "blend_method"):
                m.blend_method = "BLEND"
            m.show_transparent_back = False
        m.diffuse_color = (r, g, b, a)
    return m


def stage():
    coll = bpy.data.collections.get(STAGE)
    if coll is None:
        coll = bpy.data.collections.new(STAGE)
        bpy.context.scene.collection.children.link(coll)
    return coll


def staging_meshes():
    return [ob for ob in stage().all_objects if ob.type == "MESH"]


def _box_data(x0, x1, y0, y1, z0, z1, base=0):
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
         (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    f = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1),
         (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    return v, [tuple(i + base for i in face) for face in f]


def _fix_normals(me):
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    me.update()


def multi_box(name, specs, mat_name):
    verts, faces = [], []
    for spec in specs:
        v, f = _box_data(*spec, base=len(verts))
        verts += v
        faces += f
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    _fix_normals(me)
    me.materials.append(mat(mat_name))
    ob = bpy.data.objects.new(name, me)
    stage().objects.link(ob)
    return ob


def box(name, x0, x1, y0, y1, z0, z1, mat_name):
    return multi_box(name, [(x0, x1, y0, y1, z0, z1)], mat_name)


def _wall(face):
    """(wall plane coord, outward sign, along-axis) — blockout convention."""
    x0, x1, y0, y1, _z0, _z1 = HOUSE
    return {"+Y": (y1, 1.0, "X"), "-Y": (y0, -1.0, "X"),
            "+X": (x1, 1.0, "Y"), "-X": (x0, -1.0, "Y")}[face]


def wall_spec(face, a0, a1, n0, n1, z0, z1):
    """Box spec against a house wall; n measured from the OUTER face
    (n<0 into the reveal, n>0 proud of it). Copied from blockout_property."""
    w, s, axis = _wall(face)
    p, q = sorted((w + s * n0, w + s * n1))
    return (a0, a1, p, q, z0, z1) if axis == "X" else (p, q, a0, a1, z0, z1)


def camera(name, loc, look_at, lens=35):
    data = bpy.data.cameras.new(name)
    data.lens = lens
    cam = bpy.data.objects.new(name, data)
    cam.location = loc
    direction = Vector(look_at) - Vector(loc)
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    return cam


def modeling_scene():
    sc = bpy.data.scenes.get("house_modeling")
    if sc is not None:
        return sc
    sc = bpy.data.scenes.new("house_modeling")
    sc.collection.children.link(stage())
    # context: existing set pieces the house must sit against. Objects can
    # live in many collections — this LINKS them, property is untouched.
    ctx = bpy.data.collections.new("hv2_context")
    sc.collection.children.link(ctx)
    for nm in ("ground_yard", "ground_roadside", "road", "driveway",
               "culvert", "bbq", "propane_tank", "truck_body", "truck_cab",
               "mailbox", "mailbox_post"):
        ob = bpy.data.objects.get(nm)
        if ob is not None:
            ctx.objects.link(ob)
    sun = bpy.data.objects.get("sun")
    if sun is not None:
        sc.collection.objects.link(sun)
    sc.world = bpy.data.worlds.get("sky")
    sc.render.engine = bpy.context.scene.render.engine
    sc.render.resolution_x, sc.render.resolution_y = 1280, 720
    sc.view_settings.view_transform = "AgX"
    for nm, loc, look, lens in (
        ("cam_model_front",  (16, -22, 4.5), (-2, 0, 2), 40),
        ("cam_model_rear",   (-2, 26, 5.0),  (-3, 2, 2), 40),
        ("cam_model_corner", (16, -16, 5.5), (-1, 0, 2), 35),
        ("cam_model_tunnel", (-10, -12, 1.4), (-10, 3, 1.2), 30),
        ("cam_model_kitchen", (-5.0, 1.2, 1.7), (5, 3, 1.5), 24),
        ("cam_model_porch",  (4, -9, 1.8), (-2, -4.5, 1.5), 32),
    ):
        cam = camera(nm, loc, look, lens)
        sc.collection.objects.link(cam)
    sc.camera = bpy.data.objects["cam_model_front"]
    return sc


def clear_stage():
    coll = bpy.data.collections.get(STAGE)
    if coll is None:
        return
    for ob in list(coll.all_objects):
        bpy.data.objects.remove(ob, do_unlink=True)


def build():
    clear_stage()
    stage()
    modeling_scene()
    # Tasks 2-8 append build calls here.


def run_checks():
    failures = []
    for fn in CHECKS:
        failures += fn()
    if failures:
        for f in failures:
            print("CHECK FAIL:", f)
        sys.exit(1)
    print(f"all {len(CHECKS)} check groups passed")


def _bounds(ob):
    pts = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    xs, ys, zs = zip(*[(p.x, p.y, p.z) for p in pts])
    return min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)


# Seven staged objects reuse a greybox name (house_roof, garage_roof,
# front_door, porch_deck, porch_post_0/1, back_stoop). While both live in
# this file, Blender would silently .001-suffix the new one — so those are
# BUILT as <name>_v2 and renamed at swap time (Task 10's RENAME_AT_SWAP).
# _ob() resolves either state; checks always use it.
def _ob(nm):
    return bpy.data.objects.get(nm + "_v2") or bpy.data.objects.get(nm)


def check_foundation():
    out = []
    prop = bpy.data.collections.get("property")
    if prop is None:
        return ["property collection missing"]
    names = {ob.name for ob in prop.objects}
    swapped = "house_wall_e" in names        # new shell present == swapped
    if not swapped and len(prop.objects) != 94:
        out.append(f"pre-swap property has {len(prop.objects)}, want 94")
    if any(n.startswith("_gb_") for n in names):
        out.append("greybox objects leaked into property")
    for ob in staging_meshes():
        for slot in ob.data.materials:
            if not slot.name.startswith("MAT_"):
                out.append(f"{ob.name}: non-zone material {slot.name}")
    return out


CHECKS.append(check_foundation)


def render_previews(outdir: Path):
    sc = bpy.data.scenes.get("house_modeling")
    outdir.mkdir(parents=True, exist_ok=True)
    for cam in [o for o in sc.collection.objects if o.type == "CAMERA"]:
        sc.camera = cam
        sc.render.filepath = str(outdir / f"{cam.name}.png")
        bpy.ops.render.render(write_still=True, scene=sc.name)
        print("rendered", cam.name)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--rebuild" in argv:
        build()
        bpy.ops.wm.save_mainfile()
        print("staging rebuilt + saved")
    if "--check" in argv:
        run_checks()
    for arg in argv:
        if arg.startswith("--previews="):
            render_previews(Path(arg.split("=", 1)[1]))
