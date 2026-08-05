"""What is actually in the index map? Paste into Blender's Python console.

Reports every distinct (albedo, tilt) pair painted into the active dab index
map and what each resolves to, plus what the brush is currently carrying.

A pair that reports OUT OF PALETTE is the signature of the encoding being
corrupted between brush.color and the stored texel — those indices land in
the LUT's black tail, so the dab renders black.

    exec(open("/Users/icarpenter/blender/redwood_video/tools/tests/"
              "decode_dabindex.py").read())
"""
import sys
from collections import Counter
from pathlib import Path

import bpy

ROOT = Path("/Users/icarpenter/blender/redwood_video")
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))
import dabpaint  # noqa: E402

albedo = dabpaint.load_palette(ROOT / "assets/materials/albedo_palette/albedo_palette.json")
tilt = dabpaint.load_palette(ROOT / "assets/materials/tilt_palette/tilt_palette.json")

canvas = bpy.context.tool_settings.image_paint.canvas
print(f"canvas: {canvas.name if canvas else None}")

img = canvas if canvas else next(
    i for i in bpy.data.images if i.name.endswith("_dabindex.png")
)
w, h = img.size
px = [0.0] * (w * h * 4)
img.pixels.foreach_get(px)

pairs = Counter(
    (round(px[i] * 255), round(px[i + 1] * 255)) for i in range(0, len(px), 4)
)


def describe(palette, index, label):
    if index >= len(palette):
        return f"{label} {index} OUT OF PALETTE (renders black; max {len(palette) - 1})"
    return f"{label} {index} = {palette.name_at(index)}"


print(f"\n{img.name} — {len(pairs)} distinct pair(s):")
for (a, t), count in pairs.most_common():
    share = 100.0 * count / (w * h)
    print(f"  ({a:3d}, {t:3d})  {share:5.1f}%   "
          f"{describe(albedo, a, 'albedo')} | {describe(tilt, t, 'tilt')}")

brush = bpy.context.tool_settings.image_paint.brush
r, g = brush.color[0], brush.color[1]
print(f"\nbrush.color -> ({r:.6f}, {g:.6f})")
print(f"  encodes albedo {round(r * 255)}, tilt {round(g * 255)}")
print(f"  scene selection: albedo {bpy.context.scene.redwood_dab_albedo}, "
      f"tilt {bpy.context.scene.redwood_dab_tilt}")
print("\nIf a painted pair does not match the brush pair, the stroke is not "
      "writing what the brush carries — that is the encoding bug.")
