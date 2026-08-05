#!/usr/bin/env python3
"""Build the mountain basin — real eroded terrain, flat poster shading.

Supersedes `tools/skyline.py`'s hand-rolled ridge rings. Those were cheap and
controllable but the silhouettes were invented, and invented ridgelines read as
invented. This gets the geometry from **World Blender Basics 2025**, a
geometry-nodes landscape library (an ASSET LIBRARY, not an add-on — 145 node
groups in one blend), whose hydraulic erosion produces drainage channels,
carved ridgelines and alluvial fans that nothing hand-authored matches.

The shape: a 3 km landscape with a radial mask holding the middle flat, so the
property sits in a basin ringed by mountains that stand over the house on every
side — which is what `refs/styles/` shows and what the ridge rings only
approximated.

But World Blender ships a PHOTOREAL rock/dirt/sediment material, and this film
is a graphic poster. So the geology is kept and the shading is thrown away:
colour comes from a flat palette ramp driven by DISTANCE from the property, not
from rock type. Distance, not height, is what reproduces the refs' near-dark to
far-pale atmospheric layering — and because the property is always the centre,
it works for every camera without being view-dependent.

BAKED TO MESH ON PURPOSE. The result is plain geometry. Leaving the geometry
nodes live would drag all 198 World Blender node groups into `property.blend`,
which is linked into every layout scene, for a backdrop that never changes.

Two post-passes the node graph cannot do cleanly:

  - **Flatten the pad.** Erosion deposits sediment in the basin, so the middle
    comes out a few metres uneven. Everything inside `--pad` is forced to
    exactly z=0 and ramped back to the eroded surface by `--blend`.
  - **Cut the hole.** `property.blend` has its own hand-built ground (x ±45,
    y −32..45) whose top sits at exactly z=0. An overlapping surface is
    coplanar and z-fights, which swallowed the yard, road, fence and treeline
    the first time. Same rect `ground_far` framed.

Requires the asset library at
`~/blender/add-ons/World Blender Basics 2025/landscape nodes main.blend`.

Run headless (writes --out):
    "$BLENDER" --background --factory-startup --python-exit-code 1 \\
        --python tools/basin.py -- [flags]

Flags:
    --out=PATH        where to save (default basin.blend)
    --size=3000       landscape extent, metres
    --resolution=380  grid resolution. Erosion cost scales with this
    --ring=1250       radius where the mountains start rising
    --height=560      noise displacement height, metres
    --noise=800       noise feature size, metres. Larger = broader mountains
    --detail=4        noise detail. Lower = smoother
    --roughness=0.5   noise roughness
    --erode=90        erosion iterations. The whole point; 0 disables
    --pad=70          radius held perfectly flat for the property, metres
    --blend=320       radius by which the eroded surface fully returns
    --hole=x0,x1,y0,y1  rect cut for the hand-built set (default -45,45,-32,45)
    --no-hole         build a full surface (standalone previews only)
    --ramp-near=0.42  palette ramp position at the property
    --ramp-far=0.96   palette ramp position at the far rim (higher = hazier)
    --bands=0         0 = smooth atmospheric gradient; N = N hard poster bands
    --seed=0          noise W offset, to reshuffle the mountains
"""
import math
import os
import sys
from pathlib import Path

import bmesh
import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shotlib

ROOT = shotlib.project_root()
DEFAULT_OUT = ROOT / "assets" / "envs" / "property" / "basin.blend"
WB_LIB = os.path.expanduser(
    "~/blender/add-ons/World Blender Basics 2025/landscape nodes main.blend")

NEEDED_NODES = ["Create landscape", "Noise displacement",
                "Radial gradient mask", "Erosion 2", "Landscape to Object"]

# refs/palette.scss, darkest to palest — same ramp skyline.py used, so the
# backdrop stays on-palette whichever generator produced it.
PALETTE_RAMP = [
    (0x52, 0x05, 0x0a),   # night bordeaux
    (0x83, 0x21, 0x61),   # royal plum
    (0x9b, 0x7e, 0xde),   # soft periwinkle
    (0xbc, 0xd2, 0xee),   # pale sky
]


def srgb_to_linear(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def ramp_color(t):
    t = min(max(t, 0.0), 1.0) * (len(PALETTE_RAMP) - 1)
    i = min(int(t), len(PALETTE_RAMP) - 2)
    f = t - i
    a, b = PALETTE_RAMP[i], PALETTE_RAMP[i + 1]
    return tuple(srgb_to_linear(a[k] + (b[k] - a[k]) * f) for k in range(3))


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / max(e1 - e0, 1e-9), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


# --- geometry --------------------------------------------------------------

def append_world_blender():
    if not os.path.exists(WB_LIB):
        raise SystemExit(f"World Blender library not found: {WB_LIB}")
    with bpy.data.libraries.load(WB_LIB, link=False) as (src, dst):
        missing = [n for n in NEEDED_NODES if n not in src.node_groups]
        if missing:
            raise SystemExit(f"library is missing node groups: {missing}")
        dst.node_groups = list(NEEDED_NODES)


def generate_raw(cfg):
    """Run the World Blender graph and bake it down to a plain mesh."""
    me = bpy.data.meshes.new("_basin_src")
    ob = bpy.data.objects.new("_basin_src", me)
    bpy.context.scene.collection.objects.link(ob)
    ng = bpy.data.node_groups.new("_basin_graph", 'GeometryNodeTree')
    ng.interface.new_socket("Geometry", in_out='OUTPUT',
                            socket_type='NodeSocketGeometry')
    ob.modifiers.new("WB", 'NODES').node_group = ng

    def grp(name, x, y):
        n = ng.nodes.new('GeometryNodeGroup')
        n.node_tree = bpy.data.node_groups[name]
        n.location = (x, y)
        return n

    def sv(node, key, val):
        if key in node.inputs:
            node.inputs[key].default_value = val

    create = grp("Create landscape", -900, 0)
    sv(create, "Size X", cfg["size"]); sv(create, "Size Y", cfg["size"])
    sv(create, "Resolution", cfg["resolution"]); sv(create, "Centered", True)

    # Min=1/Max=0 masks the noise OUT at the centre — verified empirically,
    # the naming is not the intuitive way round.
    mask = grp("Radial gradient mask", -900, -400)
    sv(mask, "Radius", cfg["ring"]); sv(mask, "Min", 1.0); sv(mask, "Max", 0.0)

    noise = grp("Noise displacement", -600, 0)
    sv(noise, "Size", cfg["noise"]); sv(noise, "Height", cfg["height"])
    sv(noise, "Detail", cfg["detail"]); sv(noise, "Roughness", cfg["roughness"])
    sv(noise, "W", float(cfg["seed"]))

    tail = noise
    if cfg["erode"] > 0:
        ero = grp("Erosion 2", -300, 0)
        sv(ero, "Erode iterations", cfg["erode"])
        sv(ero, "Activate in Viewport", True)
        ng.links.new(noise.outputs["Landscape"], ero.inputs["Landscape"])
        tail = ero

    to_obj = grp("Landscape to Object", 0, 0)
    sv(to_obj, "Shade Smooth", True)
    out = ng.nodes.new('NodeGroupOutput'); out.location = (300, 0)

    L = ng.links.new
    L(create.outputs["Landscape"], noise.inputs["Landscape"])
    L(mask.outputs["Mask"], noise.inputs["Mask"])
    L(tail.outputs["Landscape"], to_obj.inputs["Landscape"])
    L(to_obj.outputs["Geometry"], out.inputs[0])

    dg = bpy.context.evaluated_depsgraph_get()
    baked = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.meshes.remove(me)
    bpy.data.node_groups.remove(ng)
    return baked


def reshape(me, cfg):
    """Sit the pad at z=0, flatten it, and report the basin's real profile."""
    n = len(me.vertices)
    co = np.empty(n * 3, dtype=np.float64)
    me.vertices.foreach_get("co", co)
    co = co.reshape(n, 3)
    x, y, z = co[:, 0], co[:, 1], co[:, 2]
    r = np.hypot(x, y)

    inner = z[r < cfg["pad"]]
    base = float(np.median(inner)) if len(inner) else 0.0
    z -= base

    # Erosion silts up the basin, so the middle is never flat enough to stage
    # on. Force it, then ease back onto the eroded surface.
    z *= smoothstep(cfg["pad"], cfg["blend"], r)

    co[:, 2] = z
    me.vertices.foreach_set("co", co.ravel())
    me.update()
    return base, r, z


def cut_hole(me, hole):
    """Remove faces inside the hand-built set's footprint. An overlapping
    surface is coplanar with property.blend's ground and z-fights."""
    x0, x1, y0, y1 = hole
    bm = bmesh.new()
    bm.from_mesh(me)
    doomed = [f for f in bm.faces
              if all(x0 <= v.co.x <= x1 and y0 <= v.co.y <= y1 for v in f.verts)]
    bmesh.ops.delete(bm, geom=doomed, context='FACES')
    loose = [v for v in bm.verts if not v.link_faces]
    if loose:
        bmesh.ops.delete(bm, geom=loose, context='VERTS')
    bm.to_mesh(me)
    bm.free()
    return len(doomed)


def basin_material(cfg):
    """Flat poster shading, banded by DISTANCE from the property.

    World Blender's own material is photoreal rock/dirt/sediment, which is the
    opposite of this film. Distance (not height) is what gives the refs their
    near-dark to far-pale atmospheric layering, and since the property is
    always at the centre it needs no view dependency.
    """
    mat = bpy.data.materials.new("basin_poster")
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    bsdf.inputs["Roughness"].default_value = 1.0
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.03

    geo = nt.nodes.new("ShaderNodeNewGeometry"); geo.location = (-1000, 0)
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); sep.location = (-820, 0)
    comb = nt.nodes.new("ShaderNodeCombineXYZ"); comb.location = (-660, 0)
    length = nt.nodes.new("ShaderNodeVectorMath"); length.location = (-500, 0)
    length.operation = 'LENGTH'
    rng = nt.nodes.new("ShaderNodeMapRange"); rng.location = (-330, 0)
    rng.inputs["From Min"].default_value = 0.0
    rng.inputs["From Max"].default_value = cfg["size"] * 0.5
    ramp = nt.nodes.new("ShaderNodeValToRGB"); ramp.location = (-150, 120)

    # Height decides ground-vs-mountain; distance only hazes the mountains.
    # Distance alone painted the desert floor plum right up to the fence.
    hrng = nt.nodes.new("ShaderNodeMapRange"); hrng.location = (-330, -260)
    hrng.inputs["From Min"].default_value = 0.0
    hrng.inputs["From Max"].default_value = cfg["ground_to"]
    mix = nt.nodes.new("ShaderNodeMix"); mix.location = (100, 0)
    mix.data_type = 'RGBA'
    mix.inputs[6].default_value = tuple(srgb_to_linear(c) for c in cfg["ground"]) + (1.0,)

    nt.links.new(geo.outputs["Position"], sep.inputs["Vector"])
    nt.links.new(sep.outputs["X"], comb.inputs["X"])
    nt.links.new(sep.outputs["Y"], comb.inputs["Y"])
    nt.links.new(comb.outputs["Vector"], length.inputs[0])
    nt.links.new(length.outputs["Value"], rng.inputs["Value"])
    nt.links.new(rng.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(sep.outputs["Z"], hrng.inputs["Value"])
    nt.links.new(hrng.outputs["Result"], mix.inputs["Factor"])
    nt.links.new(ramp.outputs["Color"], mix.inputs[7])
    nt.links.new(mix.outputs[2], bsdf.inputs["Base Color"])

    el = ramp.color_ramp.elements
    near, far = cfg["ramp_near"], cfg["ramp_far"]
    if cfg["bands"] > 0:
        ramp.color_ramp.interpolation = 'CONSTANT'
        stops = cfg["bands"]
    else:
        ramp.color_ramp.interpolation = 'LINEAR'
        stops = 5
    while len(el) > 1:
        el.remove(el[-1])
    for i in range(stops):
        f = i / max(stops - 1, 1)
        e = el[0] if i == 0 else el.new(f)
        e.position = f
        e.color = ramp_color(near + (far - near) * f) + (1.0,)
    return mat


# --- entry point -----------------------------------------------------------

def parse_args(argv):
    cfg = {
        # Ring pushed out to 1600 over a 4000 m field: at 1250/3000 the peaks
        # subtended 15.7 deg, past the 15 deg half-FOV of the 45 mm intro
        # camera, so they filled frame edge to edge with no sky above them.
        "out": DEFAULT_OUT, "size": 4000.0, "resolution": 400, "ring": 1600.0,
        # 520 at this radius fell to ~11 deg — under the house's 11.3. Aim for
        # ~13.5: clears the house, still leaves sky above at 45 mm.
        "height": 660.0, "noise": 850.0, "detail": 4.0, "roughness": 0.5,
        "erode": 90, "pad": 70.0, "blend": 320.0, "seed": 0,
        "hole": (-45.0, 45.0, -32.0, 45.0),
        "ramp_near": 0.42, "ramp_far": 0.96, "bands": 0,
        "ground": (0xC2, 0xA4, 0x8A),   # desert floor, matches skyline_ground
        "ground_to": 55.0,              # metres over which ground -> mountain
    }
    floats = {"size", "ring", "height", "noise", "detail", "roughness",
              "pad", "blend", "ramp_near", "ramp_far", "ground_to"}
    ints = {"resolution", "erode", "bands", "seed"}
    for arg in argv:
        if arg == "--no-hole":
            cfg["hole"] = None
            continue
        if not arg.startswith("--") or "=" not in arg:
            raise SystemExit(f"unrecognised argument: {arg}\n{__doc__}")
        key, _, val = arg[2:].partition("=")
        key = key.replace("-", "_")
        if key == "out":
            cfg[key] = Path(val).expanduser().resolve()
        elif key == "hole":
            cfg[key] = tuple(float(v) for v in val.split(","))
        elif key in ints:
            cfg[key] = int(val)
        elif key in floats:
            cfg[key] = float(val)
        else:
            raise SystemExit(f"unknown flag: --{key}\n{__doc__}")
    return cfg


def build(cfg):
    # factory-startup ships a Cube/Camera/Light and this file is an asset, so
    # clear them — but ONLY in a fresh unsaved session. Doing this
    # unconditionally deletes the property and its cameras when the tool is run
    # inside property.blend, which is exactly what happened once.
    if not bpy.data.filepath:
        for ob in list(bpy.data.objects):
            bpy.data.objects.remove(ob, do_unlink=True)
    before = {ng.name for ng in bpy.data.node_groups}
    append_world_blender()
    print(f"basin: {cfg['size']:.0f} m @ res {cfg['resolution']}, "
          f"ring {cfg['ring']:.0f} m, erosion {cfg['erode']} iterations")
    me = generate_raw(cfg)
    me.name = "basin"
    base, r, z = reshape(me, cfg)
    print(f"  baked {len(me.vertices):,} verts; pad sat at {base:+.1f} m -> z=0")

    if cfg["hole"]:
        n = cut_hole(me, cfg["hole"])
        hx0, hx1, hy0, hy1 = cfg["hole"]
        print(f"  cut {n} faces for the set ({hx0:g}..{hx1:g}, {hy0:g}..{hy1:g})")

    # REPLACE, don't append: `Landscape to Object` bakes its own photoreal
    # "Default land" material into slot 0, and every face is assigned to it —
    # appending just adds an unused second slot and nothing changes.
    me.materials.clear()
    me.materials.append(basin_material(cfg))
    me.polygons.foreach_set("material_index", [0] * len(me.polygons))
    ob = bpy.data.objects.new("basin", me)
    coll = bpy.data.collections.get("basin") or bpy.data.collections.new("basin")
    if coll.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(coll)
    coll.objects.link(ob)

    report(me, cfg)
    strip_world_blender(before)
    return coll


def strip_world_blender(before):
    """Remove exactly the node groups this run appended — nothing else.

    Two traps. They are marked as ASSETS, which gives them a fake user, so a
    plain `orphans_purge` leaves all 48 (11 MB) in a file that is linked into
    every layout scene. And a blanket recursive purge is not the answer either:
    run inside property.blend it happily collects that file's own data too.
    So: track what appeared, unmark it, and delete only those, leaf-first.
    """
    mine = [ng for ng in bpy.data.node_groups if ng.name not in before]
    for ng in mine:
        if ng.asset_data:
            ng.asset_clear()
        ng.use_fake_user = False
    removed = 0
    while True:
        gone = False
        for ng in list(mine):
            if ng.users == 0:
                mine.remove(ng)
                bpy.data.node_groups.remove(ng)
                removed += 1
                gone = True
        if not gone:
            break
    print(f"  removed {removed} World Blender node groups"
          + (f" ({len(mine)} still referenced)" if mine else ""))


def report(me, cfg):
    n = len(me.vertices)
    co = np.empty(n * 3, dtype=np.float64)
    me.vertices.foreach_get("co", co)
    co = co.reshape(n, 3)
    x, y, z = co[:, 0], co[:, 1], co[:, 2]
    r = np.hypot(x, y)

    pad = z[r < 60.0]
    if len(pad):
        print(f"  property pad (r<60 m): {pad.min():+.3f}..{pad.max():+.3f} m")
    print(f"  peak {z.max():.0f} m")
    print("\n  does the ridge stand over the house (11.3 deg) on all sides?")
    EYE = 1.6
    for tag, (dx, dy) in [("W (+Y)", (0, 1)), ("E (-Y)", (0, -1)),
                          ("N (+X)", (1, 0)), ("S (-X)", (-1, 0))]:
        d = x * dx + y * dy
        off = np.abs(y if dx else x)
        sel = (d > 150.0) & (off < 150.0)
        if not sel.any():
            continue
        ang = np.degrees(np.arctan2(z[sel] - EYE, d[sel])).max()
        print(f"    {tag}: {ang:5.1f} deg   "
              f"{'clears' if ang > 11.3 else 'TOO LOW'}")


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    cfg = parse_args(argv)
    build(cfg)
    if bpy.app.background and cfg["out"]:
        cfg["out"].parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(cfg["out"]))
        print(f"\n  wrote {cfg['out']}")
    else:
        print("\n  built into the current scene; nothing saved.")


if __name__ == "__main__":
    main()
