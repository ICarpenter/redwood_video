#!/usr/bin/env python3
"""Build the mountain backdrop — a close, enclosing ring of stylised peaks.

This replaces the real-DEM approach in `tools/terrain.py`. Real geography was
the wrong instrument: `refs/styles/` wants mountains that sit RIGHT BEHIND the
house and stand above the roofline on every side, in big simple faceted forms
with hard shading breaks and strong near-to-far value separation. That is a
theatre backdrop, not a landscape — a painted cyclorama with parallax.

Read the refs and the shape is unambiguous
(`il_fullxfull.5572769945_bsf5`, `il_570xN.5698411872_362y`):

  - the range fills the band between roofline and sky, edge to edge
  - two or three overlapping ridges, near one darker, far one paler
  - few, large planes; the silhouette carries everything
  - close enough to read as a wall, not a horizon

So the silhouette is the design surface. Each ridge is a 1D height function of
ANGLE — a curve you edit — swept into geometry. Nothing is simulated, so
nothing has to be fought.

    h(theta) = ridged periodic noise, sharpened, clamped to a floor

Sampling noise around a circle of radius `freq` makes it periodic in theta for
free, so the ring always closes. `1 - |noise|` creates ridges (creases become
peaks) rather than the rolling blobs plain noise gives, and `--sharp` pushes
the valleys down to make the peaks dramatic.

HOW BIG. The ridge has to clear what is already in front of it. From a 1.6 m
camera the house fascia (3.6 m, 10 m away) subtends 11.3 deg, and the
BACKYARD TREELINE is worse — 8.7 m canopies about 21 m out subtend 18.7 deg.
A ridge at radius r must therefore stand at least r*tan(18.7deg) just to graze
the trees. At 300 m that is 101 m, which is why the near ring defaults to 150.
`--report` prints this check for the real cameras rather than trusting it.

Cost is trivial: three rings at 96 segments is about 900 verts. The DEM version
was 476,000.

Run headless (writes --out):
    "$BLENDER" --background --factory-startup --python-exit-code 1 \\
        --python tools/skyline.py -- [flags]

Or open it in Blender's Text Editor and press Run Script: it detects the
interactive session and builds into the current scene without saving.

Flags:
    --out=PATH        where to save (headless only; default skyline.blend)
    --facets=smooth   smooth | hard. `hard` is flat-shaded with coarse
                      segments — the cut-paper read the LOCKED style wants
                      (Mid-Century Print, 2026-08-05). `smooth` is smooth-
                      shaded and fine; it served the dead claymation
                      candidate. NOTE the default is still `smooth` and so
                      no longer matches the film — pass --facets=hard.
                      NOTE: `smooth` alone makes the silhouette SPIKIER, not
                      smoother — see --sharp.
    --segments=N      angular samples per ring. Default 480 smooth / 96 hard.
                      This IS the facet size — fewer means chunkier.
    --rings=r,h;r,h   ring crest radius and peak height, near to far.
                      Default 380,70;800,175;1500,400
    --sharp=1.1       >1 pushes valleys down and makes peaks pointier; <1
                      rounds them off. This, not --facets, is what controls how
                      smooth the SHAPES read. 1.6 gives alpine spikes, 0.85
                      gives broad dune-like swells.
    --floor=0.25      minimum ridge height as a fraction of peak, so the ring
                      never drops to the horizon and opens a sky gap
    --jitter=0.06     per-angle wobble of the crest radius, so rings do not
                      read as perfect circles
    --octaves=3       detail in the silhouette; fewer = smoother
    --freq=2.2        base angular frequency — roughly how many big peaks
    --seed=1993       fixed, so the skyline never reshuffles between runs
    --ramp-near=0.30  where the near ring samples the film's palette ramp
    --ramp-far=0.92   where the far ring samples it (higher = paler/hazier)
    --ground=1        build the flat desert floor out to the rings
    --hole=x0,x1,y0,y1  rect left uncut for the hand-built set
                      (default -45,45,-32,45, matching property.blend)
    --report          print the clearance check and exit codes only
"""
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import noise

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shotlib

ROOT = shotlib.project_root()
DEFAULT_OUT = ROOT / "assets" / "envs" / "property" / "skyline.blend"

# The film's palette (refs/palette.scss), darkest to palest. Ridges sample this
# ramp so the backdrop is on-palette by construction: near ridges land near the
# plum end, far ones fade toward pale sky, which is the atmospheric
# near-dark/far-pale separation the refs lean on so heavily.
PALETTE_RAMP = [
    (0x52, 0x05, 0x0a),   # night bordeaux
    (0x83, 0x21, 0x61),   # royal plum
    (0x9b, 0x7e, 0xde),   # soft periwinkle
    (0xbc, 0xd2, 0xee),   # pale sky
]
GROUND_RGB = (0xC2, 0xA4, 0x8A)

# What the ridge has to clear, measured from property.blend. The treeline, not
# the house, is the binding constraint.
CLEARANCE = [
    ("house fascia",      3.60, 10.0),
    ("backyard treeline", 8.70, 21.0),
    ("garage roof",       3.25, 12.0),
]
EYE = 1.6


def srgb_to_linear(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def ramp_color(t):
    """Sample the film's palette ramp at t in [0,1] -> linear RGBA."""
    t = min(max(t, 0.0), 1.0) * (len(PALETTE_RAMP) - 1)
    i = min(int(t), len(PALETTE_RAMP) - 2)
    f = t - i
    a, b = PALETTE_RAMP[i], PALETTE_RAMP[i + 1]
    return tuple(srgb_to_linear(a[k] + (b[k] - a[k]) * f) for k in range(3)) + (1.0,)


def material(name, rgba):
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba
        bsdf.inputs["Roughness"].default_value = 1.0
        if "Specular IOR Level" in bsdf.inputs:
            bsdf.inputs["Specular IOR Level"].default_value = 0.05
    return mat


# --- the silhouette --------------------------------------------------------

def ridge_profile(thetas, cfg, layer):
    """Height along the ring, normalised to [floor, 1].

    Sampled on a circle so it is periodic in theta and the ring always closes.
    `1 - |noise|` turns creases into peaks (ridged noise); plain noise gives
    rolling blobs, which is not what the refs show.
    """
    noise.seed_set(cfg["seed"] + layer * 101)
    h = np.zeros(len(thetas))
    amp, freq, total = 1.0, cfg["freq"], 0.0
    zoff = 3.7 * (layer + 1)
    for _ in range(cfg["octaves"]):
        c, s = np.cos(thetas) * freq, np.sin(thetas) * freq
        for i in range(len(thetas)):
            h[i] += amp * (1.0 - abs(noise.noise((c[i], s[i], zoff))))
        total += amp
        amp *= 0.5
        freq *= 2.0
    h /= total
    span = h.max() - h.min()
    h = (h - h.min()) / span if span > 1e-9 else np.full_like(h, 0.5)
    h = h ** cfg["sharp"]
    return cfg["floor"] + (1.0 - cfg["floor"]) * h


def radius_jitter(thetas, cfg, layer):
    noise.seed_set(cfg["seed"] + 977 + layer * 31)
    c, s = np.cos(thetas) * 1.7, np.sin(thetas) * 1.7
    j = np.array([noise.noise((c[i], s[i], 11.3 * (layer + 1)))
                  for i in range(len(thetas))])
    return 1.0 + cfg["jitter"] * j


def build_ring(cfg, layer, crest_r, peak_h):
    n = cfg["segments"]
    thetas = np.linspace(0.0, 2.0 * math.pi, n, endpoint=False)
    prof = ridge_profile(thetas, cfg, layer)
    rr = crest_r * radius_jitter(thetas, cfg, layer)
    hh = prof * peak_h

    dx, dy = np.cos(thetas), np.sin(thetas)
    foot = crest_r * cfg["foot"]

    verts = np.empty((n * 3, 3))
    # ring 0 = foot on the ground, 1 = crest, 2 = the back slope falling away
    verts[0::3, 0], verts[0::3, 1], verts[0::3, 2] = (rr - foot) * dx, (rr - foot) * dy, 0.0
    verts[1::3, 0], verts[1::3, 1], verts[1::3, 2] = rr * dx, rr * dy, hh
    back = rr + foot * 0.7
    verts[2::3, 0], verts[2::3, 1], verts[2::3, 2] = back * dx, back * dy, hh * 0.35

    faces = []
    for i in range(n):
        j = (i + 1) % n
        a0, a1, a2 = i * 3, i * 3 + 1, i * 3 + 2
        b0, b1, b2 = j * 3, j * 3 + 1, j * 3 + 2
        faces.append((a0, b0, b1, a1))   # front face
        faces.append((a1, b1, b2, a2))   # back slope
    return verts, faces, float(hh.max()), float(hh.min())


def ring_object(cfg, layer, crest_r, peak_h, n_layers):
    verts, faces, hmax, hmin = build_ring(cfg, layer, crest_r, peak_h)
    name = f"skyline_ridge_{layer + 1}"
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts.tolist(), [], faces)
    me.update()
    smooth = cfg["facets"] == "smooth"
    me.polygons.foreach_set("use_smooth", [smooth] * len(me.polygons))
    t = cfg["ramp_near"]
    if n_layers > 1:
        t += (cfg["ramp_far"] - cfg["ramp_near"]) * layer / (n_layers - 1)
    me.materials.append(material(f"{name}_mat", ramp_color(t)))
    print(f"  ridge {layer + 1}: crest r={crest_r:.0f} m  height {hmin:.0f}..{hmax:.0f} m "
          f"  ramp t={t:.2f}  {len(me.vertices)} verts")
    return bpy.data.objects.new(name, me), hmax


def ground_object(cfg, reach):
    """Flat desert floor, framed around the hand-built set so it never overlaps
    (an overlapping slab is coplanar with property.blend's ground and z-fights
    — the mistake terrain.py had to be corrected for)."""
    hx0, hx1, hy0, hy1 = cfg["hole"] if cfg["hole"] else (0, 0, 0, 0)
    g = reach
    rects = ([(-g, hx0, -g, g), (hx1, g, -g, g),
              (hx0, hx1, -g, hy0), (hx0, hx1, hy1, g)]
             if cfg["hole"] else [(-g, g, -g, g)])
    verts, faces = [], []
    for x0, x1, y0, y1 in rects:
        if x1 - x0 < 1e-6 or y1 - y0 < 1e-6:
            continue
        b = len(verts)
        verts += [(x0, y0, 0.0), (x1, y0, 0.0), (x1, y1, 0.0), (x0, y1, 0.0)]
        faces.append((b, b + 1, b + 2, b + 3))
    me = bpy.data.meshes.new("skyline_ground")
    me.from_pydata(verts, [], faces)
    me.update()
    me.materials.append(material("skyline_ground_mat",
                                 tuple(srgb_to_linear(c) for c in GROUND_RGB) + (1.0,)))
    return bpy.data.objects.new("skyline_ground", me)


def report(cfg, rings, heights):
    """Angular sizes, so 'over the house on all sides' is checked not assumed.

    The house is the thing to clear. The backyard treeline is a LOCAL occluder
    — 8.7 m canopies 21 m away subtend 18.7 deg, more than any sane ridge — so
    it is listed for reference, not used as the target. Chasing it is what made
    the first pass fill the whole frame with a wall.
    """
    print("\n  what the ridge has to stand over (1.6 m camera):")
    for name, h, d in CLEARANCE:
        print(f"    {name:<20} {h:.2f} m at {d:>2.0f} m -> "
              f"{math.degrees(math.atan2(h - EYE, d)):5.1f} deg")
    house = max(math.degrees(math.atan2(h - EYE, d))
                for n, h, d in CLEARANCE if "tree" not in n)
    print(f"    target: clear the house ({house:.1f} deg) without filling frame\n")
    prev = 0.0
    for (r, _), hmax in zip(rings, heights):
        ang = math.degrees(math.atan2(hmax, r))
        notes = []
        notes.append("clears house" if ang > house else "BELOW the house")
        notes.append("stacks above the one in front" if ang > prev
                     else "HIDDEN behind the nearer ridge")
        if ang > 20.0:
            notes.append("WARNING >20 deg: overshoots a 32 mm frame")
        prev = ang
        print(f"    ridge r={r:<6.0f} peak {hmax:6.0f} m -> {ang:5.1f} deg   "
              + "; ".join(notes))
    return True


# --- entry point -----------------------------------------------------------

def parse_args(argv):
    cfg = {
        "out": DEFAULT_OUT, "facets": "smooth", "segments": None,
        # Ridges ASCEND with distance — near low, far tall. Measured off
        # `il_fullxfull.5572769945_bsf5`, where the foothills sit under the
        # far range rather than beside it. Equal angular heights collapse the
        # layers into one slab, which is exactly how the first pass failed.
        "rings": [(380.0, 70.0), (800.0, 175.0), (1500.0, 400.0)],
        # sharp 1.1 / 3 octaves, not 1.6 / 4. Smooth SHADING alone made the
        # skyline spikier, not smoother: 480 segments fully resolves the ridged
        # noise where 96 was quietly smoothing it by undersampling. Softening
        # the profile is what actually reads as smooth.
        "sharp": 1.1, "floor": 0.25, "jitter": 0.06, "foot": 0.45,
        "octaves": 3, "freq": 2.2, "seed": 1993,
        # Start well up the ramp: royal plum at 0.30 rendered as a saturated
        # magenta wall. The refs' mountains are hazy and desaturated.
        "ramp_near": 0.55, "ramp_far": 0.96, "ground": True,
        "hole": (-45.0, 45.0, -32.0, 45.0), "report": False,
    }
    floats = {"sharp", "floor", "jitter", "foot", "freq", "ramp_near", "ramp_far"}
    for arg in argv:
        if arg == "--report":
            cfg["report"] = True
            continue
        if arg == "--no-hole":
            cfg["hole"] = None
            continue
        if not arg.startswith("--") or "=" not in arg:
            raise SystemExit(f"unrecognised argument: {arg}\n{__doc__}")
        key, _, val = arg[2:].partition("=")
        key = key.replace("-", "_")
        if key == "out":
            cfg[key] = Path(val).expanduser().resolve()
        elif key == "facets":
            if val not in ("hard", "smooth"):
                raise SystemExit("--facets must be hard or smooth")
            cfg[key] = val
        elif key == "rings":
            cfg[key] = [tuple(float(v) for v in p.split(","))
                        for p in val.split(";") if p]
            if any(len(p) != 2 for p in cfg[key]):
                raise SystemExit("--rings needs r,h;r,h;...")
        elif key == "hole":
            cfg[key] = tuple(float(v) for v in val.split(","))
        elif key in ("segments", "octaves", "seed"):
            cfg[key] = int(val)
        elif key == "ground":
            cfg[key] = val not in ("0", "false", "no")
        elif key in floats:
            cfg[key] = float(val)
        else:
            raise SystemExit(f"unknown flag: --{key}\n{__doc__}")
    if cfg["segments"] is None:
        cfg["segments"] = 96 if cfg["facets"] == "hard" else 480
    return cfg


def build(cfg):
    coll = bpy.data.collections.get("skyline") or bpy.data.collections.new("skyline")
    if coll.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(coll)

    print(f"skyline: {len(cfg['rings'])} ridges, {cfg['facets']} facets, "
          f"{cfg['segments']} segments")
    heights = []
    for i, (r, h) in enumerate(cfg["rings"]):
        ob, hmax = ring_object(cfg, i, r, h, len(cfg["rings"]))
        coll.objects.link(ob)
        heights.append(hmax)
    if cfg["ground"]:
        reach = max(r for r, _ in cfg["rings"]) * 1.6
        coll.objects.link(ground_object(cfg, reach))
        print(f"  ground: flat frame to {reach:.0f} m")

    total = sum(len(o.data.vertices) for o in coll.objects)
    print(f"  total {total:,} verts")
    report(cfg, cfg["rings"], heights)
    return coll


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    cfg = parse_args(argv)
    if cfg["report"]:
        report(cfg, cfg["rings"], [h for _, h in cfg["rings"]])
        return
    build(cfg)
    if bpy.app.background and cfg["out"]:
        cfg["out"].parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(cfg["out"]))
        print(f"\n  wrote {cfg['out']}")
    else:
        print("\n  built into the current scene; nothing saved.")


if __name__ == "__main__":
    main()
