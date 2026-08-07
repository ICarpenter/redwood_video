# boy — orthographic model sheet (sculpting reference)

**Generated 2026-08-05, Nano Banana Pro (Gemini).**
Source image passed to the generator: `boy_v3_arcane_b-backyard-dusk.png`

Files:
- `boy_modelsheet.png` — the full two-view sheet as generated (2752 × 1536)
- `boy_modelsheet_front.png` — front view, cropped (960 × 1427)
- `boy_modelsheet_side.png` — profile, cropped (960 × 1427)

The two crops share an identical vertical window, so the views are aligned by
construction. Both are loaded in `assets/chars/cast.blend` as image empties in
collection `boy_modeling_sculptref`.

## Measured from the generated sheet

| | value |
|---|---|
| front figure | x 314–1211, y 80–1486 |
| side figure | x 1639–1942, y 80–1484 |
| shared crop window | y 70–1497 (1427 px tall), 960 px wide |
| figure height | 1406 px ≡ **1.45 m** → 1.0313 mm/px |
| empty display size | 1.4717 (crop height in world units) |
| z offset | 0.7245 (puts feet on z = 0) |

Both figures topped out at y=80 and their ground lines landed within 2 px of each
other — the alignment instruction in the prompt worked.

## The prompt

```
Convert the attached character illustration into a clean two-view ORTHOGRAPHIC
MODEL SHEET for 3D sculpting reference. Landscape format, roughly 16:9.

=== WHAT THIS IS FOR ===
This is a technical modelling reference, not an illustration. It will be loaded
into Blender as background image planes and sculpted over. Accuracy of proportion
and silhouette matters more than mood, atmosphere or beauty. Every choice below
serves that.

=== LAYOUT ===
Exactly two full-body views of the SAME character, side by side on one sheet:
- LEFT: FRONT view — dead-on, face on, perfectly symmetrical.
- RIGHT: SIDE view — a true 90-degree profile, the character facing to the right.
Both figures at the SAME SCALE, standing on the same invisible ground line, with
generous even margins. Nothing cropped — the full figure from the top of the hair
to the soles of the shoes is inside the frame in both views.

=== CRITICAL: THE TWO VIEWS MUST ALIGN ===
Both views are the same character at the same height, drawn as if rotated 90
degrees on a turntable with the camera locked. These landmarks must sit at the
EXACT SAME HEIGHT in both views, so a horizontal line drawn across the sheet
touches the same feature in each:
top of the hair, brow, eyeline, tip of the nose, chin, shoulder, elbow, wrist,
hem of the t-shirt, hip, knee, ankle, ground.
This alignment is the single most important requirement of the image.

=== CRITICAL: ORTHOGRAPHIC PROJECTION ===
Flat orthographic projection with ZERO perspective. No vanishing points, no
foreshortening, no lens distortion, no wide-angle effect, no depth. The camera is
infinitely far away with a flat telephoto-like read. Do not tilt the camera up or
down — it is level with the middle of the figure. The front view must be exactly
front-on, not three-quarter, not angled even slightly. The side view must be
exactly side-on.

=== POSE — NEUTRALISE THE ACTION ===
The reference image shows a dynamic excited bounce. REPLACE it with a neutral
modelling A-pose:
- Standing straight and still, weight even on both feet, spine vertical.
- Head level and facing straight forward. No tilt, no turn, no lean.
- Arms straight down and angled about 45 degrees away from the body, clearly
  separated from the torso so the silhouette of both arm and torso reads cleanly.
- Hands open and relaxed, fingers slightly spread, palms facing the body. Do NOT
  clench the fists.
- Legs straight, feet flat on the ground, shoulder width apart, toes forward.
- In the SIDE view, the near arm must not cover the torso — keep it hanging
  slightly behind the body line so the chest, belly and hip silhouette stay visible.

=== PRESERVE THE CHARACTER EXACTLY ===
Keep the identity, proportions and wardrobe from the reference image:
- Skinny, wiry build. Narrow shoulders, thin arms, thin legs, long neck, large head.
- Thick blond bowl cut as one solid mass: straight fringe cut square across the
  brow, ends curling under, sitting above the ears. In profile it reads as one
  clean helmet-shaped silhouette.
- Heavy, droopy, hooded eyelids over the eyes — the eyes stay OPEN, just heavily
  lidded and sleepy. Do not close them, do not make them squint arcs.
- The huge wide open toothy grin with big front teeth, corners pulled up.
- Oversized boxy black t-shirt hanging past the hips off narrow shoulders.
- Enormous baggy pale wide-leg jeans, two clearly separate trouser legs with an
  obvious gap between them, cuffs breaking and pooling over the shoes.
- Chunky black sneakers.

=== LIGHTING — FLAT AND EVEN ===
Completely flat, even, shadowless frontal lighting on both views. NO dramatic key
light, NO rim light, NO coloured light, NO cast shadow on the ground, NO shadow
under the chin or in the folds, no ambient occlusion, no atmosphere. Shadows hide
form and lie about volume — the surface must be evenly lit everywhere so the true
silhouette and proportions are unambiguous. Discard the dusk lighting of the
reference image entirely.

=== RENDERING ===
Clean, flat local colours — the black tee reads as flat dark grey, the jeans as
flat pale blue, the hair as flat blond, skin as flat and even. Simplify the
t-shirt graphic to a plain simple shape or leave the tee blank; do not render the
detailed band artwork, it clutters the reference. Crisp readable edges so every
form is clearly separated. Minimal internal detail — no painterly brushwork, no
texture, no fabric wear, no stains, no grain.

=== BACKGROUND ===
Completely plain, flat, light neutral grey. Empty. No scenery, no backyard, no
fence, no sky, no ground plane, no horizon, no gradient, no vignette, no border,
no drop shadow.

=== AVOID ===
perspective, foreshortening, three-quarter angle, tilted head, dynamic or action
pose, clenched fists, arms touching the torso, dramatic lighting, rim light, cast
shadows, coloured light, scenery, background objects, painterly brushwork, heavy
texture, closed or squinting eyes, misaligned views, different scale between the
two views, cropped feet or hair, text, labels, arrows, measurement lines, grids,
watermarks, signatures.
```

## Head-only variant

Swap the LAYOUT block for two views of the head and neck only, cut off at the
base of the neck, head filling most of the frame height. Alignment landmarks
become: top of hair, brow, eyeline, nose tip, mouth line, chin, jaw, base of neck.

## Known deviation

The open toothy grin is kept because it is the character's signature, but an open
mouth is awkward to sculpt and retopologise. The usual approach is a neutral
closed mouth for the base mesh with the grin as a shape key — change the grin
line to "mouth closed and neutral, lips together, relaxed" for that sheet.
