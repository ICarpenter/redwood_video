"""Redwood scale-guide dropper.

Drops a linked instance of a cast/prop guide into the current board scene's
non-rendering guides collection, facing the board camera. Locates the project
by walking up from the open .blend (boards.blend), so enable it with a board
file open. Asset-Browser drag-drop is the manual equivalent.
"""
import sys
from pathlib import Path

import bpy

bl_info = {
    "name": "Redwood Guides",
    "author": "redwood_video",
    "version": (1, 0),
    "blender": (5, 1, 0),
    "location": "View3D > Sidebar > Redwood",
    "description": "Drop movable scale-guides into board scenes",
    "category": "Object",
}


def _project_root():
    """Walk up from the open file to a dir containing tools/ and assets/."""
    if not bpy.data.filepath:
        return None
    for p in Path(bpy.data.filepath).resolve().parents:
        if (p / "tools" / "guides.py").exists() and (p / "assets").is_dir():
            return p
    return None


def _load_guides():
    root = _project_root()
    if root is None:
        return None, None
    tools = str(root / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    import guides  # noqa: E402
    import make_boards  # noqa: E402
    return root, (guides, make_boards)


def add_guide_instance(scene, name):
    """Link guide `name` and drop a collection instance into `scene`'s guides
    collection at DROP_LOCATION. Returns the created instance object.
    Raises RuntimeError with a clear message if the project/guide can't be
    resolved.
    """
    root, mods = _load_guides()
    if mods is None:
        raise RuntimeError("Open boards.blend from the project first")
    guides_mod, make_boards = mods
    spec = guides_mod.guide_by_name(name)
    if spec is None:
        raise RuntimeError(f"Unknown guide {name}")

    make_boards.ensure_guides_collection(scene)
    gname = guides_mod.guides_collection_name(scene.name)
    gcoll = scene.collection.children.get(gname)
    if gcoll is None:
        raise RuntimeError(f"could not resolve guides collection {gname}")

    filepath = str(root / spec.file)
    linked = next((c for c in bpy.data.collections
                   if c.name == spec.name and c.library
                   and Path(c.library.filepath).name == Path(spec.file).name),
                  None)
    if linked is None:
        with bpy.data.libraries.load(filepath, link=True) as (src, dst):
            if spec.name not in src.collections:
                raise RuntimeError(f"{spec.name} not in {spec.file}")
            dst.collections = [spec.name]
        linked = dst.collections[0]

    inst = bpy.data.objects.new(spec.name, None)
    inst.instance_type = "COLLECTION"
    inst.instance_collection = linked
    inst.location = guides_mod.DROP_LOCATION
    gcoll.objects.link(inst)
    return inst


# Cache the item tuples: Blender can crash if an EnumProperty items callback
# returns strings that Python then garbage-collects. Keep a strong reference.
_ITEMS_CACHE = [("__none__", "Open a board file first", "")]


def _guide_items(self, context):
    global _ITEMS_CACHE
    root, mods = _load_guides()
    if mods is not None:
        guides_mod, _ = mods
        _ITEMS_CACHE = [(g.name, g.name.replace("_", " "), g.catalog)
                        for g in guides_mod.GUIDES]
    return _ITEMS_CACHE


class REDWOOD_OT_add_guide(bpy.types.Operator):
    bl_idname = "redwood.add_guide"
    bl_label = "Add Guide"
    bl_description = "Link the chosen guide into this scene's guides collection"
    bl_options = {"REGISTER", "UNDO"}

    guide: bpy.props.EnumProperty(name="Guide", items=_guide_items)

    def execute(self, context):
        try:
            inst = add_guide_instance(context.scene, self.guide)
        except RuntimeError as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}

        for ob in context.selected_objects:
            ob.select_set(False)
        inst.select_set(True)
        context.view_layer.objects.active = inst
        self.report({"INFO"}, f"Added {inst.name}")
        return {"FINISHED"}


class REDWOOD_PT_guides(bpy.types.Panel):
    bl_label = "Add Guide"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Redwood"

    def draw(self, context):
        col = self.layout.column()
        if _project_root() is None:
            col.label(text="Open boards.blend from the project", icon="ERROR")
            return
        col.prop(context.scene, "redwood_guide", text="")
        op = col.operator("redwood.add_guide", icon="OUTLINER_OB_EMPTY")
        op.guide = context.scene.redwood_guide


def register():
    bpy.utils.register_class(REDWOOD_OT_add_guide)
    bpy.utils.register_class(REDWOOD_PT_guides)
    bpy.types.Scene.redwood_guide = bpy.props.EnumProperty(
        name="Guide", items=_guide_items)


def unregister():
    del bpy.types.Scene.redwood_guide
    bpy.utils.unregister_class(REDWOOD_PT_guides)
    bpy.utils.unregister_class(REDWOOD_OT_add_guide)


if __name__ == "__main__":
    register()
