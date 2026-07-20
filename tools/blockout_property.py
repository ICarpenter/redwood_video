#!/usr/bin/env python3
"""Build assets/envs/property/property.blend — greybox layout of the house,
road, and yards. Throwaway massing to establish the space so boards and
shot cameras agree on where everything is.

Site convention (documented in docs/treatment/site.md):
  +X east / -X west, +Y north = BACKYARD, -Y south = ROAD, +Z up.
  House faces south. Sun rises east (opening) and sets west (final sprint).

Everything lives in one root collection named `property` so shots can link
it; preview cameras stay outside that collection.

Run:
  "$BLENDER" --background --factory-startup --python-exit-code 1 \
      --python tools/blockout_property.py
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shotlib

ROOT = shotlib.project_root()
OUT = ROOT / "assets" / "envs" / "property" / "property.blend"

PALETTE = {
    "grass":     (0.32, 0.42, 0.16),
    "dirt":      (0.46, 0.36, 0.24),
    "gravel":    (0.55, 0.52, 0.47),
    "house":     (0.86, 0.83, 0.72),
    "roof":      (0.28, 0.24, 0.22),
    "porch":     (0.70, 0.66, 0.58),
    "window":    (0.45, 0.62, 0.72),
    "figure":    (0.85, 0.55, 0.20),
    "bbq":       (0.30, 0.31, 0.34),
    "santa":     (0.72, 0.13, 0.13),
    "truck":     (0.45, 0.28, 0.20),
    "marker":    (0.85, 0.20, 0.55),
    "label":     (0.05, 0.05, 0.05),
}

collection = None


def mat(name):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        bsdf = m.node_tree.nodes.get("Principled BSDF")
        col = PALETTE.get(name, (0.5, 0.5, 0.5))
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (*col, 1.0)
            bsdf.inputs["Roughness"].default_value = 0.85
        m.diffuse_color = (*col, 1.0)
    return m


def link(ob):
    collection.objects.link(ob)
    return ob


def box(name, x0, x1, y0, y1, z0, z1, material):
    """Axis-aligned box from opposing corners."""
    me = bpy.data.meshes.new(name)
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
         (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    f = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1),
         (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    me.from_pydata(v, [], f)
    me.update()
    me.materials.append(mat(material))
    return link(bpy.data.objects.new(name, me))


def gable_roof(name, x0, x1, y0, y1, z_eave, z_ridge):
    """Gable roof with the ridge running along X."""
    ym = (y0 + y1) / 2
    me = bpy.data.meshes.new(name)
    v = [(x0, y0, z_eave), (x1, y0, z_eave), (x1, y1, z_eave),
         (x0, y1, z_eave), (x0, ym, z_ridge), (x1, ym, z_ridge)]
    f = [(0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5)]
    me.from_pydata(v, [], f)
    me.update()
    me.materials.append(mat("roof"))
    return link(bpy.data.objects.new(name, me))


def cyl(name, x, y, z, radius, depth, material, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth,
                                        location=(x, y, z), rotation=rot)
    ob = bpy.context.active_object
    ob.name = name
    ob.data.materials.append(mat(material))
    # the primitive op links into whatever collection is active
    for coll in list(ob.users_collection):
        coll.objects.unlink(ob)
    collection.objects.link(ob)
    return ob


def label(text, x, y, size=0.9):
    """Flat ground label, readable from the top-down site plan."""
    curve = bpy.data.curves.new(f"lbl_{text}", type="FONT")
    curve.body = text
    curve.size = size
    curve.align_x = "CENTER"
    curve.materials.append(mat("label"))
    ob = bpy.data.objects.new(f"lbl_{text}", curve)
    ob.location = (x, y, 0.12)
    return link(ob)


def camera(name, loc, look_at, lens=35, ortho_scale=None):
    """Preview camera aimed at a point; kept OUT of the property collection."""
    data = bpy.data.cameras.new(name)
    data.lens = lens
    if ortho_scale:
        data.type = "ORTHO"
        data.ortho_scale = ortho_scale
    cam = bpy.data.objects.new(name, data)
    cam.location = loc
    direction = Vector(look_at) - Vector(loc)
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.collection.objects.link(cam)
    return cam


def build():
    global collection
    scene = bpy.context.scene
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)

    collection = bpy.data.collections.new("property")
    scene.collection.children.link(collection)

    # --- ground, road, ditch, driveway -------------------------------------
    # the yard and the roadside are separate slabs so the ditch between them
    # is an actual open trench the cruiser can nose into
    box("ground_yard", -45, 45, -14, 45, -0.1, 0.0, "grass")
    box("ground_roadside", -45, 45, -32, -17, -0.1, 0.0, "grass")
    box("road", -45, 45, -23, -17, 0.0, 0.03, "dirt")
    box("ditch_floor", -45, 45, -17, -14, -0.85, -0.80, "dirt")
    box("ditch_wall_s", -45, 45, -17.05, -17.0, -0.85, 0.0, "dirt")
    box("ditch_wall_n", -45, 45, -14.0, -13.95, -0.85, 0.0, "dirt")
    # culvert: the driveway crosses the ditch
    box("culvert", -12.5, -7.5, -17, -14, -0.1, 0.05, "gravel")
    box("driveway", -12.5, -7.5, -14, -3, 0.0, 0.03, "gravel")
    cyl("mailbox_post", -6.5, -15.5, 0.6, 0.07, 1.2, "porch")
    box("mailbox", -6.85, -6.15, -15.75, -15.25, 1.2, 1.55, "bbq")

    # --- house (faces south) + attached garage on the WEST ------------------
    box("house", -7, 5, -4, 5, 0.0, 3.2, "house")
    gable_roof("house_roof", -7.6, 5.6, -4.6, 5.6, 3.2, 5.2)
    box("garage", -13, -7, -3, 3, 0.0, 2.9, "house")
    gable_roof("garage_roof", -13.5, -6.9, -3.5, 3.5, 2.9, 4.1)
    box("garage_door", -12.4, -7.6, -3.05, -2.95, 0.1, 2.4, "porch")

    # front porch + steps (Mom fires from here in the final shot)
    box("porch_deck", -5, 1, -6.4, -4, 0.0, 0.5, "porch")
    for i, px in enumerate((-4.7, 0.7)):
        box(f"porch_post_{i}", px - 0.12, px + 0.12, -6.3, -6.06, 0.5, 3.0, "porch")
    box("porch_roof", -5.2, 1.2, -6.6, -3.9, 3.0, 3.2, "roof")
    box("front_door", -2.4, -1.4, -4.05, -3.95, 0.5, 2.5, "porch")

    # back stoop
    box("back_stoop", -4, -1, 5, 6.2, 0.0, 0.45, "porch")

    # --- windows: kitchen at the NE corner sees BOTH backyard and side ------
    box("win_kitchen_north", 1.4, 4.2, 4.95, 5.05, 1.2, 2.4, "window")
    box("win_kitchen_east", 4.95, 5.05, 1.6, 4.2, 1.2, 2.4, "window")
    box("win_front", -6.0, -4.2, -4.05, -3.95, 1.2, 2.4, "window")

    # --- backyard set pieces ------------------------------------------------
    # firing squad line (5 action figures), north end of the yard
    for i in range(5):
        fx = -6 + i * 3.0
        box(f"figure_{i}", fx - 0.45, fx + 0.45, 19.6, 20.4, 0.0, 1.9, "figure")

    # old truck on blocks — east edge: the ricochet surface, and set dressing
    box("truck_body", 10.5, 14.5, 13.0, 19.0, 0.7, 2.3, "truck")
    box("truck_cab", 10.5, 14.5, 13.0, 15.2, 2.3, 3.1, "truck")

    # propane BBQ — east of centre, where the boy's spray swings across
    box("bbq", 5.2, 7.0, 10.4, 11.8, 0.0, 1.1, "bbq")
    cyl("propane_tank", 7.4, 11.1, 0.45, 0.28, 0.9, "bbq")

    # vintage Santa — Mom's one rule, near the back stoop, in the blast zone
    cyl("santa", -8.5, 7.5, 0.9, 0.55, 1.8, "santa")

    # clothesline (ventilated in the firefight; her floral dress hangs here)
    for i, cx in enumerate((-13.5, -4.5)):
        cyl(f"line_post_{i}", cx, 11.0, 1.1, 0.09, 2.2, "porch")
    box("laundry", -12.6, -5.4, 10.9, 11.1, 1.5, 2.1, "window")

    # --- yard boundary: fence + treeline contain the backyard ---------------
    for i in range(15):
        fx = -21 + i * 3.0
        box(f"fence_post_{i}", fx - 0.09, fx + 0.09, 26.9, 27.1, 0.0, 1.3, "porch")
    box("fence_rail_hi", -21, 21, 26.95, 27.05, 1.05, 1.2, "porch")
    box("fence_rail_lo", -21, 21, 26.95, 27.05, 0.45, 0.6, "porch")

    for i, (tx, ty, scale) in enumerate([
        (-19, 31, 1.15), (-12, 33, 0.9), (-4, 31.5, 1.3), (5, 34, 1.0),
        (13, 31, 1.2), (20, 33.5, 0.95), (25, 29, 1.1), (-25, 30, 1.0),
    ]):
        cyl(f"trunk_{i}", tx, ty, 1.4 * scale, 0.35 * scale, 2.8 * scale, "truck")
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=2.6 * scale, location=(tx, ty, 4.6 * scale), segments=12,
            ring_count=8)
        canopy = bpy.context.active_object
        canopy.name = f"canopy_{i}"
        canopy.scale = (1.0, 1.0, 0.8)
        canopy.data.materials.append(mat("grass"))
        for coll in list(canopy.users_collection):
            coll.objects.unlink(canopy)
        collection.objects.link(canopy)

    # --- action markers -----------------------------------------------------
    cyl("mark_boy", -2.0, 8.5, 0.9, 0.45, 1.8, "marker")
    cyl("mark_sheriff_crash", 10.0, -15.5, 0.5, 0.6, 1.0, "marker")

    # --- labels (site plan only; hidden before perspective renders) ---------
    for text, x, y in (
        ("ROAD (sprint west ->)", 0, -20), ("DITCH / CRASH", 10, -15.5),
        ("DRIVEWAY", -10, -10), ("GARAGE", -10, 0), ("HOUSE", -1, 0),
        ("PORCH", -2, -7.4), ("KITCHEN WINDOWS", 12.5, 4.5),
        ("SIDE CORRIDOR", 10.5, -6), ("BACKYARD", -2, 14),
        ("FIRING SQUAD", 0, 21.6), ("TRUCK", 12.5, 20.2), ("BBQ", 6, 9.2),
        ("SANTA", -8.5, 5.9), ("CLOTHESLINE", -9, 12.2), ("BOY", -2.0, 7.0),
    ):
        label(text, x, y)

    # --- lighting -----------------------------------------------------------
    world = bpy.data.worlds.new("sky")
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.42, 0.55, 0.75, 1.0)
        bg.inputs["Strength"].default_value = 0.6
    scene.world = world

    sun_data = bpy.data.lights.new("sun", type="SUN")
    sun_data.energy = 3.2
    sun_data.angle = math.radians(2.0)
    sun = bpy.data.objects.new("sun", sun_data)
    # low morning sun out of the east (light travels west; 255 deg would be
    # a sunset). The final sprint reverses this to a western sunset.
    sun.rotation_euler = (math.radians(62), 0.0, math.radians(75))
    scene.collection.objects.link(sun)

    # --- render settings + preview cameras ----------------------------------
    engines = {i.identifier for i in
               bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items}
    scene.render.engine = ("BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engines
                           else "BLENDER_EEVEE")
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"

    camera("cam_site", (0, 2, 70), (0, 2, 0), ortho_scale=62)
    camera("cam_intro", (-26, -30, 5.5), (-3, 2, 3), lens=45)
    # behind the boy (house wall is at y=5 — keep cameras out of the box)
    camera("cam_backyard", (-4.5, 6.4, 2.5), (1, 19, 1.2), lens=32)
    camera("cam_kitchen", (3.2, 5.4, 1.9), (-1, 16, 1.2), lens=28)
    camera("cam_road", (26, -20, 1.6), (-10, -19, 1.6), lens=40)
    camera("cam_sidecorridor", (9.0, -12.0, 1.2), (7.5, 12, 1.2), lens=30)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT), relative_remap=True)
    print(f"blockout saved: {OUT.relative_to(ROOT)}")


def render_previews(outdir: Path):
    scene = bpy.context.scene
    outdir.mkdir(parents=True, exist_ok=True)
    labels = [ob for ob in bpy.data.objects if ob.name.startswith("lbl_")]

    for cam_name in ("cam_site", "cam_intro", "cam_backyard", "cam_kitchen",
                     "cam_road", "cam_sidecorridor"):
        cam = bpy.data.objects.get(cam_name)
        if cam is None:
            continue
        scene.camera = cam
        # labels are for the plan view only; the plan renders square so the
        # road and the far end of the backyard both fit
        is_plan = cam_name == "cam_site"
        for lb in labels:
            lb.hide_render = not is_plan
        scene.render.resolution_x = 1280
        scene.render.resolution_y = 1280 if is_plan else 720
        scene.render.filepath = str(outdir / f"{cam_name}.png")
        bpy.ops.render.render(write_still=True)
        print(f"rendered {cam_name}")


if __name__ == "__main__":
    build()
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    for arg in argv:
        if arg.startswith("--previews="):
            render_previews(Path(arg.split("=", 1)[1]))
