#!/usr/bin/env python3
"""Build the animatic scale-guide asset files.

Writes assets/chars/cast.blend and assets/props/props.blend: one collection
per guide (see tools/guides.py), each assembled from primitives into a
recognisable silhouette, marked as a catalogued Asset. Also writes
assets/blender_assets.cats.txt. Guides are authored in real metres, facing -Y,
feet at Z=0, centred on X=0 (see guides.py for the placement rationale).

Run (default → the real asset paths; refuses to clobber without --force):
  "$BLENDER" --background --factory-startup --python-exit-code 1 \
      --python tools/guide_assets.py

Flags (after --):
  --force                 overwrite the real asset files
  --out=<dir>            build throwaway copies into <dir> (cats file too)
  --previews=<dir>       render each guide to <dir>/<name>.png
  --check                build to a temp dir + assert invariants, then exit
  --mark-property        mark the `property` collection in property.blend
  --add=<name>           append ONE new guide to its existing asset file and
                         save in place; never wipes, refuses if it exists
  --build-set=<name>     build ONE mini set into assets/envs/<name>/<name>.blend
                         (refuses to clobber an existing file without --force)
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
    "glass":    (0.55, 0.72, 0.85),
    "lightbar": (0.85, 0.20, 0.20),
    "santa":    (0.72, 0.13, 0.13),
    "white":    (0.90, 0.90, 0.90),
    "ref":      (0.90, 0.50, 0.10),
    "dark":     (0.10, 0.10, 0.12),
    "wood":     (0.50, 0.35, 0.20),
    "bread":    (0.87, 0.78, 0.60),
    "egg":      (0.90, 0.74, 0.25),
    # war flashback
    "helmet":   (0.22, 0.26, 0.19),
    "sandbag":  (0.62, 0.55, 0.38),
    "mud":      (0.34, 0.28, 0.20),
    "jungle":   (0.16, 0.34, 0.15),
    "bamboo":   (0.58, 0.56, 0.30),
    "tin":      (0.42, 0.42, 0.40),
}


GLASS_ALPHA = 0.25


def _mat(color_key):
    name = f"guide_{color_key}"
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        col = PALETTE.get(color_key, (0.5, 0.5, 0.5))
        alpha = GLASS_ALPHA if color_key == "glass" else 1.0
        bsdf = m.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (*col, 1.0)
            bsdf.inputs["Roughness"].default_value = 0.9
            bsdf.inputs["Alpha"].default_value = alpha
        if alpha < 1.0:
            # EEVEE Next alpha-blends via surface_render_method (5.x);
            # older builds only have blend_method — set whichever exists.
            if hasattr(m, "surface_render_method"):
                m.surface_render_method = "BLENDED"
            elif hasattr(m, "blend_method"):
                m.blend_method = "BLEND"
        m.diffuse_color = (*col, alpha)
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
    # Hollow greenhouse instead of a solid cabin block: corner pillars, a
    # thin roof, and alpha-blended glass panes, so blocking inside the car
    # (the sheriff at the wheel) reads through the windows. Nose is -X,
    # matching dt_cab; driver side is -Y.
    box(c, "cr_body", 0, 0, 0.70, 3.60, 1.70, 0.60, "cruiser")
    box(c, "cr_roof", 0, 0, 1.42, 1.70, 1.44, 0.06, "cruiser")
    for px, fx in ((-0.90, "f"), (0.90, "b")):
        for py, fy in ((-0.72, "l"), (0.72, "r")):
            box(c, f"cr_pillar_{fx}{fy}", px, py, 1.20, 0.10, 0.10, 0.40,
                "cruiser")
    box(c, "cr_glass_front", -0.92, 0, 1.20, 0.04, 1.40, 0.36, "glass")
    box(c, "cr_glass_back", 0.92, 0, 1.20, 0.04, 1.40, 0.36, "glass")
    box(c, "cr_glass_left", 0, -0.78, 1.20, 1.70, 0.04, 0.36, "glass")
    box(c, "cr_glass_right", 0, 0.78, 1.20, 1.70, 0.04, 0.36, "glass")
    box(c, "cr_dash", -0.70, 0, 1.06, 0.30, 1.40, 0.16, "dark")
    cyl(c, "cr_steering", -0.50, -0.40, 1.14, 0.09, 0.03, "dark", axis="X")
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


def build_box(c):
    # The printer's shipping carton: the boy drags it in sq010_sh040 and tears
    # it open in sh045. Flaps and a tape stripe give the silhouette a definite
    # top, so it reads as a carton rather than an anonymous crate.
    box(c, "bx_body", 0.00, 0, 0.60, 1.10, 0.90, 1.20, "wood")
    box(c, "bx_tape", 0.00, 0, 1.20, 1.12, 0.10, 0.02, "white")
    box(c, "bx_flap_l", -0.28, 0, 1.21, 0.54, 0.88, 0.02, "wood")
    box(c, "bx_flap_r", 0.28, 0, 1.21, 0.54, 0.88, 0.02, "wood")


def build_egg_salad_sando(c):
    # Hand-prop scale (a 12 cm sandwich): two bread slices around a filling
    # layer that squishes proud of the cut face, which faces -Y so the
    # egg-chunk cross-section reads from the preview camera.
    box(c, "es_bread_bot", 0, 0, 0.0125, 0.12, 0.12, 0.025, "bread")
    box(c, "es_filling", 0, -0.003, 0.035, 0.125, 0.121, 0.02, "egg")
    box(c, "es_bread_top", 0, 0, 0.0575, 0.12, 0.12, 0.025, "bread")
    ball(c, "es_egg_0", -0.030, -0.060, 0.035, 0.012, "white")
    ball(c, "es_egg_1", 0.035, -0.058, 0.036, 0.010, "white")


def build_scale_stick(c):
    cyl(c, "ss_pole", 0, 0, 1.00, 0.03, 2.00, "ref", axis="Z")
    for i in range(1, 5):
        col = "white" if i % 2 else "ref"
        cyl(c, f"ss_tick_{i}", 0, 0, i * 0.5, 0.12, 0.02, col, axis="Z")


def build_gun_cabinet(c):
    """Mom's gun cabinet: glazed door, racked long guns, drawer plinth.

    Authored facing -Y like every guide, so the glass door faces the viewer at
    rotZ 0. Reuses the `glass` material, which already carries the alpha +
    BLENDED setup the cruiser's windows use, so the guns read THROUGH the door
    rather than the door reading as a slab.
    """
    box(c, "gc_base", 0, 0, 0.13, 0.94, 0.46, 0.26, "dark")
    box(c, "gc_body", 0, 0, 1.10, 0.90, 0.42, 1.68, "wood")
    box(c, "gc_back", 0, 0.19, 1.10, 0.86, 0.03, 1.62, "dark")
    for i, x in enumerate((-0.25, 0.0, 0.25)):
        box(c, f"gc_barrel_{i}", x, 0.04, 1.34, 0.06, 0.06, 1.02, "metal")
        box(c, f"gc_stock_{i}", x, 0.04, 0.74, 0.09, 0.09, 0.34, "wood")
    box(c, "gc_rail", 0, 0.04, 1.86, 0.82, 0.06, 0.05, "dark")
    box(c, "gc_glass", 0, -0.20, 1.18, 0.78, 0.03, 1.44, "glass")
    box(c, "gc_handle", 0.31, -0.23, 1.12, 0.04, 0.05, 0.24, "metal")


def build_sheriff_war(c):
    """The sheriff in-country: same body, M1 helmet instead of the stetson.

    Body dimensions are copied from build_sheriff verbatim and deliberately so
    — the flashback cuts against present-day shots of the same man, and if the
    silhouette changed size the match would read as a different character
    rather than the same one, younger. Only the head-dress and a flak vest
    differ, which is what carries the setting change.
    """
    box(c, "sw_leg_l", -0.13, 0, 0.34, 0.18, 0.20, 0.68, "sheriff")
    box(c, "sw_leg_r", 0.13, 0, 0.34, 0.18, 0.20, 0.68, "sheriff")
    ball(c, "sw_belly", 0, -0.06, 0.98, 0.30, "sheriff")
    box(c, "sw_torso", 0, 0, 1.20, 0.46, 0.26, 0.40, "sheriff")
    box(c, "sw_vest", 0, -0.15, 1.18, 0.44, 0.10, 0.44, "helmet")
    box(c, "sw_arm_l", -0.34, 0, 1.10, 0.11, 0.11, 0.50, "sheriff")
    box(c, "sw_arm_r", 0.34, 0, 1.10, 0.11, 0.11, 0.50, "sheriff")
    ball(c, "sw_head", 0, 0, 1.58, 0.16, "skin")
    # dome + shallow brim: reads as a helmet against the stetson's wide flat
    # brim even in silhouette, which is all a 6.8s sepia flashback gets
    ball(c, "sw_helmet", 0, 0, 1.64, 0.19, "helmet")
    cyl(c, "sw_helmet_brim", 0, 0, 1.58, 0.22, 0.03, "helmet", axis="Z")
    box(c, "sw_chinstrap", 0, -0.15, 1.50, 0.24, 0.03, 0.03, "dark")


def build_trench(c):
    """Vietnam trench mini-set for the sq050 war flashback.

    The cut MIRRORS the property's roadside ditch on purpose: ditch_floor is
    y -17..-14 (3 m across) with its floor at z=-0.85, so this is 3 m across
    and 0.85 m deep too. That means the sheriff's blocking reads at the same
    height in the flashback as in the present-day ditch he is lying in, and a
    match cut between them lands.

    Everything above the parapet is what does the transporting: sandbags,
    bamboo stakes, wire and broad jungle leaves instead of a white picket
    fence and oaks. It is 18 m long, enough to fill a wide frame.

    Ground sits at z=0 like every other asset, so instance it AWAY from the
    property (whose ground_yard spans x -45..45, y -32..45) or the two ground
    planes will z-fight.
    """
    HALF_W, DEPTH, L = 1.5, 0.85, 9.0

    # the cut itself: floor, both walls, and a shelf either side so the set
    # reads as trench-in-ground on its own, with no property underneath
    box(c, "tr_floor", 0, 0, -DEPTH - 0.03, L * 2, HALF_W * 2, 0.06, "mud")
    box(c, "tr_wall_n", 0, HALF_W, -DEPTH / 2, L * 2, 0.10, DEPTH, "mud")
    box(c, "tr_wall_s", 0, -HALF_W, -DEPTH / 2, L * 2, 0.10, DEPTH, "mud")
    # generous shelf either side and past both ends: a 3 m apron left every
    # camera placed outside the footprint staring into void
    box(c, "tr_shelf_n", 0, HALF_W + 6.5, -0.05, L * 2.6, 13.0, 0.10, "mud")
    box(c, "tr_shelf_s", 0, -HALF_W - 6.5, -0.05, L * 2.6, 13.0, 0.10, "mud")
    box(c, "tr_shelf_e", L + 3.0, 0, -0.05, 6.0, HALF_W * 2, 0.10, "mud")
    box(c, "tr_shelf_w", -L - 3.0, 0, -0.05, 6.0, HALF_W * 2, 0.10, "mud")
    # end caps, so looking down the trench does not show the world background
    box(c, "tr_end_e", L, 0, -DEPTH / 2, 0.12, HALF_W * 2, DEPTH, "mud")
    box(c, "tr_end_w", -L, 0, -DEPTH / 2, 0.12, HALF_W * 2, DEPTH, "mud")

    for i in range(8):                       # duckboards underfoot
        box(c, f"tr_duck_{i}", -7.9 + i * 2.25, 0, -DEPTH + 0.05,
            1.5, HALF_W * 1.85, 0.07, "wood")

    for i in range(9):                       # timber revetment shoring the walls
        x = -8.2 + i * 2.05
        box(c, f"tr_post_n_{i}", x, HALF_W - 0.09, -DEPTH / 2, 0.14, 0.10, DEPTH, "wood")
        box(c, f"tr_post_s_{i}", x, -HALF_W + 0.09, -DEPTH / 2, 0.14, 0.10, DEPTH, "wood")

    for i in range(10):                      # sandbag parapet, staggered courses
        x = -8.1 + i * 1.8
        box(c, f"tr_bag_n_{i}", x, HALF_W + 0.26, 0.13, 0.78, 0.46, 0.26, "sandbag")
        box(c, f"tr_bag_s_{i}", x, -HALF_W - 0.26, 0.13, 0.78, 0.46, 0.26, "sandbag")
        if i < 9:
            box(c, f"tr_bag_n2_{i}", x + 0.9, HALF_W + 0.20, 0.38,
                0.78, 0.46, 0.26, "sandbag")

    for i in range(6):                       # bamboo stakes + a wire strand
        x = -7.5 + i * 3.0
        cyl(c, f"tr_stake_{i}", x, HALF_W + 1.5, 0.45, 0.045, 0.95, "bamboo", axis="Z")
    cyl(c, "tr_wire_hi", 0, HALF_W + 1.5, 0.82, 0.02, L * 1.9, "metal", axis="X")
    cyl(c, "tr_wire_lo", 0, HALF_W + 1.5, 0.52, 0.02, L * 1.9, "metal", axis="X")

    # ammo crates and a sheet of corrugated tin over one end as overhead cover
    box(c, "tr_crate_a", -5.6, -0.55, -DEPTH + 0.30, 0.80, 0.50, 0.44, "wood")
    box(c, "tr_crate_b", -4.7, -0.60, -DEPTH + 0.22, 0.70, 0.45, 0.36, "wood")
    box(c, "tr_crate_c", 4.9, 0.60, -DEPTH + 0.26, 0.75, 0.48, 0.40, "wood")
    box(c, "tr_tin", 6.9, 0, 0.06, 2.6, HALF_W * 2.1, 0.05, "tin")
    box(c, "tr_tin_prop", 5.7, 1.1, -DEPTH / 2, 0.10, 0.10, DEPTH, "wood")

    # jungle canopy: clustered, tilted fronds on each stem. Single flat discs
    # read as lollipops from every angle, which is a fence line with mushrooms,
    # not a jungle
    for i in range(8):
        x = -7.6 + i * 2.2
        side = 1 if i % 2 else -1
        base_y = side * (HALF_W + 2.1)
        h = 1.05 + 0.3 * (i % 3)
        cyl(c, f"tr_stem_{i}", x, base_y, h / 2, 0.05, h, "bamboo", axis="Z")
        for j in range(3):
            a = math.radians(35 + j * 118 + i * 27)
            leaf = ball(c, f"tr_leaf_{i}_{j}", x + 0.46 * math.cos(a),
                        base_y + 0.46 * math.sin(a), h - 0.06, 0.52, "jungle")
            leaf.scale = (1.55, 0.40, 0.20)
            leaf.rotation_euler = (math.radians(16), math.radians(-24), a)


BUILDERS = {
    "boy": build_boy, "mom": build_mom, "sheriff": build_sheriff,
    "sheriff_war": build_sheriff_war, "trench": build_trench,
    "machine_gun": build_machine_gun, "printer": build_printer,
    "action_figure": build_action_figure, "delivery_truck": build_delivery_truck,
    "cruiser": build_cruiser, "rosco": build_rosco, "big_pistol": build_big_pistol,
    "santa": build_santa, "box": build_box, "scale_stick": build_scale_stick,
    "egg_salad_sando": build_egg_salad_sando,
    "gun_cabinet": build_gun_cabinet,
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


def add_guide(name):
    """Build ONE guide into its existing asset file, leaving the rest alone.

    The default build path wipes the file and regenerates every guide, so it
    refuses to touch a hand-maintained cast.blend/props.blend without --force.
    This is the non-destructive way in: open the file, append the single new
    collection, save. Refuses to overwrite a guide that already exists —
    removing one is a deliberate act, done in Blender.
    """
    spec = guides.guide_by_name(name)
    if spec is None:
        known = ", ".join(sorted(BUILDERS))
        sys.exit(f"error: no guide named {name!r}; known guides: {known}")
    if spec.name not in BUILDERS:
        sys.exit(f"error: {spec.name!r} has no builder (the `property` set is "
                 "marked in place via --mark-property, never built)")

    path = shotlib.project_root() / spec.file
    if not path.exists():
        sys.exit(f"error: {spec.file} does not exist; build it first")
    bpy.ops.wm.open_mainfile(filepath=str(path))
    if bpy.data.collections.get(spec.name) is not None:
        sys.exit(f"error: {spec.name!r} already exists in {spec.file}; remove "
                 "it in Blender first if you mean to rebuild it")

    scene = bpy.context.scene
    coll = bpy.data.collections.new(spec.name)
    scene.collection.children.link(coll)
    BUILDERS[spec.name](coll)
    coll.asset_mark()
    uuid, _path, _simple = guides.CATALOGS[spec.catalog]
    coll.asset_data.catalog_id = uuid
    check_structural([spec])
    check_dimensions([spec])
    bpy.ops.wm.save_as_mainfile(filepath=str(path), relative_remap=True)
    print(f"added guide {spec.name!r} to {spec.file}")


def build_set(name, force=False):
    """Build ONE mini set into its own assets/envs/<name>/<name>.blend.

    Sets get their own single-asset file rather than a slot in props.blend,
    matching the property: one root collection named after the file. They are
    structurally checked but NOT dimension-checked — a trench's lowest point
    is its floor below z=0, which would fail the feet-at-zero rule.
    """
    spec = next((s for s in guides.SETS if s.name == name), None)
    if spec is None:
        known = ", ".join(s.name for s in guides.SETS)
        sys.exit(f"error: no set named {name!r}; known sets: {known}")
    if spec.name == "property":
        sys.exit("error: the property set is hand-built and marked in place "
                 "via --mark-property, never generated")
    if spec.name not in BUILDERS:
        sys.exit(f"error: {spec.name!r} has no builder")

    path = shotlib.project_root() / spec.file
    if path.exists() and not force:
        sys.exit(f"error: {spec.file} exists; pass --force to regenerate "
                 "(DESTROYS manual edits to that file)")
    build_guide_file([spec], path)
    print(f"built set {spec.name!r} -> {spec.file}")


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
    add_name = set_name = None
    for a in argv:
        if a.startswith("--out="):
            out_dir = Path(a.split("=", 1)[1])
        elif a.startswith("--previews="):
            previews = Path(a.split("=", 1)[1])
        elif a.startswith("--add="):
            add_name = a.split("=", 1)[1]
        elif a.startswith("--build-set="):
            set_name = a.split("=", 1)[1]

    if "--check" in argv:
        run_check()
        return
    if add_name is not None:
        add_guide(add_name)
        return
    if set_name is not None:
        build_set(set_name, force=force)
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
