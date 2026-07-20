#!/usr/bin/env python3
"""Build the animatic scale-guide asset files.

Writes assets/chars/cast.blend and assets/props/props.blend: one collection
per guide (see tools/guides.py), each assembled from primitives into a
recognisable silhouette, marked as a catalogued Asset. Also writes
assets/blender_assets.cats.txt. Guides are authored in real metres, facing -Y,
feet at Z=0, centred on X=0 (see guides.py for the board-camera rationale).

Run (default → the real asset paths; refuses to clobber without --force):
  "$BLENDER" --background --factory-startup --python-exit-code 1 \
      --python tools/guide_assets.py

Flags (after --):
  --force                 overwrite the real asset files
  --out=<dir>            build throwaway copies into <dir> (cats file too)
  --previews=<dir>       render each guide to <dir>/<name>.png
  --check                build to a temp dir + assert invariants, then exit
  --mark-property        mark the `property` collection in property.blend
"""
import math
import sys
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import guides
import shotlib

# --- dimension-check tolerances -----------------------------------------
FEET_TOL = 0.03    # |min Z| — feet must sit on the floor
CENTRE_TOL = 0.12  # |centre X| — centred on the drawing axis
HEIGHT_TOL = 0.25  # relative tolerance on target height (art wiggle room)

PALETTE = {
    "skin":     (0.85, 0.62, 0.45),
    "boy":      (0.20, 0.40, 0.70),
    "mom":      (0.72, 0.30, 0.52),
    "sheriff":  (0.28, 0.36, 0.30),
    "hat":      (0.32, 0.26, 0.18),
    "metal":    (0.30, 0.32, 0.35),
    "plastic":  (0.80, 0.75, 0.22),
    "tire":     (0.06, 0.06, 0.06),
    "truck":    (0.45, 0.28, 0.20),
    "cruiser":  (0.14, 0.20, 0.45),
    "lightbar": (0.85, 0.20, 0.20),
    "santa":    (0.72, 0.13, 0.13),
    "white":    (0.90, 0.90, 0.90),
    "ref":      (0.90, 0.50, 0.10),
    "dark":     (0.10, 0.10, 0.12),
    "wood":     (0.50, 0.35, 0.20),
}


def _mat(color_key):
    name = f"guide_{color_key}"
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        col = PALETTE.get(color_key, (0.5, 0.5, 0.5))
        bsdf = m.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (*col, 1.0)
            bsdf.inputs["Roughness"].default_value = 0.9
        m.diffuse_color = (*col, 1.0)
    return m


def _move_to(ob, coll):
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    coll.objects.link(ob)


def box(coll, name, cx, cy, cz, sx, sy, sz, color):
    """Box centred at (cx,cy,cz) with full sizes (sx,sy,sz)."""
    hx, hy, hz = sx / 2, sy / 2, sz / 2
    x0, x1, y0, y1, z0, z1 = cx-hx, cx+hx, cy-hy, cy+hy, cz-hz, cz+hz
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
         (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    f = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1),
         (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(v, [], f)
    me.update()
    me.materials.append(_mat(color))
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    return ob


def cyl(coll, name, cx, cy, cz, radius, depth, color, axis="Z"):
    rot = {"Z": (0, 0, 0), "X": (0, math.radians(90), 0),
           "Y": (math.radians(90), 0, 0)}[axis]
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth,
                                        location=(cx, cy, cz), rotation=rot,
                                        vertices=16)
    ob = bpy.context.active_object
    ob.name = name
    ob.data.materials.append(_mat(color))
    _move_to(ob, coll)
    return ob


def ball(coll, name, cx, cy, cz, radius, color):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=(cx, cy, cz),
                                         segments=16, ring_count=8)
    ob = bpy.context.active_object
    ob.name = name
    ob.data.materials.append(_mat(color))
    _move_to(ob, coll)
    return ob


# --- builders (initial geometry; refine against --previews) --------------
# Each takes the target collection; builds facing -Y, feet at Z=0, centred X=0.

def build_boy(c):
    box(c, "boy_leg_l", -0.11, 0, 0.30, 0.16, 0.18, 0.60, "boy")
    box(c, "boy_leg_r", 0.11, 0, 0.30, 0.16, 0.18, 0.60, "boy")
    box(c, "boy_torso", 0, 0, 0.85, 0.42, 0.24, 0.55, "boy")
    box(c, "boy_arm_l", -0.30, 0, 0.85, 0.10, 0.10, 0.48, "skin")
    box(c, "boy_arm_r", 0.30, 0, 0.85, 0.10, 0.10, 0.48, "skin")
    ball(c, "boy_head", 0, 0, 1.20, 0.15, "skin")


def build_mom(c):
    box(c, "mom_skirt", 0, 0, 0.42, 0.52, 0.34, 0.84, "mom")
    box(c, "mom_torso", 0, 0, 1.05, 0.42, 0.24, 0.52, "mom")
    box(c, "mom_apron", 0, -0.18, 0.62, 0.30, 0.04, 0.60, "white")
    box(c, "mom_arm_l", -0.30, 0, 1.05, 0.10, 0.10, 0.46, "skin")
    box(c, "mom_arm_r", 0.30, 0, 1.05, 0.10, 0.10, 0.46, "skin")
    ball(c, "mom_head", 0, 0, 1.52, 0.16, "skin")
    for i in range(6):
        a = math.radians(30 + i * 24)
        ball(c, f"mom_curler_{i}", 0.13 * math.cos(a), 0.02,
             1.62 + 0.06 * math.sin(a), 0.04, "white")


def build_sheriff(c):
    box(c, "sh_leg_l", -0.13, 0, 0.34, 0.18, 0.20, 0.68, "sheriff")
    box(c, "sh_leg_r", 0.13, 0, 0.34, 0.18, 0.20, 0.68, "sheriff")
    ball(c, "sh_belly", 0, -0.06, 0.98, 0.30, "sheriff")
    box(c, "sh_torso", 0, 0, 1.20, 0.46, 0.26, 0.40, "sheriff")
    box(c, "sh_arm_l", -0.34, 0, 1.10, 0.11, 0.11, 0.50, "sheriff")
    box(c, "sh_arm_r", 0.34, 0, 1.10, 0.11, 0.11, 0.50, "sheriff")
    ball(c, "sh_head", 0, 0, 1.58, 0.16, "skin")
    cyl(c, "sh_hat_brim", 0, 0, 1.70, 0.28, 0.03, "hat", axis="Z")
    cyl(c, "sh_hat_crown", 0, 0, 1.77, 0.15, 0.14, "hat", axis="Z")


def build_machine_gun(c):
    # Shifted -0.05 on X from the naive layout (which centres ~0.10, right at
    # the CENTRE_TOL edge): the long barrel dominates the +X side, so the
    # whole gun is nudged toward -X for a safer margin.
    box(c, "mg_receiver", -0.05, 0, 0.18, 0.55, 0.12, 0.14, "metal")
    cyl(c, "mg_barrel", 0.43, 0, 0.20, 0.03, 0.55, "metal", axis="X")
    box(c, "mg_mag", -0.03, 0, 0.06, 0.10, 0.08, 0.16, "metal")
    box(c, "mg_stock", -0.45, 0, 0.15, 0.30, 0.10, 0.16, "wood")
    box(c, "mg_grip", -0.15, 0, 0.05, 0.08, 0.08, 0.12, "wood")


def build_printer(c):
    box(c, "pr_base", 0, 0, 0.10, 0.90, 0.90, 0.20, "plastic")
    for i, (x, y) in enumerate([(-0.4, -0.4), (0.4, -0.4), (-0.4, 0.4), (0.4, 0.4)]):
        cyl(c, f"pr_post_{i}", x, y, 0.75, 0.03, 1.10, "metal", axis="Z")
    box(c, "pr_gantry", 0, 0, 1.00, 0.90, 0.12, 0.08, "metal")
    box(c, "pr_head", 0, 0, 0.95, 0.12, 0.12, 0.14, "metal")
    box(c, "pr_top", 0, 0, 1.35, 0.90, 0.90, 0.10, "plastic")


def build_action_figure(c):
    box(c, "af_leg_l", -0.14, 0, 0.45, 0.18, 0.20, 0.90, "plastic")
    box(c, "af_leg_r", 0.14, 0, 0.45, 0.18, 0.20, 0.90, "plastic")
    box(c, "af_torso", 0, 0, 1.20, 0.50, 0.28, 0.60, "plastic")
    box(c, "af_arm_l", -0.36, 0, 1.20, 0.12, 0.12, 0.58, "plastic")
    box(c, "af_arm_r", 0.36, 0, 1.20, 0.12, 0.12, 0.58, "plastic")
    ball(c, "af_head", 0, 0, 1.65, 0.15, "skin")


def build_delivery_truck(c):
    # Recentred on X=0: cab and cargo straddle the origin so the combined
    # bounding-box centre satisfies CENTRE_TOL (was cab=-2.1..cargo=1.4,
    # centre~=-0.35). Cargo box is wider than the cab, so the cab is shifted
    # further negative and the cargo less positive to balance the box.
    box(c, "dt_cargo", 0.9, 0, 1.80, 2.20, 2.00, 2.40, "truck")
    box(c, "dt_cab", -1.5, 0, 1.20, 1.00, 2.00, 1.60, "cruiser")
    for i, (x, y) in enumerate([(-1.3, -1.0), (-1.3, 1.0),
                                (1.7, -1.0), (1.7, 1.0)]):
        cyl(c, f"dt_wheel_{i}", x, y, 0.40, 0.40, 0.30, "tire", axis="Y")


def build_cruiser(c):
    box(c, "cr_body", 0, 0, 0.70, 3.60, 1.70, 0.60, "cruiser")
    box(c, "cr_cabin", 0, 0, 1.15, 1.90, 1.60, 0.60, "cruiser")
    for i, (x, y) in enumerate([(-1.2, -0.85), (-1.2, 0.85),
                                (1.2, -0.85), (1.2, 0.85)]):
        cyl(c, f"cr_wheel_{i}", x, y, 0.35, 0.35, 0.25, "tire", axis="Y")
    box(c, "cr_lightbar", 0, 0, 1.50, 0.60, 0.40, 0.12, "lightbar")


def build_rosco(c):
    box(c, "ro_slide", 0.0, 0, 0.15, 0.22, 0.05, 0.06, "metal")
    box(c, "ro_grip", -0.07, 0, 0.065, 0.06, 0.05, 0.13, "dark")


def build_big_pistol(c):
    box(c, "bp_slide", 0.0, 0, 0.34, 0.52, 0.10, 0.12, "metal")
    cyl(c, "bp_barrel", 0.30, 0, 0.34, 0.05, 0.14, "metal", axis="X")
    box(c, "bp_grip", -0.16, 0, 0.15, 0.12, 0.10, 0.30, "dark")


def build_santa(c):
    box(c, "sa_body", 0, 0, 0.60, 0.60, 0.42, 1.20, "santa")
    box(c, "sa_belt", 0, -0.01, 0.72, 0.62, 0.44, 0.12, "dark")
    ball(c, "sa_head", 0, 0, 1.42, 0.22, "skin")
    ball(c, "sa_hat", 0, 0, 1.62, 0.15, "santa")
    ball(c, "sa_hat_tip", 0.05, 0, 1.76, 0.05, "white")
    box(c, "sa_tape", 0, -0.22, 0.90, 0.20, 0.02, 0.34, "white")


def build_scale_stick(c):
    cyl(c, "ss_pole", 0, 0, 1.00, 0.03, 2.00, "ref", axis="Z")
    for i in range(1, 5):
        col = "white" if i % 2 else "ref"
        cyl(c, f"ss_tick_{i}", 0, 0, i * 0.5, 0.12, 0.02, col, axis="Z")


BUILDERS = {
    "boy": build_boy, "mom": build_mom, "sheriff": build_sheriff,
    "machine_gun": build_machine_gun, "printer": build_printer,
    "action_figure": build_action_figure, "delivery_truck": build_delivery_truck,
    "cruiser": build_cruiser, "rosco": build_rosco, "big_pistol": build_big_pistol,
    "santa": build_santa, "scale_stick": build_scale_stick,
}


# --- build / check / previews -------------------------------------------

def _wipe():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    scene = bpy.context.scene
    for coll in list(bpy.data.collections):
        try:
            scene.collection.children.unlink(coll)
        except (RuntimeError, ReferenceError):
            pass
        bpy.data.collections.remove(coll)


def build_guide_file(specs, out_path):
    _wipe()
    scene = bpy.context.scene
    for spec in specs:
        coll = bpy.data.collections.new(spec.name)
        scene.collection.children.link(coll)
        BUILDERS[spec.name](coll)
        coll.asset_mark()
        uuid, _path, _simple = guides.CATALOGS[spec.catalog]
        coll.asset_data.catalog_id = uuid
        # catalog_simple_name is read-only on this Blender (5.1.2) — setting
        # catalog_id alone satisfies the asset-marking contract.
    check_structural(specs)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out_path), relative_remap=True)
    print(f"guide file saved: {out_path}")


def _coll_bounds(coll):
    xs, ys, zs = [], [], []
    for ob in coll.objects:
        for corner in ob.bound_box:
            wc = ob.matrix_world @ Vector(corner)
            xs.append(wc.x); ys.append(wc.y); zs.append(wc.z)
    return (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))


def check_structural(specs):
    for spec in specs:
        coll = bpy.data.collections.get(spec.name)
        assert coll is not None, f"missing collection {spec.name}"
        assert coll.asset_data is not None, f"{spec.name} not marked as asset"
        expect = guides.CATALOGS[spec.catalog][0]
        assert coll.asset_data.catalog_id == expect, \
            f"{spec.name} catalog {coll.asset_data.catalog_id} != {expect}"
        assert len(coll.objects) > 0, f"{spec.name} is empty"


def check_dimensions(specs):
    for spec in specs:
        coll = bpy.data.collections.get(spec.name)
        x0, x1, _y0, _y1, z0, z1 = _coll_bounds(coll)
        assert abs(z0) <= FEET_TOL, f"{spec.name} feet z={z0:.3f} not at 0"
        cx = (x0 + x1) / 2
        assert abs(cx) <= CENTRE_TOL, f"{spec.name} centre x={cx:.3f} off-axis"
        h = z1 - z0
        assert abs(h - spec.height) <= HEIGHT_TOL * spec.height, \
            f"{spec.name} height {h:.2f} != {spec.height} (+-{HEIGHT_TOL:.0%})"


def run_check():
    tmp = Path(tempfile.mkdtemp(prefix="guides_check_"))
    for rel in (guides.CAST_FILE, guides.PROPS_FILE):
        specs = guides.guides_for_file(rel)
        build_guide_file(specs, tmp / Path(rel).name)
        check_dimensions(specs)
    print("GUIDE CHECK OK")


def render_previews(specs, outdir):
    outdir.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    engines = {i.identifier for i in
               bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items}
    scene.render.engine = ("BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engines
                           else "BLENDER_EEVEE")
    scene.render.resolution_x = scene.render.resolution_y = 512
    scene.render.film_transparent = True
    for spec in specs:
        coll = bpy.data.collections.get(spec.name)
        x0, x1, _y0, _y1, z0, z1 = _coll_bounds(coll)
        span = max(x1 - x0, z1 - z0, 0.3) * 1.4
        cam_data = bpy.data.cameras.new(f"prev_{spec.name}")
        cam_data.type = "ORTHO"
        cam_data.ortho_scale = span
        cam = bpy.data.objects.new(f"prev_{spec.name}", cam_data)
        cam.location = (0.0, -8.0, (z0 + z1) / 2)
        cam.rotation_euler = (math.radians(90), 0.0, 0.0)
        scene.collection.objects.link(cam)
        scene.camera = cam
        for other in guides.guides_for_file(spec.file):
            oc = bpy.data.collections.get(other.name)
            oc.hide_render = (other.name != spec.name)
        scene.render.filepath = str(outdir / f"{spec.name}.png")
        bpy.ops.render.render(write_still=True)
        bpy.data.objects.remove(cam, do_unlink=True)
        print(f"preview: {spec.name}")


def mark_property_asset():
    root = shotlib.project_root()
    path = root / guides.PROPERTY_FILE
    bpy.ops.wm.open_mainfile(filepath=str(path))
    coll = bpy.data.collections.get("property")
    if coll is None:
        sys.exit("error: no `property` collection in property.blend")
    if coll.asset_data is None:
        coll.asset_mark()
    uuid, _p, _simple = guides.CATALOGS["set"]
    coll.asset_data.catalog_id = uuid
    # catalog_simple_name is read-only on this Blender (5.1.2) — setting
    # catalog_id alone satisfies the asset-marking contract.
    # ensure the shared cats file exists next to assets/
    (root / "assets" / "blender_assets.cats.txt").write_text(guides.cats_file_text())
    bpy.ops.wm.save_as_mainfile(filepath=str(path), relative_remap=True)
    print(f"marked property collection as asset in {path}")


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    force = "--force" in argv
    out_dir = previews = None
    for a in argv:
        if a.startswith("--out="):
            out_dir = Path(a.split("=", 1)[1])
        elif a.startswith("--previews="):
            previews = Path(a.split("=", 1)[1])

    if "--check" in argv:
        run_check()
        return
    if "--mark-property" in argv:
        mark_property_asset()
        return

    root = shotlib.project_root()
    for rel in (guides.CAST_FILE, guides.PROPS_FILE):
        specs = guides.guides_for_file(rel)
        out_path = (out_dir / Path(rel).name) if out_dir else (root / rel)
        if out_dir is None and out_path.exists() and not force:
            sys.exit(f"error: {out_path.relative_to(root)} exists and is now "
                     "hand-maintained. Edit it in Blender, or pass --force to "
                     "regenerate (DESTROYS manual edits); --out=<dir> for a "
                     "throwaway build.")
        build_guide_file(specs, out_path)
        if previews:
            render_previews(specs, previews)

    cats_dir = out_dir if out_dir else (root / "assets")
    cats_dir.mkdir(parents=True, exist_ok=True)
    (cats_dir / "blender_assets.cats.txt").write_text(guides.cats_file_text())
    print("cats file written")


if __name__ == "__main__":
    main()
