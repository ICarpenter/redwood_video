# Tilt-dab proof — mint C10

Tablet-free validation of the tangent-space tilt-dab technique from
`docs/treatment/style.md`. Open `tilt_dab_test.blend`.

## The headline finding — and the decision it forced

**Banding and tilt dabs are competing mechanisms, not complementary ones.**

The treatment guessed that "with dabs carrying the painterly read, banding may
be redundant." The test found the opposite — under poster banding it is the
*dabs* that become redundant:

| Banding | What the dabs do |
|---|---|
| **On** (poster bands) | Dabs are invisible across the lit surface. They only read along the terminator, where a small tilt is enough to cross the hard step. Ragged terminator edge, flat interior. |
| **Off** (soft physical) | Dabs read everywhere. All-over gouache grain, strongest where light falls off. The kettle-file look. |

Why: a hard `ColorRamp` step means a 3–14° normal tilt changes the output
*only* within a narrow band around the threshold. Everywhere else the tilted
and untilted normals land in the same band and shade identically.

> **DECIDED 2026-08-04: banding is dead film-wide.** The dabs are the look, so
> banding loses. `MCM_Toon` is now a plain diffuse + tilt normal, and the
> `Banding` input is gone. Recorded in the treatment's banned list.

### Consequence: the engine is unforced

`Shader to RGB` was the only EEVEE-only node in the stack. Without it the
shader runs unmodified in both engines — verified by rendering the same file in
each. But they don't look the same: **EEVEE holds dab contrast crisp and
graphic; Cycles' bounce fill lifts the shadow side and visibly dilutes the dab
read**, with warm ground bounce creeping up the body. Nothing forces the engine
any more, but the look leans EEVEE unless Cycles gets clamped diffuse bounces.

### Consequence: shadow tint moved

The global shadow tint used to ride on the banding ramp, which needed
`Shader to RGB`. It now lives in the **world**: a `Light Path > Is Camera Ray`
split gives a sky-teal *backdrop* while the *fill* lighting shadowed faces
carries the shadow tint. Art-directable, and engine-agnostic.

## Second finding — tier vs shot size

- **whisper (3°)** is barely visible even in an 85 mm closeup at 2.8 m.
- **medium (14°)** reads clearly at hero distance on a full-truck wide.

At the time of the test the treatment assigned `diecast = whisper, strong
reserved for crease accents`, which would have made the truck read essentially
flat in any wide shot. **That rule is gone** — per-family tier legality was
dropped 2026-08-04 and any tier is legal on any surface, so this is now a
judgement call at the brush: whisper when the grain should only be felt in
closeup, medium or strong when a wide has to carry it. It interacts with the
distance-scaling rule still in the treatment — but note it bites at *hero*
distance, not just background depth bands.

## What's in the file

| Object / datablock | Notes |
|---|---|
| `LowBody` / `LowGlass` / `LowInterior` | 1963 C10, 8.5k polys, scaled to 2.09 × 4.86 × 1.78 m, wheels on z=0 |
| `MCM_C10_Body` | the `MCM_Toon` group + paintable albedo and tilt maps |
| `MCM_Toon` node group | inputs: Albedo, Tilt Normal, Tilt Strength. Plain diffuse — runs in EEVEE and Cycles |
| `truck_tilt.png` | 2048², **Non-Color**, flat `#8080ff` — paint dabs here (pass 1) |
| `truck_albedo.png` | 2048², sRGB, flat mint `#76e7cd` — paint drift here (pass 2) |
| `tilt_DEMO_*.png` | procedural demo maps used for the findings above |
| `tilt_DIECAST_legal` palette | flat + 12 whisper + 12 strong, exact swatch values |
| `tilt_ALL` palette | all 49 swatches |
| `SUN_RIG` | empty parented to a hard sun, keyed 360° over frames 1–96 |
| `cam_hero` / `cam_detail` | 50 mm three-quarter, 85 mm hood closeup |

There is no `Banding` control any more — it was removed with the decision
above. Shadow hue is set on the **world** nodes (the Light Path split), not in
the material.

## The palette solves the colorspace trap

The treatment's open item — *"Blender color-pick behavior on Non-Color images
(sample from the sheet, don't type hex — hex field assumes sRGB)"* — is handled.

`tilt_DIECAST_legal` is a real Blender palette built directly from
`tilt_palette.json`'s `rgb8` values, stored as raw floats (`r/255`). Painting
with a palette swatch onto a Non-Color image writes the exact intended byte.
**Click swatches. Never type hex, never eyedropper the sheet** — the hex field
assumes sRGB and the eyedropper samples display-transformed pixels, and either
route silently corrupts the normal encoding.

`tilt_DIECAST_legal` holds only whisper + strong, from back when the treatment
restricted diecast to those tiers. That rule is dropped — use `tilt_ALL`.
The narrow palette survives only as a convenient short list.

## Painting workflow

1. Open the file — it lands in the Texture Paint workspace with `LowBody`
   active and `truck_tilt` as the canvas.
2. Sidebar → Tool → Color Palette → click a swatch.
3. Paint dabs. Keep the brush **hard-edged with no falloff** — a dab is one
   flat facet, not a soft blob. Soft falloff produces gradients, which the
   style bans outright.
4. Neighbouring dabs must *disagree* about direction — that disagreement is
   the whole effect. Same tier, different clock hours.
5. Scrub the timeline (1–96) to spin the sun and watch the grain react. This is
   the actual test: does it read as laid pigment or as noise?
6. Render `cam_hero` and `cam_detail`. Switch engine freely — the shader is
   the same in both.

## Still open

- Whether `Standard` or `AgX` view transform is right. Currently **Standard**,
  which preserves flat painted colour exactly; AgX rolls off the mint. For a
  flat-poster style this is a real style decision, not a technical default.
- Ucupaint (2.4.9, installed) layer-based workflow vs this flat two-image
  setup. The flat setup is deliberately simple so the *technique* is what's
  under test, not the tooling.
