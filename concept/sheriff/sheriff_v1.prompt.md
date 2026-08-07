# sheriff — v1, Arcane / high contrast

**Written 2026-08-06. For Nano Banana Pro (`gemini-3-pro-image`), 4K.**

Four sheets: three full-figure states and an expression board. He is the only
character who changes appearance across the film, so the states *are* the
design.

| sheet | state | shots |
|---|---|---|
| A | **first sighting** — crisp, hat, aviators, sandwich | `sq040-sh030/035` |
| B | **out of the ditch** — no glasses, mangled hat, egg salad on the moustache | `sq040-sh060` onward, which is most of the film |
| C | **the flashback** — same man, M1 helmet, flak vest, sepia | `sq050-sh010` |
| D | expression board, six cells keyed to real shots | — |

## Refs to attach

| ref | role | sheets |
|---|---|---|
| `refs/cop/N150_0030_018.jpg` | **The man.** Ian's call, 2026-08-06 — this is the face: thick dark wavy hair swept back and over the ears, heavy full 1980s moustache covering the top lip and running past the corners of the mouth, lean strong jaw, prominent nose, deep-set eyes under dark brows. | all |
| `refs/cop/cops_shaking_hands.jpeg` | **The uniform.** Ian's call — dark brown shirt with a TAN YOKE panel across the chest and shoulders, tan tie, gold star-in-shield patch on both sleeves, gold epaulettes, gold badge and name plate, black basketweave leather duty belt, tan trousers. | A, B, D |
| `concept/boy/boy_v3_arcane_b-backyard-dusk.png` | Style target — same film, same artist. | all |

## Two things from the ref are deliberately NOT taken

1. **The N150 man's build.** He is lean; the sheriff is not. `guide_assets.py`
   `build_sheriff` gives him a **0.30 m belly ball** on a 1.8 m frame under a
   0.28 m-radius hat brim. Take the face and the hair from the photograph and put
   them on the body described below.

   **Revised 2026-08-06, Ian's call — he is not a doughboy.** Round 1 read as an
   all-over fat man and that is wrong. He is **naturally tall and genuinely
   wide-shouldered**, big-boned, with **bad posture** and **a gut**, and a
   **naturally big backside** — which is where the butt-crack runner
   (`sq040-sh060`, `sq050-sh020`, `sq080-sh040`) actually comes from. The frame
   is a big man's; the softness is only in the belly and the seat.
2. **The uniform photo's men.** Their faces, ages and builds are irrelevant —
   only the garment is being copied.

## The flashback is the same body, on purpose

`build_sheriff_war`'s docstring is explicit: the body dimensions are copied from
`build_sheriff` verbatim, because "the flashback cuts against present-day shots
of the same man, and if the silhouette changed size the match would read as a
different character rather than the same one, younger. Only the head-dress and a
flak vest differ."

So **Sheet C is not a slim young marine.** Same height, same broad shoulders,
same big backside, same moustache, same forward-rolled posture — an M1 helmet and
a flak jacket instead of the hat, and twenty-five years off the face.

**The frame is what bridges the two periods** (Ian, 2026-08-06), which is the
point of the revised build: a tall wide-shouldered big-seated man reads as the
same man at twenty-three and at forty-five, where an all-over fat man does not.
The one thing the sheets let differ is the **gut, which is smaller in the
flashback** — present but not yet earned. That is a deliberate half-step away
from `build_sheriff_war`'s "identical body": in guide primitives the belly ball
is the same in both, and if this design stands, `sw_belly` wants shrinking.
Flagged, not changed.

## The state changes, tracked

| | hat | aviators | uniform | face |
|---|---|---|---|---|
| A | campaign hat, clean | **on** | pressed, tucked, tie straight | clean |
| B | **mangled** | **gone** — lost in the crash | torn, untucked, dust, one sleeve out | **egg salad in the moustache and on one cheek** |
| C | M1 helmet | none | jungle utilities, flak vest | young, sweat, no lines yet |

The aviators are Ian's call (2026-08-06): mirrored teardrop aviators when we
first see him, **lost in the crash and never seen again**. They are the cheapest
possible way to show that the crash cost him something, and they hide his eyes
for exactly as long as he is a threat.

The egg salad is his too. `egg_salad_sando` is already an L3 prop that appears
two-handed in `sq040-sh035` and again in `sh042`; wearing some of it out of the
ditch turns a prop into a running gag at no cost.

## ⚠️ Departs from `docs/treatment/style.md`

Same three crossings the boy's v3 and the mom's v1 make, and for the same reason
— this is a look argument, not canon: **modelled dimensional form**, **saturated
coloured shadows**, and a **hot rim light**. `style.md` § Characters wants
UPA-flat, unmodelled, no rim. If a sheet wins, the doc gets updated; until then
the doc is canon and this folder is the argument.

Nothing here changes his one recorded line in `style.md` § Characters — "the man
reads timeless county lawman; his anachronism is the car."

---

## Sheet A — first sighting

```
A character concept illustration for a 1993-set animated film: a full-length
portrait of a county sheriff, painted in exactly the style of the attached
illustration of the blond boy. Vertical 3:4.

=== THE MAN — from the attached photograph of the moustached deputy ===
Take his FACE and HAIR exactly: thick dark wavy hair swept back off the forehead
and down over the ears, a heavy full dark 1980s moustache that covers the whole
top lip and runs down past the corners of the mouth, a lean strong jaw, a
prominent straight nose, deep-set eyes under heavy dark brows. Mid-forties.
Weathered, sun-creased, entirely serious about himself.

DO NOT take his build — the photograph's man is lean and this one is not.

=== THE BUILD — big-framed, not fat ===
Read this carefully; it is the thing most likely to go wrong. He is NOT a
doughboy and NOT obese.

His FRAME is naturally big: TALL — 1.8 metres — and genuinely BROAD, wide across
the shoulders and the back, big-boned, long-limbed. That frame is what he was
born with and it never changes.

What twenty-five years in a car seat did to it is POSTURE and a GUT, in that
order:
- BAD POSTURE is the first thing you read in his silhouette. His shoulders roll
  FORWARD and down, his upper back curves over, his head carries forward of his
  shoulders on a thick neck, and his pelvis tips so the belly leads and the
  backside sits back and out. He is not standing up straight and he has not for
  a long time.
- A GUT — round, firm and low, sitting over the belt the way a beer gut does,
  pushing the shirt out below the chest and hanging a little over the buckle.
  **His shoulders are still wider than his belly.** It is a gut on a big man,
  not a fat man's spread.
- A NATURALLY BIG BACKSIDE — heavy, wide and round, and seen from the side it
  sticks out as far as the gut does. His trousers pull tight across it and ride
  down at the back.

His arms and legs stay solid and reasonably lean — the weight is all in the
belly and the seat. The read is a big strong man who stopped moving, not a soft
round one. Do not make him spherical, do not make him waddle, do not give him a
double chin, do not round his shoulders into his neck.

=== THE UNIFORM — from the attached photograph of the two officers ===
Copy the GARMENT exactly, ignoring those men entirely:
- A DARK BROWN uniform shirt with a TAN YOKE — a panel of tan across the
  shoulders and upper chest, dipping to a point in the middle of the chest. This
  two-tone yoke is the most recognisable thing about the uniform; get it right.
- A tan necktie, tucked in.
- A gold star-in-shield patch on BOTH shoulders.
- Gold epaulettes with a brass button at the collar end.
- A gold six-point star badge on the left chest and a small name plate.
- A wide BLACK leather duty belt in basketweave, riding under the gut, hung with
  a holstered revolver, a radio and pouches.
- TAN trousers with a sharp crease, breaking over plain black leather boots.

=== THE TWO THINGS HE LOSES ===
- A TAN CAMPAIGN HAT — a wide flat-brimmed Smokey-Bear sheriff's hat with a
  pinched crown, worn dead level, brim wider than his shoulders are thick.
- MIRRORED TEARDROP AVIATOR SUNGLASSES, the lenses fully opaque and reflective,
  hiding his eyes completely. Catch a hot slash of the low sun in one lens.

=== POSE ===
FULL BODY, framed loose — the whole figure from the top of the hat to the soles
of the boots inside the frame, with clear ground beneath him. Do not crop the
hat and do not crop the boots. THREE-QUARTER VIEW, turned slightly away from
camera.

Standing beside his car with his weight settled back on one heel and thumbs
hooked into the duty belt either side of the buckle. Absolutely unhurried.
CARRY THE POSTURE INTO THE POSE: shoulders rolled forward, upper back curved,
head pushed forward of the shoulders, pelvis tipped so the gut leads and the
seat sits back. Chin slightly raised in spite of all that, because he is pleased
with the morning. A man who has never once been in a rush and does not expect
today to be different. Not menacing and not comic.

=== SETTING ===
A rural dirt road in high desert at mid-morning. Behind him, cropped by the frame
and softly out of focus, the front quarter of a cream-and-rust 1980s Crown
Victoria sheriff's cruiser with a single roof beacon. Do not render the car in
detail and do not let it compete — it is a shape and a colour behind him.

=== LIGHT ===
Hard warm low sun raking in from one side. A hot saturated RIM LIGHT along the
brim of the hat, one shoulder, the curve of the belly and the barrel of one arm,
cutting him off the background. His lit planes go hot and near-white gold; his
shadow side drives deep into saturated teal and indigo, nearly black under the
hat brim, under the gut and beneath the belt. Cool saturated bounce kicks back up
into the shadow side from the pale road.

PUSH THE CONTRAST FURTHER THAN FEELS COMFORTABLE. The failure mode on this kind
of sheet is a figure that stays mid-toned while only the background goes dark.
The brightest thing in the picture is his lit shoulder and the top of the hat
brim; the darkest is the shadow under the brim and beneath the belly, and they
are a long way apart.

=== RENDER ===
Painted 3D, matching the attached illustration exactly: hand-painted directional
gouache strokes over real dimensional form, brush marks left in, no smooth
digital gradients, no airbrush, no plastic CG shine, NO ink outlines, NO line
art. Shadows deeply and openly coloured — saturated teal and indigo, never grey
and never black-crushed. Matte surfaces throughout; the only gloss is the
aviator lenses and the polish on the boots and the badge.

PALETTE: paper-cream, sand, khaki, olive, sky-teal, terracotta, rust, coral,
golden, warm charcoal — never pure black. NO MINT and NO PALE AQUA-GREEN
anywhere; that hue is reserved elsewhere in this film.

=== AVOID ===
an obese man, a doughboy, a spherical body, a soft round body, a double chin,
a waddle, narrow or sloping shoulders, a belly wider than the shoulders, a lean
or slim build, a flat stomach, an athletic figure, a young man, a modern
police uniform, navy blue or black uniform, a baseball cap, a peaked cap, no hat,
clear or tinted glasses, visible eyes, a clean-shaven face, a beard, stubble,
sideburns past the ear, a rendered detailed car, a car competing with the figure,
scenery detail, crowds, other people, weapons drawn, a menacing pose, an action
pose, smooth digital gradients, airbrush, plastic CG shine, ink outlines, line
art, grey shadows, black-crushed shadows, low contrast, flat even lighting, mint,
aqua-green, text, labels, captions, watermarks, signatures.
```

---

## Sheet A2 — edit pass on Sheet A

Contrast is the one thing this model will not give on the first call — the same
failure the mom sheets hit and recorded. Per `concept/mom/mom_v1_arcane.prompt.md`
the two-stage edit is the technique that works: hand the image back and change a
named short list, rather than re-rolling and trading one success for another.

**Round 1 also needed the necktie added here; round 2 painted it first time**, so
the tie clause has been dropped and this pass is now contrast only. Run it before
Sheets B, C and D, because they all take Sheet A as a reference and inherit
whatever it looks like.

Attach the Sheet A output plus `boy_v3_arcane_b-backyard-dusk.png`.

```
Edit the attached illustration (IMAGE 1). Keep the CHARACTER and the COMPOSITION
completely unchanged — the same man, the same face, the same moustache, the same
heavy build and gut, the same tan campaign hat at the same angle, the same
mirrored aviators, the same dark brown shirt with its tan yoke, the same badge
and shoulder patch, the same duty belt, the same tan trousers and boots, the same
pose, the same cruiser behind him, the same framing.

IMAGE 2 is the contrast and paint target — the same film, the same artist.

Change exactly one thing:

DRIVE THE CONTRAST TO MATCH IMAGE 2. Right now the whole figure sits in one
   mid-tone band and the light is flat and even. It needs a hard directional sun:
   - Choose ONE side as the light side. On it, push the lit planes almost to
     WHITE-GOLD — the top of the hat brim, one shoulder, the top of the gut, one
     forearm, one thigh. These become the brightest things in the picture.
   - The other side goes DEEP and SATURATED — the shadow side of the shirt, under
     the hat brim, beneath the gut, under the belt and inside the trouser folds
     drive into saturated TEAL and INDIGO, nearly black. Not grey. Not brown.
     Coloured.
   - Add a hot rim of light along the edge of the hat brim, the shoulder and the
     curve of the belly, separating him from the background.
   - Deepen the cast shadow on the ground and drive it teal.
   The gap between the brightest and darkest points must be much larger than it
   is now. If it still looks evenly lit, it is not finished.

Do not change anything else. Do not restage, do not re-pose, do not re-frame, do
not redesign the uniform, do not alter the car.
```

---

## Sheet B — out of the ditch

The state that carries `sq050` through `sq080`. Run it with Sheet A attached as
a second ref so the man does not drift.

```
A character concept illustration for a 1993-set animated film: a full-length
portrait of a county sheriff who has just climbed out of a car wreck, painted in
exactly the style of the attached illustrations. Vertical 3:4.

=== SAME MAN AS THE ATTACHED SHERIFF SHEET ===
Identical face: mid-forties, thick dark wavy hair, heavy full dark 1980s
moustache, lean strong jaw, prominent nose, deep-set eyes. He must read instantly
as the same man in the same uniform, wrecked.

=== THE BUILD — big-framed, not fat ===
Read this carefully; it is the thing most likely to go wrong. He is NOT a
doughboy and NOT obese.

His FRAME is naturally big: TALL — 1.8 metres — and genuinely BROAD, wide across
the shoulders and the back, big-boned, long-limbed. That frame is what he was
born with and it never changes.

What twenty-five years in a car seat did to it is POSTURE and a GUT, in that
order:
- BAD POSTURE is the first thing you read in his silhouette. His shoulders roll
  FORWARD and down, his upper back curves over, his head carries forward of his
  shoulders on a thick neck, and his pelvis tips so the belly leads and the
  backside sits back and out. He is not standing up straight and he has not for
  a long time.
- A GUT — round, firm and low, sitting over the belt the way a beer gut does,
  pushing the shirt out below the chest and hanging a little over the buckle.
  **His shoulders are still wider than his belly.** It is a gut on a big man,
  not a fat man's spread.
- A NATURALLY BIG BACKSIDE — heavy, wide and round, and seen from the side it
  sticks out as far as the gut does. His trousers pull tight across it and ride
  down at the back.

His arms and legs stay solid and reasonably lean — the weight is all in the
belly and the seat. The read is a big strong man who stopped moving, not a soft
round one. Do not make him spherical, do not make him waddle, do not give him a
double chin, do not round his shoulders into his neck.

=== WHAT THE CRASH DID ===
- THE AVIATORS ARE GONE. His eyes are visible for the first time and they are
  small, pale and slightly stunned. Nothing on his face but the moustache.
- THE HAT IS MANGLED — still on his head but crushed out of shape, the brim
  bent up on one side and folded on the other, a split in the crown, coated in
  pale dust. It must still read as the same hat.
- EGG SALAD ON HIS FACE. A smear of pale yellow egg salad caught in the left
  side of the moustache and a second smear up one cheekbone, with a fleck on the
  eyebrow. Small, specific and completely unnoticed by him. Do not make it drip
  and do not turn it into slapstick — it is a detail, not a gag.
- THE UNIFORM IS WRECKED but still the same uniform: the dark brown shirt with
  its TAN YOKE panel across the chest, now untucked on one side, one sleeve torn
  open at the elbow, two buttons gone, the tan tie dragged round under one ear.
  The black basketweave duty belt has slipped low under the gut. Tan trousers
  filthy at the knees, one boot unlaced.
- PALE ROAD DUST over everything, heaviest down one whole side of him, and a
  long grass stain up the other.
- He is holding a full-length wooden-stocked rifle loosely in one hand, barrel
  down, as a plain dark shape — no mechanical detail, no readable make.

=== POSE ===
FULL BODY, framed loose — the whole figure from the top of the mangled hat to
the soles of the boots inside the frame, with clear ground beneath him. Do not
crop the hat, do not crop the boots. THREE-QUARTER VIEW.

Standing in the open at the lip of a drainage ditch, planted, slightly
lopsided, one shoulder lower than the other, breathing. Not comic, not beaten —
recalibrating. Something has just happened to him that he has not decided about
yet. The stillness is the point.

=== SETTING ===
The dry grass shoulder of a rural road in high desert, the lip of a drainage
ditch cutting across behind his boots. Do not render the crashed car — it is out
of frame entirely.

=== LIGHT ===
Hard warm low sun from one side. A hot saturated RIM LIGHT along the broken brim
of the hat, one shoulder, the gut and one arm. His lit planes go hot and
near-white gold; his shadow side drives deep into saturated teal and indigo,
nearly black under the brim and beneath the belly. Cool saturated bounce from the
pale road into the shadow side. The dust on him catches the light and reads
almost white where the sun hits it.

PUSH THE CONTRAST FURTHER THAN FEELS COMFORTABLE — brightest is the dust on his
lit shoulder, darkest is under the brim, and they are a long way apart.

=== RENDER ===
Painted 3D, matching the attached illustrations exactly: hand-painted directional
gouache strokes over real dimensional form, brush marks left in, no smooth
digital gradients, no airbrush, no plastic CG shine, NO ink outlines, NO line
art. Shadows deeply and openly coloured — saturated teal and indigo, never grey.
Matte throughout.

PALETTE: paper-cream, sand, khaki, olive, sky-teal, terracotta, rust, coral,
golden, warm charcoal — never pure black. NO MINT and NO PALE AQUA-GREEN.

=== AVOID ===
sunglasses, aviators, an intact hat, no hat, a clean uniform, a modern police
uniform, navy or black uniform, an obese man, a doughboy, a spherical body, a double chin, narrow shoulders, a
belly wider than the shoulders, a lean or athletic build, a flat stomach, blood, injuries, wounds, bruises, torn skin, a comic or slapstick
expression, a pratfall, a rendered crashed car, a detailed rifle, scenery detail,
other people, smooth digital gradients, airbrush, plastic CG shine, ink outlines,
line art, grey shadows, low contrast, flat lighting, mint, aqua-green, text,
labels, captions, watermarks, signatures.
```

---

## Sheet C — the flashback

Two seconds of sepia at `sq050-sh010`. Run with Sheet A attached.

```
A character concept illustration for a 1993-set animated film: a full-length
portrait of the SAME man in the attached sheriff sheet, twenty-five years
younger, as an American marine in Vietnam. Painted in exactly the style of the
attached illustrations. Vertical 3:4.

=== SAME FRAME, YOUNGER, SLIGHTLY LESS GUT ===
This is critical and it is counter-intuitive. The FRAME is identical to the
attached sheet and it is what bridges the two time periods:
- The SAME height — 1.8 metres — and the SAME genuinely broad, wide shoulders
  and big-boned long-limbed build.
- The SAME naturally BIG BACKSIDE, heavy and wide and sticking out behind him.
- The SAME bad posture already setting in: shoulders rolled forward, upper back
  curved, head carried forward of the shoulders.

**Do not make him athletic, do not make him slim, do not give him a V-taper or a
flat stomach.** He was always this shape. The cut depends on the silhouette
matching.

The ONE thing that is different: at twenty-three the GUT is smaller — present,
soft and there over the belt, but noticeably less than the man in the attached
sheet has. Twenty-five years put the rest of it on. Everything else about the
body is the same.

What else changes is only the FACE and the KIT:
- Early twenties. The same thick dark wavy hair, cut shorter at the sides. The
  same heavy dark moustache. No sun creases, no jowls, no grey — the face is
  smooth and young under it, and that is the only thing telling you the year.
- Sweat instead of dust. Wet hair at the temples.

=== THE KIT ===
- An M1 STEEL HELMET with a cloth cover, the chinstrap hanging loose and
  unbuckled, a rubber band around the cover with a spare cigarette pushed under
  it.
- A dull olive FLAK JACKET, open, bulky and square, over a sweat-soaked olive
  t-shirt.
- Olive jungle utility trousers, filthy, bloused into scuffed black-and-olive
  jungle boots.
- A full-length black rifle held across his body in both hands, low and ready,
  rendered as a plain dark silhouette shape — no mechanical detail, no readable
  make or model.
- NO sunglasses. NO sheriff's hat. NO badge. Nothing brown or tan from the
  uniform.

=== POSE ===
FULL BODY, framed loose — the whole figure from the top of the helmet to the
soles of the boots inside the frame, with ground beneath him. Do not crop the
helmet or the boots. THREE-QUARTER VIEW.

Stopped mid-movement and looking off past camera at something, jaw set, mouth
pulled into a hard flat working line — the salty, unimpressed, thousand-yard mug
of a man who has been wet for a month. Weight forward, shoulders up.

=== SETTING AND COLOUR — SEPIA ===
Elephant grass and a wall of jungle behind him, hot and blown out. **The whole
image is SEPIA** — desaturated into warm browns, ambers and bone, as though this
is a colour-degraded photograph from 1969. There is NO blue and NO teal anywhere
in this picture; the film's usual cool shadow colour is deliberately absent here,
because the absence of it is what marks the flashback.

Shadows go deep warm brown and near-black rather than teal. The lit planes go hot
amber and bone-white. Contrast still pushed hard — this is a high-contrast image
that happens to be monochromatic.

=== RENDER ===
Painted 3D, matching the attached illustrations exactly: hand-painted directional
gouache strokes over real dimensional form, brush marks left in, no smooth
digital gradients, no airbrush, no plastic CG shine, NO ink outlines, NO line
art. Matte throughout. Heavy film grain is acceptable here and only here.

=== AVOID ===
a slim build, an athletic build, a V-taper, a flat stomach, a lean young soldier,
a tall lanky figure, an obese man, a doughboy, a spherical body, narrow or
sloping shoulders, a different man, teal, blue, cyan, cool shadows, full colour, a
sheriff's uniform or hat or badge, sunglasses, modern military kit, body armour
plates, a detailed rifle, blood, wounds, combat action, explosions, other
soldiers, smooth digital gradients, airbrush, plastic CG shine, ink outlines,
line art, low contrast, mint, aqua-green, text, labels, captions, watermarks,
signatures.
```

---

## Sheet C2 — edit pass on Sheet C

Round 1 got the sepia, the helmet, the flak jacket, the M16A1 and the young face
right, and then **slimmed him down anyway** — the one thing the prompt called
critical. `build_sheriff_war` requires the silhouette to match the present-day
man or the cut reads as a different character. Edit rather than re-roll: the
sepia and the staging are good and a re-roll would trade them away.

Attach the Sheet C output plus the Sheet A output.

```
Edit the attached illustration (IMAGE 1). Keep almost everything exactly as it
is: the same sepia colour, the same warm monochrome palette with no blue and no
teal, the same jungle and elephant grass, the same M1 helmet with its loose
chinstrap, the same open flak jacket, the same sweat-soaked t-shirt, the same
jungle trousers and boots, the same rifle, the same pose, the same framing, the
same grain, the same young face and moustache.

IMAGE 2 is the SAME MAN twenty-five years later. Look at his body.

Change exactly one thing: HIS BUILD.

He is currently drawn as a lean, athletic soldier. He must be the same big heavy
man as in IMAGE 2 — that is the entire point of the shot, because this image cuts
directly against present-day footage of him and the silhouette has to match or he
reads as a different person.

- Give him a REAL GUT, round and heavy, pushing the sweat-soaked t-shirt out over
  his belt and forcing the open flak jacket to sit wide and hang away from his
  sides. The belly is the first thing you read in his silhouette.
- Thicken the neck until it is as wide as the jaw.
- Broaden the shoulders and the chest, and thicken the upper arms and forearms —
  heavy and solid, not muscular and cut.
- Widen the hips and thighs so the trousers pull across them.
- Keep him the same height and keep his head the same size.

He is a big heavy young man, not a fat one and not a soft one — solid, thick and
wide. Do not slim him. Do not give him a flat stomach. Do not make him athletic.

Change nothing else at all.
```

---

## Sheet D — expression board

Six heads keyed to shots the film contains. Run last, with Sheets A and B
attached.

```
A character EXPRESSION SHEET: six head-and-shoulders studies of the SAME man —
the sheriff in the attached sheets — painted in exactly their style. Landscape,
roughly 3:2.

=== READ THIS FIRST — ONE RULE THAT OVERRIDES EVERYTHING ===
NO TEXT AND NO PANEL LINES. There is not one single letter, word, number or
caption anywhere on this image. Do NOT label the cells. Do NOT name the
expressions. Do NOT write "PURE BLISS" or "THE SALTY MUG" or anything else. Do
NOT draw a grid, a border, a frame or a dividing rule between the cells — they
are separated by EMPTY BACKGROUND ONLY. This sheet gets loaded into 3D software
as a bare plate; writing and rules land on top of the model and ruin it.

=== LAYOUT ===
Six cells in a 3-wide by 2-tall grid, generous even margins, each cell separated
by EMPTY BACKGROUND ONLY. No panel lines, no dividers, no frames, no boxes, no
captions, no labels, no numbers, no text of any kind anywhere on the sheet.
Same character, same scale, same camera distance and the same three-quarter head
angle in every cell. Head and shoulders only, cut off at the chest.

=== THE CHARACTER — identical in all six ===
Mid-forties, thick dark wavy hair swept back and over the ears, a heavy full dark
1980s moustache covering the top lip and running past the corners of the mouth,
lean strong jaw, prominent straight nose, small deep-set eyes under heavy dark
brows, weathered sun-creased skin. The dark brown uniform shirt with its TAN YOKE
panel and a tan tie at the collar.

He is a big-framed man with BROAD shoulders and a thick neck, and his head
carries FORWARD of his shoulders on it — bad posture, visible even in a
head-and-shoulders crop. His face is not fat: the jaw is still strong and there
is no double chin. A heavy man's neck on a lean man's jaw.

=== THE SIX ===
1. PURE BLISS — eyes closed, head tipped back, moustache lifted by a wide
   closed-mouth smile of total private contentment. He is eating a sandwich and
   nothing else exists. Wearing MIRRORED TEARDROP AVIATORS pushed up onto his
   forehead above the closed eyes.
2. STOPPED DEAD — the mangled hat on, no glasses, dusty. Eyes wide open and
   fixed, mouth slightly open under the moustache, every muscle stopped at once.
   He has just seen something over the lip of a ditch and has not processed it.
3. "…DANNY?" — the same dusty face, but broken. Brows driven up and together,
   eyes glassy and unfocused, mouth open and shaped around a name he is barely
   saying. Twenty-five years arriving at once. This is the most vulnerable he
   gets and it should be uncomfortable to look at.
4. THE SALTY MUG — younger by twenty-five years, under an M1 helmet, sweating.
   The face puckered into a hard flat unimpressed working line, jaw set, eyes
   narrowed. Sepia — this cell alone is warm monochrome, no teal.
5. THE TWITCH OF RECOGNITION — dusty and hatless. The stunned mask cracking:
   brows lifting, eyes focusing properly for the first time, mouth going slack
   as it lands. He has just worked out he has been in a gunfight with a child and
   his mother. Dawning horror, not anger.
6. HAT OFF IN APOLOGY — holding the crushed hat against his chest, out of frame
   at the bottom. Hair flattened into a hat ring, forehead pale where the brim
   sat and the rest of the face weathered dark. A rueful, sheepish, closed-mouth
   smile, eyes down and to one side. Caught being ridiculous and taking it well.
   A little EGG SALAD still in the moustache that he has not noticed.

=== RENDER ===
Painted 3D, matching the attached illustrations: hand-painted directional gouache
strokes over real dimensional form, brush marks left in, no smooth gradients, no
plastic CG shine, no ink outlines, no line art. High contrast — deep near-black
shadow masses against hot luminous lit planes. Shadows deeply and openly
coloured, driving into saturated teal and indigo, never grey. Warm saturated key
from one side, cool saturated fill, matte throughout.

Consistent lighting across all six cells so the sheet reads as one shoot, except
cell 4, which is sepia.

=== BACKGROUND ===
Plain flat neutral field, slightly warm, empty. No scenery, no props, no
gradients, no vignette, no borders, no drop shadows.

=== AVOID ===
panel lines, dividers, boxes, captions, labels, numbers, text, watermarks,
different men between cells, drifting facial structure, drifting moustache shape,
a clean-shaven cell, a beard, different scale between cells, a modern police
uniform, navy or black uniform, blood, wounds, photorealism, airbrush, ink
outlines, low contrast, grey shadows, mint, aqua-green.
```

---

## Sheet D2 — edit pass on Sheet D

Two rounds, and each lost what the other won. **Round 1** matched the man —
heavy dark wavy hair, the ref's jaw, the same face as Sheets A and B — but
captioned every cell, drew a black grid, and hyphenated "RECO-GNITION" across a
line break. **Round 2**, with `NO TEXT` hoisted to the top, dropped the grid and
set the captions cleanly below each cell, and drifted his face to a thinner,
lighter-haired, generic leading man that no longer matches the other sheets.

Identity beats layout on a character sheet, so **round 1 is the keeper** and the
text comes off by edit pass. Attach the round-1 output only.

```
Edit the attached illustration. This is a six-cell character expression sheet.

Keep all six painted heads EXACTLY as they are — the same six faces, the same
expressions, the same moustache, the same hats and helmet and sunglasses, the
same sandwich, the same colours, the same lighting, the same sepia in the
bottom-left cell, the same positions, the same sizes. Do not repaint, redraw,
restyle or move any part of any head. Do not change the background colour.

Change exactly two things, both of them removals:

1. REMOVE ALL TEXT. Every caption is deleted — the words in the top-left corner
   of each of the six cells, all of them, every letter. Where a caption was,
   there is now only the plain flat background that surrounds it. No text
   remains anywhere on the image.

2. REMOVE THE PANEL LINES. Delete the black rules that divide the six cells —
   the two vertical lines and the one horizontal line — and the border around the
   outside if there is one. Fill what was behind them with the same plain flat
   background. The six heads are then separated by empty background only.

Nothing else changes. Do not add anything. Do not re-letter, do not re-caption,
do not add a title.
```

---

## What came back — ROUND 1 (superseded, kept in `round1/`)

**Generated 2026-08-06.** Seven calls: A, an A2 edit, B, C, a C2 edit, two Ds and
a D2 edit.

**Superseded the same day** by Ian's build note — round 1 read as an all-over fat
man. The images are kept in `round1/` because the staging, the uniform and the
expression beats were all right and only the body was wrong; `round1/` also holds
`sheriff_v1_faces_alt-drifted.png`, the second D attempt whose face drifted off
model.

| image | size | state |
|---|---|---|
| `sheriff_v1_a-first-sighting.png` | 3584 × 4800 | crisp, hat, aviators. Two-stage: A then A2. |
| `sheriff_v1_b-out-of-the-ditch.png` | 3584 × 4800 | wrecked, no glasses, egg salad. One call. |
| `sheriff_v1_c-flashback.png` | 3584 × 4800 | sepia, M1 helmet. Two-stage: C then C2. |
| `sheriff_v1_faces.png` | 5056 × 3392 | six expressions. Round 1 kept, text removed by D2. |

### The edit pass is doing all the work

Three of the four sheets needed one, and in every case it fixed the named fault
without disturbing anything else — which re-rolling never manages. This is now
the third character to prove it out. **Reach for the edit pass second, always.**

| sheet | what round 1 got wrong | what the edit fixed |
|---|---|---|
| A | Open collar with a white undershirt; contrast flat and even | Added the tan necktie; pushed the lit planes to near-white and put a rim on the hat brim, shoulder and belly |
| C | **Slimmed him to a lean athletic soldier** — the one thing the prompt called critical | Gave him the gut, thick neck and heavy shoulders back, and left the sepia, helmet, rifle, pose and grain untouched |
| D | Captioned every cell, drew a black grid, and hyphenated "RECO-GNITION" across a line break | Removed all six captions and all three rules, keeping the six painted heads exactly as they were |

### Round 2 of D is a warning worth keeping

Hoisting `NO TEXT` to the top of the prompt worked — round 2 dropped the grid and
set its captions cleanly — but **his face drifted** to a thinner, lighter-haired,
generic leading man that no longer matched Sheets A and B. Round 1 matched the
`N150_0030_018` man properly. **Identity beats layout on a character sheet**, so
round 1 was kept and the text taken off by edit. Round 2 is in the scratch, not
the repo.

### What is right

- The **build** landed first time and held across all four sheets: a big heavy
  man with a real gut, which `build_sheriff` requires and the butt-crack runner
  depends on. Naming the 0.30 m belly ball and saying "do not take the
  photograph's build" is what did it.
- The **uniform** is correct from the ref: dark brown shirt with the tan yoke,
  tan tie, gold star patch and badge, black duty belt, tan trousers.
- **The three states read apart instantly** — glasses on, glasses gone, helmet —
  which was the whole point of splitting them.
- Cell 6 of the expression board put the **egg salad in his moustache unasked**
  beyond the one line describing it, and the hat-ring in the hair is there too.
- Sheet C's sepia is total. No blue, no teal, exactly as specified — the absence
  of the film's cool shadow colour is what marks the flashback.

### Known deviations, live

- **Contrast never reaches the boy's v3 range.** Same ceiling the mom sheets hit
  and recorded; one edit pass moved Sheet A most of the way and B and C settled
  flatter. The shadows go deep but they stay brown rather than driving into
  saturated teal and indigo.
- **The egg salad on Sheet B is bigger than "small and specific"** — it reads as
  a splat on the cheek rather than a smear nobody noticed. The expression board's
  version is the better one.
- **Sheet B's expression is angrier than written.** The brief said recalibrating,
  not aggressive. Not worth a round, since the expression board covers his actual
  beats.
- **The rifles are rendered in more detail than "a plain dark shape".** Both are
  right for the canon — the M16A1 in the flashback, the wood-stocked M14 out of
  the ditch — so they were left.
- Sheet B rolls the sleeve rather than tearing it at the elbow.
- A faint tonal seam survives on the expression board where the panel rules were.

### Not done

**No modelling references yet, and no Blender scene.** These are concept sheets,
the same stage the mom reached before `mom_modelsheet.prompt.md`. The model sheet
derives from whichever of these is accepted — the same order the boy and the mom
went.

---

## What came back — ROUND 2, current

**The build note, 2026-08-06 — Ian:** *"He needs to be thinner. A gut is fine but
he isn't a total dough boy. He is naturally tall and wide shouldered but has bad
posture and a gut. His butt is naturally big too, hence the buttcrack. This will
make it easier to bridge his looks between nam and present day."*

Five calls: A, an A2 contrast edit, B, C, D. **No C2 and no D2 this round** — the
two faults that needed edit passes in round 1 did not recur once the build block
was rewritten.

| what changed | result |
|---|---|
| The `THE BUILD — big-framed, not fat` block replaced the old "BIG and HEAVY" line in all four sheets | Shoulders now read wider than the belly, the gut sits low rather than spreading, the head carries forward, and the legs lengthened |
| Sheet A's pose now carries the posture explicitly | Rolled shoulders and a forward head, still chin-up and pleased with himself |
| Sheet C reframed from "same body" to "same frame, smaller gut" | **The bridge works.** He reads as the same man at twenty-three — same shoulders, same seat, less belly — where round 1 had to be edited to stop him being athletic |
| `NO TEXT` hoisted to the top of Sheet D | Captions and panel rules gone first time; no D2 needed |

### What round 2 fixed for free

- **The necktie painted itself in on Sheet A**, so the A2 edit is now contrast
  only. Round 1 needed it added by hand.
- **Sheet B's expression** is stunned rather than angry, which is what the brief
  asked for and round 1 missed.
- **Sheet B tears the sleeve at the elbow** this round instead of rolling it.
- **Sheet D holds identity across all six cells** and against the full-figure
  sheets, which was exactly what round 1's second attempt lost.

### Known deviations, live

- **Contrast is at its ceiling.** The A2 pass barely moved the image this time —
  the first round got a real improvement from the same prompt, this one did not.
  Shadows go deep but stay brown rather than driving into saturated teal and
  indigo. Same wall the mom sheets hit. Not worth further calls.
- **Sheet B loses the necktie** — his collar is open over a white undershirt
  where Sheet A has him in a tan tie. Defensible for a man who has just crawled
  out of a wreck, but it is not what the prompt says (it asks for the tie
  "dragged round under one ear"), so it is a continuity choice somebody should
  make on purpose.
- **The egg salad is still bigger than "small and specific"** on Sheet B — a
  yellow splat on the cheek rather than a smear he has not noticed. There is now
  also a smear down his shirt front, which is unasked and good. The expression
  board's fleck-in-the-moustache remains the better read.
- **Sheet B is drawn from a slightly high angle**, looking down at him, which
  costs some of the height the build note is trying to establish.
- **Sheet D's faces run leaner and younger** than the full-figure sheets. They
  are consistent with each other, so the sheet works, but a head from D next to
  the body from A is not quite the same age.
- The cruiser competes for attention on Sheet A more than "a shape and a colour
  behind him" intends.

### Still not done

**No modelling references and no Blender scene** — same as after round 1. The
model sheet derives from whichever of these is accepted, the order the boy and
the mom both went.
