#!/usr/bin/env python3
"""Build assets/envs/property/property.blend — greybox layout of the house,
road, and yards. Throwaway massing to establish the space so layout scenes and
shot cameras agree on where everything is.

Builds the static SET only (environment + set-dressing). The cast and props
are never staged here: each layout scene stages its own cast/prop guide
instances, in world space, into its own `<code>_blocking` collection (via
tools/stage_shots.py or the Redwood Guides add-on) — so they reference their
source files directly and never travel with the linkable `property` set.

Site convention (docs/treatment/site.md has the canonical table). The
compass does NOT line up with the axes the way you would guess -- it is
fixed by the sun, which is the film's clock:

  -Y = EAST  = the ROAD      (sunrise; the film opens here)
  +Y = WEST  = the BACKYARD  (sunset; the film ends here)
  +X = NORTH = the SIDE CORRIDOR (truck, clothesline, the sheriff's crawl)
  -X = SOUTH = the GARAGE
  +Z = up

So the house FACES EAST, the kitchen is its NORTH-WEST corner, and the
kitchen's NORTH window is the one looking down the corridor at the truck.

Everything lives in one root collection named `property` so shots can link
it; preview cameras stay outside that collection.

Run:
  "$BLENDER" --background --factory-startup --python-exit-code 1 \
      --python tools/blockout_property.py
"""
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

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
    # hanging sheets on the clothesline. Its own entry because it used to
    # borrow "window", and windows are now transparent — sheets are not.
    "laundry":   (0.90, 0.89, 0.86),
    # painted window casing/sash trim
    "trim":      (0.93, 0.92, 0.88),
    # painted interior: walls, window reveals, the kitchen partition. Light,
    # not dark — a camera INSIDE the house (sq050_sh040 shoots the gun cabinet
    # from across the kitchen) is looking at these surfaces, and a near-black
    # interior renders the whole frame black.
    "interior":  (0.90, 0.89, 0.85),
}

# Per-material alpha. Anything absent is fully opaque.
ALPHA = {
    "window": 0.25,
}

# --- house shell ---------------------------------------------------------
# The house used to be a solid block, so a "window" could only ever be a
# decal on the outside. It is now a shell: real openings, a painted interior
# behind them, and casements that actually swing.
HOUSE = (-7.0, 5.0, -4.0, 5.0, 0.0, 3.2)     # x0 x1 y0 y1 z0 z1
WALL_T = 0.25
TRIM = 0.08                                   # casing width
SASH_T = 0.06                                 # casement thickness

# name, face, a0, a1, sill, head, open_degrees
#   face is the OUTWARD normal; a0..a1 runs along that wall
#   (x for the ±Y walls, y for the ±X walls)
# Names are COMPASS names; the `face` column is the blend axis it sits on.
WINDOWS = [
    # the two kitchen windows, NW corner of the house — open double casements.
    # `kitchen_north` is the one down the corridor at the truck: Mom watches
    # the sheriff creep past the laundry through it, and later shoots at him
    # through it. `kitchen_west` looks over the backyard at the massacre.
    ("kitchen_west",  "+Y",  1.40,  4.20, 1.20, 2.40, 62.0),
    ("kitchen_north", "+X",  1.60,  4.20, 1.20, 2.40, 62.0),
    # front of the house, facing the road: either side of the door
    ("front_south",   "-Y", -6.00, -4.20, 1.20, 2.40,  0.0),
    ("front_north",   "-Y",  1.99,  3.79, 1.20, 2.40,  0.0),
    # further down the corridor, toward the road end
    ("north_east",    "+X", -2.80, -1.40, 1.20, 2.40,  0.0),
    # backyard wall, south of the stoop
    ("west_south",    "+Y", -6.40, -5.20, 1.50, 2.40,  0.0),
    # south gable, west of where the garage attaches (garage spans y -3..3)
    ("south_west",    "-X",  3.40,  4.60, 1.20, 2.40,  0.0),
]

collection = None
labels_coll = None


def mat(name):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        bsdf = m.node_tree.nodes.get("Principled BSDF")
        col = PALETTE.get(name, (0.5, 0.5, 0.5))
        alpha = ALPHA.get(name, 1.0)
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (*col, 1.0)
            bsdf.inputs["Roughness"].default_value = 0.85
            bsdf.inputs["Alpha"].default_value = alpha
        if alpha < 1.0:
            # EEVEE Next alpha-blends via surface_render_method (5.x); older
            # builds only have blend_method — set whichever exists. Same
            # approach guide_assets.py uses for the cruiser's glass.
            if hasattr(m, "surface_render_method"):
                m.surface_render_method = "BLENDED"
            elif hasattr(m, "blend_method"):
                m.blend_method = "BLEND"
            m.show_transparent_back = False
        m.diffuse_color = (*col, alpha)
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
    fix_normals(me)
    me.materials.append(mat(material))
    return link(bpy.data.objects.new(name, me))


def fix_normals(me):
    """Make face normals point outward.

    The hand-written box winding here is inside-out. Nothing noticed for a
    long time — EEVEE shades backfaces with a flipped normal, so a greybox
    looks identical either way — but a boolean reads an inverted solid as its
    own complement, and every cut silently does nothing. Measured: the house
    hollow reported FINISHED and left 8 verts as 8 verts.
    """
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    me.update()
    return me


def _box_data(x0, x1, y0, y1, z0, z1, base=0):
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
         (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    f = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1),
         (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    return v, [tuple(i + base for i in face) for face in f]


def multi_box(name, specs, material, link_it=True):
    """One mesh from several boxes — a casing or a sash ring stays one object."""
    verts, faces = [], []
    for spec in specs:
        v, f = _box_data(*spec, base=len(verts))
        verts += v
        faces += f
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    fix_normals(me)
    me.materials.append(mat(material))
    ob = bpy.data.objects.new(name, me)
    return link(ob) if link_it else ob


def cut(target, name, x0, x1, y0, y1, z0, z1, material="house"):
    """Boolean-difference a box out of `target` and apply it.

    material_mode TRANSFER so the new interior faces carry the CUTTER's
    material — that is what makes a reveal or a hollow read as dark inside
    instead of as more clapboard.
    """
    cutter = box(f"_cut_{name}", x0, x1, y0, y1, z0, z1, material)
    m = target.modifiers.new(f"cut_{name}", "BOOLEAN")
    m.operation = "DIFFERENCE"
    m.object = cutter
    m.solver = "EXACT"
    if hasattr(m, "material_mode"):
        m.material_mode = "TRANSFER"
    # A cutter created this tick is not in the depsgraph yet, and applying
    # against it is a silent no-op that still reports FINISHED. Measured: the
    # very first cut of the run (the house hollow) left 8 verts as 8 verts.
    bpy.context.view_layer.update()
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    return target


def _wall(face):
    """(wall plane coord, outward sign, axis) for a named house face."""
    x0, x1, y0, y1, _z0, _z1 = HOUSE
    return {"+Y": (y1, 1.0, "X"), "-Y": (y0, -1.0, "X"),
            "+X": (x1, 1.0, "Y"), "-X": (x0, -1.0, "Y")}[face]


def wall_spec(face, a0, a1, n0, n1, z0, z1):
    """Box spec placed against a wall.

    `a` runs along the wall, `n` runs along the OUTWARD normal measured from
    the wall's outer face — so n<0 is into the reveal, n>0 is proud of it.
    """
    w, s, axis = _wall(face)
    p, q = sorted((w + s * n0, w + s * n1))
    return (a0, a1, p, q, z0, z1) if axis == "X" else (p, q, a0, a1, z0, z1)


def _sash_matrix(hinge, u, n, swing_deg):
    """Place a sash built in local space (x = hinge->free edge, y = outward).

    Written straight into matrix_world rather than as loc/rot/scale: the
    closed-state basis for the second leaf of a pair is a REFLECTION, and no
    Euler rotation produces one. Blender decomposes the negative determinant
    into a -1 scale itself.

    Opening swings the free edge along the outward normal, so the sign of the
    swing depends on the handedness of (u, n): +theta when n == Z x u.
    """
    sign = 1.0 if (Vector((0, 0, 1)).cross(u) - n).length < 1e-6 else -1.0
    t = math.radians(swing_deg) * sign
    c, s = math.cos(t), math.sin(t)
    rz = Matrix(((c, -s, 0.0), (s, c, 0.0), (0.0, 0.0, 1.0)))
    uu, nn = rz @ u, rz @ n
    return Matrix(((uu.x, nn.x, 0.0, hinge.x),
                   (uu.y, nn.y, 0.0, hinge.y),
                   (uu.z, nn.z, 1.0, hinge.z),
                   (0.0, 0.0, 0.0, 1.0)))


def build_window(name, face, a0, a1, z0, z1, open_deg):
    """A real opening through the shell, cased, with glass or open casements.

    Closed windows get a fixed pane behind a centre mullion. The two kitchen
    windows get a pair of casements hinged on the outer jambs and swung out,
    which only reads because the opening is a genuine hole with a dark
    interior behind it.
    """
    w, s, axis = _wall(face)
    # the hole: through the full wall, over-long on the normal so the cut
    # never leaves a coplanar sliver on either face
    cut(bpy.data.objects["house"], name,
        *wall_spec(face, a0, a1, -WALL_T - 0.05, 0.05, z0, z1),
        material="interior")

    # casing: four boxes around the opening, standing proud of the cladding
    multi_box(f"win_{name}_casing", [
        wall_spec(face, a0 - TRIM, a1 + TRIM, 0.0, 0.05, z1, z1 + TRIM),
        wall_spec(face, a0 - TRIM, a1 + TRIM, 0.0, 0.05, z0 - TRIM, z0),
        wall_spec(face, a0 - TRIM, a0, 0.0, 0.05, z0, z1),
        wall_spec(face, a1, a1 + TRIM, 0.0, 0.05, z0, z1),
    ], "trim")
    # sill, projecting far enough to catch light
    multi_box(f"win_{name}_sill", [
        wall_spec(face, a0 - TRIM - 0.04, a1 + TRIM + 0.04,
                  -WALL_T, 0.14, z0 - TRIM - 0.05, z0 - TRIM),
    ], "trim")

    if open_deg <= 0.0:
        # fixed sash: mullion + one pane, set back into the reveal
        mid = (a0 + a1) / 2
        multi_box(f"win_{name}_mullion", [
            wall_spec(face, mid - 0.03, mid + 0.03, -0.16, -0.07, z0, z1),
        ], "trim")
        multi_box(f"win_{name}_glass", [
            wall_spec(face, a0, a1, -0.14, -0.11, z0, z1),
        ], "window")
        return

    # open double casement: two leaves hinged on the outer jambs
    half = (a1 - a0) / 2
    height = z1 - z0
    n = Vector((0.0, s, 0.0)) if axis == "X" else Vector((s, 0.0, 0.0))
    for leaf, (a_hinge, along) in enumerate(((a0, 1.0), (a1, -1.0))):
        u = (Vector((along, 0.0, 0.0)) if axis == "X"
             else Vector((0.0, along, 0.0)))
        hinge = (Vector((a_hinge, w, z0)) if axis == "X"
                 else Vector((w, a_hinge, z0)))
        m = _sash_matrix(hinge, u, n, open_deg)
        # local: x hinge->free edge, y outward (thickness), z up
        rail = 0.07
        stile = multi_box(f"win_{name}_sash{leaf}", [
            (0.0, half, 0.0, SASH_T, 0.0, rail),
            (0.0, half, 0.0, SASH_T, height - rail, height),
            (0.0, rail, 0.0, SASH_T, 0.0, height),
            (half - rail, half, 0.0, SASH_T, 0.0, height),
        ], "trim")
        pane = multi_box(f"win_{name}_sash{leaf}_glass", [
            (rail, half - rail, 0.015, 0.045, rail, height - rail),
        ], "window")
        for ob in (stile, pane):
            ob.matrix_world = m


def far_ground(name, dx0, dx1, dy0, dy1, reach, rise):
    """Ring of ground from the detailed set out to the horizon, rising slightly.

    A FRAME, not a slab: a slab roofs over the roadside ditch (an open trench
    at y -17..-14 dropping to z -0.85) that the cruiser noses into.

    It RISES because the sky itself draws a hard dark band just above the
    horizon — measured: 6 near-black rows (lum 0.001) sitting above the
    geometric horizon in a 648px frame, with the ground continuous right up to
    it. No amount of flat ground reaches above horizontal, so flat ground can
    never cover it. Lifting the far rim puts the land's silhouette ~0.6 deg
    up, which hides the band from every camera in the film including the
    craned wide at z=20, and at that slope reads as distant country.
    """
    inner = [(dx0, dy0, 0.0), (dx1, dy0, 0.0), (dx1, dy1, 0.0), (dx0, dy1, 0.0)]
    outer = [(-reach, -reach, rise), (reach, -reach, rise),
             (reach, reach, rise), (-reach, reach, rise)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(inner + outer, [],
                   [(i, (i + 1) % 4, 4 + (i + 1) % 4, 4 + i) for i in range(4)])
    me.update()
    fix_normals(me)
    me.materials.append(mat("grass"))
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
    fix_normals(me)
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
    # labels live outside the `property` collection so linking shots never
    # imports floating site-plan text
    labels_coll.objects.link(ob)
    return ob


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


def build(out_path, force):
    global collection
    # the .blend is hand-maintained once layout edits begin — don't clobber
    if out_path == OUT and out_path.exists() and not force:
        sys.exit(f"error: {out_path.relative_to(ROOT)} exists and is now "
                 "hand-maintained. Edit it in Blender, or pass --force to "
                 "regenerate from scratch (DESTROYS manual layout edits). Use "
                 "--out=<path> to build a throwaway copy for previews.")
    scene = bpy.context.scene
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)

    collection = bpy.data.collections.new("property")
    scene.collection.children.link(collection)
    global labels_coll
    labels_coll = bpy.data.collections.new("site_labels")
    scene.collection.children.link(labels_coll)

    # --- ground, road, ditch, driveway -------------------------------------
    # the yard and the roadside are separate slabs so the ditch between them
    # is an actual open trench the cruiser can nose into
    # Ground out to the visual horizon. The detailed ground stops at ~45 m, so
    # past that the world HDRI's dark lower hemisphere showed as a black band
    # against the sky.
    #
    # Reaches 4 km, not 900 m. The far edge sits atan(eye / reach) below the
    # true horizon, so at 900 m an eye-level camera still left a 0.08 deg
    # black line all the way across frame — thin, but a hard dark edge against
    # bright sky reads as a seam. 4 km makes it 0.02 deg and it disappears,
    # and still sits inside make_layout's 5000 m camera clip_end.
    #
    # Built as a FRAME around the detailed ground, not a slab across it: a
    # slab roofs over the roadside ditch (an open trench from y -17..-14 down
    # to z -0.85), which is a set piece the cruiser noses into. Because the
    # frame never overlaps the detailed ground there is nothing to z-fight,
    # so its top sits flush at z=0 and the seam has no step either.
    far_ground("ground_far", -45.0, 45.0, -32.0, 45.0, reach=4000.0, rise=42.0)
    box("ground_yard", -45, 45, -14, 45, -0.1, 0.0, "grass")
    box("ground_roadside", -45, 45, -32, -17, -0.1, 0.0, "grass")
    box("road", -45, 45, -23, -17, 0.0, 0.03, "dirt")
    box("ditch_floor", -45, 45, -17, -14, -0.85, -0.80, "dirt")
    box("ditch_wall_e", -45, 45, -17.05, -17.0, -0.85, 0.0, "dirt")
    box("ditch_wall_w", -45, 45, -14.0, -13.95, -0.85, 0.0, "dirt")
    # culvert: the driveway crosses the ditch
    box("culvert", -12.5, -7.5, -17, -14, -0.1, 0.05, "gravel")
    box("driveway", -12.5, -7.5, -14, -3, 0.0, 0.03, "gravel")
    cyl("mailbox_post", -6.5, -15.5, 0.6, 0.07, 1.2, "porch")
    box("mailbox", -6.85, -6.15, -15.75, -15.25, 1.2, 1.55, "bbq")

    # --- house (faces EAST, onto the road) + garage attached on the SOUTH ---
    hx0, hx1, hy0, hy1, hz0, hz1 = HOUSE
    house = box("house", hx0, hx1, hy0, hy1, hz0, hz1, "house")
    # hollow it out, leaving floor and ceiling — windows can then be real
    # openings with something dark behind them instead of decals on a solid
    cut(house, "hollow", hx0 + WALL_T, hx1 - WALL_T, hy0 + WALL_T,
        hy1 - WALL_T, hz0 + WALL_T, hz1 - WALL_T, material="interior")
    gable_roof("house_roof", -7.6, 5.6, -4.6, 5.6, 3.2, 5.2)

    garage = box("garage", -13, -7, -3, 3, 0.0, 2.9, "house")
    gable_roof("garage_roof", -13.5, -6.9, -3.5, 3.5, 2.9, 4.1)
    # PASSTHROUGH: front door faces the road/delivery, rear door opens onto
    # the backyard — the boy hauls the printer in the front and carries the
    # printed junk out the back to the killing field. An actual tunnel, not
    # two door-shaped slabs on a solid block.
    cut(garage, "passthrough", -12.4, -7.6, -3.6, 3.6, 0.1, 2.4,
        material="interior")
    for nm, dy in (("garage_door_front", -3.0), ("garage_door_rear", 3.0)):
        multi_box(nm, [
            (-12.4 - TRIM, -7.6 + TRIM, dy - 0.06, dy + 0.06, 2.4, 2.4 + TRIM),
            (-12.4 - TRIM, -12.4, dy - 0.06, dy + 0.06, 0.1, 2.4),
            (-7.6, -7.6 + TRIM, dy - 0.06, dy + 0.06, 0.1, 2.4),
        ], "trim")

    # The kitchen is the whole REAR (west) half of the house, open all the way
    # across to the back door — one partition across the middle, nothing
    # boxing off a corner. An earlier version walled off just the NW corner,
    # which put a wall directly in front of the sq050_sh040 camera and
    # rendered the entire shot black.
    box("wall_kitchen_east", hx0 + WALL_T, hx1 - WALL_T, 0.0, 0.25, 0.0,
        hz1 - WALL_T, "interior")

    # back door onto the stoop (stoop spans x -4..-1 at y 5..6.2)
    cut(house, "back_door", *wall_spec("+Y", -3.40, -2.20, -WALL_T - 0.05,
                                       0.05, 0.45, 2.55), material="interior")
    multi_box("back_door_casing", [
        wall_spec("+Y", -3.40 - TRIM, -2.20 + TRIM, 0.0, 0.05, 2.55, 2.55 + TRIM),
        wall_spec("+Y", -3.40 - TRIM, -3.40, 0.0, 0.05, 0.45, 2.55),
        wall_spec("+Y", -2.20, -2.20 + TRIM, 0.0, 0.05, 0.45, 2.55),
    ], "trim")

    # front porch + steps (Mom fires from here in the final shot)
    box("porch_deck", -5, 1, -6.4, -4, 0.0, 0.5, "porch")
    for i, px in enumerate((-4.7, 0.7)):
        box(f"porch_post_{i}", px - 0.12, px + 0.12, -6.3, -6.06, 0.5, 3.0, "porch")
    box("porch_roof", -5.2, 1.2, -6.6, -3.9, 3.0, 3.2, "roof")
    box("front_door", -2.4, -1.4, -4.05, -3.95, 0.5, 2.5, "porch")

    # back stoop
    box("back_stoop", -4, -1, 5, 6.2, 0.0, 0.45, "porch")

    # --- windows: the kitchen's two see the backyard AND down the corridor --
    # The two kitchen windows are open double casements; the rest are fixed.
    # Cuts run against the house shell, so this must follow the hollow above.
    for nm, face, a0, a1, sill, head, swing in WINDOWS:
        build_window(nm, face, a0, a1, sill, head, swing)

    # --- backyard set pieces ------------------------------------------------
    # NOTE: the firing squad, the boy, the Santa, the vehicles and the guns are
    # LINKED guide instances staged per-shot in layout/layout.blend (world
    # space, via tools/stage_shots.py or the Redwood Guides add-on) — this
    # script builds only the static set below.

    # old truck on blocks, in the NORTH side corridor near the road end: the
    # ricochet surface that kicks the boy's stray shot to the sheriff's tire,
    # the cover the crawling sheriff ducks behind, and what Mom's rounds
    # hammer when she opens up through the kitchen's north window
    box("truck_body", 11.0, 14.0, -3.1, 1.5, 0.5, 1.8, "truck")
    box("truck_cab", 11.0, 14.0, -3.1, -1.4, 1.8, 2.4, "truck")

    # propane BBQ — pulled in beside the back stoop so one blast catches the
    # whole cast (and the Santa) when the boy's spray rakes it
    box("bbq", -6.7, -4.9, 5.4, 6.8, 0.0, 1.1, "bbq")
    cyl("propane_tank", -4.5, 6.15, 0.45, 0.28, 0.9, "bbq")

    # clothesline — north side, running east-west along the corridor; her
    # floral dress hangs here (ventilated in the firefight) and the kitchen's
    # north window looks straight down it
    for i, cy in enumerate((5.78, 14.78)):
        cyl(f"line_post_{i}", 8.6, cy, 1.1, 0.09, 2.2, "porch")
    box("laundry", 8.5, 8.7, 6.7, 13.9, 1.5, 2.1, "laundry")

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

    # --- labels (site plan only; hidden before perspective renders) ---------
    for text, x, y in (
        ("ROAD - EAST (the escape)", 0, -20), ("DITCH / CRASH", 10, -15.5),
        ("DRIVEWAY", -10, -10), ("GARAGE", -10, 0), ("HOUSE", -1, 0),
        ("PORCH", -2, -7.4), ("KITCHEN WINDOWS", 12.5, 4.5),
        ("SIDE CORRIDOR - NORTH", 12.8, -7), ("BACKYARD - WEST", 2.5, 16),
        ("FIRING SQUAD", 0, 21.6), ("TRUCK", 12.8, 3.2), ("BBQ", -6.0, 8.6),
        ("SANTA", -11.2, 4.6), ("CLOTHESLINE", 11.0, 10.5), ("BOY", 0.6, 8.5),
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
    # SUN ARC = the film's clock. Morning key: low sun rising over the ROAD
    # (−Y) as the delivery lands — light rakes toward the backyard, the
    # road-facing front of the house is lit. The firefight/sprint relight to
    # a dusk key sinking over the backyard (+Y). See docs/treatment/site.md.
    sun.rotation_euler = (math.radians(66), 0.0, math.radians(12))
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

    out_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out_path), relative_remap=True)
    print(f"blockout saved: {out_path}")


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
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    force = "--force" in argv
    out_path = OUT
    previews = None
    for arg in argv:
        if arg.startswith("--out="):
            out_path = Path(arg.split("=", 1)[1])
        elif arg.startswith("--previews="):
            previews = Path(arg.split("=", 1)[1])
    build(out_path, force)
    if previews:
        render_previews(previews)
