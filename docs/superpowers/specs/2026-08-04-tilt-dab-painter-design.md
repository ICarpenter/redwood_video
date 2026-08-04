# Tilt-dab painter add-on — design

**Date:** 2026-08-04 · **Branch:** animatic-sq060-sq090 · **Status:** approved, ready to plan

## Problem

The MCM candidate's shading technique is **tangent-space tilt dabs**
(`docs/treatment/style-midcentury-print.md`): each brush dab is one flat facet
of paint carrying *both* a colour and a surface tilt. Normals follow albedo
exactly — a dab is one unit. If colour boundaries and facet boundaries don't
coincide, the surface stops reading as hand-laid gouache.

Blender cannot natively paint two images with one stroke. Every workaround
tried on 2026-08-04 failed on ergonomics or on undo:

- **Two images painted in separate passes.** The treatment's own fallback
  ("escalation path 1"). Rejected: dab boundaries don't coincide, which defeats
  the technique.
- **Ucupaint layer-pair kit.** Confirmed working — one stroke drives a Color
  override and a Normal override through the same mask. Rejected on layer
  count: a layer per (albedo × tilt) pair means a layer switch before *every
  dab*, forcing pass-based painting rather than freeform work. Also could not
  be built by script (see "Why not" below).
- **Scratch image + auto-commit operator.** A modal timer stamped a scratch
  into both maps on stroke end. Rejected: incomprehensible in use, and it wrote
  pixels behind Blender's back, so undo desynced the two maps silently. It also
  outlined every stroke in black, because the scratch's black base bled into
  antialiased dab edges and was committed as albedo.

The requirement, stated by Ian:

> Select albedo colour, select tilt colour, then paint to two images
> simultaneously with same brush and stroke. Change colour and/or tilt then
> paint to the same set of images. Palettes available for both channels for easy
> switching. Albedo and tilt fully independent. Tilt colour constrained to a
> valid normal map palette.

Plus one hard constraint: **Ctrl+Z must work properly** — one press undoes a
dab in both channels, cleanly, every time.

## Goals

- One native brush stroke sets both an albedo colour and a tilt normal.
- Albedo and tilt fully independent: any swatch with any swatch.
- Two palettes, freeform selection, no legality enforcement.
- Tilt values can only ever be legal tangent-space normals.
- Undo correct **by construction**, not by careful engineering.
- Per-asset setup automated — colorspace and interpolation mistakes fail
  silently and must not be hand-managed.
- Regenerable palettes; retuning a palette repaints nothing.

## Non-goals

- **No family legality.** The `diecast` / `characters` / `stucco` tier
  restrictions are not enforced, and the corresponding rule should be deleted
  from `style-midcentury-print.md` rather than left claiming a constraint the
  tool ignores. Ian: *"the categories like diecast don't apply to MCM… freeform,
  lets me make artistic choices on the spot and experiment."*
- No palette *generation logic inside the add-on*. The add-on only reads
  generated artifacts. `tools/albedo_palette.py` is in scope for this project,
  but as a standalone CLI generator matching `tilt_palette.py`.
- No Ucupaint dependency. Ucupaint stays installed and is still the right tool
  for layered region work; it is not this painter.
- No custom brush engine. Blender's projection painting is used unmodified.
- No code running during a stroke — no modal operator, no timer, no handler.

## Conventions (the load-bearing decisions)

**One painted image, two index channels.** The paint target stores
`R = albedo swatch index`, `G = tilt swatch index`, both 0–255. Any R with any G
is valid, so independence needs no bookkeeping and there is no pair table.

**Undo is structural.** There is exactly one image, Blender paints it, Blender
undoes it. Nothing can desync because there is nothing to keep in sync. This is
the reason for the whole design.

**LUTs are film-wide, not per-asset.** Two 256×1 images
(`albedo_lut.png` sRGB, `tilt_lut.png` Non-Color) are shared by every asset.
Regenerating a palette recolours every dab in the film — the "one hand paints
the movie" property extended from tilt to colour, and the live-variable
behaviour the Ucupaint kit was meant to provide.

**Palette *ordering* is append-only; palette *values* stay editable forever.**
Index 8 means "whatever sits at LUT position 8", so reordering invalidates every
painted pixel. New swatches append. The add-on stores a hash of the ordering and
warns on mismatch.

**LUT ordering is by perceptual similarity.** Neighbouring indices should be
near-neighbours in colour, so that edge fringing (below) degrades into a
transitional colour rather than a stray one. `tilt_palette.py` already satisfies
this — flat, then 12 hours × 4 tiers, so adjacent indices are adjacent clock
hours in the same tier. `albedo_palette.py` must sort by hue then value.

**Index maps are 8-bit, Non-Color, Closest.** An 8-bit Non-Color texel returns
exactly `i/255`, which is what makes the round-trip exact. Linear interpolation
or an sRGB colorspace breaks it silently.

**`<asset>` is the object's active material name, lowercased**, falling back to
the object name if the material is unnamed. `MCM_C10_Body` → `mcm_c10_body`. All
generated files for that asset share the stem.

## The albedo palette

`tools/albedo_palette.py` generates it, mirroring `tilt_palette.py`'s structure.
Ian's requirement: *"a full palette with a range of hues for every colour."*

- **Base swatches** — the 11 core swatches from the treatment's palette table
  (paper-cream, sand, khaki, olive, sky-teal, terracotta, rust, dusty-rose,
  coral, golden, mint) plus the 4 annex swatches (charcoal-plastic, faded-denim,
  mall-mauve, seafoam-grey). 15 total.
- **Drift variants per base** — the treatment's albedo-drift rule. Generated as
  HSV shifts, not RGB blends: measured 2026-08-04, RGB multiply/overlay is not
  universal across bases (multiply-cool swings paper-cream +174° of hue into
  blue-grey), whereas a hue rotation applies the same delta to every base by
  construction, with a measured hue standard deviation of 0.000.
  Variants: `warm` (hue −8°), `cool` (hue +8°), `dusk` (hue −6°, value ×0.92),
  `pale` (sat ×0.85), `deep` (sat ×1.15, value ×0.94).
- **Total** 15 bases × (1 base + 5 drifts) = 90 swatches, well inside 256.
- **Ordering** sorted by hue then value, so LUT neighbours are perceptual
  neighbours and edge fringing degrades into a transitional colour.

## Architecture

```
  paint target:  <asset>_dabindex.png   1024/2048/4096, 8-bit, Non-Color, Closest
                 R = albedo index        G = tilt index

  film-wide:     assets/materials/albedo_palette/albedo_lut.png  256x1  sRGB
                 assets/materials/tilt_palette/tilt_lut.png      256x1  Non-Color

  shader:
    dabindex -> Separate Color -+- R -> u = R*(255/256) + 0.5/256 -> albedo_lut -> Albedo
                                +- G -> u = G*(255/256) + 0.5/256 -> tilt_lut -> Normal Map -> Tilt
                                                                              -> MCM_Toon
```

The multiply-add converts an exact `i/255` texel into the texel centre
`(i+0.5)/256` of a 256-wide LUT. Exact for every index and independent of how
many swatches a palette actually contains.

Painting is entirely native. The add-on's only role during a session is having
set `brush.color` to `(a/255, t/255, 0)` when you clicked a swatch.

### Known cost: edge fringing

Blender antialiases dab silhouettes, so a boundary texel between two dabs holds
a blend of two indices and resolves to a third LUT entry. It is always a **valid
palette swatch** — never an invented colour, never black — and with
similarity-ordered LUTs it reads as a transitional colour. Dab-over-base
degrades toward the base swatch, which is the common case and looks like
ordinary antialiasing. Accepted; to be eyeballed early on a real asset rather
than discovered late.

## Components

| File | Role |
|---|---|
| `tools/addons/redwood_dabpaint.py` | the add-on: panel, operators, state |
| `tools/albedo_palette.py` | **new** CLI generator, mirrors `tilt_palette.py` |
| `tools/tilt_palette.py` | **extend**: also emit LUT PNG + swatch icons |

Both generators emit four artifacts into
`assets/materials/<palette_name>/` — `tilt_palette/` and `albedo_palette/`:

| artifact | purpose |
|---|---|
| `<name>.json` | swatch values + ordering, read by the add-on |
| `<name>.png` | human picker sheet (already exists for tilt) |
| `<name>_lut.png` | 256×1 lookup, linked by every asset's material |
| `swatches/<swatch>.png` | 32×32 icon per swatch, for the panel grid |

The add-on follows `tools/addons/redwood_guides.py`: single file, `bl_info`,
`_project_root()` walking up from the open `.blend` to find `tools/` and
`assets/`, importing the bpy-free palette modules via `sys.path`.

### UI

`View3D > Sidebar > Redwood > Dab Paint`, alongside the existing guides panel.

```
> Dab Paint
    [ Make Paintable ]        (only when the object isn't set up)
    map: truck_dabindex 2048

  > Albedo
     swatch grid (clickable)
     selected: terracotta / warm

  > Tilt
     swatch grid (clickable)
     selected: 3 o'clock / whisper

    [ Bake to PNG ]
```

Swatch grids are drawn with `bpy.utils.previews` icons generated from the
palette `swatches/` PNGs, as `layout.operator(..., icon_value=...)`. Blender's
native palette widget cannot be used: it sets `brush.color` to the swatch's
display colour, but the brush must carry an index encoding.

Operators: `dab_make_paintable`, `dab_set_albedo`, `dab_set_tilt`, `dab_bake`.
State lives in registered Scene properties (not ID custom properties) so it
participates in undo — an undo restores the selection and the brush colour
together, keeping them consistent.

`dab_bake` applies the LUTs and writes real `<asset>_albedo.png` (sRGB) and
`<asset>_tilt.png` (Non-Color) beside the index map in
`assets/<kind>/<name>/`, for when files are wanted by another tool or a final
render. It does not alter the material — the index map stays authoritative.

### Setup flow

Idempotent — adds and heals, following `make_layout`'s culture:

1. Create `<asset>_dabindex.png` at the chosen resolution, 8-bit, Non-Color,
   Closest, filled with the current selection so the surface starts flat.
2. Ensure both LUT images are loaded.
3. Create `MCM_Toon` if absent, patch it if present; wire the chain above.
4. Set paint mode to Single Image on the index map; set the brush to hard
   falloff, strength 1.0, MIX.
5. Write the index map to `assets/<kind>/<name>/<name>_dabindex.png` per
   `pipeline.md`.

Re-running heals drift: wrong colorspace, Linear interpolation, unlinked LUT,
missing paint slot.

## Failure modes

| Condition | Behaviour |
|---|---|
| File unsaved or outside the repo | Panel explains — `_project_root()` needs an anchor |
| Palette JSON or LUT missing | Message naming the generator command to run |
| Object has no UV layer | Refuse with a clear reason |
| Colorspace / interpolation drifted | Healed on next setup run, flagged in the panel |
| Soft brush falloff selected | Warn — soft edges worsen index fringing |
| Palette reordered after painting | Loud warning via stored ordering hash |

## Testing

`tools/tests/` runs unittest; most of the interesting logic is bpy-free.

- **Round-trip:** index → brush colour → 8-bit byte → index, exact for all
  0–255. The correctness core; off-by-one here means every dab is wrong.
- **LUT uv maths:** every index lands on its texel centre, no off-by-half.
- **Ordering hash:** stable across regeneration, changes on reorder.
- **Acceptance (headless):** write index *i* directly into the map, render,
  assert the pixel equals swatch *i* exactly. Needs no interactive painting, so
  it runs in the existing `test_blender_smoke.py` pattern.

The acceptance test is the one that would have caught every bug hit on
2026-08-04 — the Bump-vs-Normal-Map slot, the black fringe, the sRGB
corruption — because it checks the whole chain end to end against a known value.

## Why not the alternatives

**Custom modal brush writing both images.** Would satisfy the literal ask, but
means reimplementing projection painting: falloff, spacing, pressure, UV seam
bleed, occlusion, symmetry, UDIM. That is where Blender's paint system earns its
keep, and a hand-rolled version would feel worse than the stock brush.

**Native paint on albedo, replay the stroke onto tilt.** Reuses Blender's real
brush engine for both maps and yields two real images. Rejected on undo: each
`bpy.ops.paint.image_paint` call pushes its own undo step and an add-on cannot
suppress that, so it needs two Ctrl+Z presses and interleaved undo desyncs the
maps — the same trap, better hidden.

**Ucupaint dab kit.** Verified working on 2026-08-04 (see the treatment's closed
verify item), but a layer per (albedo × tilt) pair forces a layer switch before
every dab. Also: a working ypaint stack could not be built from Python — the
tree is assembled by UI-driven update callbacks, and `override_1_color` has no
update callback because it mirrors a node input socket. So the planned "dab-kit
builder" could not have been generated anyway.
