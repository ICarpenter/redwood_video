# boy — hands & feet reference sheets (sculpting / posing reference)

**Generated 2026-08-06, Nano Banana Pro (`gemini-3-pro-image`), 4K, 3:2.**
Source image passed to every call: `boy_modelsheet.png` (the two-view
orthographic sheet). Attach `boy_v3_arcane_b-backyard-dusk.png` as a second ref
only if the hands read too generic — it has more character in the fingers.

Files:
- `boy_hands_anatomy.png` — sheet 1 (5056 × 3392)
- `boy_hands_grips.png` — sheet 2 (5056 × 3392)
- `boy_shoe_ortho.png` — sheet 3 (5056 × 3392, captions painted out — see below)
- `boy_foot_poses.png` — sheet 4 (5056 × 3392)

The prompts below are the ones that produced these images, already carrying the
corrections that four rounds of generation forced. **See "What came back" at the
foot of this file** before re-running anything — it records which instructions
the model obeys, which it ignores no matter how they are worded, and what still
has to be fixed by hand.

## In Blender

All four are loaded in `assets/chars/cast.blend`, scene `boy_modeling`, as image
empties in their own collection **`boy_modeling_sculptref_detail`** — separate
from `boy_modeling_sculptref` so the detail board toggles without taking the body
plates with it. Same settings as the body plates (centred offset, `BACK` depth,
double-sided, alpha 0.9, `hide_select`) with one deliberate difference: these
have `show_empty_image_only_axis_aligned` **off**, because a detail board you can
only see from one axis is useless while orbiting a sculpt.

They sit as a stack at x −5.74…−4.05, in the clear gap between the rodin head
shelf and the lookdev floor edge. Everything nearer the origin is already taken
by `ref_concept_v2` and the body plates.

| object | `empty_display_size` | world size | scaled so that |
|---|---|---|---|
| `sculptref_hands_anatomy` | 0.695 | 0.70 × 0.47 m | the flat hand in cell 1 is 15.5 cm |
| `sculptref_hands_grips` | 0.666 | 0.67 × 0.45 m | the hand in the flat-push cell is 15.5 cm |
| `sculptref_shoe_ortho` | 0.866 | 0.87 × 0.58 m | the profile shoe is 27 cm toe-to-heel |
| `sculptref_foot_poses` | 1.690 | 1.69 × 1.13 m | the shoe in cell 1 is 27 cm |

**Where those two numbers come from.** The shoe is measured, the hand is not.
Thresholding `boy_modelsheet_side.png` at the sheet's own 1.0313 mm/px puts the
drawn shoe at **~27 cm long, ~9.7 cm tall**, and the front view puts it at 15.7 cm
wide. That is 21% of his stature where a real foot is about 15% — his sneakers
are drawn deliberately enormous, and the sculpt should match the drawing, not
anatomy. The hand could not be isolated the same way (skin against skin), so it
uses the anthropometric 0.107 × stature = **15.5 cm**. If the sculpted hand ends
up disagreeing, `empty_display_size` is the one field to change.

Four separate calls, not one sheet. Image models degrade hard as cells shrink,
and a shoe wants true orthographic views that do not belong on the same page as
action poses.

| sheet | what it is | why it exists |
|---|---|---|
| 1 | hand anatomy, 6 cells | the sculpting reference — flat, spread, unambiguous |
| 2 | hand grips, 6 cells | the poses the film actually asks for — gun, box, fence |
| 3 | sneaker orthographic, 6 views | the shoe is what gets modelled; the foot never appears bare |
| 4 | foot in action, 6 cells | animation reference, optional — run it last |

Scale from the model sheet: the figure is 1406 px ≡ 1.45 m. A kid that size has
a hand roughly 15 cm wrist-crease to fingertip and a shoe roughly 22 cm long.
Nothing in the prompts states measurements — the generator will ignore them and
the numbers are here for you when you set the empty sizes in Blender.

## Known risk

Hands are the classic failure. Every prompt below carries an explicit
finger-count clause and demands generous space between cells. Expect to
regenerate. If one cell is mangled, re-run the whole sheet rather than trying to
patch a cell — the whole point is that every cell is the *same* hand.

---

## Sheet 1 — hand anatomy

```
The attached image is the orthographic model sheet for a character. Using HIS
HANDS as the subject, produce a clean HAND STUDY SHEET for 3D sculpting
reference. Landscape format, roughly 3:2.

=== WHAT THIS IS FOR ===
This is a technical modelling reference, not an illustration. It will be loaded
into Blender as a background image and sculpted over. Accuracy of proportion and
silhouette matters more than mood, atmosphere or beauty. Every choice below
serves that.

=== LAYOUT ===
Exactly SIX cells in a clean 3-across, 2-down arrangement on one sheet. One hand
per cell, large, centred in its cell, with generous empty space around it. No
cell touches or overlaps another. No dividing lines, no boxes, no borders — the
separation is empty background only.

Top row, left to right:
1. BACK of the hand. Flat, palm down, fingers straight and slightly spread, all
   four fingers clearly separated with visible gaps, thumb out to the side.
2. PALM of the same hand. Flat, palm up, fingers straight and slightly spread,
   thumb out to the side. This is cell 1 flipped over — same hand, same size.
3. EDGE view from the little-finger side. Hand flat and straight, seen exactly
   side-on, so the thickness of the palm and the taper to the fingertips read.

Bottom row, left to right:
4. RELAXED HANGING hand, back of hand toward camera. Fingers in their natural
   half-curl at rest, not straight and not gripping, thumb resting alongside the
   index finger. This is the rest pose.
5. FIST, seen from the back of the hand. Fingers curled fully in, thumb folded
   ACROSS THE OUTSIDE of the index and middle fingers, not tucked inside.
6. OPEN SPREAD claw. Fingers spread as wide as they go and slightly hooked,
   thumb spread away, as if about to grab something big. Seen from the back.

=== SAME HAND EVERY TIME ===
Every cell is the SAME hand — his RIGHT hand — at the SAME SCALE, drawn the same
size in every cell. Do not draw a left hand anywhere. Do not vary the size
between cells: the distance from the wrist crease to the tip of the middle
finger is IDENTICAL in all six cells — a ruler laid across the sheet would
measure the same length in each. Each hand is cut off cleanly at the wrist with
a short stub of forearm included, and the wrist runs roughly vertical in every
cell.

=== CRITICAL: FIVE FINGERS ===
Every hand has exactly five digits: thumb, index, middle, ring, little. Count
them in every cell. No sixth finger, no missing finger, no two fingers fused
into one, no fingers melting into each other, no extra knuckle. Every finger has
three visible segments except the thumb, which has two. Fingernails are simple
flat shapes or omitted entirely — do not render nail detail.

=== CRITICAL: ORTHOGRAPHIC PROJECTION ===
Flat orthographic projection with ZERO perspective. No vanishing points, no
foreshortening, no lens distortion, no depth. The camera is infinitely far away
with a flat telephoto-like read. No finger points toward or away from the
camera; every finger lies flat in the plane of the picture so its true length
and taper are visible.
This applies to EVERY cell including cells 4 and 6. Cells 1, 4, 5 and 6 are all
seen from DIRECTLY ABOVE the back of the hand, dead-on and square, with the hand
flat in the plane of the picture. They are NOT three-quarter views, NOT tilted,
and NOT angled away. Cell 6 in particular must stay flat and square to the
camera — spread the fingers sideways within the picture plane, never toward the
viewer.

=== CRITICAL: THIS IS A CHILD'S HAND, NOT AN ADULT'S ===
The character is an ELEVEN-YEAR-OLD BOY. Drawing a generic adult hand study is
the single most common way this sheet fails. It must read unmistakably as a
kid's hand:
- SHORT fingers. A child's fingers are short relative to the palm — roughly the
  same length as the palm, not longer. Do not draw long elegant tapering fingers.
- BLUNT, rounded fingertips that barely taper from base to tip. Small nails, or
  no nails.
- SOFT knuckles — shallow dimples, not pronounced bony knots.
- A little padding across the palm and at the base of the fingers, but he is a
  skinny wiry kid, so it is not a fat toddler hand either.
- NO visible veins. NO tendon ridges running down the back of the hand. NO
  prominent knobbly wrist bone. NO deep wrinkles or age creases anywhere.
- Thin wrist, narrow forearm stub.
If the drawing would look at home in an adult anatomy textbook, it is wrong.
Keep the simplified illustrative style of the attached sheet — clean shapes, no
photo-realism — but keep the anatomy honest and countable.

=== LIGHTING — FLAT AND EVEN ===
Completely flat, even, shadowless lighting. NO key light, NO rim light, NO
coloured light, NO cast shadow, NO shadow between the fingers, no ambient
occlusion. Shadows hide form and lie about volume — the surface must be evenly
lit everywhere so the true silhouette is unambiguous.

=== RENDERING ===
Flat even skin tone matching the character. Crisp readable edges so every finger
is clearly separated from its neighbour and from the palm. Minimal internal
detail — a few clean crease lines at the knuckles and the wrist are fine, but no
painterly brushwork, no texture, no skin pores, no veins, no grain, no hatching.

=== BACKGROUND ===
Completely plain, flat, light neutral grey. Empty. No scenery, no props, no
surface for the hands to rest on, no ground plane, no gradient, no vignette, no
border, no drop shadow.

=== AVOID ===
adult hands, an adult anatomy study, long slender tapering fingers, fingers
longer than the palm, prominent tendon ridges, visible veins, bony knuckles,
large fingernails, deep skin creases, perspective, foreshortening, fingers
pointing at the camera, three-quarter views, left hands, varying hand size
between cells, six fingers, four fingers, fused or melted fingers, mitten hands,
holding any object, dramatic lighting, cast shadows, coloured
light, scenery, background objects, painterly brushwork, heavy texture, wrinkled
or aged skin, jewellery, watches, sleeves covering the wrist, text, labels,
arrows, measurement lines, grids, panel borders, watermarks, signatures.
```

---

## Sheet 2 — hand grips

Run this second. It reuses sheet 1's rules but poses the hand around the things
the film hands him: the printed machine gun (`sq020`, `sq030`, `sq060`), the
delivery box (`sq010-sh040`, `sq010-sh045`), the fence (`sq080-sh040`).

```
The attached image is the orthographic model sheet for a character. Using HIS
HANDS as the subject, produce a clean HAND GRIP SHEET for 3D posing and rigging
reference. Landscape format, roughly 3:2.

=== WHAT THIS IS FOR ===
This is a technical reference for posing a rigged 3D hand, not an illustration.
It shows how this character's hand wraps around the things he handles. Clarity of
the finger wrap matters more than mood, atmosphere or beauty.

=== LAYOUT ===
Exactly SIX cells in a clean 3-across, 2-down arrangement on one sheet. One hand
per cell, large, centred in its cell, with generous empty space around it. No
cell touches or overlaps another. The cells are separated by EMPTY BACKGROUND
ONLY — there are no dividing lines, no rules, no gutters, no boxes, no panel
borders and no frames anywhere on the sheet. Do not draw a grid. Do not draw a
line between the top and bottom rows.

Top row, left to right:
1. PISTOL GRIP. The hand is WRAPPED AROUND the vertical pistol grip of a toy
   gun, seen from the little-finger side so the wrap reads. Middle, ring and
   little fingers curl firmly all the way around the grip, their tips almost
   meeting the thumb, which comes round from the far side with its tip visible.
   The INDEX FINGER reaches forward off the grip and curls onto the trigger,
   clearly separated from the other three. Show ONLY the grip and the trigger:
   the rest of the gun — body, barrel, sights — is cropped away at the top and
   right edges of the cell, so no recognisable gun silhouette appears on the
   sheet. The grip and trigger are plain flat featureless grey shapes.
2. FOREGRIP. The same hand wrapped around a horizontal cylinder from
   underneath — all four fingers curled over the top of it, thumb wrapped up the
   near side. Seen from the side.
3. OVERHAND RAIL GRIP. The hand hooked over the top of a horizontal rail as if
   hauling himself over a fence — fingers hooked down over the far side, thumb
   hooked up from the near side, palm pressed on top. Seen from the side.

Bottom row, left to right:
4. FLAT PUSH. The hand pressed flat against a vertical surface, shoving it —
   palm and the heel of the hand loaded flat against it, fingers straight and
   bent slightly back, all four fingers together. Seen from the little-finger
   side so the flat contact and the bent-back fingers read.
5. HOOKED PULL. Fingertips hooked hard under a lip, as if pulling a cardboard
   flap open — fingers curled tight at the first two joints, palm open, thumb
   braced above. Seen from the side.
6. POINTING. Index finger straight out, middle, ring and little fingers curled
   down into the palm, thumb resting up against the middle finger. Seen from the
   back of the hand.

=== HOW TO SHOW THE OBJECT ===
Where the hand grips something, draw ONLY a plain, featureless, flat mid-grey
placeholder shape — a bare cylinder, a bare bar, a bare flat slab. It exists
solely to make the finger wrap readable. NO gun, NO trigger guard, NO box, NO
fence, NO detail, NO texture, NO colour, NO logo on the placeholder. Crop the
placeholder off at the edge of the cell so it does not become the subject. The
hand is the subject.

Cell 1 is the exception that proves the rule: the hand really is holding a
pistol grip and a trigger, because that is the only way the trigger finger reads
correctly — but both are drawn as plain flat grey shapes with no detail, and the
gun they belong to is cropped off at the edge of the cell. Never draw a whole
gun. Never draw a bottle, a pump, a nozzle or a handle — cell 1 is a grip, not
an object the hand is carrying.

=== SAME HAND EVERY TIME ===
Every cell is the SAME hand — his RIGHT hand — at the SAME SCALE, drawn the same
size in every cell. Do not draw a left hand anywhere. Each hand is cut off
cleanly at the wrist with a short stub of forearm included.

=== CRITICAL: FIVE FINGERS ===
Every hand has exactly five digits: thumb, index, middle, ring, little. Count
them in every cell. No sixth finger, no missing finger, no fused fingers, no
fingers melting into the object being gripped. Where a finger passes behind the
gripped object it disappears cleanly behind the object's silhouette and
reappears — it does not merge with it.

=== CRITICAL: ORTHOGRAPHIC PROJECTION ===
Flat orthographic projection with ZERO perspective. No vanishing points, no
foreshortening, no lens distortion. The camera is infinitely far away. No finger
points toward or away from the camera.

=== CRITICAL: THIS IS A CHILD'S HAND, NOT AN ADULT'S ===
The character is an ELEVEN-YEAR-OLD BOY. Drawing a generic adult hand is the
single most common way this sheet fails. It must read unmistakably as a kid's
hand: SHORT fingers, roughly the same length as the palm and not longer; blunt
rounded fingertips that barely taper; soft dimpled knuckles, not bony knots;
small nails or none; a little padding at the base of the fingers; thin wrist.
NO visible veins, NO tendon ridges on the back of the hand, NO prominent wrist
bone, NO deep wrinkles. He is skinny and wiry, so it is not a fat toddler hand
either. If the drawing would look at home in an adult anatomy textbook, it is
wrong. Keep the simplified illustrative style of the attached sheet, but keep
the anatomy honest and countable.

The hand is SMALL relative to what it grips. A child's hand does not close
comfortably around an adult-sized grip — the fingers only just meet the thumb,
or do not quite meet at all. Show that honestly.

=== LIGHTING — FLAT AND EVEN ===
Completely flat, even, shadowless lighting. NO key light, NO rim light, NO
coloured light, NO cast shadow, NO shadow between the fingers or under the
gripped object, no ambient occlusion.

=== RENDERING ===
Flat even skin tone. Crisp readable edges so every finger is clearly separated
from its neighbour, from the palm, and from the grey placeholder object.
Minimal internal detail — clean knuckle creases only. No painterly brushwork, no
texture, no grain, no hatching.

=== BACKGROUND ===
Completely plain, flat, light neutral grey, slightly lighter than the placeholder
objects so they read against it. Empty. No scenery, no ground plane, no gradient,
no vignette, no border, no drop shadow.

=== AVOID ===
adult hands, an adult anatomy study, long slender tapering fingers, fingers
longer than the palm, prominent tendon ridges, visible veins, bony knuckles,
deep skin creases, perspective, foreshortening, left hands, varying hand size
between cells, six fingers, fused or melted fingers, mitten hands, a
recognisable gun, a pistol silhouette, a trigger guard, a recognisable box, a
recognisable fence, detailed props, the prop becoming the subject, dramatic
lighting, cast shadows, coloured light, scenery, painterly brushwork, heavy
texture, sleeves covering the wrist, text, labels, arrows, measurement lines,
grids, panel borders, dividing lines between cells, watermarks, signatures.
```

---

## Sheet 3 — sneaker, orthographic

The boy is never barefoot, so the shoe is the thing that gets modelled. The jean
cuff pools over it and hides it, so this sheet excludes the cuff entirely —
sheet 4 shows how the cuff breaks.

```
The attached image is the orthographic model sheet for a character. Using HIS
CHUNKY BLACK SNEAKER as the subject, produce a clean six-view ORTHOGRAPHIC SHOE
SHEET for 3D modelling reference. Landscape format, roughly 3:2.

=== READ THIS FIRST — TWO RULES THAT OVERRIDE EVERYTHING ===
1. NO TEXT. There is not one single letter, word, number or caption anywhere on
   this image. Do NOT label the views. This is not a product tech pack and it
   carries no annotation layer — it is a bare plate that gets loaded into 3D
   software, where any writing lands on top of the model and ruins it. Views are
   identified by their position on the page, never by writing.
2. ALL SIX VIEWS ARE THE SAME SIZE. This is one shoe photographed six times by a
   locked camera that never moved closer or further away. The top view and the
   sole view are exactly as long as the side profiles. Do not shrink the top
   view. Do not enlarge the sole view.

=== WHAT THIS IS FOR ===
This is a technical modelling reference, not an illustration. It will be loaded
into Blender as background image planes and modelled over. Accuracy of
proportion and silhouette matters more than mood, atmosphere or beauty.

=== LAYOUT ===
Exactly SIX views of the SAME single shoe — his RIGHT shoe — in a clean
3-across, 2-down arrangement. One view per cell, large, centred, with generous
even space around it. No cell touches another. No dividing lines, no borders.

Top row, left to right:
1. OUTSIDE PROFILE — a true 90-degree side view of the outer face of the shoe,
   toe pointing to the RIGHT, sole flat on an invisible horizontal ground line.
2. INSIDE PROFILE — a true 90-degree side view of the inner face, toe pointing
   to the LEFT, sole flat on the same invisible ground line. This is view 1 seen
   from the opposite side, not a different shoe.
3. TOP — looking straight down on the shoe from directly above, toe pointing UP
   the page, dead-on with no tilt.

Bottom row, left to right:
4. SOLE — looking straight up at the underside, toe pointing UP the page. Show
   the tread as simple flat shapes.
5. FRONT — looking straight at the toe, dead-on.
6. BACK — looking straight at the heel, dead-on.

=== CRITICAL: THE VIEWS MUST ALIGN ===
All six are the same shoe at the same scale, as if rotated on a locked turntable.
Views 1, 2, 5 and 6 all stand on the same invisible ground line and their sole
line, the top of the heel counter, the top of the collar and the top of the
tongue all sit at the same height across the sheet.
Views 1, 2, 3 and 4 are all EXACTLY the same toe-to-heel length — a ruler laid
across the sheet would measure the identical length in each. In particular the
TOP view and the SOLE view are the same size as each other AND the same length
as the two profiles; do not shrink the top view or enlarge the sole view. Views
5 and 6 are the same width as each other and as the widest point of the top
view, and the same height as the profiles.
This alignment is the single most important requirement of the image.

=== CRITICAL: ORTHOGRAPHIC PROJECTION ===
Flat orthographic projection with ZERO perspective. No vanishing points, no
foreshortening, no lens distortion, no depth, no three-quarter angles anywhere.
The camera is infinitely far away with a flat telephoto-like read, level and
square to each view.

=== THE SHOE ===
A CHUNKY, heavy, blocky kids' sneaker from about 1993, copied from the shoe in
the attached model sheet. Fat and oversized on a skinny kid's foot: a THICK deep
sole with a heavy chunky lug tread, taking up nearly a third of the shoe's total
height; a bulky rounded bulbous toe; a LOW collar that sits below the ankle bone;
a simple tongue; three or four plain lace bars.
It is NOT a slim modern running shoe and NOT a sleek fashion sneaker — if the
silhouette looks light or streamlined, it is wrong.

THE ENTIRE SHOE IS BLACK. Upper black, sole black, tread black, laces black.
There is NO white midsole, NO cream midsole, NO pale sole, NO contrast stripe and
NO two-tone anything — this is not a basketball sneaker. Separate the sole from
the upper with a clean outline and at most a very slight shift in the darkness of
the black, never with a light colour. Check the attached model sheet: the shoe
there is one solid black mass from the laces to the ground. Match it.
Worn-in but not filthy. Simplify the lacing to a few clean straight bars — do not render
every eyelet or a complicated lace knot. NO brand logo, NO swoosh, NO stripes,
NO printed graphic, NO text on the shoe.

The shoe is EMPTY and shown ALONE. No leg, no ankle, no sock, and above all NO
JEAN CUFF over it — the cuff hides the shoe and this sheet exists to see it.
Cut off cleanly at the top of the collar.

=== LIGHTING — FLAT AND EVEN ===
Completely flat, even, shadowless lighting. NO key light, NO rim light, NO
coloured light, NO cast shadow on the ground, NO ambient occlusion, no
reflections, no specular highlights on the toe.

=== RENDERING ===
Flat local colours — the whole shoe reads as one flat near-black, upper and sole
alike, sitting clearly against the pale grey background. Crisp readable edges,
and clean outlines where the sole meets the upper so the two forms are still
separable in silhouette. Minimal internal detail — the major panel seams as clean
lines, nothing more. No painterly brushwork, no leather texture,
no canvas weave, no scuffs, no stains, no grain.

=== BACKGROUND ===
Completely plain, flat, light neutral grey. Empty. No scenery, no ground plane,
no horizon, no gradient, no vignette, no border, no drop shadow.

=== CRITICAL: NO TEXT ANYWHERE ===
Do not label the views. No caption under any view, no title, no heading, no
view name, no words, no letters, no numbers anywhere on the sheet. Do not write
"OUTSIDE PROFILE" or "TOP" or "SOLE" or anything else. The views are identified
by where they sit on the page, not by writing. Any text on this sheet ruins it —
it gets loaded into 3D software as a background plate and the writing lands in
the middle of the model.

=== AVOID ===
perspective, foreshortening, three-quarter angles, tilted views, a pair of shoes,
a left shoe, different scale between views, misaligned views, a white midsole, a
cream sole, a pale sole, a two-tone shoe, a contrast stripe, a high-top or
mid-top collar, a leg or ankle or sock or jean cuff, laces untied and flying,
complicated knots, brand logos,
dramatic lighting, rim light, cast shadows, reflections, coloured light, scenery,
painterly brushwork, heavy texture, text, labels, arrows, measurement lines,
grids, panel borders, watermarks, signatures.
```

---

## Sheet 4 — foot in action (optional, animation reference)

Not a modelling sheet — this is for posing the foot rig and for judging how the
jean cuff behaves. Run it last, and only if sheets 1–3 came back clean.

```
The attached image is the orthographic model sheet for a character. Using HIS
LEG AND CHUNKY BLACK SNEAKER as the subject, produce a clean FOOT POSE SHEET for
3D animation reference. Landscape format, roughly 3:2.

=== WHAT THIS IS FOR ===
This is a technical posing reference, not an illustration. It shows how this
character's foot and its baggy jean cuff behave through a running and jumping
cycle. Clarity of the ankle angle and the cuff behaviour matters more than mood
or beauty.

=== LAYOUT ===
Exactly SIX cells in a clean 3-across, 2-down arrangement. One leg per cell,
large, centred, with generous space around it. No cell touches another. No
dividing lines, no borders. Every cell shows the leg from mid-shin down, seen in
TRUE SIDE PROFILE, toe pointing to the RIGHT, at the SAME SCALE.

Top row, left to right:
1. STANDING FLAT. Foot flat on the ground, ankle neutral, weight on it. The
   baggy jean cuff breaks and pools over the top of the shoe.
2. HEEL STRIKE. The ONLY point touching the ground line is the back corner of
   the heel. The ankle is flexed UP and the whole shoe is tilted TOE-UP, its sole
   climbing away from the ground at about 30 degrees so there is a clear wedge of
   empty space between the ground line and the front of the sole. The toe is
   lifted high and points slightly up. This is the landing foot at the front of a
   running stride.
3. TOE-OFF. The exact opposite of cell 2. The ONLY point touching the ground line
   is the front tip of the toe. The heel is lifted high and the whole shoe is
   tilted TOE-DOWN at about 45 degrees, with a clear wedge of empty space between
   the ground line and the heel. This is the pushing foot at the back of a running
   stride.

Bottom row, left to right:
4. AIRBORNE, TOE POINTED. Foot off the ground entirely, ankle fully extended,
   toe pointing down and back — the trailing leg mid-jump.
5. TUCKED. Knee pulled up, ankle relaxed and slightly flexed, foot hanging — the
   leading leg mid-dive.
6. PLANTED ON A RAIL. The ball of the foot pressed on a plain horizontal grey
   bar, heel hanging off it, ankle flexed, as if pushing up over a fence.

=== HOW TO SHOW THE GROUND AND THE RAIL ===
The ground is a single thin plain grey horizontal line, nothing more — no
texture, no grass, no shadow on it. The rail in cell 6 is a plain, featureless,
flat grey bar. No fence, no scenery, no detail.

=== SAME LEG EVERY TIME ===
Every cell is the SAME leg — his RIGHT leg — at the SAME SCALE, cut off cleanly
at mid-shin. Same shoe in every cell: a chunky low-collared 1990s kids' sneaker
that is ENTIRELY BLACK — black upper, black chunky lug sole, black laces, no
white midsole, no pale sole, no contrast stripe, no logo — copied from the shoe
in the attached model sheet. Same jeans in every cell: enormous baggy pale blue
wide-leg denim.

=== THE JEAN CUFF ===
The cuff behaviour is half the point of this sheet, and it is the thing most
often drawn too timidly. These jeans are ENORMOUS and far too long for him — a
1990s wide-leg cut, the leg opening much wider than his ankle, hanging like a
loose tube well clear of the shin rather than tapering down to it.
In cell 1, standing flat, the cuff SWALLOWS the ankle and the top half of the
shoe and stacks into two or three deep horizontal folds, with the back edge of
the cuff dragging all the way down to the ground line behind the heel. That is
the baseline — the other cells depart from it, they do not get shorter jeans.
Show honestly, in each pose, how much of the shoe the cuff covers and where it
folds: pooled and stacked when the foot is flat, riding up the shin and swinging
back off the shoe when the ankle extends, hanging loose and straight down and
away from the leg when the foot is airborne. Keep the folds few, large and
simple — three or four big soft folds, not a mass of small wrinkles.

=== CRITICAL: ORTHOGRAPHIC PROJECTION ===
Flat orthographic projection with ZERO perspective. No vanishing points, no
foreshortening, no lens distortion. The camera is infinitely far away, level with
the foot and exactly square to the side of the leg. Every cell is a true
90-degree profile — no three-quarter angles anywhere.

=== LIGHTING — FLAT AND EVEN ===
Completely flat, even, shadowless lighting. NO key light, NO rim light, NO
coloured light, NO cast shadow on the ground, NO ambient occlusion, no
reflections.

=== RENDERING ===
Flat local colours — the shoe one flat near-black mass, upper and sole alike, and
denim that is clearly a pale washed BLUE, not white and not grey, so it separates
from both the grey background and the black shoe. Crisp readable edges. Minimal internal detail
— the big fold lines and the major seams only. No painterly brushwork, no denim
texture, no stitching detail, no scuffs, no grain.

=== BACKGROUND ===
Completely plain, flat, light neutral grey. Empty apart from the thin grey ground
line and the grey rail in cell 6. No scenery, no fence, no grass, no horizon, no
gradient, no vignette, no border, no drop shadow.

=== AVOID ===
perspective, foreshortening, three-quarter angles, both legs in one cell,
different scale between cells, a bare foot, a sock, tight or fitted jeans, a
cuff that ignores the pose, masses of small wrinkles, brand logos, dramatic
lighting, cast shadows, coloured light, scenery, fences, grass, painterly
brushwork, heavy texture, text, labels, arrows, measurement lines, grids, panel
borders, watermarks, signatures.
```

---

## What came back

Four rounds. The prompts above are the last version of each; what follows is
what the model actually did with them, so the next person does not re-fight the
same arguments.

### Corrections the prompts already absorbed

| the model did this | the fix now in the prompt |
|---|---|
| Drew adult hands — long tapered fingers, tendon ridges, veins | The `THIS IS A CHILD'S HAND` block, stated as the sheet's main failure mode |
| Drew panel divider lines on the grip sheet | "separated by EMPTY BACKGROUND ONLY", plus dividers in AVOID |
| Made the top view ~40% the length of the profiles | The `READ THIS FIRST` block: one locked camera, all six views the same size |
| Put a white midsole and a mid-top collar on the shoe | **This was our error, not the model's** — the shoe in `boy_modelsheet.png` is one solid black mass, low-collared. The prompt now says so and points at the ref |
| Turned an abstract grey grip into a soap dispenser | Cell 1 names a real pistol grip and trigger and crops the gun off at the cell edge. Abstracting the object breaks the pose; naming it fixes it |

### What it will not do, however it is worded

- **It labels the shoe views.** Three attempts, including hoisting `NO TEXT` to
  the top of the prompt with a justification. "Footwear tech pack" is too strong
  a prior. The captions on `boy_shoe_ortho.png` were painted out afterwards, not
  prompted away — ImageMagick finds each thin ink band inside a column strip and
  covers it with a patch of clean background lifted from the top margin at the
  same x, so the paper grain still lines up. **Re-run the sheet and the captions
  come back — strip them again.**
- **Heel strike, cell 2 of sheet 4.** Asked for three times, with degrees and
  contact points. It keeps drawing a toe-down foot. Pose it by hand.

### Known deviations, live

- The hands read left, not right — cells 1 and 2 of sheet 1 are internally
  consistent (a back view flipping to a palm view), just mirrored from what was
  asked. Harmless: mirror it in Blender.
- Cell sizes still drift a few percent. On the shoe sheet the profiles measure
  1577 px toe-to-heel, the top view 1565 px, the sole 1682 px — within ~7%, good
  enough to model against after a nudge. On the hand sheets the fist and edge
  cells run smaller than the flat cells.
- The eleven-year-old's hand is better than round one but is still on the mature
  side. If the sculpt comes out reading adult, that is where it came from.

### Style

These sheets deliberately discard the locked look — flat, shadowless, no
tilt-dab — because they are modelling references, not frames. Same allowed
departure `boy_modelsheet.prompt.md` takes.
