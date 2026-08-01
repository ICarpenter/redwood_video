"""Redwood scale-guide dropper.

Drops a linked instance of a cast/prop guide into the current layout scene's
per-shot `<code>_blocking` collection, feet on the ground where the camera is
looking: the camera's view ray is cast onto the property's z=0 ground plane,
so the guide lands at a real place on the set rather than a fixed spot in a
picture. Guides are authored facing -Y; a drop does not rotate them, the
artist turns them by hand. Locates the project by walking up from the open
.blend (layout.blend), so enable it with a layout file open. Asset-Browser
drag-drop is the manual equivalent.

The property set is deliberately NOT offered here: it is linked at identity
in every layout scene already (invariant 1 — the property never moves), and
a second instance dropped as "just another guide" cannot be told apart from
staged blocking by any later heal pass, so it survives forever. To frame a
wide establishing shot, move the *camera* instead (invariant 2).
"""
import sys
from pathlib import Path

import bpy
import mathutils

bl_info = {
    "name": "Redwood Guides",
    "author": "redwood_video",
    "version": (1, 0),
    "blender": (5, 1, 0),
    "location": "View3D > Sidebar > Redwood",
    "description": "Drop movable scale-guides into layout scenes, on the ground",
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
    import make_layout  # noqa: E402
    return root, (guides, make_layout)


def ground_drop_location(scene):
    """Where the camera is looking, on the ground.

    Guides are authored feet-at-z=0, and the property's ground IS z=0, so
    intersecting the camera's view ray with that plane drops a character
    exactly where they would stand. If the camera is level or tilted up the
    ray never meets the ground — fall back to DROP_DISTANCE along the view
    ray, flattened to z=0.

    Reads matrix_basis, not matrix_world. matrix_world is a depsgraph-
    evaluated cache that can be stale in --background mode until the scene
    has been evaluated (e.g. frame_set() has run) — a real trap for a scene
    built entirely in-script with no such call, which is exactly how
    check_addon.py's ground-drop check constructs its camera. matrix_basis
    is composed live from location/rotation/scale on every read, sidestepping
    that cache — safe in both the add-on's live interactive context and this
    headless one.

    matrix_basis ignores parenting AND constraints (see migrate_layout.py's
    solve_camera for the same tradeoff spelled out the other way — it uses
    the scene's depsgraph specifically because it needs both folded in).
    Neither exists on any layout camera today (checked: cameras are
    top-level objects; only the script-prompt note is ever parented, and
    always TO the camera, never the reverse), so matrix_basis is exactly
    equal to a correctly-evaluated matrix_world here. If a future camera
    rig adds a parent (e.g. a dolly empty) or a constraint (e.g. Track To),
    this needs to go back to an evaluated matrix_world instead — via the
    target scene's own depsgraph (scene.view_layers[0].depsgraph, after
    something has built it), not bpy.context's, which may be a different
    scene entirely.
    """
    root, mods = _load_guides()
    guides_mod = mods[0] if mods else None
    distance = guides_mod.DROP_DISTANCE if guides_mod else 8.0

    cam = scene.camera
    if cam is None:
        return (0.0, 0.0, 0.0)
    basis = cam.matrix_basis
    origin = basis.translation
    forward = (basis.to_quaternion()
               @ mathutils.Vector((0.0, 0.0, -1.0)))
    if forward.z < -1e-4:
        t = -origin.z / forward.z
        if 0.0 < t < 1000.0:
            hit = origin + forward * t
            return (hit.x, hit.y, 0.0)
    flat = mathutils.Vector((forward.x, forward.y, 0.0))
    if flat.length < 1e-6:
        return (origin.x, origin.y, 0.0)
    hit = origin + flat.normalized() * distance
    return (hit.x, hit.y, 0.0)


def add_guide_instance(scene, name):
    """Link guide `name` and drop a collection instance into `scene`'s
    blocking collection, feet on the ground where the camera is looking.
    Returns the created instance object. Raises RuntimeError with a clear
    message if the project/guide can't be resolved.
    """
    root, mods = _load_guides()
    if mods is None:
        raise RuntimeError("Open layout.blend from the project first")
    guides_mod, make_layout = mods
    if name == guides_mod.SET_GUIDE.name:
        raise RuntimeError(
            "the property is linked at identity in every layout scene "
            "already and must never be instanced again — pull the camera "
            "back to frame a wide shot instead"
        )
    spec = guides_mod.guide_by_name(name)
    if spec is None:
        raise RuntimeError(f"Unknown guide {name}")

    make_layout.ensure_blocking_collection(scene)
    gname = guides_mod.blocking_collection_name(scene.name)
    gcoll = scene.collection.children.get(gname)
    if gcoll is None:
        raise RuntimeError(f"could not resolve blocking collection {gname}")

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
    inst.location = ground_drop_location(scene)
    gcoll.objects.link(inst)
    return inst


# Cache the item tuples: Blender can crash if an EnumProperty items callback
# returns strings that Python then garbage-collects. Keep a strong reference.
_ITEMS_CACHE = [("__none__", "Open a layout file first", "")]


def _guide_items(self, context):
    global _ITEMS_CACHE
    root, mods = _load_guides()
    if mods is not None:
        guides_mod, _ = mods
        # GUIDES (cast + props) only, never DROPPABLE — the property is
        # linked at identity in every layout scene and must not be offered
        # as something to drop in. See the module docstring.
        _ITEMS_CACHE = [(g.name, g.name.replace("_", " "), g.catalog)
                        for g in guides_mod.GUIDES]
    return _ITEMS_CACHE


class REDWOOD_OT_add_guide(bpy.types.Operator):
    bl_idname = "redwood.add_guide"
    bl_label = "Add Guide"
    bl_description = "Link the chosen guide into this scene's blocking collection"
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
            col.label(text="Open layout.blend from the project", icon="ERROR")
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
