#!/usr/bin/env python3
"""Damage squibs: a geometry-nodes bullet-impact system.

Builds `assets/fx/squibs.blend`, holding one node group (`squib_burst`) and
seven materials, then applies it to objects in layout scenes as a modifier.

WHAT IT DOES
------------
Each impact point sprays debris along the surface normal, then the spray dies
and RESOLVES TO A HOLE that stays for the rest of the shot. Timing is driven
by the Scene Time node, so nothing needs keyframing — set Start Frame on the
modifier and it plays.

Two emission modes on the same group:
  Targeted = OFF  impacts scatter randomly over the whole model
  Targeted = ON   one impact at `Target`, pointing along `Direction`

Six surfaces, chosen by index on the modifier:
  0 dirt   1 grass   2 plastic   3 wood   4 stucco   5 metal

Run (Blender must be CLOSED for both modes — they write .blend files):

  "$BLENDER" --background --factory-startup --python-exit-code 1 \
      --python tools/squib.py -- --install [--force]

  "$BLENDER" --background --python-exit-code 1 \
      --python tools/squib.py -- --apply=sq060_sh010:some_object \
      [--surface=stucco] [--start=3100] [--count=12] [--targeted] \
      [--target=1,2,0.5]   # world space; converted to local
      [--dry-run]
"""
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shotlib

LIB = "assets/fx/squibs.blend"
GROUP = "squib_burst"

# index -> (material name, base colour, roughness)
SURFACES = [
    ("squib_dirt",    (0.36, 0.26, 0.16), 0.95),
    ("squib_grass",   (0.24, 0.36, 0.13), 0.90),
    ("squib_plastic", (0.80, 0.75, 0.22), 0.40),
    ("squib_wood",    (0.50, 0.35, 0.20), 0.85),
    ("squib_stucco",  (0.80, 0.77, 0.70), 0.95),
    ("squib_metal",   (0.55, 0.57, 0.60), 0.25),
]
SURFACE_NAMES = [s[0].replace("squib_", "") for s in SURFACES]
HOLE_MAT = "squib_hole"


def _mat(name, col, rough):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        b = m.node_tree.nodes.get("Principled BSDF")
        if b:
            b.inputs["Base Color"].default_value = (*col, 1.0)
            b.inputs["Roughness"].default_value = rough
        m.diffuse_color = (*col, 1.0)
    return m


def build_group():
    """Construct the squib_burst geometry node group."""
    if bpy.data.node_groups.get(GROUP):
        bpy.data.node_groups.remove(bpy.data.node_groups[GROUP])
    t = bpy.data.node_groups.new(GROUP, "GeometryNodeTree")
    itf = t.interface

    def sock(name, stype, default=None, mn=None, mx=None, in_out="INPUT"):
        s = itf.new_socket(name, in_out=in_out, socket_type=stype)
        if default is not None:
            s.default_value = default
        if mn is not None:
            s.min_value = mn
        if mx is not None:
            s.max_value = mx
        return s

    sock("Geometry", "NodeSocketGeometry", in_out="OUTPUT")
    sock("Geometry", "NodeSocketGeometry")
    sock("Surface", "NodeSocketInt", 0, 0, len(SURFACES) - 1)
    sock("Targeted", "NodeSocketBool", False)
    sock("Target", "NodeSocketVector", (0.0, 0.0, 0.0))
    sock("Direction", "NodeSocketVector", (0.0, 0.0, 1.0))
    sock("Count", "NodeSocketFloat", 8.0, 0.0, 500.0)
    sock("Start Frame", "NodeSocketFloat", 1.0)
    sock("Stagger", "NodeSocketFloat", 10.0, 0.0, 500.0)
    sock("Life", "NodeSocketFloat", 12.0, 1.0, 500.0)
    sock("Debris Count", "NodeSocketInt", 6, 1, 64)
    sock("Debris Scale", "NodeSocketFloat", 0.06, 0.0, 10.0)
    sock("Spread", "NodeSocketFloat", 0.5, 0.0, 50.0)
    sock("Hole Size", "NodeSocketFloat", 0.09, 0.0, 10.0)
    sock("Seed", "NodeSocketInt", 0)

    n = t.nodes
    gin = n.new("NodeGroupInput")
    gout = n.new("NodeGroupOutput")
    gin.location = (-1400, 0)
    gout.location = (1400, 0)
    L = t.links.new

    def I(name):
        return gin.outputs[name]

    # --- impact points -------------------------------------------------
    dpof = n.new("GeometryNodeDistributePointsOnFaces")
    dpof.location = (-1100, 250)
    L(I("Geometry"), dpof.inputs["Mesh"])
    L(I("Count"), dpof.inputs["Density"])
    L(I("Seed"), dpof.inputs["Seed"])

    pts = n.new("GeometryNodePoints")
    pts.location = (-1100, -100)
    pts.inputs["Count"].default_value = 1
    L(I("Target"), pts.inputs["Position"])

    geo_sw = n.new("GeometryNodeSwitch")
    geo_sw.input_type = "GEOMETRY"
    geo_sw.location = (-880, 80)
    L(I("Targeted"), geo_sw.inputs["Switch"])
    L(dpof.outputs["Points"], geo_sw.inputs["False"])
    L(pts.outputs["Points"], geo_sw.inputs["True"])

    # one normal for both modes, so only one alignment is needed downstream
    nrm_sw = n.new("GeometryNodeSwitch")
    nrm_sw.input_type = "VECTOR"
    nrm_sw.location = (-880, -220)
    L(I("Targeted"), nrm_sw.inputs["Switch"])
    L(dpof.outputs["Normal"], nrm_sw.inputs["False"])
    L(I("Direction"), nrm_sw.inputs["True"])

    align = n.new("FunctionNodeAlignRotationToVector") \
        if "FunctionNodeAlignRotationToVector" in dir(bpy.types) \
        else n.new("FunctionNodeAlignEulerToVector")
    align.location = (-660, -220)
    align.axis = "Z"
    L(nrm_sw.outputs[0], align.inputs["Vector"])

    # --- per-impact clock ----------------------------------------------
    # Scene Time, not keyframes: the modifier plays wherever it is dropped.
    stime = n.new("GeometryNodeInputSceneTime")
    stime.location = (-1100, -520)
    rnd = n.new("FunctionNodeRandomValue")
    rnd.data_type = "FLOAT"
    rnd.location = (-1100, -700)
    rnd.inputs[2].default_value = 0.0     # Min
    rnd.inputs[3].default_value = 1.0     # Max
    L(I("Seed"), rnd.inputs["Seed"])

    stag = n.new("ShaderNodeMath")
    stag.operation = "MULTIPLY"
    stag.location = (-880, -700)
    L(rnd.outputs[1], stag.inputs[0])
    L(I("Stagger"), stag.inputs[1])

    t0 = n.new("ShaderNodeMath")
    t0.operation = "ADD"
    t0.location = (-700, -600)
    L(I("Start Frame"), t0.inputs[0])
    L(stag.outputs[0], t0.inputs[1])

    local = n.new("ShaderNodeMath")
    local.operation = "SUBTRACT"
    local.location = (-520, -560)
    L(stime.outputs["Frame"], local.inputs[0])
    L(t0.outputs[0], local.inputs[1])

    tnorm = n.new("ShaderNodeMapRange")
    tnorm.clamp = True
    tnorm.location = (-340, -560)
    L(local.outputs[0], tnorm.inputs["Value"])
    tnorm.inputs["From Min"].default_value = 0.0
    L(I("Life"), tnorm.inputs["From Max"])
    tnorm.inputs["To Min"].default_value = 0.0
    tnorm.inputs["To Max"].default_value = 1.0

    # --- debris ----------------------------------------------------------
    chunk = n.new("GeometryNodeMeshIcoSphere")
    chunk.location = (-340, 420)
    chunk.inputs["Radius"].default_value = 1.0
    chunk.inputs["Subdivisions"].default_value = 1

    # One chunk per impact is nothing to look at -- a single targeted hit
    # threw exactly one pebble. Duplicate each impact point first so every
    # round throws a handful. Only the DEBRIS branch is duplicated; the hole
    # branch still takes geo_sw directly, so one impact still means one hole.
    dup = n.new("GeometryNodeDuplicateElements")
    dup.location = (-300, 300)
    dup.domain = "POINT"
    L(geo_sw.outputs[0], dup.inputs["Geometry"])
    L(I("Debris Count"), dup.inputs["Amount"])

    debris = n.new("GeometryNodeInstanceOnPoints")
    debris.location = (-80, 300)
    L(dup.outputs["Geometry"], debris.inputs["Points"])
    L(chunk.outputs["Mesh"], debris.inputs["Instance"])
    L(align.outputs[0], debris.inputs["Rotation"])

    # pop fast, decay out: min(t*8,1) * (1-t). Zero at t=0 AND t=1, so debris
    # is invisible before the impact and after it without a Selection test.
    ramp = n.new("ShaderNodeMath")
    ramp.operation = "MULTIPLY"
    ramp.location = (-340, -380)
    L(tnorm.outputs[0], ramp.inputs[0])
    ramp.inputs[1].default_value = 8.0
    ramp_min = n.new("ShaderNodeMath")
    ramp_min.operation = "MINIMUM"
    ramp_min.location = (-180, -380)
    L(ramp.outputs[0], ramp_min.inputs[0])
    ramp_min.inputs[1].default_value = 1.0
    decay = n.new("ShaderNodeMath")
    decay.operation = "SUBTRACT"
    decay.location = (-180, -520)
    decay.inputs[0].default_value = 1.0
    L(tnorm.outputs[0], decay.inputs[1])
    envelope = n.new("ShaderNodeMath")
    envelope.operation = "MULTIPLY"
    envelope.location = (0, -440)
    L(ramp_min.outputs[0], envelope.inputs[0])
    L(decay.outputs[0], envelope.inputs[1])
    dscale = n.new("ShaderNodeMath")
    dscale.operation = "MULTIPLY"
    dscale.location = (160, -440)
    L(envelope.outputs[0], dscale.inputs[0])
    L(I("Debris Scale"), dscale.inputs[1])

    sc_inst = n.new("GeometryNodeScaleInstances")
    sc_inst.location = (160, 300)
    L(debris.outputs["Instances"], sc_inst.inputs["Instances"])
    L(dscale.outputs[0], sc_inst.inputs["Scale"])

    # fly outward: mostly along the normal, with a lateral scatter
    jitter = n.new("FunctionNodeRandomValue")
    jitter.data_type = "FLOAT_VECTOR"
    jitter.location = (-880, -900)
    jitter.inputs[0].default_value = (-1.0, -1.0, -0.2)
    jitter.inputs[1].default_value = (1.0, 1.0, 1.0)
    L(I("Seed"), jitter.inputs["Seed"])
    # explicit per-instance ID, so the duplicates of one impact fly different
    # ways instead of moving as a clump
    jidx = n.new("GeometryNodeInputIndex")
    jidx.location = (-1060, -1000)
    L(jidx.outputs[0], jitter.inputs["ID"])
    mixdir = n.new("ShaderNodeVectorMath")
    mixdir.operation = "ADD"
    mixdir.location = (-660, -900)
    L(nrm_sw.outputs[0], mixdir.inputs[0])
    L(jitter.outputs[0], mixdir.inputs[1])
    travel = n.new("ShaderNodeMath")
    travel.operation = "MULTIPLY"
    travel.location = (-340, -760)
    L(tnorm.outputs[0], travel.inputs[0])
    L(I("Spread"), travel.inputs[1])
    disp = n.new("ShaderNodeVectorMath")
    disp.operation = "SCALE"
    disp.location = (-160, -860)
    L(mixdir.outputs[0], disp.inputs[0])
    L(travel.outputs[0], disp.inputs["Scale"])

    tr_inst = n.new("GeometryNodeTranslateInstances")
    tr_inst.location = (380, 300)
    L(sc_inst.outputs["Instances"], tr_inst.inputs["Instances"])
    L(disp.outputs[0], tr_inst.inputs["Translation"])
    # Local Space would multiply the throw by the instance's own scale, and
    # the instance is shrinking on the death envelope -- so debris flies out
    # and then sucks straight back into the hole. Throw in object space.
    tr_inst.inputs["Local Space"].default_value = False

    # --- surface material, picked by index --------------------------------
    isw = n.new("GeometryNodeIndexSwitch")
    isw.data_type = "MATERIAL"
    isw.location = (380, 60)
    while len(isw.index_switch_items) < len(SURFACES):
        isw.index_switch_items.new()
    L(I("Surface"), isw.inputs["Index"])
    for i, (name, col, rough) in enumerate(SURFACES):
        isw.inputs[i + 1].default_value = _mat(name, col, rough)

    setmat = n.new("GeometryNodeSetMaterial")
    setmat.location = (620, 300)
    L(tr_inst.outputs["Instances"], setmat.inputs["Geometry"])
    L(isw.outputs[0], setmat.inputs["Material"])

    # --- the hole it resolves to -----------------------------------------
    disc = n.new("GeometryNodeMeshCircle")
    disc.fill_type = "NGON"
    disc.location = (-340, 700)
    disc.inputs["Vertices"].default_value = 12
    disc.inputs["Radius"].default_value = 1.0

    holes = n.new("GeometryNodeInstanceOnPoints")
    holes.location = (-80, 700)
    L(geo_sw.outputs[0], holes.inputs["Points"])
    L(disc.outputs["Mesh"], holes.inputs["Instance"])
    L(align.outputs[0], holes.inputs["Rotation"])

    # opens over the first quarter of the burst, then holds for good
    hgrow = n.new("ShaderNodeMapRange")
    hgrow.clamp = True
    hgrow.location = (-180, -180)
    L(tnorm.outputs[0], hgrow.inputs["Value"])
    hgrow.inputs["From Min"].default_value = 0.0
    hgrow.inputs["From Max"].default_value = 0.25
    hgrow.inputs["To Min"].default_value = 0.0
    hgrow.inputs["To Max"].default_value = 1.0
    hscale = n.new("ShaderNodeMath")
    hscale.operation = "MULTIPLY"
    hscale.location = (0, -180)
    L(hgrow.outputs[0], hscale.inputs[0])
    L(I("Hole Size"), hscale.inputs[1])

    hsc_inst = n.new("GeometryNodeScaleInstances")
    hsc_inst.location = (160, 700)
    L(holes.outputs["Instances"], hsc_inst.inputs["Instances"])
    L(hscale.outputs[0], hsc_inst.inputs["Scale"])

    # lift off the surface so the decal never z-fights the wall it is on
    lift = n.new("ShaderNodeVectorMath")
    lift.operation = "SCALE"
    lift.location = (160, 880)
    L(nrm_sw.outputs[0], lift.inputs[0])
    lift.inputs["Scale"].default_value = 0.004
    htr = n.new("GeometryNodeTranslateInstances")
    htr.location = (380, 700)
    L(hsc_inst.outputs["Instances"], htr.inputs["Instances"])
    L(lift.outputs[0], htr.inputs["Translation"])
    # same reason, and here it matters for z-fighting: in local space the 4mm
    # lift off the surface shrinks to 0.4mm at hole scale 0.09
    htr.inputs["Local Space"].default_value = False

    hmat = n.new("GeometryNodeSetMaterial")
    hmat.location = (620, 700)
    L(htr.outputs["Instances"], hmat.inputs["Geometry"])
    hmat.inputs["Material"].default_value = _mat(HOLE_MAT, (0.03, 0.03, 0.04), 1.0)

    join = n.new("GeometryNodeJoinGeometry")
    join.location = (1000, 200)
    L(I("Geometry"), join.inputs["Geometry"])
    L(hmat.outputs["Geometry"], join.inputs["Geometry"])
    L(setmat.outputs["Geometry"], join.inputs["Geometry"])
    L(join.outputs["Geometry"], gout.inputs["Geometry"])
    return t


def build_impacts_group():
    """`squib_impacts`: same burst, but driven by BAKED hit points.

    squib_burst decides WHERE impacts land (scatter or one target) and WHEN
    from a single Start Frame. This one is handed a points object whose every
    vertex is a real raycast hit, carrying two named attributes:

        hit_frame   float   the frame that impact lands
        hit_normal  vector  the surface normal at the hit

    So one modifier covers a whole burst of shots landing at different times
    on the same object, which is what makes the gun -> ray -> squib chain
    automatic.
    """
    name = "squib_impacts"
    if bpy.data.node_groups.get(name):
        bpy.data.node_groups.remove(bpy.data.node_groups[name])
    t = bpy.data.node_groups.new(name, "GeometryNodeTree")
    itf = t.interface

    def sock(nm, st, default=None, in_out="INPUT"):
        s = itf.new_socket(nm, in_out=in_out, socket_type=st)
        if default is not None:
            s.default_value = default
        return s

    sock("Geometry", "NodeSocketGeometry", in_out="OUTPUT")
    sock("Geometry", "NodeSocketGeometry")
    sock("Surface", "NodeSocketInt", 0)
    sock("Life", "NodeSocketFloat", 12.0)
    sock("Debris Count", "NodeSocketInt", 7)
    sock("Debris Scale", "NodeSocketFloat", 0.06)
    sock("Spread", "NodeSocketFloat", 0.5)
    sock("Hole Size", "NodeSocketFloat", 0.09)
    sock("Seed", "NodeSocketInt", 0)

    n = t.nodes
    gin = n.new("NodeGroupInput"); gin.location = (-1200, 0)
    gout = n.new("NodeGroupOutput"); gout.location = (1200, 0)
    L = t.links.new

    def I(nm):
        return gin.outputs[nm]

    hf = n.new("GeometryNodeInputNamedAttribute")
    hf.data_type = "FLOAT"; hf.location = (-1000, -400)
    hf.inputs["Name"].default_value = "hit_frame"
    hn = n.new("GeometryNodeInputNamedAttribute")
    hn.data_type = "FLOAT_VECTOR"; hn.location = (-1000, -650)
    hn.inputs["Name"].default_value = "hit_normal"

    align = n.new("FunctionNodeAlignRotationToVector")
    align.location = (-800, -650); align.axis = "Z"
    L(hn.outputs[0], align.inputs["Vector"])

    stime = n.new("GeometryNodeInputSceneTime"); stime.location = (-1000, -200)
    local = n.new("ShaderNodeMath"); local.operation = "SUBTRACT"
    local.location = (-800, -300)
    L(stime.outputs["Frame"], local.inputs[0])
    L(hf.outputs[0], local.inputs[1])

    tn = n.new("ShaderNodeMapRange"); tn.clamp = True; tn.location = (-620, -300)
    L(local.outputs[0], tn.inputs["Value"])
    tn.inputs["From Min"].default_value = 0.0
    L(I("Life"), tn.inputs["From Max"])
    tn.inputs["To Min"].default_value = 0.0
    tn.inputs["To Max"].default_value = 1.0

    # Each hit is ONE point, so instancing straight off it gives one chunk of
    # debris per bullet -- invisible. Duplicate the hit first so a single
    # impact throws a handful of fragments. Named attributes ride along
    # through the duplicate, so every fragment keeps its hit's frame/normal.
    dup = n.new("GeometryNodeDuplicateElements"); dup.location = (-800, 300)
    dup.domain = "POINT"
    L(I("Geometry"), dup.inputs["Geometry"])
    L(I("Debris Count"), dup.inputs["Amount"])

    chunk = n.new("GeometryNodeMeshIcoSphere"); chunk.location = (-620, 400)
    chunk.inputs["Radius"].default_value = 1.0
    chunk.inputs["Subdivisions"].default_value = 1
    debris = n.new("GeometryNodeInstanceOnPoints"); debris.location = (-360, 300)
    L(dup.outputs["Geometry"], debris.inputs["Points"])
    L(chunk.outputs["Mesh"], debris.inputs["Instance"])
    L(align.outputs[0], debris.inputs["Rotation"])

    ramp = n.new("ShaderNodeMath"); ramp.operation = "MULTIPLY"; ramp.location = (-440, -140)
    L(tn.outputs[0], ramp.inputs[0]); ramp.inputs[1].default_value = 8.0
    rmin = n.new("ShaderNodeMath"); rmin.operation = "MINIMUM"; rmin.location = (-280, -140)
    L(ramp.outputs[0], rmin.inputs[0]); rmin.inputs[1].default_value = 1.0
    dec = n.new("ShaderNodeMath"); dec.operation = "SUBTRACT"; dec.location = (-280, -280)
    dec.inputs[0].default_value = 1.0
    L(tn.outputs[0], dec.inputs[1])
    env = n.new("ShaderNodeMath"); env.operation = "MULTIPLY"; env.location = (-120, -200)
    L(rmin.outputs[0], env.inputs[0]); L(dec.outputs[0], env.inputs[1])
    dsc = n.new("ShaderNodeMath"); dsc.operation = "MULTIPLY"; dsc.location = (40, -200)
    L(env.outputs[0], dsc.inputs[0]); L(I("Debris Scale"), dsc.inputs[1])

    sci = n.new("GeometryNodeScaleInstances"); sci.location = (40, 300)
    L(debris.outputs["Instances"], sci.inputs["Instances"])
    L(dsc.outputs[0], sci.inputs["Scale"])

    jit = n.new("FunctionNodeRandomValue"); jit.data_type = "FLOAT_VECTOR"
    jit.location = (-800, -900)
    jit.inputs[0].default_value = (-1.0, -1.0, -0.2)
    jit.inputs[1].default_value = (1.0, 1.0, 1.0)
    L(I("Seed"), jit.inputs["Seed"])
    # explicit per-instance ID: fragments of one hit must fly different ways,
    # and leaving ID implicit makes that depend on a copied `id` attribute
    jidx = n.new("GeometryNodeInputIndex"); jidx.location = (-980, -1000)
    L(jidx.outputs[0], jit.inputs["ID"])
    mix = n.new("ShaderNodeVectorMath"); mix.operation = "ADD"; mix.location = (-620, -900)
    L(hn.outputs[0], mix.inputs[0]); L(jit.outputs[0], mix.inputs[1])
    trav = n.new("ShaderNodeMath"); trav.operation = "MULTIPLY"; trav.location = (-440, -760)
    L(tn.outputs[0], trav.inputs[0]); L(I("Spread"), trav.inputs[1])
    disp = n.new("ShaderNodeVectorMath"); disp.operation = "SCALE"; disp.location = (-260, -860)
    L(mix.outputs[0], disp.inputs[0]); L(trav.outputs[0], disp.inputs["Scale"])
    tri = n.new("GeometryNodeTranslateInstances"); tri.location = (240, 300)
    L(sci.outputs["Instances"], tri.inputs["Instances"])
    L(disp.outputs[0], tri.inputs["Translation"])
    tri.inputs["Local Space"].default_value = False   # see squib_burst

    isw = n.new("GeometryNodeIndexSwitch"); isw.data_type = "MATERIAL"
    isw.location = (240, 60)
    while len(isw.index_switch_items) < len(SURFACES):
        isw.index_switch_items.new()
    L(I("Surface"), isw.inputs["Index"])
    for i, (nm, col, rough) in enumerate(SURFACES):
        isw.inputs[i + 1].default_value = _mat(nm, col, rough)
    sm = n.new("GeometryNodeSetMaterial"); sm.location = (480, 300)
    L(tri.outputs["Instances"], sm.inputs["Geometry"])
    L(isw.outputs[0], sm.inputs["Material"])

    disc = n.new("GeometryNodeMeshCircle"); disc.fill_type = "NGON"
    disc.location = (-620, 700)
    disc.inputs["Vertices"].default_value = 12
    disc.inputs["Radius"].default_value = 1.0
    holes = n.new("GeometryNodeInstanceOnPoints"); holes.location = (-360, 700)
    L(I("Geometry"), holes.inputs["Points"])
    L(disc.outputs["Mesh"], holes.inputs["Instance"])
    L(align.outputs[0], holes.inputs["Rotation"])
    hg = n.new("ShaderNodeMapRange"); hg.clamp = True; hg.location = (-280, 60)
    L(tn.outputs[0], hg.inputs["Value"])
    hg.inputs["From Min"].default_value = 0.0
    hg.inputs["From Max"].default_value = 0.25
    hg.inputs["To Min"].default_value = 0.0
    hg.inputs["To Max"].default_value = 1.0
    hs = n.new("ShaderNodeMath"); hs.operation = "MULTIPLY"; hs.location = (-120, 60)
    L(hg.outputs[0], hs.inputs[0]); L(I("Hole Size"), hs.inputs[1])
    hsi = n.new("GeometryNodeScaleInstances"); hsi.location = (40, 700)
    L(holes.outputs["Instances"], hsi.inputs["Instances"])
    L(hs.outputs[0], hsi.inputs["Scale"])
    lift = n.new("ShaderNodeVectorMath"); lift.operation = "SCALE"; lift.location = (40, 880)
    L(hn.outputs[0], lift.inputs[0]); lift.inputs["Scale"].default_value = 0.004
    htr = n.new("GeometryNodeTranslateInstances"); htr.location = (240, 700)
    L(hsi.outputs["Instances"], htr.inputs["Instances"])
    L(lift.outputs[0], htr.inputs["Translation"])
    htr.inputs["Local Space"].default_value = False   # see squib_burst
    hm = n.new("GeometryNodeSetMaterial"); hm.location = (480, 700)
    L(htr.outputs["Instances"], hm.inputs["Geometry"])
    hm.inputs["Material"].default_value = _mat(HOLE_MAT, (0.03, 0.03, 0.04), 1.0)

    join = n.new("GeometryNodeJoinGeometry"); join.location = (860, 400)
    L(hm.outputs["Geometry"], join.inputs["Geometry"])
    L(sm.outputs["Geometry"], join.inputs["Geometry"])
    L(join.outputs["Geometry"], gout.inputs["Geometry"])
    return t


def install(force):
    root = shotlib.project_root()
    out = root / LIB
    if out.exists() and not force:
        sys.exit(f"error: {LIB} exists; pass --force to rebuild")
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    t = build_group()
    t.use_fake_user = True
    build_impacts_group().use_fake_user = True
    for name, col, rough in SURFACES:
        _mat(name, col, rough).use_fake_user = True
    _mat(HOLE_MAT, (0.03, 0.03, 0.04), 1.0).use_fake_user = True
    out.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out), relative_remap=True)
    print(f"squib install: {GROUP} + squib_impacts + "
          f"{len(SURFACES) + 1} materials -> {LIB}")


def _sockets(group):
    return {s.name: s.identifier for s in group.interface.items_tree
            if getattr(s, "in_out", None) == "INPUT"}


def apply(scene_name, ob_name, surface, start, count, targeted, target,
          direction, spread, hole, debris, life, stagger, chunks,
          dry_run):
    root = shotlib.project_root()
    lay = root / "layout" / "layout.blend"
    bpy.ops.wm.open_mainfile(filepath=str(lay))
    scene = bpy.data.scenes.get(scene_name)
    if scene is None:
        sys.exit(f"error: no scene {scene_name!r}")
    bpy.context.window.scene = scene
    ob = scene.objects.get(ob_name)
    if ob is None:
        sys.exit(f"error: no object {ob_name!r} in {scene_name}")
    if ob.type != "MESH":
        sys.exit(f"error: {ob_name!r} is {ob.type}, squibs need a MESH")

    grp = bpy.data.node_groups.get(GROUP)
    if grp is None:
        with bpy.data.libraries.load(str(root / LIB), link=True) as (src, dst):
            if GROUP not in src.node_groups:
                sys.exit(f"error: {GROUP} not in {LIB}; run --install first")
            dst.node_groups = [GROUP]
        grp = dst.node_groups[0]

    idx = SURFACE_NAMES.index(surface)
    print(f"{scene_name}/{ob_name}: surface={surface}({idx}) start={start} "
          f"count={count} targeted={targeted}")
    if dry_run:
        print("--dry-run: nothing written")
        return

    mod = next((m for m in ob.modifiers if m.type == "NODES"
                and m.node_group == grp), None)
    if mod is None:
        mod = ob.modifiers.new("squibs", "NODES")
        mod.node_group = grp
    ids = _sockets(grp)
    mod[ids["Surface"]] = idx
    mod[ids["Start Frame"]] = float(start)
    mod[ids["Count"]] = float(count)
    # Stagger spreads impacts randomly forward in time, which is what makes a
    # burst feel like a burst -- but it applies to a single targeted hit too,
    # so leaving it at the default delays one impact by up to 10 frames and
    # the hit lands nowhere near its Start Frame. Pass --stagger=0 for a hit
    # that has to happen ON a beat.
    mod[ids["Stagger"]] = float(stagger)
    mod[ids["Targeted"]] = bool(targeted)
    mod[ids["Spread"]] = float(spread)
    mod[ids["Hole Size"]] = float(hole)
    # Debris Scale is worth reaching for on any shot that is not a close-up:
    # the authored 6 cm chunk simply does not read past a few metres.
    mod[ids["Debris Scale"]] = float(debris)
    mod[ids["Debris Count"]] = int(chunks)
    mod[ids["Life"]] = float(life)
    if target is not None:
        # --target is given in WORLD space because that is how a hit is
        # described, but the socket is object-LOCAL: geometry nodes run in
        # local space, so a world value lands the impact off the model by the
        # object's own offset. Convert here.
        from mathutils import Vector
        local = ob.matrix_world.inverted() @ Vector(target)
        mod[ids["Target"]] = local
        print(f"  target world {tuple(round(v, 2) for v in target)} "
              f"-> local {tuple(round(v, 2) for v in local)}")
    if direction is not None:
        # same trap as Target, and easier to miss: Direction is local too, so
        # a world normal aims the hole decal edge-on the moment the object is
        # rotated. Rotation only — it is a direction, not a position.
        from mathutils import Vector as V
        d = (ob.matrix_world.inverted().to_3x3() @ V(direction)).normalized()
        mod[ids["Direction"]] = d
        print(f"  direction world {tuple(round(v, 2) for v in direction)} "
              f"-> local {tuple(round(v, 2) for v in d)}")
    bpy.ops.wm.save_mainfile()
    print(f"applied {GROUP} to {ob_name}")


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    force = "--force" in argv
    dry_run = "--dry-run" in argv
    targeted = "--targeted" in argv
    spec = target = direction = None
    surface, start, count, spread, hole = "dirt", 1, 8, 0.5, 0.09
    debris, life, stagger, chunks = 0.06, 12.0, 10.0, 6
    for a in argv:
        if a.startswith("--apply="):
            spec = a.split("=", 1)[1]
        elif a.startswith("--surface="):
            surface = a.split("=", 1)[1]
        elif a.startswith("--start="):
            start = float(a.split("=", 1)[1])
        elif a.startswith("--count="):
            count = float(a.split("=", 1)[1])
        elif a.startswith("--spread="):
            spread = float(a.split("=", 1)[1])
        elif a.startswith("--hole="):
            hole = float(a.split("=", 1)[1])
        elif a.startswith("--debris="):
            debris = float(a.split("=", 1)[1])
        elif a.startswith("--life="):
            life = float(a.split("=", 1)[1])
        elif a.startswith("--stagger="):
            stagger = float(a.split("=", 1)[1])
        elif a.startswith("--chunks="):
            chunks = int(a.split("=", 1)[1])
        elif a.startswith("--target="):
            target = tuple(float(v) for v in a.split("=", 1)[1].split(","))
        elif a.startswith("--direction="):
            direction = tuple(float(v) for v in a.split("=", 1)[1].split(","))

    if "--install" in argv:
        install(force)
        return
    if spec:
        if surface not in SURFACE_NAMES:
            sys.exit(f"error: surface must be one of {', '.join(SURFACE_NAMES)}")
        if ":" not in spec:
            sys.exit("error: --apply=<scene>:<object>")
        sc, ob = spec.split(":", 1)
        apply(sc, ob, surface, start, count, targeted, target, direction,
              spread, hole, debris, life, stagger, chunks, dry_run)
        return
    sys.exit("usage: --install [--force] | --apply=<scene>:<object> "
             "[--surface=dirt|grass|plastic|wood|stucco|metal] [--start=N] "
             "[--count=N] [--targeted --target=x,y,z --direction=x,y,z] "
             "[--spread=N] [--hole=N] [--debris=N] [--life=N] "
             "[--stagger=N] [--chunks=N]   "
             "(target/direction are WORLD space)")


if __name__ == "__main__":
    main()
