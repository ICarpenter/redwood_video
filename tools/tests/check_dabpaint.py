"""Headless acceptance for the dab painter: does an index actually resolve?

Write index i into the paint target, render, and assert the rendered pixel is
swatch i. This is the test that would have caught every bug hit on
2026-08-04 — the Bump-vs-Normal-Map slot, the black stroke fringe, the sRGB
corruption — because it checks the whole chain end to end against a known
value instead of checking any one link.

It builds its own scene from factory startup and never opens or writes a
repo .blend, so it is safe to run while Blender is open elsewhere.

Run: blender --background --factory-startup --python-exit-code 1 \
       --python tools/tests/check_dabpaint.py
"""
import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "addons"))

import dabpaint  # noqa: E402
import redwood_dabpaint as addon  # noqa: E402

FAILURES = []


def check(label, condition, detail=""):
    if condition:
        print(f"  ok   {label}")
    else:
        print(f"  FAIL {label} {detail}")
        FAILURES.append(f"{label} {detail}")


def flat_plane():
    """A UV-unwrapped plane filling an orthographic camera."""
    bpy.ops.mesh.primitive_plane_add(size=2)
    obj = bpy.context.active_object
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.uv.smart_project()
    bpy.ops.object.mode_set(mode="OBJECT")
    return obj


def emissive_readback(mat, lut_socket_node):
    """Swap the shading group for pure emission of the LUT colour.

    The acceptance question is 'did index i resolve to swatch i', not 'is the
    lighting right'. Emission plus a Standard view transform makes the
    rendered pixel the swatch value itself, so a mismatch is unambiguous.
    """
    nt = mat.node_tree
    for n in list(nt.nodes):
        if n.type == "GROUP":
            nt.nodes.remove(n)
    emit = nt.nodes.new("ShaderNodeEmission")
    emit.inputs["Strength"].default_value = 1.0
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    nt.links.new(lut_socket_node.outputs["Color"], emit.inputs["Color"])
    nt.links.new(emit.outputs["Emission"], out.inputs["Surface"])


def render_centre_pixel(scene):
    bpy.ops.render.render()
    img = bpy.data.images["Render Result"]
    # Render Result pixels are not directly readable; round-trip via a file.
    out = Path(bpy.app.tempdir) / "dabcheck.png"
    img.save_render(str(out))
    loaded = bpy.data.images.load(str(out))
    loaded.colorspace_settings.name = "Non-Color"
    w, h = loaded.size
    px = [0.0] * (w * h * 4)
    loaded.pixels.foreach_get(px)
    i = ((h // 2) * w + (w // 2)) * 4
    result = tuple(round(c * 255) for c in px[i : i + 3])
    bpy.data.images.remove(loaded)
    return result


def main():
    print("dabpaint acceptance")

    # Factory startup ships a cube at the origin — it sits exactly where the
    # test plane goes and the camera renders *it* instead, giving a constant
    # grey for every index. Start genuinely empty.
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # --- the add-on registers at all -----------------------------------------
    try:
        addon.register()
        registered = True
    except Exception as e:  # noqa: BLE001 - the point is to report it
        registered = False
        print(f"  register() raised: {e!r}")
    check("add-on registers", registered)
    if registered:
        check("operators are available",
              all(hasattr(bpy.ops.redwood, op) for op in
                  ("dab_make_paintable", "dab_set_albedo", "dab_set_tilt", "dab_bake")))
        check("selection lives on the Scene so it participates in undo",
              hasattr(bpy.types.Scene, "redwood_dab_albedo")
              and hasattr(bpy.types.Scene, "redwood_dab_tilt"))
        # The panel passes the swatch name through the operator, so if that
        # property fails to register every click silently does nothing.
        # Ask the *operator's* RNA — a class's own bl_rna does not report
        # operator properties and reads as an empty dead panel when it is fine.
        for op in ("dab_set_albedo", "dab_set_tilt"):
            props = getattr(bpy.ops.redwood, op).get_rna_type().properties.keys()
            check(f"{op} takes a swatch name", "swatch" in props, str(list(props)))

    albedo = dabpaint.load_palette(
        ROOT / "assets/materials/albedo_palette/albedo_palette.json"
    )
    tilt = dabpaint.load_palette(
        ROOT / "assets/materials/tilt_palette/tilt_palette.json"
    )
    check("palettes load", len(albedo) == 90 and len(tilt) == 49,
          f"albedo={len(albedo)} tilt={len(tilt)}")

    scene = bpy.context.scene
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = scene.render.resolution_y = 64
    scene.render.filter_size = 0.0
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.display_settings.display_device = "sRGB"

    bpy.ops.object.camera_add(location=(0, 0, 5))
    cam = bpy.context.active_object
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 1.0
    scene.camera = cam

    obj = flat_plane()
    a_lut = addon._lut_image(
        ROOT / "assets/materials/albedo_palette/albedo_lut.png",
        dabpaint.ALBEDO_LUT_SPEC,
    )
    t_lut = addon._lut_image(
        ROOT / "assets/materials/tilt_palette/tilt_lut.png",
        dabpaint.TILT_LUT_SPEC,
    )

    # --- the index map is what we claim it is --------------------------------
    stem = dabpaint.asset_stem("MCM_Check", obj.name)
    img = addon.ensure_index_map(stem, 64, 0, 0, dabpaint)
    check("index map is 8-bit", not img.is_float, f"is_float={img.is_float}")
    check("index map is Non-Color",
          img.colorspace_settings.name == "Non-Color",
          img.colorspace_settings.name)

    mat = addon.build_material(obj, img, a_lut, t_lut, dabpaint)
    tex_nodes = [n for n in mat.node_tree.nodes if n.type == "TEX_IMAGE"]
    check("three image textures wired", len(tex_nodes) == 3, f"got {len(tex_nodes)}")
    check("all sampled Closest",
          all(n.interpolation == "Closest" for n in tex_nodes),
          str([n.interpolation for n in tex_nodes]))
    nmap = [n for n in mat.node_tree.nodes if n.type == "NORMAL_MAP"]
    check("tilt goes through a Normal Map node, not Bump", len(nmap) == 1)

    # --- the end-to-end promise ----------------------------------------------
    a_tex = next(n for n in tex_nodes if n.label == "albedo LUT")
    emissive_readback(mat, a_tex)

    probes = [0, 1, 42, len(albedo) - 1]
    for index in probes:
        name = albedo.name_at(index)
        expected = tuple(albedo.swatch(name)["rgb8"])
        addon.ensure_index_map(stem, 64, index, 0, dabpaint)
        got = render_centre_pixel(scene)
        delta = max(abs(a - b) for a, b in zip(got, expected))
        check(f"index {index} renders as {name} {expected}", delta <= 1,
              f"got {got}, delta {delta}")

    # --- the tilt channel is independent of the albedo channel ---------------
    addon.ensure_index_map(stem, 64, 42, 7, dabpaint)
    px = [0.0] * (64 * 64 * 4)
    img = bpy.data.images[dabpaint.index_map_name(stem)]
    img.pixels.foreach_get(px)
    got = dabpaint.indices_from_texels(
        (round(px[0] * 255), round(px[1] * 255), round(px[2] * 255))
    )
    check("both channels survive independently", got == (42, 7), f"got {got}")

    if registered:
        try:
            addon.unregister()
            check("add-on unregisters cleanly", True)
        except Exception as e:  # noqa: BLE001
            check("add-on unregisters cleanly", False, repr(e))

    if FAILURES:
        print(f"\n{len(FAILURES)} FAILED")
        for f in FAILURES:
            print(f"  {f}")
        sys.exit(1)
    print("\nDABPAINT CHECK OK")


main()
