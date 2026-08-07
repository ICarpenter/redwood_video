# mom — modelling references

**Written 2026-08-06. For Nano Banana Pro (`gemini-3-pro-image`), 4K.**

Refs to attach to every call:
- `mom_v1_arcane_a-garage-doorway.png` — the hero. Identity anchor: face, bob,
  glasses, blouse, trousers, shoes, build.
- `mom_v1_faces.png` — the expression board, for the head at a larger size.

**Ignore the oven mitts in both refs.** They are dead as of 2026-08-06 and every
prompt below says so explicitly. Her hands are bare, and on these sheets they are
a subject in their own right — see `style.md` § Characters.

| sheet | what it is |
|---|---|
| 1 | two-view orthographic model sheet — the sculpting plate |
| 2 | hand anatomy, six cells |
| 3 | hand grips, six cells, keyed to her shots |
| 4 | court shoe, six orthographic views |

Flat, shadowless and orthographic on purpose: plates to sculpt over, not frames.
The refs are painted-3D with saturated shadows and rim light — **that treatment
is deliberately discarded here.** Same allowed departure the boy's modelling
references take.

## Scale

**She is 1.70 m**, per `tools/guides.py:55` (`GuideSpec("mom", …, 1.7)`), which is
also the sheriff at 1.8 and the boy at 1.3 in the same table.

⚠️ **Pre-existing discrepancy, flagged not fixed:** `boy_modelsheet.prompt.md`
calibrates the boy's plate to **1.45 m**, while `guides.py` gives the standing boy
guide **1.3 m**. The two disagree and something downstream will eventually care.
Mom's plate uses the guide number, so if the boy's plate is right and the guide is
wrong, mom is the one that is consistent with the blocking and the boy is not.

## The identity block

Every prompt repeats this. If a sheet comes back off-model, harden this, not the
cell list.

> A wiry, angular woman in her late thirties, caricatured well past naturalism:
> long tendony neck, narrow bony shoulders, large head, thin limbs, no softness
> and no glamour anywhere. Long narrow jaw to a pointed chin, hard high
> cheekbones with hollows beneath, small wedge nose, heavy hooded eyelids. Large
> round wire-rimmed glasses with thin warm-gold frames and big lenses covering
> the cheekbones. Dark honey-blond permed CURLY BOB — one rounded solid mass
> stopping at the jaw, never past the shoulders, its length spent on volume, the
> curl described only around the outer contour. Hot saturated red lipstick.
> Bare hands: long slender bony fingers, prominent knuckles, oval nails painted
> the same hot red as the lipstick.

---

## Sheet 1 — two-view orthographic model sheet

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
waistband, hip, knee, ankle, ground.
This alignment is the single most important requirement of the image.

=== CRITICAL: ORTHOGRAPHIC PROJECTION ===
Flat orthographic projection with ZERO perspective. No vanishing points, no
foreshortening, no lens distortion, no wide-angle effect, no depth. The camera is
infinitely far away with a flat telephoto-like read. Do not tilt the camera up or
down — it is level with the middle of the figure. The front view must be exactly
front-on, not three-quarter, not angled even slightly. The side view must be
exactly side-on.

=== POSE — NEUTRALISE THE ACTION ===
The reference shows her standing still with one finger raised in a scold.
REPLACE it with a neutral modelling A-pose:
- Standing straight and still, weight even on both feet, spine vertical.
- Head level and facing straight forward. No tilt, no turn, no lean.
- Arms straight down and angled about 45 degrees away from the body, clearly
  separated from the torso so the silhouette of both arm and torso reads cleanly.
- Hands open and relaxed, fingers slightly spread, palms facing the body. Do NOT
  clench the fists and do NOT raise a finger.
- Legs straight, feet flat on the ground, shoulder width apart, toes forward.
- In the SIDE view, the near arm must be swung clearly BEHIND the body line, with
  a visible gap of empty background between the arm and the torso, so the chest,
  waist, seat and hip silhouette are all readable. The arm must not overlap the
  torso at any point.
- Mouth CLOSED and neutral, lips together, relaxed and level. Her huge toothy
  grin is her signature but an open mouth is awkward to sculpt and retopologise;
  it belongs on the expression sheet, not on the base plate.

=== PRESERVE THE CHARACTER EXACTLY ===
Keep the identity, proportions and wardrobe from the reference image:
- A wiry, angular woman in her late thirties, caricatured well past naturalism:
  long tendony neck, narrow bony shoulders, large head, thin limbs, no softness
  and no glamour anywhere.
- Long narrow jaw to a pointed chin, hard high cheekbones with hollows beneath,
  small wedge nose, heavy hooded eyelids.
- Large round wire-rimmed glasses, thin warm-gold frames, big lenses covering the
  cheekbones. In profile they read as one clean shape on the face.
- Dark honey-blond permed CURLY BOB as one rounded solid mass stopping at the
  jaw, never past the shoulders, its length spent on volume, the curl described
  only around the outer contour. No individual strands, no separated locks.
- Hot saturated red lipstick — the strongest colour note on her.
- 1988 button-front blouse in dusty mall-mauve with a HARD SQUARE shoulder shelf:
  the shoulder line is a sharp horizontal ledge with a crisp corner, not soft or
  sloped. Full gathered sleeves below the shelf, cuffs buttoned narrow at the
  wrist.
- High-waisted sand-coloured trousers, pleated at the waistband, tapered to the
  ankle, with a thin belt. Turned-up cuffs.
- Plain flat leather court shoes, closed toe, low heel.

=== CRITICAL: SHE IS A CARICATURE, NOT A PRETTY WOMAN ===
The reference is already stylised well past naturalism, and a modelling plate
must not quietly soften it back toward a normal attractive face. Hold all of
this:
- The JAW is LONG and NARROW and runs down to a POINTED chin. It is a wedge, not
  an oval and not a heart. Seen from the front the lower face tapers hard.
- The CHEEKBONES are high, hard and wide, with a clear HOLLOW beneath each one.
  The cheeks are not full and not rounded.
- The NECK is LONG and THIN, with the tendons visible down the front of it.
- The SHOULDERS are narrow and bony underneath the pads, and the pad line is a
  HARD HORIZONTAL SHELF meeting the sleeve at a sharp square corner — not
  sloped, not rounded, not softly padded.
- The arms and legs are thin and straight, the elbows and knees knobbly.
There is NO glamour and NO beauty rendering anywhere on this sheet. If she reads
as pretty, soft or conventionally attractive, it is wrong. She is angular,
tendony and hard-working, and she is drawn as far past naturalism as a cartoon
gets.

=== CRITICAL: BARE HANDS ===
Her hands are BARE. The reference shows her wearing quilted floral OVEN MITTS on
both hands — those are gone and must not appear. Draw her actual hands instead:
long, slender, bony, with prominent knuckles and visible tendons on the back, and
neat oval nails painted the same hot red as her lipstick. Five fingers on each
hand — thumb, index, middle, ring, little — no more and no fewer. No gloves, no
mitts, no oven mitts, nothing covering the hands.

=== LIGHTING — FLAT AND EVEN ===
Completely flat, even, shadowless frontal lighting on both views. NO dramatic key
light, NO rim light, NO coloured light, NO cast shadow on the ground, NO shadow
under the chin or in the folds, no ambient occlusion, no atmosphere. Shadows hide
form and lie about volume — the surface must be evenly lit everywhere so the true
silhouette and proportions are unambiguous. Discard the dark garage lighting of
the reference image entirely.

=== RENDERING ===
Clean, flat local colours — the blouse a flat dusty mauve, the trousers a flat
sand, the hair a flat dark honey blond, skin flat and even, the shoes flat brown.
Crisp readable edges so every form is clearly separated. Minimal internal detail
— no painterly brushwork, no texture, no fabric weave, no stains, no grain. Draw
the pleats and the buttons as clean simple lines and nothing more.

=== BACKGROUND ===
Completely plain, flat, light neutral grey. Empty. No scenery, no garage, no
fridge, no doorway, no ground plane, no horizon, no gradient, no vignette, no
border, no drop shadow.

=== AVOID ===
oven mitts, gloves, covered hands, perspective, foreshortening, three-quarter
angle, tilted head, raised or pointing finger, dynamic or action pose, clenched
fists, arms touching the torso, open mouth, dramatic lighting, rim light, cast
shadows, coloured light, scenery, background objects, painterly brushwork, heavy
texture, soft or sloped shoulders, glamour, beauty rendering, misaligned views,
different scale between the two views, cropped feet or hair, text, labels,
arrows, measurement lines, grids, watermarks, signatures.
```

---

## Sheet 2 — hand anatomy

Her hands matter more than most characters' do. The mitts came off precisely so
they could be seen, and the film asks them to wag, grip, rack a slide and pour
sweet tea. **The contrast is the character:** wiry working hands — tendons,
knuckles, no softness — finished with immaculate painted nails.

```
The attached image is a character illustration. Using HER HANDS as the subject,
produce a clean HAND STUDY SHEET for 3D sculpting reference. Landscape, roughly
3:2.

=== WHAT THIS IS FOR ===
This is a technical modelling reference, not an illustration. It will be loaded
into Blender as a background image and sculpted over. Accuracy of proportion and
silhouette matters more than mood, atmosphere or beauty.

=== IGNORE THE OVEN MITTS ===
The reference shows quilted floral OVEN MITTS on both hands. They are gone. This
entire sheet is her BARE hands. No gloves, no mitts, nothing covering them.

=== NOTHING BUT HANDS ===
This sheet contains HANDS AND NOTHING ELSE. No head, no face, no hair, no
glasses, no clothing, no body, no props. The attached reference is there for her
identity and colouring only — do NOT copy her head or her curly hair into any
cell. Every cell is a bare hand on an empty background.

=== LAYOUT ===
Exactly SIX cells in a clean 3-across, 2-down arrangement. One hand per cell,
large, centred, with generous empty space around it. The cells are separated by
EMPTY BACKGROUND ONLY — no dividing lines, no rules, no gutters, no boxes, no
panel borders, no frames. Do NOT draw a grid and do NOT draw a line between the
rows or between the columns.

Top row, left to right:
1. BACK of the hand. Flat, palm down, fingers straight and slightly spread, all
   four fingers clearly separated with visible gaps, thumb out to the side.
2. PALM of the same hand. Flat, palm up, fingers straight and slightly spread,
   thumb out to the side. This is cell 1 flipped over — same hand, same size.
3. EDGE view from the little-finger side. Hand flat and straight, fingers
   together and pointing to one side, seen exactly side-on, so the thickness of
   the palm and the taper to the fingertips read. This cell contains the hand and
   forearm stub ONLY — no hair, no head, no object of any kind resting on it.

Bottom row, left to right:
4. RELAXED HANGING hand, back of hand toward camera. Fingers in their natural
   half-curl at rest, thumb resting alongside the index finger. The rest pose.
5. FIST, seen from the back of the hand. Fingers curled fully in, thumb folded
   ACROSS THE OUTSIDE of the index and middle fingers, not tucked inside.
6. OPEN SPREAD. Fingers spread as wide as they go and slightly hooked, thumb
   spread away. Seen from the back.

=== SAME HAND EVERY TIME ===
Every cell is the SAME hand — her RIGHT hand — at the SAME SCALE. The distance
from the wrist crease to the tip of the middle finger is IDENTICAL in all six
cells; a ruler laid across the sheet would measure the same length in each. Each
hand is cut off cleanly at the wrist with a short stub of forearm, and the wrist
runs roughly vertical in every cell.

=== THE CHARACTER'S HAND ===
The hand of a wiry, angular, hard-working woman in her late thirties. It is NOT
a soft or glamorous hand and NOT a young one:
- LONG and SLENDER. Long narrow palm, long thin fingers, noticeably longer in
  proportion than an average hand.
- BONY. Prominent knuckles standing up as distinct knobs, visible tendon lines
  running down the back of the hand to each finger, a defined wrist bone.
- Thin, with the skin close over the structure. No padding, no plumpness.
- NAILS ARE THE EXCEPTION: neat, well-kept, filed to a clean rounded oval and
  painted a hot saturated RED. They are SHORT to MODERATE — extending only a
  little way past the fingertip, no further. They are NOT long, NOT pointed, NOT
  almond-sharp, NOT stiletto, NOT talons and NOT salon extensions; this is a
  woman who keeps her nails done, not a manicure advert. They are the one
  immaculate thing about a pair of working hands, and that contradiction is the
  character. Paint every visible nail — on the palm view the nail edges show just
  past the fingertips.

=== CRITICAL: FIVE FINGERS ===
Every hand has exactly five digits: thumb, index, middle, ring, little. Count
them in every cell. No sixth finger, no missing finger, no fused fingers, no
fingers melting into each other.

=== CRITICAL: ORTHOGRAPHIC PROJECTION ===
Flat orthographic projection with ZERO perspective. No vanishing points, no
foreshortening, no lens distortion. The camera is infinitely far away. No finger
points toward or away from the camera; every finger lies flat in the plane of the
picture so its true length is visible. Cells 1, 4, 5 and 6 are all seen from
DIRECTLY ABOVE the back of the hand, dead-on and square — not three-quarter, not
tilted.

=== LIGHTING — FLAT AND EVEN ===
Completely flat, even, shadowless lighting. NO key light, NO rim light, NO
coloured light, NO cast shadow, NO shadow between the fingers, no ambient
occlusion.

=== RENDERING ===
Flat even skin tone. Clean confident outlines so every finger is clearly
separated from its neighbour and from the palm. Minimal internal detail — the
knuckle creases and the tendon lines as clean single lines, nothing more. No
painterly brushwork, no texture, no grain, no hatching, no rendered veins.

=== BACKGROUND ===
Completely plain, flat, light neutral grey. Empty. No scenery, no props, no
surface for the hands to rest on, no gradient, no vignette, no border, no drop
shadow.

=== AVOID ===
oven mitts, gloves, covered hands, soft plump hands, short fingers, young hands,
glamour retouching, jewellery, rings, watches, sleeves covering the wrist,
perspective, foreshortening, fingers pointing at the camera, three-quarter views,
left hands, varying hand size between cells, six fingers, four fingers, fused or
melted fingers, unpainted nails, dramatic lighting, cast shadows, coloured light,
scenery, painterly brushwork, heavy texture, text, labels, captions, numbers,
arrows, grids, panel borders, dividing lines between cells, watermarks,
signatures.
```

---

## Sheet 3 — hand grips

Every cell is a thing she actually does. Cell 3 is the one that changed on
2026-08-06: she used to rack the slide with her teeth because the mitts left her
no fingers, and now she does it with her hands and it costs her nothing.

```
The attached image is a character illustration. Using HER HANDS as the subject,
produce a clean HAND GRIP SHEET for 3D posing and rigging reference. Landscape,
roughly 3:2.

=== WHAT THIS IS FOR ===
This is a technical reference for posing a rigged 3D hand. It shows how this
character's hands hold the things she handles. Clarity of the finger wrap matters
more than mood or beauty.

=== IGNORE THE OVEN MITTS ===
The reference shows quilted floral OVEN MITTS on both hands. They are gone. This
entire sheet is her BARE hands. No gloves, no mitts, nothing covering them.

=== LAYOUT ===
Exactly SIX cells in a clean 3-across, 2-down arrangement. One hand per cell
(except cell 3, which needs two), large, centred, with generous empty space
around it. The cells are separated by EMPTY BACKGROUND ONLY — no dividing lines,
no rules, no boxes, no panel borders, no frames. Do not draw a grid.

Top row, left to right:
1. THE WAG. A loose bare fist with the INDEX FINGER extended straight up out of
   it, held as if scolding somebody — one unhurried wag. The other three fingers
   curled down into the palm, thumb resting against the middle finger. Seen from
   the back of the hand. Long, slender and precise, with the painted nail on the
   end of the raised finger doing the pointing. This is the most important cell
   on the sheet.
2. PISTOL GRIP. The hand wrapped around the vertical grip of a pistol, seen from
   the little-finger side so the wrap reads. Middle, ring and little fingers
   curled firmly around the grip, thumb coming round from the far side with its
   tip visible, INDEX FINGER reaching forward onto the trigger and clearly
   separated from the other three. Show ONLY the grip and the trigger — the rest
   of the gun is cropped away at the top and right edges of the cell, so no
   recognisable gun silhouette appears. Grip and trigger are plain flat grey
   shapes with no detail.
3. RACKING THE SLIDE — TWO HANDS. The lower hand holds the pistol grip as in
   cell 2. The upper hand comes over the TOP of the slide from the far side and
   pinches it between the thumb and the side of a hooked index finger, the other
   fingers folded down, hauling straight back. Both hands bare, both sets of red
   nails visible. Draw the slide as a plain flat grey bar with a few vertical
   grooves cut into its rear end for grip; crop the rest of the gun off at the
   cell edges. Her hands are doing this easily — no strain, no white knuckles.
4. THE CASUAL CARRY. The hand wrapped loosely around a pistol grip with the arm
   relaxed, the gun hanging at an angle, held the way somebody carries a full
   grocery bag rather than a weapon. Fingers closed but not tight, wrist loose.
   Same plain grey cropped grip.
5. THE POUR. The hand wrapped around the handle of a jug, thumb over the top of
   the handle, all four fingers hooked through it, wrist rolled forward as if
   tipping it to pour. Draw the handle as a plain flat grey curved bar and crop
   the jug off at the cell edge.
6. HAND ON HIP. The hand planted on her own hip, seen from the back — fingers
   spread and pressed down over the curve, thumb forward, wrist bent. Draw a
   plain flat grey band across the bottom of the cell for the hip and crop it at
   the edges.

=== HOW TO SHOW THE OBJECTS ===
Everything she grips is a plain, featureless, flat mid-grey placeholder — a bare
bar, a bare block, a bare curved handle. NO rendered gun, NO trigger guard ring,
NO barrel, NO sights, NO jug, NO fabric detail, NO texture, NO logo. Crop each
placeholder off at the edge of its cell so it never becomes the subject. The
HANDS are the subject.

=== SAME HANDS EVERY TIME ===
The same woman's hands at the SAME SCALE in every cell, cut off cleanly at the
wrist with a short stub of forearm.

=== THE CHARACTER'S HANDS ===
Long, slender, bony hands: long narrow palm, long thin fingers, prominent
knuckles, visible tendon lines, defined wrist bone, no padding. Neat oval nails
painted a hot saturated RED, on every visible finger. Wiry working hands with
immaculate nails — that contradiction is the character.

=== CRITICAL: FIVE FINGERS ===
Every hand has exactly five digits. Count them in every cell. No sixth finger, no
missing finger, no fused fingers, and no finger melting into the grey placeholder
— where a finger passes behind an object it disappears cleanly behind its
silhouette and reappears.

=== CRITICAL: ORTHOGRAPHIC PROJECTION ===
Flat orthographic projection with ZERO perspective. No vanishing points, no
foreshortening. The camera is infinitely far away. No finger points toward or
away from the camera.

=== LIGHTING — FLAT AND EVEN ===
Completely flat, even, shadowless lighting. NO key light, NO rim light, NO
coloured light, NO cast shadow, no ambient occlusion.

=== RENDERING ===
Flat even skin tone. Clean confident outlines so every finger is separated from
its neighbour, from the palm and from the grey placeholder. Minimal internal
detail — knuckle creases and tendon lines only. No painterly brushwork, no
texture, no grain.

=== BACKGROUND ===
Completely plain, flat, light neutral grey, slightly lighter than the placeholder
objects so they read against it. Empty. No scenery, no gradient, no vignette, no
border, no drop shadow.

=== AVOID ===
oven mitts, gloves, covered hands, teeth, a mouth, a face, biting, soft plump
hands, short fingers, unpainted nails, jewellery, rings, a recognisable gun, a
pistol silhouette, a trigger guard, a rendered jug, detailed props, the prop
becoming the subject, perspective, foreshortening, varying hand size between
cells, six fingers, fused or melted fingers, dramatic lighting, cast shadows,
coloured light, scenery, painterly brushwork, heavy texture, sleeves covering the
wrist, text, labels, captions, numbers, arrows, grids, panel borders, dividing
lines between cells, watermarks, signatures.
```

---

## Sheet 4 — court shoe, orthographic

```
The attached image is a character illustration. Using HER SHOE as the subject,
produce a clean six-view ORTHOGRAPHIC SHOE SHEET for 3D modelling reference.
Landscape, roughly 3:2.

=== READ THIS FIRST — TWO RULES THAT OVERRIDE EVERYTHING ===
1. NO TEXT. There is not one single letter, word, number or caption anywhere on
   this image. Do NOT label the views. This is not a product tech pack and it
   carries no annotation layer — it is a bare plate that gets loaded into 3D
   software, where any writing lands on top of the model and ruins it.
2. ALL SIX VIEWS ARE THE SAME SIZE. One shoe photographed six times by a locked
   camera that never moved closer or further away.
   Measure toe to heel: the OUTSIDE PROFILE, the INSIDE PROFILE, the TOP view and
   the SOLE view are all EXACTLY the same length as each other. The single most
   common failure on this kind of sheet is drawing the top view too small — if
   the top view is shorter end to end than the profile beside it, it is WRONG.
   The FRONT and BACK views are exactly as TALL as the profiles and stand on the
   same ground line.

=== WHAT THIS IS FOR ===
A technical modelling reference, not an illustration. Accuracy of proportion and
silhouette matters more than mood, atmosphere or beauty.

=== LAYOUT ===
Exactly SIX views of the SAME single shoe — her RIGHT shoe — in a clean 3-across,
2-down arrangement. One view per cell, large, centred, with generous even space
around it. No cell touches another. No dividing lines, no borders.

Top row, left to right:
1. OUTSIDE PROFILE — a true 90-degree side view of the outer face, toe pointing
   RIGHT, sole flat on an invisible horizontal ground line.
2. INSIDE PROFILE — a true 90-degree side view of the inner face, toe pointing
   LEFT, sole flat on the same invisible ground line. The same shoe from the
   opposite side, not a different shoe.
3. TOP — looking straight down from directly above, toe pointing UP the page.

Bottom row, left to right:
4. SOLE — looking straight up at the underside, toe pointing UP the page. Tread
   as simple flat shapes.
5. FRONT — looking straight at the toe, dead-on.
6. BACK — looking straight at the heel, dead-on.

=== CRITICAL: THE VIEWS MUST ALIGN ===
Views 1, 2, 5 and 6 all stand on the same invisible ground line, and the sole
line, the top of the heel and the top of the collar sit at the same height across
the sheet. Views 1, 2, 3 and 4 are all EXACTLY the same toe-to-heel length — a
ruler laid across the sheet would measure the identical length in each.

=== CRITICAL: ORTHOGRAPHIC PROJECTION ===
Flat orthographic projection with ZERO perspective. No vanishing points, no
foreshortening, no lens distortion, no three-quarter angles anywhere. The camera
is infinitely far away, level and square to each view.

=== THE SHOE ===
A plain flat leather COURT SHOE — a simple closed-toe slip-on pump of the kind a
working woman wore in 1988. Rounded almond toe, a low stacked heel of about three
centimetres, a plain topline cut low across the top of the foot, and nothing else
whatsoever: no laces, no buckle, no strap, no bow, no perforation, no stitching
pattern, no logo. Mid-brown leather, worn but cared for. The whole shoe is one
simple honest shape — if it looks fashionable or decorated, it is wrong.

The shoe is EMPTY and shown ALONE. No foot, no leg, no ankle, no stocking, no
trouser cuff. Cut off cleanly at the topline.

=== LIGHTING — FLAT AND EVEN ===
Completely flat, even, shadowless lighting. NO key light, NO rim light, NO
coloured light, NO cast shadow on the ground, NO ambient occlusion, no
reflections, no specular highlights on the toe. Leather is matte here.

=== RENDERING ===
Flat local colours — the upper a flat mid-brown, the sole and heel a slightly
darker flat brown, clearly separated so the sole line is unmistakable. Crisp
readable edges. Minimal internal detail — the topline and the heel seam as clean
lines, nothing more. No painterly brushwork, no leather grain, no scuffs, no
stains.

=== BACKGROUND ===
Completely plain, flat, light neutral grey. Empty. No scenery, no ground plane,
no horizon, no gradient, no vignette, no border, no drop shadow.

=== AVOID ===
text, labels, captions, view names, words, letters, numbers, perspective,
foreshortening, three-quarter angles, tilted views, a pair of shoes, a left shoe,
different scale between views, misaligned views, a foot or leg or ankle or
stocking or trouser cuff, high heels, stilettos, pointed toes, straps, buckles,
bows, laces, decoration, brand logos, patent shine, reflections, dramatic
lighting, rim light, cast shadows, coloured light, scenery, painterly brushwork,
heavy texture, grids, panel borders, watermarks, signatures.
```

---

## What came back

**Generated 2026-08-06.** Sheet 1 took two rounds, sheets 2 and 4 took two,
sheet 3 took one.

Files:
- `mom_modelsheet.png` (5504 × 3072) + `mom_modelsheet_front.png` /
  `mom_modelsheet_side.png` (1800 × 2929 each, identical vertical window)
- `mom_hands_anatomy.png`, `mom_hands_grips.png`, `mom_shoe_ortho.png`
  (5056 × 3392)

### Measured

| | value |
|---|---|
| front figure | x 483–2253, y 92–3000 |
| side figure | x 3988–4624, y 96–2997 |
| figure height | 2909 px ≡ **1.70 m** → 0.5844 mm/px |
| crop window | y 82–3010, 1800 px wide (2929 tall) |
| empty display size | 1.7117 (crop height in world units) |
| z offset | 0.8494 (puts feet on z = 0) |
| her shoe | 395 px ≡ **23.1 cm** — realistic, unlike the boy's deliberately oversized 27 cm |

**The alignment instruction worked, twice.** Tops landed within 4 px and the two
figures' heights differ by 0.24%.

### Corrections the prompts absorbed

| the model did this | the fix now in the prompt |
|---|---|
| Softened her toward a normal pretty face — rounded jaw, full cheeks, sloped shoulders | The `SHE IS A CARICATURE, NOT A PRETTY WOMAN` block, naming the wedge jaw, the hollows, the tendony neck and the square shoulder shelf |
| Side view: near arm laid over the torso | "swung clearly BEHIND the body line, with a visible gap of empty background" |
| Hand sheet cell 3: drew her **curly hair sitting on the hand** instead of an edge view | The `NOTHING BUT HANDS` block — the refs are for identity only, do not copy her head into a cell |
| Shoe: top view 27% shorter than the profiles | Named as "the single most common failure on this kind of sheet" — improved to 21%, see below |

### Known deviations, live

- **The shoe sheet's TOP view is 21% short.** Profiles measure 1687 and 1686 px
  toe-to-heel and the sole 1721, but the top view is 1334. Two rounds and a
  named-failure clause only moved it from 27% to 21%; the boy's sheet fought the
  same prior. **Scale the top view by 1.26× if you set it up as its own plate.**
  The front and back views also run 17–23% taller than the profiles.
- **Captions are a coin flip on the shoe sheet.** Round 1 came back clean; round 2
  captioned all six views from the identical prompt. Round 2's were painted out.
- **Panel dividers on the hand sheets.** The grips sheet drew full-span rules
  between cells; they were filled out afterwards rather than re-rolled, because
  the cells themselves were good. The anatomy re-run came back clean.
- **The nails run longer and more pointed than asked.** "Short to moderate,
  rounded oval" produced something closer to a long almond. In character for a
  woman who keeps them done, so kept — but it is not what the prompt says.
- **The palm cell's nails read pale**, not red, where every other cell has them
  hot red.
- **The side view came back facing LEFT** on both rounds despite the prompt asking
  for right. `mom_modelsheet_side.png` is flopped when the crop is cut, so the
  shipped crop faces right like the boy's. The full sheet still has her facing
  left.
- Round 2 of the hand anatomy sheet came back on a **darker grey field with softer
  shading** than round 1 — slightly less flat than the brief.

## In Blender

`assets/chars/cast.blend`, scene `mom_modeling` — Ian's scene, his `momref_`
naming and his empty settings.

| object | collection | `empty_display_size` | scaled so that |
|---|---|---|---|
| `momref_modelsheet_front` | `mom_modeling_sculptref` | 1.7117 | she is 1.70 m, feet on z = 0 |
| `momref_modelsheet_side` | `mom_modeling_sculptref` | 1.7117 | same, flopped to face right |
| `momref_hands_anatomy` | `mom_modeling_sculptref_detail` | 0.731 | a hand is ~18 cm |
| `momref_hands_grips` | `mom_modeling_sculptref_detail` | 0.731 | matches the anatomy sheet |
| `momref_shoe_ortho` | `mom_modeling_sculptref_detail` | 0.692 | the profile shoe is 23.1 cm |

**Which numbers are measured and which are not.** The model sheet is calibrated
exactly — 2909 px of figure against the 1.70 m in `guides.py`. The shoe is
measured off the model sheet's own side view. **The two hand sheets are
estimates**: the hand could not be isolated against skin the way the shoe could,
so they use the anthropometric 0.107 × stature ≈ 18 cm plus a cell-bbox
proportion. If the sculpted hand disagrees, `empty_display_size` is the one field
to change.

### Every plate in the scene is now at true scale

**Done 2026-08-06, Ian's call.** The three concept plates were at arbitrary sizes
(2.0, 2.0 and 2.5) from before the model sheet existed. They are now measured
against the model sheet's calibration and rescaled, so **every image in
`mom_modeling` shows her at 1.70 m and the full-body plates all stand on z = 0**.
You can read her height off any of them.

| plate | figure in the image | display size | z |
|---|---|---|---|
| `momref_concept_scold` | y 84–2319 of 2400 → 2235 px | 2.000 → **1.8255** | 1.200 → **0.8512** |
| `momref_concept_finalboss` | y 96–2339 of 2400 → 2243 px | 2.000 → **1.8190** | 1.200 → **0.8633** |
| `momref_faces` | cell-1 hair 1546 px vs the model sheet's 710 px | 2.500 → **1.3570** | unchanged (heads, no feet) |

The two full-body figures were measured by eye off cropped bands rather than by
threshold — the painted backgrounds defeat an automatic ink box, and hair against
dark teal and a brown shoe against a bright floor are both low-contrast edges.
Call them good to a percent or two, not to the pixel like the model sheet.

### One thing left to decide

**The front plate is not where it wants to be.** It sits at x = −1.30, in the gap
between the concept plates, because x = 0 — directly behind the blockout — is
occupied by `momref_concept_finalboss`. Nothing was moved. Swapping the two is
one drag.

### Resolved

⚠️ `mom_modeling_wip` measured **1.409 m** against canon's 1.70 m. **It was
copied in from the boy** (Ian, 2026-08-06) — that is why it carries his height.
Ian is rebuilding it; the plates were left at canon rather than dragged down to
meet it.
