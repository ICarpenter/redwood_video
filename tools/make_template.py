"""Build tools/shot_template.blend with the locked project settings.

Run:
  "$BLENDER" --background --factory-startup --python-exit-code 1 \
      --python tools/make_template.py
"""
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parent.parent

scene = bpy.context.scene
scene.name = "shot"

# EEVEE's enum id differs across Blender versions; pick what this build has.
engines = {
    item.identifier
    for item in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items
}
scene.render.engine = (
    "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engines else "BLENDER_EEVEE"
)

scene.render.fps = 24
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.render.image_settings.color_depth = "16"
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "None"
scene.sync_mode = "AUDIO_SYNC"

# Empty stage: wipe factory objects, build the shot collection layout.
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
for name in ("cam", "chars", "env", "fx"):
    coll = bpy.data.collections.new(name)
    scene.collection.children.link(coll)

cam_data = bpy.data.cameras.new("cam")
cam_obj = bpy.data.objects.new("cam", cam_data)
bpy.data.collections["cam"].objects.link(cam_obj)
scene.camera = cam_obj

out = ROOT / "tools" / "shot_template.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(out), relative_remap=True)
print(f"template saved: {out}")
