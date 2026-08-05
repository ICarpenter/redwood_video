"""Does a brush stroke store the byte the brush carries? One controlled test.

Sets the brush to a known index pair using the *current* (uncompensated)
encoding, then asks for a stroke. What lands in the map distinguishes the two
candidate explanations for black dabs:

    stored (10, 5)   -> the stroke is faithful; black dabs are something else
    stored (56, 38)  -> Blender sRGB-encodes on write despite the image being
                        Non-Color, and brush.color has to pre-compensate

Anything else is a third mechanism and the printed numbers say what it is.

    exec(open("/Users/icarpenter/blender/redwood_video/tools/tests/"
              "probe_encoding.py").read())
"""
import sys
from pathlib import Path

import bpy

ROOT = Path("/Users/icarpenter/blender/redwood_video")
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))
import dabpaint  # noqa: E402

ALBEDO_PROBE = 10
TILT_PROBE = 5

brush = bpy.context.tool_settings.image_paint.brush
brush.color = dabpaint.brush_color_for(ALBEDO_PROBE, TILT_PROBE)
brush.strength = 1.0
brush.blend = "MIX"

canvas = bpy.context.tool_settings.image_paint.canvas
print(f"canvas:      {canvas.name if canvas else 'NONE — run Make Paintable'}")
print(f"brush.color: {tuple(round(c, 6) for c in brush.color[:3])}")
print(f"carrying:    albedo {ALBEDO_PROBE}, tilt {TILT_PROBE}")
print()
print("Now paint ONE stroke somewhere clean, then run:")
print('  exec(open("' + str(ROOT / "tools/tests/decode_dabindex.py") + '").read())')
print()
print(f"  ({ALBEDO_PROBE:3d}, {TILT_PROBE:3d})  -> stroke is faithful")
print(f"  ( 56,  38)  -> sRGB encode on write; I pre-compensate brush.color")
