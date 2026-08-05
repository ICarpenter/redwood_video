#!/usr/bin/env python3
"""Build background terrain for the property from real elevation data.

The film's canon fixes what is out there: the house is a "1962 flat-roof
desert-modern pavilion" (docs/treatment/house.md), and the FINAL IMAGE of the
film is the boy and the sheriff running west into the sunset, "into the
treeline and the desert and mountains beyond" (docs/treatment/script.md).
So the west horizon is not set dressing -- it is the last shot of the movie,
backlit. This tool gives it a real mountain silhouette instead of an invented
one.

Source location: PALM SPRINGS, CALIFORNIA. It is the literal canon (style.md
calls the house "a 1962 Palm Springs fantasy"), and the geography is a gift --
the valley floor sits at ~109 m and Mount San Jacinto rises to 3302 m about
16 km due WEST, one of the steepest escarpments in North America, with the
sun setting straight behind it.

Elevation data: AWS Terrain Tiles (the old Mapzen set), public, no API key.
    https://registry.opendata.aws/terrain-tiles/
"terrarium" PNG encoding, one tile = 256x256 samples:
    elevation_m = (R * 256 + G + B / 256) - 32768
Tiles are decoded with Blender's own image loader, which is bit-exact against
a reference zlib/PNG decoder (verified: 0/65536 pixels differ) and much faster
than unfiltering Paeth scanlines in Python.

ORIENTATION. The site's compass does not line up with the axes the way you
would guess -- docs/treatment/site.md is canonical:

    -Y = EAST  = the ROAD       +Y = WEST = the BACKYARD (the final image)
    +X = NORTH = the CORRIDOR   -X = SOUTH = the GARAGE

So real-world WEST must land on film +Y. `--bearing` sets which real compass
bearing points along +Y; the default 270 (due west) keeps the landscape
honest. 262 aims +Y straight at San Jacinto Peak instead. The mapping is a
proper rotation -- the terrain is never mirrored.

HEIGHTS. Three zones, blended smoothly, so the terrain cannot break blocking
that is already staged in world space at z=0:

    r < --flat (15 m)        exactly z=0. The house, garage and porch pad
                             stays dead flat and true.
    --flat .. --dem-in       gentle procedural roll, +/- --undulation metres.
                             Real 30 m DEM cannot resolve 1 m ground undulation
                             on a flat valley floor, so this part is honestly
                             art-directed noise, not data.
    beyond --dem-full        100% real DEM: the alluvial fan, then the wall.

By default this writes a SEPARATE file (assets/envs/property/terrain.blend)
and never opens or touches property.blend -- that file is hand-maintained and
is often dirty or open in a GUI session. Link or append the `terrain`
collection from there when you are happy with it.

Run headless (writes --out):
    "$BLENDER" --background --factory-startup --python-exit-code 1 \
        --python tools/terrain.py -- [flags]

Or open it in Blender's Text Editor and press Run Script: it detects the
interactive session and builds into the current scene without saving anything.

Flags:
    --out=PATH        where to save (headless only; default terrain.blend)
    --lat=, --lon=    anchor; the property origin sits here at z=0
    --bearing=270     real compass bearing that points along film +Y (west)
    --radius=28000    how far the terrain reaches, metres
    --step=120        far-field sample spacing, metres. 60 doubles skyline
                      detail (and quadruples the vertex count) for hero frames
    --fine=70         radius of the fine inner grid, metres
    --fine-step=2     inner grid spacing. Must stay well under --roll or the
                      undulation aliases instead of reading as ground
    --mid=700         radius of the middle tier, metres
    --mid-step=20     middle tier spacing, metres
    --flat=15         dead-flat pad radius, metres. 15 clears the house
                      (r 8.6), garage (r 13.3) and porch (r 8.1)
    --ramp=8          distance over which the roll fades in past the pad
    --undulation=0.25 peak deviation of the gentle roll under the set, metres
    --roll=16         wavelength of that roll, metres
    --dem-in=70       radius where the real DEM starts blending in
    --dem-full=900    radius where the terrain is pure DEM
    --zoom=12         tile zoom (12 is ~32 m/sample at this latitude)
    --cache=PATH      tile cache dir (default <repo>/.cache/dem)
    --keep-flat       skip the procedural roll entirely; only the DEM shapes it
    --hole=x0,x1,y0,y1  rect cut out for the hand-built set. Default is
                      -45,45,-32,45, the footprint of ground_yard + ditch +
                      ground_roadside. Their tops sit at exactly z=0, so a slab
                      laid over them is coplanar and z-fights; the frame abuts
                      them flush instead. Keep --flat big enough to cover the
                      hole's corners (r 63.6 for the default) or the seam steps.
    --no-hole         build a full slab (only for a standalone terrain file)
"""
import math
import sys
import urllib.error
import urllib.request
from pathlib import Path

import bpy
import numpy as np
from mathutils import noise

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shotlib

ROOT = shotlib.project_root()
DEFAULT_OUT = ROOT / "assets" / "envs" / "property" / "terrain.blend"
DEFAULT_CACHE = ROOT / ".cache" / "dem"

TILE_URL = "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"
TILE_PX = 256

# Coachella Valley floor (~109 m), out in the open east of Palm Springs and on
# San Jacinto Peak's exact latitude, so the 3302 m summit sits DUE WEST -- dead
# centre in the final image. Chosen by measuring the westward profile rather
# than by eye: from here the ground stays flat desert for 4 km (+14 m), then
# climbs to +509 m at 8 km and +2550 m at 16 km. Anchoring at the town edge
# instead (33.8303, -116.5453) starts the wall only 1 km out, which buries the
# "treeline and the desert and mountains beyond" the script asks for.
ANCHOR_LAT = 33.8147
ANCHOR_LON = -116.4800

# Fixed so the art-directed ground roll is identical on every run -- the set
# must not shuffle underneath blocking that has already been staged on it.
ROLL_SEED = 1993

# The key world-space positions from docs/treatment/site.md. Printed with
# their new ground height at the end of a run so the re-grounding cost of any
# --undulation setting is visible rather than discovered later in a render.
SITE_POINTS = [
    ("house centre",   -4.0,   0.5),
    ("garage centre",  -10.0,  0.0),
    ("front porch",    -2.0,  -5.2),
    ("boy",            -2.0,   8.5),
    ("firing squad",    0.0,  20.0),
    ("BBQ + propane",  -5.8,   6.1),
    ("santa",          -9.25,  5.05),
    ("old truck",      12.5,  -0.8),
    ("clothesline",     8.6,  10.28),
    ("back fence",      0.0,  27.0),
    ("ditch / crash",  10.0, -15.5),
    ("road centre",     0.0, -20.0),
]


# --- geodesy ---------------------------------------------------------------

def metres_per_degree(lat_deg):
    """WGS84 local scale, good to about a metre. Used to turn the local
    metre grid into lon/lat before projecting into Web Mercator."""
    p = math.radians(lat_deg)
    m_lat = 111132.92 - 559.82 * math.cos(2 * p) + 1.175 * math.cos(4 * p)
    m_lon = 111412.84 * math.cos(p) - 93.5 * math.cos(3 * p)
    return m_lat, m_lon


def lonlat_to_pixel(lon, lat, zoom):
    """Web Mercator global pixel coordinates at `zoom`. Arrays in, arrays out."""
    n = 2.0 ** zoom
    px = (lon + 180.0) / 360.0 * n * TILE_PX
    p = np.radians(lat)
    py = (1.0 - np.log(np.tan(p) + 1.0 / np.cos(p)) / math.pi) / 2.0 * n * TILE_PX
    return px, py


def film_to_geo(x, y, bearing_deg):
    """Film axes -> local (east, north) metres.

    Film +Y is the real compass bearing `bearing_deg` (west by default) and
    film +X is bearing+90 (north by default). The inverse of a rotation is its
    transpose, and the determinant is +1, so no mirroring ever happens.
    """
    b = math.radians(bearing_deg)
    bx = math.radians(bearing_deg + 90.0)
    east = x * math.sin(bx) + y * math.sin(b)
    north = x * math.cos(bx) + y * math.cos(b)
    return east, north


# --- tiles -----------------------------------------------------------------

def fetch_tile(zoom, tx, ty, cache_dir):
    path = cache_dir / str(zoom) / str(tx) / f"{ty}.png"
    if path.exists() and path.stat().st_size > 0:
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    url = TILE_URL.format(z=zoom, x=tx, y=ty)
    req = urllib.request.Request(url, headers={"User-Agent": "redwood_video/terrain.py"})
    last = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
            path.write_bytes(data)
            return path
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last = exc
    raise RuntimeError(f"could not fetch {url}: {last}")


def read_tile(path):
    """Decode one terrarium tile to a (256, 256) float array of metres.

    Blender's loader is used deliberately: with the colorspace forced to
    Non-Color it round-trips the 8-bit channels exactly (verified bit-for-bit
    against a zlib PNG decoder), and it is C-speed where a pure-Python Paeth
    unfilter is not.
    """
    img = bpy.data.images.load(str(path), check_existing=False)
    try:
        img.colorspace_settings.name = "Non-Color"
        img.alpha_mode = "NONE"
        w, h = img.size
        buf = np.empty(w * h * img.channels, dtype=np.float32)
        img.pixels.foreach_get(buf)
        rgb = buf.reshape(h, w, img.channels)[::-1, :, :3]   # Blender is bottom-up
        rgb = np.rint(rgb * 255.0).astype(np.float64)
        return (rgb[:, :, 0] * 256.0 + rgb[:, :, 1] + rgb[:, :, 2] / 256.0) - 32768.0
    finally:
        bpy.data.images.remove(img)


def build_mosaic(px_min, px_max, py_min, py_max, zoom, cache_dir):
    """Download and stitch every tile covering a global-pixel bbox."""
    n = 2 ** zoom
    tx0, tx1 = int(math.floor(px_min / TILE_PX)), int(math.floor(px_max / TILE_PX))
    ty0, ty1 = int(math.floor(py_min / TILE_PX)), int(math.floor(py_max / TILE_PX))
    tx0, tx1 = max(tx0, 0), min(tx1, n - 1)
    ty0, ty1 = max(ty0, 0), min(ty1, n - 1)

    cols, rows = tx1 - tx0 + 1, ty1 - ty0 + 1
    total = cols * rows
    print(f"  fetching {total} tile(s) at zoom {zoom} "
          f"(x {tx0}..{tx1}, y {ty0}..{ty1})")
    mosaic = np.zeros((rows * TILE_PX, cols * TILE_PX), dtype=np.float64)
    done = 0
    for j, ty in enumerate(range(ty0, ty1 + 1)):
        for i, tx in enumerate(range(tx0, tx1 + 1)):
            mosaic[j * TILE_PX:(j + 1) * TILE_PX,
                   i * TILE_PX:(i + 1) * TILE_PX] = read_tile(
                       fetch_tile(zoom, tx, ty, cache_dir))
            done += 1
            if done % 10 == 0 or done == total:
                print(f"    {done}/{total}")
    return mosaic, tx0 * TILE_PX, ty0 * TILE_PX


def _catmull_rom_weights(t):
    """Catmull-Rom basis. Interpolating and C1-continuous, which is the whole
    point: bilinear has a slope discontinuity at every DEM sample boundary,
    and on a near-flat valley floor a low raking sun turns those breaks into
    visible streaks across the ground."""
    t2, t3 = t * t, t * t * t
    return (-0.5 * t3 + t2 - 0.5 * t,
            1.5 * t3 - 2.5 * t2 + 1.0,
            -1.5 * t3 + 2.0 * t2 + 0.5 * t,
            0.5 * t3 - 0.5 * t2)


def build_mips(mosaic, levels=5):
    """Box-filtered pyramid of the elevation mosaic.

    The far field samples the mesh at --step (120 m) from a DEM whose real
    ground resolution is ~32 m, i.e. 3.8x undersampled. Point-sampling that is
    aliasing, and no amount of interpolation fixes aliasing -- the signal has
    to be low-passed BEFORE it is decimated. Level L is 2^L DEM samples wide.
    """
    mips = [mosaic]
    m = mosaic
    for _ in range(levels - 1):
        h2, w2 = m.shape[0] // 2, m.shape[1] // 2
        if h2 < 4 or w2 < 4:
            break
        m = 0.25 * (m[0:2 * h2:2, 0:2 * w2:2] + m[1:2 * h2:2, 0:2 * w2:2] +
                    m[0:2 * h2:2, 1:2 * w2:2] + m[1:2 * h2:2, 1:2 * w2:2])
        mips.append(m)
    return mips


def sample_lod(mips, ox, oy, px, py, lod):
    """Trilinear: bicubic within each mip level, linear between levels.

    Blending between levels rather than switching is what keeps the tier
    boundaries invisible -- a hard change of filter width would put a ring
    around the set.
    """
    out = np.zeros_like(px)
    acc = np.zeros_like(px)
    for level in range(len(mips)):
        wgt = np.clip(1.0 - np.abs(lod - level), 0.0, 1.0)
        if not np.any(wgt > 0.0):
            continue
        s = float(1 << level)
        # level L texel (0,0) covers global pixels [o, o+s), so its centre
        # sits half a texel in.
        lx = (px - ox - (s - 1.0) * 0.5) / s
        ly = (py - oy - (s - 1.0) * 0.5) / s
        out += sample_bicubic(mips[level], lx, ly) * wgt
        acc += wgt
    return out / np.maximum(acc, 1e-9)


def sample_bicubic(mosaic, fx, fy):
    """Bicubic lookup in mosaic-local pixel coordinates, clamped at the edges."""
    h, w = mosaic.shape
    fx = np.clip(fx, 0.0, w - 1.0001)
    fy = np.clip(fy, 0.0, h - 1.0001)
    x1 = fx.astype(np.int64)
    y1 = fy.astype(np.int64)
    tx, ty = fx - x1, fy - y1
    wx = _catmull_rom_weights(tx)
    wy = _catmull_rom_weights(ty)
    xs = [np.clip(x1 + d, 0, w - 1) for d in (-1, 0, 1, 2)]
    ys = [np.clip(y1 + d, 0, h - 1) for d in (-1, 0, 1, 2)]
    out = np.zeros_like(fx)
    for j in range(4):
        row = np.zeros_like(fx)
        for i in range(4):
            row += mosaic[ys[j], xs[i]] * wx[i]
        out += row * wy[j]
    return out


# --- height field ----------------------------------------------------------

def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / max(e1 - e0, 1e-9), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


class Terrain:
    """Height field for the property. Sampling is exposed so a follow-up
    re-grounding pass can drop staged objects onto the same surface."""

    def __init__(self, cfg):
        self.cfg = cfg
        m_lat, m_lon = metres_per_degree(cfg["lat"])
        self.m_lat, self.m_lon = m_lat, m_lon
        self.mosaic = None
        self.mips = None
        self.ox = self.oy = 0
        self.base = 0.0
        # Real ground resolution of one DEM sample at this latitude/zoom.
        self.mpp = (156543.03392804097 * math.cos(math.radians(cfg["lat"]))
                    / 2.0 ** cfg["zoom"])

    def _pixels(self, x, y):
        cfg = self.cfg
        east, north = film_to_geo(x, y, cfg["bearing"])
        lat = cfg["lat"] + north / self.m_lat
        lon = cfg["lon"] + east / self.m_lon
        return lonlat_to_pixel(lon, lat, cfg["zoom"])

    def load(self, reach):
        """Fetch the tiles covering a square of +/- reach metres."""
        c = np.array([-reach, reach])
        gx, gy = np.meshgrid(c, c)
        px, py = self._pixels(gx.ravel(), gy.ravel())
        self.mosaic, self.ox, self.oy = build_mosaic(
            px.min(), px.max(), py.min(), py.max(),
            self.cfg["zoom"], self.cfg["cache"])
        self.mips = build_mips(self.mosaic)
        apx, apy = self._pixels(np.array([0.0]), np.array([0.0]))
        self.base = float(sample_bicubic(self.mosaic, apx - self.ox, apy - self.oy)[0])
        print(f"  anchor ground elevation {self.base:.1f} m -> scene z = 0")
        print(f"  DEM range {self.mosaic.min():.0f}..{self.mosaic.max():.0f} m "
              f"({self.mosaic.max() - self.base:.0f} m above the pad)")
        print(f"  DEM resolution {self.mpp:.1f} m/sample, "
              f"{len(self.mips)} mip level(s) for anti-aliased far field")

    def mesh_step(self, r):
        """Local mesh sample spacing at radius r, smoothed across the tier
        boundaries. Discontinuous spacing would step the filter width and put
        a visible ring around the set."""
        cfg = self.cfg
        s = np.full_like(r, cfg["fine_step"])
        s = s + (cfg["mid_step"] - s) * smoothstep(cfg["fine"] * 0.8,
                                                   cfg["fine"] * 1.25, r)
        s = s + (cfg["step"] - s) * smoothstep(cfg["mid"] * 0.8,
                                               cfg["mid"] * 1.25, r)
        return s

    def dem(self, x, y, r=None):
        px, py = self._pixels(x, y)
        if r is None:
            r = np.hypot(x, y)
        lod = np.maximum(np.log2(self.mesh_step(r) / self.mpp), 0.0)
        return sample_lod(self.mips, self.ox, self.oy, px, py, lod) - self.base

    def roll(self, x, y, r, weight):
        """Gentle art-directed undulation under the acting area.

        Deliberately NOT from the DEM: 30 m elevation samples on a flat
        alluvial fan cannot resolve metre-scale ground roll, so pretending
        they do would be a lie. Only evaluated where it actually contributes.
        """
        cfg = self.cfg
        out = np.zeros_like(x)
        if cfg["undulation"] <= 0.0:
            return out
        hot = np.nonzero(weight > 1e-4)[0]
        if not len(hot):
            return out
        s = cfg["roll"]
        noise.seed_set(ROLL_SEED)
        for i in hot:
            out[i] = noise.fractal((x[i] / s, y[i] / s, 0.0), 1.0, 2.0, 3)
        # Centre and normalise so --undulation is literally the peak deviation
        # in metres, and the roll never drifts the whole yard up or down.
        # Calibrate on the yard (r < dem_in) rather than the whole rolled
        # region -- otherwise the far field sets the scale and the undulation
        # you actually see on camera shrinks to nothing.
        vals = out[hot]
        vals -= vals.mean()
        near = vals[r[hot] < cfg["dem_in"]]
        peak = np.max(np.abs(near)) if len(near) else np.max(np.abs(vals))
        out[hot] = vals / peak * cfg["undulation"] if peak > 1e-9 else 0.0
        return out

    def height(self, x, y):
        """Final scene z for flat arrays of film-space x, y."""
        cfg = self.cfg
        x = np.asarray(x, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        r = np.hypot(x, y)
        w_dem = smoothstep(cfg["dem_in"], cfg["dem_full"], r)
        # Ramp the roll in over a short --ramp so it reaches full amplitude
        # just outside the house pad. The whole acting area is only r ~ 35 m
        # (road at y -20, fence at y +27), so a lazy ramp would flatten
        # exactly the ground the camera spends the film looking at.
        w_roll = smoothstep(cfg["flat"], cfg["flat"] + cfg["ramp"], r) * (1.0 - w_dem)
        return self.dem(x, y, r) * w_dem + self.roll(x, y, r, w_roll) * w_roll


# --- mesh ------------------------------------------------------------------

def graded_axis(tiers, must_include=()):
    """Symmetric, monotonic 1D sample positions from (half_width, step) tiers.

    `must_include` forces exact sample positions into the axis, so the hole cut
    for the hand-built set lands precisely on its edge instead of near it.

    Rectilinear, so changing step between tiers cannot crack the surface.

    Uniform spacing in the FAR tier is not an oversight -- the hero mountain is
    12.5 km away, so a distance-graded far field would blur exactly the
    silhouette the final shot depends on. The fine tier instead exists to
    out-sample the ground roll: at --roll 16 m wavelength a 12.5 m grid is
    below Nyquist and aliases the undulation into noise.
    """
    pos = [0.0]
    for half, step in tiers:
        while pos[-1] < half - 1e-9:
            pos.append(min(pos[-1] + step, half))
    vals = [-p for p in reversed(pos[1:])] + pos + [float(v) for v in must_include]
    return np.unique(np.array(vals))


def build_mesh(terrain, cfg):
    tiers = [(cfg["fine"], cfg["fine_step"]),
             (cfg["mid"], cfg["mid_step"]),
             (cfg["radius"], cfg["step"])]
    hole = cfg["hole"]
    ax = graded_axis(tiers, hole[:2] if hole else ())
    ay = graded_axis(tiers, hole[2:] if hole else ())
    nx, ny = len(ax), len(ay)

    gx, gy = np.meshgrid(ax, ay, indexing="xy")
    xs, ys = gx.ravel(), gy.ravel()
    zs = terrain.height(xs, ys)

    verts = np.empty((nx * ny, 3), dtype=np.float64)
    verts[:, 0], verts[:, 1], verts[:, 2] = xs, ys, zs

    jj, ii = np.meshgrid(np.arange(ny - 1), np.arange(nx - 1), indexing="ij")
    a = jj * nx + ii
    faces = np.stack([a, a + 1, a + nx + 1, a + nx], axis=-1)

    if hole:
        # Cut out the hand-built set rather than laying a slab over it. The
        # detailed ground's top sits at exactly z=0 and so does the pad here,
        # so an overlapping slab is coplanar and z-fights -- it swallowed the
        # yard, road, fence and treeline. `ground_far` framed the set for the
        # same reason. Because `must_include` put the hole's edge exactly on
        # the axis, the frame abuts it flush with no gap and no overlap.
        hx0, hx1, hy0, hy1 = hole
        eps = 1e-6
        inside = (((ax[ii] >= hx0 - eps) & (ax[ii + 1] <= hx1 + eps)) &
                  ((ay[jj] >= hy0 - eps) & (ay[jj + 1] <= hy1 + eps)))
        faces = faces[~inside]
        used = np.unique(faces)
        remap = np.full(nx * ny, -1, dtype=np.int64)
        remap[used] = np.arange(len(used))
        faces = remap[faces]
        verts = verts[used]
        print(f"  hole x {hx0:g}..{hx1:g}, y {hy0:g}..{hy1:g} "
              f"cut for the hand-built set")
    else:
        faces = faces.reshape(-1, 4)

    print(f"  grid {nx} x {ny} -> {len(verts):,} verts, {len(faces):,} faces")

    me = bpy.data.meshes.new("terrain")
    me.from_pydata(verts.tolist(), [], faces.tolist())
    me.update()
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    me.materials.append(desert_material())
    return bpy.data.objects.new("terrain", me)


def desert_material():
    """Flat placeholder. The film's style is NOT locked (two candidates are
    still live in docs/treatment/style.md, decided by rendering a test frame),
    so this deliberately commits to nothing but a readable desert value."""
    mat = bpy.data.materials.get("terrain_desert")
    if mat:
        return mat
    mat = bpy.data.materials.new("terrain_desert")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.42, 0.33, 0.23, 1.0)
        bsdf.inputs["Roughness"].default_value = 1.0
        if "Specular IOR Level" in bsdf.inputs:
            bsdf.inputs["Specular IOR Level"].default_value = 0.15
    return mat


# --- entry point -----------------------------------------------------------

def parse_args(argv):
    cfg = {
        "out": DEFAULT_OUT, "cache": DEFAULT_CACHE,
        "lat": ANCHOR_LAT, "lon": ANCHOR_LON, "bearing": 270.0,
        "radius": 28000.0, "step": 120.0, "fine": 70.0, "fine_step": 2.0,
        "mid": 700.0, "mid_step": 20.0,
        "flat": 15.0, "ramp": 8.0, "undulation": 0.25, "roll": 16.0,
        "dem_in": 70.0, "dem_full": 900.0, "zoom": 12,
        # Footprint of the hand-built ground in property.blend (ground_yard +
        # ditch + ground_roadside). Same rect ground_far framed.
        "hole": (-45.0, 45.0, -32.0, 45.0),
    }
    floats = {"lat", "lon", "bearing", "radius", "step", "fine", "fine_step",
              "mid", "mid_step", "flat", "ramp", "undulation", "roll",
              "dem_in", "dem_full"}
    for arg in argv:
        if arg == "--keep-flat":
            cfg["undulation"] = 0.0
            continue
        if arg == "--no-hole":
            cfg["hole"] = None
            continue
        if arg.startswith("--hole="):
            cfg["hole"] = tuple(float(v) for v in arg[7:].split(","))
            if len(cfg["hole"]) != 4:
                raise SystemExit("--hole needs x0,x1,y0,y1")
            continue
        if not arg.startswith("--") or "=" not in arg:
            raise SystemExit(f"unrecognised argument: {arg}\n{__doc__}")
        key, _, val = arg[2:].partition("=")
        key = key.replace("-", "_")
        if key in ("out", "cache"):
            cfg[key] = Path(val).expanduser().resolve()
        elif key == "zoom":
            cfg[key] = int(val)
        elif key in floats:
            cfg[key] = float(val)
        else:
            raise SystemExit(f"unknown flag: --{key}\n{__doc__}")
    return cfg


def report(terrain, cfg):
    """Print the ground height under every staged position in site.md.

    Everything in the film is blocked in world space at z=0. Any non-zero
    number here is a real re-grounding cost, and it should be visible now
    rather than in a render three shots later.
    """
    xs = np.array([p[1] for p in SITE_POINTS])
    ys = np.array([p[2] for p in SITE_POINTS])
    zs = terrain.height(xs, ys)
    print("\n  ground height under the staged positions (site.md):")
    for (name, x, y), z in zip(SITE_POINTS, zs):
        flag = "" if abs(z) < 0.005 else "   <- re-ground"
        print(f"    {name:<16} ({x:6.2f}, {y:6.2f})   z = {z:+.3f}{flag}")
    worst = float(np.max(np.abs(zs)))
    print(f"  largest offset {worst:.3f} m "
          f"({'nothing to re-ground' if worst < 0.005 else 'these need dropping onto the surface'})")

    # The set sits on a real alluvial fan, so the ground around it genuinely
    # slopes. Print it rather than assume it: a steep or lopsided rise here
    # means the property is sitting in a bowl and the anchor wants moving.
    print("\n  surrounding grade (real DEM, metres above the pad):")
    print(f"    {'radius':>8}  {'N (+X)':>9} {'S (-X)':>9} "
          f"{'W (+Y)':>9} {'E (-Y)':>9}")
    for rad in (100, 300, 900, 3000, 12500):
        xs = np.array([rad, -rad, 0.0, 0.0])
        ys = np.array([0.0, 0.0, rad, -rad])
        h = terrain.height(xs, ys)
        print(f"    {rad:>7}m  {h[0]:>9.1f} {h[1]:>9.1f} {h[2]:>9.1f} {h[3]:>9.1f}")
    print("    (W is the final image: the run into the sunset)")


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    cfg = parse_args(argv)

    print(f"terrain: Palm Springs DEM at {cfg['lat']:.4f}, {cfg['lon']:.4f}")
    print(f"  bearing {cfg['bearing']:.0f} deg -> film +Y (west / the final image)")

    terrain = Terrain(cfg)
    terrain.load(cfg["radius"] * 1.05)

    ob = build_mesh(terrain, cfg)
    coll = bpy.data.collections.get("terrain") or bpy.data.collections.new("terrain")
    if coll.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(coll)
    coll.objects.link(ob)

    report(terrain, cfg)

    if bpy.app.background:
        cfg["out"].parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(cfg["out"]))
        print(f"\n  wrote {cfg['out']}")
        print("  property.blend was not opened or modified.")
    else:
        print("\n  built into the current scene. Nothing was saved -- "
              "save yourself if you like it.")


if __name__ == "__main__":
    main()
