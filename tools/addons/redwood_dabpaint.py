"""Redwood dab painter — one stroke carries both colour and facet.

Pick an albedo swatch and a tilt swatch, then paint. Both channels land in a
single native brush stroke, because the image you paint is not colour: it
stores R = albedo swatch index and G = tilt swatch index, and two film-wide
256x1 LUTs resolve those into the real colour and the real tangent normal.

One image is the whole point. Blender paints it and Blender undoes it, so
one Ctrl+Z takes back a dab in both channels and there is nothing that can
desync — undo is correct by construction rather than by careful engineering.
Nothing here runs during a stroke: no modal operator, no timer, no handler.
The add-on's only job while you paint is having set `brush.color` when you
clicked a swatch.

Regenerating a palette recolours every dab in the film, which is the live
variable the Ucupaint kit was meant to provide. Appending swatches is safe;
*reordering* repaints existing artwork, so the ordering hash is stored and
checked.

Design: docs/superpowers/specs/2026-08-04-tilt-dab-painter-design.md
Enable it with a file inside the project saved, so the project root is findable.
"""
import sys
from pathlib import Path

import bpy

bl_info = {
    "name": "Redwood Dab Paint",
    "author": "redwood_video",
    "version": (1, 0),
    "blender": (5, 1, 0),
    "location": "View3D > Sidebar > Redwood > Dab Paint",
    "description": "Paint albedo and tilt in one stroke, via an index map",
    "category": "Paint",
}

_previews = None
_palettes = {}


# --- project ------------------------------------------------------------------


def _project_root():
    """Walk up from the open file to a dir containing tools/ and assets/."""
    if not bpy.data.filepath:
        return None
    for p in Path(bpy.data.filepath).resolve().parents:
        if (p / "tools" / "dabpaint.py").exists() and (p / "assets").is_dir():
            return p
    return None


def _load_core():
    root = _project_root()
    if root is None:
        return None, None
    tools = str(root / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    import dabpaint  # noqa: E402
    return root, dabpaint


def palette_dir(root, which):
    return root / "assets" / "materials" / which


def load_palettes(root, dabpaint, force=False):
    """Both palettes, cached. Returns (albedo, tilt) or raises PaletteMissing."""
    if force:
        _palettes.clear()
    if not _palettes:
        _palettes["albedo"] = dabpaint.load_palette(
            palette_dir(root, dabpaint.ALBEDO_PALETTE_DIR) / "albedo_palette.json"
        )
        _palettes["tilt"] = dabpaint.load_palette(
            palette_dir(root, dabpaint.TILT_PALETTE_DIR) / "tilt_palette.json"
        )
    return _palettes["albedo"], _palettes["tilt"]


# --- material -----------------------------------------------------------------


def ensure_mcm_toon():
    """The shading group. Created flat-and-physical if it isn't in the file.

    Diffuse only, no Shader to RGB: banding was dropped 2026-08-04, which is
    what left this engine-agnostic.
    """
    group = bpy.data.node_groups.get("MCM_Toon")
    if group:
        return group
    group = bpy.data.node_groups.new("MCM_Toon", "ShaderNodeTree")
    group.interface.new_socket("Albedo", in_out="INPUT", socket_type="NodeSocketColor")
    group.interface.new_socket("Tilt Normal", in_out="INPUT", socket_type="NodeSocketVector")
    group.interface.new_socket("BSDF", in_out="OUTPUT", socket_type="NodeSocketShader")

    nin = group.nodes.new("NodeGroupInput")
    nin.location = (-300, 0)
    nout = group.nodes.new("NodeGroupOutput")
    nout.location = (300, 0)
    bsdf = group.nodes.new("ShaderNodeBsdfDiffuse")
    bsdf.location = (0, 0)
    group.links.new(nin.outputs["Albedo"], bsdf.inputs["Color"])
    group.links.new(nin.outputs["Tilt Normal"], bsdf.inputs["Normal"])
    group.links.new(bsdf.outputs["BSDF"], nout.inputs["BSDF"])
    return group


def _lut_image(path, spec):
    """Load a LUT once and keep its sampling honest on every run."""
    img = bpy.data.images.get(path.name)
    if img is None:
        img = bpy.data.images.load(str(path), check_existing=True)
    img.colorspace_settings.name = spec["colorspace"]
    return img


def _index_uv_chain(nodes, links, channel_out, x, y):
    """channel value -> the centre of its LUT texel, as a UV vector.

    The multiply-add turns an exact i/255 texel into (i+0.5)/256. Landing
    off-centre bleeds a swatch into its neighbour, silently.
    """
    mul = nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = 255.0 / 256.0
    mul.location = (x, y)
    add = nodes.new("ShaderNodeMath")
    add.operation = "ADD"
    add.inputs[1].default_value = 0.5 / 256.0
    add.location = (x + 180, y)
    combine = nodes.new("ShaderNodeCombineXYZ")
    combine.inputs["Y"].default_value = 0.5
    combine.location = (x + 360, y)
    links.new(channel_out, mul.inputs[0])
    links.new(mul.outputs[0], add.inputs[0])
    links.new(add.outputs[0], combine.inputs["X"])
    return combine.outputs["Vector"]


def build_material(obj, index_image, albedo_lut, tilt_lut, dabpaint):
    """Wire index map -> both LUTs -> MCM_Toon. Idempotent: rebuilds the tree."""
    mat = obj.active_material
    if mat is None:
        mat = bpy.data.materials.new(f"MCM_{obj.name}")
        obj.data.materials.append(mat)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    nodes, links = nt.nodes, nt.links

    tex = nodes.new("ShaderNodeTexImage")
    tex.image = index_image
    tex.interpolation = dabpaint.INDEX_MAP_SPEC["interpolation"]
    tex.extension = "EXTEND"
    tex.location = (-900, 0)
    tex.label = "dab index map"

    sep = nodes.new("ShaderNodeSeparateColor")
    sep.location = (-620, 0)
    links.new(tex.outputs["Color"], sep.inputs["Color"])

    a_uv = _index_uv_chain(nodes, links, sep.outputs["Red"], -440, 200)
    a_tex = nodes.new("ShaderNodeTexImage")
    a_tex.image = albedo_lut
    a_tex.interpolation = dabpaint.ALBEDO_LUT_SPEC["interpolation"]
    a_tex.extension = "EXTEND"
    a_tex.location = (0, 200)
    a_tex.label = "albedo LUT"
    links.new(a_uv, a_tex.inputs["Vector"])

    t_uv = _index_uv_chain(nodes, links, sep.outputs["Green"], -440, -220)
    t_tex = nodes.new("ShaderNodeTexImage")
    t_tex.image = tilt_lut
    t_tex.interpolation = dabpaint.TILT_LUT_SPEC["interpolation"]
    t_tex.extension = "EXTEND"
    t_tex.location = (0, -220)
    t_tex.label = "tilt LUT"
    links.new(t_uv, t_tex.inputs["Vector"])

    nmap = nodes.new("ShaderNodeNormalMap")
    nmap.location = (280, -220)
    links.new(t_tex.outputs["Color"], nmap.inputs["Color"])

    grp = nodes.new("ShaderNodeGroup")
    grp.node_tree = ensure_mcm_toon()
    grp.location = (560, 0)
    links.new(a_tex.outputs["Color"], grp.inputs["Albedo"])
    links.new(nmap.outputs["Normal"], grp.inputs["Tilt Normal"])

    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (800, 0)
    links.new(grp.outputs["BSDF"], out.inputs["Surface"])
    return mat


def ensure_index_map(stem, size, albedo_index, tilt_index, dabpaint, directory=None):
    """The paint target: 8-bit, Non-Color, filled with the current selection.

    Starting filled (rather than black) means the surface reads as a flat
    coat of the chosen swatch before the first dab, instead of index 0.
    """
    name = dabpaint.index_map_name(stem)
    img = bpy.data.images.get(name)
    if img is None or tuple(img.size) != (size, size):
        if img:
            bpy.data.images.remove(img)
        img = bpy.data.images.new(name, size, size, alpha=False, float_buffer=False)
    img.colorspace_settings.name = dabpaint.INDEX_MAP_SPEC["colorspace"]
    texel = list(dabpaint.brush_color_for(albedo_index, tilt_index)) + [1.0]
    img.pixels.foreach_set(texel * (size * size))
    img.update()
    if directory is not None:
        img.filepath_raw = str(Path(directory) / name)
        img.file_format = "PNG"
    return img


# --- operators ----------------------------------------------------------------


class DAB_OT_make_paintable(bpy.types.Operator):
    bl_idname = "redwood.dab_make_paintable"
    bl_label = "Make Paintable"
    bl_description = "Create or heal this object's dab index map and material"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = context.active_object
        root, dabpaint = _load_core()
        if root is None:
            self.report({"ERROR"}, "Save this file inside the project first")
            return {"CANCELLED"}
        if obj is None or obj.type != "MESH":
            self.report({"ERROR"}, "Select a mesh")
            return {"CANCELLED"}
        if not obj.data.uv_layers:
            self.report({"ERROR"}, "Object has no UV layer — there is nowhere to paint")
            return {"CANCELLED"}
        try:
            albedo, tilt = load_palettes(root, dabpaint, force=True)
        except dabpaint.PaletteMissing as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}

        scene = context.scene
        mat_name = obj.active_material.name if obj.active_material else None
        stem = dabpaint.asset_stem(mat_name, obj.name)
        size = int(scene.redwood_dab_resolution)
        img = ensure_index_map(
            stem, size, scene.redwood_dab_albedo, scene.redwood_dab_tilt, dabpaint
        )
        a_lut = _lut_image(
            palette_dir(root, dabpaint.ALBEDO_PALETTE_DIR) / "albedo_lut.png",
            dabpaint.ALBEDO_LUT_SPEC,
        )
        t_lut = _lut_image(
            palette_dir(root, dabpaint.TILT_PALETTE_DIR) / "tilt_lut.png",
            dabpaint.TILT_LUT_SPEC,
        )
        build_material(obj, img, a_lut, t_lut, dabpaint)

        scene.redwood_dab_albedo_hash = albedo.ordering_hash
        scene.redwood_dab_tilt_hash = tilt.ordering_hash
        _apply_brush(context, dabpaint, scene.redwood_dab_albedo, scene.redwood_dab_tilt)
        self.report({"INFO"}, f"{stem} paintable at {size}px")
        return {"FINISHED"}


def _apply_brush(context, dabpaint, albedo_index, tilt_index):
    """Set the brush to carry this (albedo, tilt) pair, hard-edged.

    A dab is one flat facet, not a soft blob: soft falloff produces gradients
    between indices, which decode as unrelated swatches at the edge.
    """
    colour = dabpaint.brush_color_for(albedo_index, tilt_index)
    settings = getattr(context.tool_settings, "image_paint", None)
    brush = getattr(settings, "brush", None) if settings else None
    if brush is None:
        return False
    brush.color = colour
    brush.strength = 1.0
    brush.blend = "MIX"
    if hasattr(brush, "curve_preset"):
        brush.curve_preset = "CONSTANT"
    return True


class _SetSwatch(bpy.types.Operator):
    """Shared behaviour for the two swatch pickers.

    `swatch` is declared on each concrete subclass rather than here, so
    registration never depends on `__annotations__` being found through the
    MRO — that lookup is a Python-version-sensitive footgun, and the failure
    would be a silently dead panel rather than an error.
    """

    bl_options = {"REGISTER", "UNDO"}
    channel = None  # "albedo" | "tilt"

    def execute(self, context):
        root, dabpaint = _load_core()
        if root is None:
            self.report({"ERROR"}, "Save this file inside the project first")
            return {"CANCELLED"}
        try:
            albedo, tilt = load_palettes(root, dabpaint)
        except dabpaint.PaletteMissing as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}
        palette = albedo if self.channel == "albedo" else tilt
        scene = context.scene
        try:
            index = palette.index_of(self.swatch)
        except KeyError as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}
        if self.channel == "albedo":
            scene.redwood_dab_albedo = index
            scene.redwood_dab_albedo_name = self.swatch
        else:
            scene.redwood_dab_tilt = index
            scene.redwood_dab_tilt_name = self.swatch
        _apply_brush(context, dabpaint, scene.redwood_dab_albedo, scene.redwood_dab_tilt)
        return {"FINISHED"}


class DAB_OT_set_albedo(_SetSwatch):
    bl_idname = "redwood.dab_set_albedo"
    bl_label = "Set Albedo Swatch"
    channel = "albedo"
    swatch: bpy.props.StringProperty()


class DAB_OT_set_tilt(_SetSwatch):
    bl_idname = "redwood.dab_set_tilt"
    bl_label = "Set Tilt Swatch"
    channel = "tilt"
    swatch: bpy.props.StringProperty()


class DAB_OT_bake(bpy.types.Operator):
    bl_idname = "redwood.dab_bake"
    bl_label = "Bake to PNG"
    bl_description = "Write real albedo and tilt PNGs beside the index map"
    bl_options = {"REGISTER"}

    def execute(self, context):
        obj = context.active_object
        root, dabpaint = _load_core()
        if root is None or obj is None:
            self.report({"ERROR"}, "Save this file inside the project, and select a mesh")
            return {"CANCELLED"}
        try:
            albedo, tilt = load_palettes(root, dabpaint)
        except dabpaint.PaletteMissing as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}
        mat_name = obj.active_material.name if obj.active_material else None
        stem = dabpaint.asset_stem(mat_name, obj.name)
        src = bpy.data.images.get(dabpaint.index_map_name(stem))
        if src is None:
            self.report({"ERROR"}, "No index map — run Make Paintable first")
            return {"CANCELLED"}

        written = bake_index_map(src, stem, albedo, tilt, dabpaint, Path(bpy.path.abspath("//")))
        self.report({"INFO"}, f"baked {', '.join(p.name for p in written)}")
        return {"FINISHED"}


def bake_index_map(src, stem, albedo, tilt, dabpaint, directory):
    """Resolve the index map through both LUTs into two real images.

    The index map stays authoritative — this is for when another tool or a
    final render wants ordinary textures. It does not alter the material.
    """
    width, height = src.size
    buf = [0.0] * (width * height * 4)
    src.pixels.foreach_get(buf)
    a_lut = albedo.rgb8_in_lut_order()
    t_lut = tilt.rgb8_in_lut_order()

    a_px = [0.0] * (width * height * 4)
    t_px = [0.0] * (width * height * 4)
    for i in range(width * height):
        ai = dabpaint.indices_from_texels(
            (round(buf[4 * i] * 255), round(buf[4 * i + 1] * 255), 0)
        )
        a_rgb = a_lut[ai[0]] if ai[0] < len(a_lut) else (0, 0, 0)
        t_rgb = t_lut[ai[1]] if ai[1] < len(t_lut) else (128, 128, 255)
        a_px[4 * i : 4 * i + 4] = [c / 255 for c in a_rgb] + [1.0]
        t_px[4 * i : 4 * i + 4] = [c / 255 for c in t_rgb] + [1.0]

    written = []
    for name, px, spec in (
        (dabpaint.baked_albedo_name(stem), a_px, dabpaint.ALBEDO_LUT_SPEC),
        (dabpaint.baked_tilt_name(stem), t_px, dabpaint.TILT_LUT_SPEC),
    ):
        img = bpy.data.images.get(name)
        if img is None or tuple(img.size) != (width, height):
            if img:
                bpy.data.images.remove(img)
            img = bpy.data.images.new(name, width, height, alpha=False, float_buffer=False)
        img.colorspace_settings.name = spec["colorspace"]
        img.pixels.foreach_set(px)
        img.filepath_raw = str(Path(directory) / name)
        img.file_format = "PNG"
        img.save()
        written.append(Path(directory) / name)
    return written


# --- panel --------------------------------------------------------------------


class VIEW3D_PT_redwood_dabpaint(bpy.types.Panel):
    bl_label = "Dab Paint"
    bl_idname = "VIEW3D_PT_redwood_dabpaint"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Redwood"

    def draw(self, context):
        layout = self.layout
        root, dabpaint = _load_core()
        if root is None:
            layout.label(text="Save this file inside the project", icon="ERROR")
            return
        try:
            albedo, tilt = load_palettes(root, dabpaint)
        except dabpaint.PaletteMissing as e:
            col = layout.column(align=True)
            col.label(text="Palette missing", icon="ERROR")
            for line in str(e).split(" — "):
                col.label(text=line)
            return

        scene = context.scene
        layout.operator(DAB_OT_make_paintable.bl_idname, icon="BRUSH_DATA")
        layout.prop(scene, "redwood_dab_resolution", text="Size")

        for label, palette, stored, name_prop, op in (
            ("Albedo", albedo, scene.redwood_dab_albedo_hash,
             scene.redwood_dab_albedo_name, DAB_OT_set_albedo),
            ("Tilt", tilt, scene.redwood_dab_tilt_hash,
             scene.redwood_dab_tilt_name, DAB_OT_set_tilt),
        ):
            box = layout.box()
            box.label(text=label)
            if palette.has_drifted(stored):
                box.label(text="palette reordered — dabs now decode wrong", icon="ERROR")
            box.label(text=f"selected: {name_prop or palette.ordering[0]}")
            grid = box.grid_flow(columns=8, even_columns=True, even_rows=True)
            for swatch in palette.ordering:
                icon_id = _icon_for(root, dabpaint, label.lower(), swatch)
                o = grid.operator(op.bl_idname, text="", icon_value=icon_id)
                o.swatch = swatch

        layout.operator(DAB_OT_bake.bl_idname, icon="FILE_IMAGE")


def _icon_for(root, dabpaint, channel, swatch):
    """Swatch icon from the generated PNGs. Blender's native palette widget
    can't be used: it writes the swatch's *display colour* to brush.color,
    but the brush has to carry an index encoding."""
    if _previews is None:
        return 0
    key = f"{channel}:{swatch}"
    if key in _previews:
        return _previews[key].icon_id
    which = dabpaint.ALBEDO_PALETTE_DIR if channel == "albedo" else dabpaint.TILT_PALETTE_DIR
    path = palette_dir(root, which) / "swatches" / f"{swatch}.png"
    if not path.exists():
        return 0
    return _previews.load(key, str(path), "IMAGE").icon_id


# --- registration -------------------------------------------------------------

_CLASSES = (
    DAB_OT_make_paintable,
    DAB_OT_set_albedo,
    DAB_OT_set_tilt,
    DAB_OT_bake,
    VIEW3D_PT_redwood_dabpaint,
)


def register():
    global _previews
    import bpy.utils.previews

    _previews = bpy.utils.previews.new()
    # Scene properties, not ID custom properties, so selection participates in
    # undo — an undo restores the swatch and the brush colour together.
    bpy.types.Scene.redwood_dab_albedo = bpy.props.IntProperty(default=0, min=0, max=255)
    bpy.types.Scene.redwood_dab_tilt = bpy.props.IntProperty(default=0, min=0, max=255)
    bpy.types.Scene.redwood_dab_albedo_name = bpy.props.StringProperty(default="")
    bpy.types.Scene.redwood_dab_tilt_name = bpy.props.StringProperty(default="")
    bpy.types.Scene.redwood_dab_albedo_hash = bpy.props.StringProperty(default="")
    bpy.types.Scene.redwood_dab_tilt_hash = bpy.props.StringProperty(default="")
    bpy.types.Scene.redwood_dab_resolution = bpy.props.EnumProperty(
        items=[(str(r), f"{r}", f"{r}x{r}") for r in (1024, 2048, 4096)],
        default="2048",
    )
    for cls in _CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    global _previews
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
    for prop in (
        "redwood_dab_albedo", "redwood_dab_tilt",
        "redwood_dab_albedo_name", "redwood_dab_tilt_name",
        "redwood_dab_albedo_hash", "redwood_dab_tilt_hash",
        "redwood_dab_resolution",
    ):
        if hasattr(bpy.types.Scene, prop):
            delattr(bpy.types.Scene, prop)
    if _previews is not None:
        bpy.utils.previews.remove(_previews)
        _previews = None


if __name__ == "__main__":
    register()
