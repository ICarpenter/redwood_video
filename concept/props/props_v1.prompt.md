# props — L3 hero sheets, v1

**Generated 2026-08-06, Nano Banana Pro (`gemini-3-pro-image`) via the Gemini
API.** Seven rounds, seventeen calls — the printer took most of them.

These are **design documents, not mood pieces** — somebody hand-models these, so
the prompts trade drama for legibility: object alone on a flat warm-grey field,
key light for clarity rather than effect, enough coloured bounce that no part
falls into darkness. A deliberate departure from how the character and location
sheets are lit, and **the recipe to reuse for any prop sheet.**

| image | asset | `props.md` |
|---|---|---|
| `prop_printer.png` | `printer` | §4, L3 — the film's biggest mechanism |
| `prop_printer_scale.png` | `printer` | scale + packaging companion: assembled machine, its carton, and the boy at one scale |
| `prop_santa.png` | `santa` | §6, L3 |
| `prop_kid_gun.png` | `machine_gun` | §9, L3 |
| `prop_mom_gun.png` | `rosco` — **silver 9mm** | §9, L3 |
| `prop_cop_gun.png` | `cop_rifle` — **M14** | §9, L3, reinstated 2026-08-06 |
| `prop_gun_lineup.png` | all three, one scale | the silhouette test |
| `prop_mom_gun_aug_superseded.png` | — | **Superseded.** The Steyr AUG bullpup from round 1, before the silver 9mm call. |

## Ian's direction

**Round 1, 2026-08-06**

- **Santa** — face from `refs/santa/santa1.jpeg`: a plastic *moulding* of a face,
  not a face. Painted features off-register from the moulded relief so the smile
  is slightly wrong. **The head rotates independently.**
- **Printer** — a beige 1993 HP LaserJet scaled up. **Materialises objects out of
  thin air from nanoparticles.**
- **Guns, and the three must read apart at silhouette** — boy's overdone like a
  toy; Mom's sleek Die Hard terrorist; sheriff's era standard issue, the M14's
  wood being what sets it apart.

**Round 2, same day** — after seeing round 1:

- **Mom's gun during the shootout is a silver 9mm.** Supersedes the AUG.
- **The sheriff has an M14 for sure.** Docs updated.
- **Printer** — look and art style approved and kept. But it must be **open on
  its left side** and use a **conveyor belt to extend its printing range**,
  keeping a **partial glass enclosure** and the buttons.
- **Another pass on Santa.**

**Rounds 3 and 4, same day**

- The printer *did not make spatial sense* — open on one side, ejecting from another,
  viewed from a third. Fresh generate, with the conveyor as the **whole floor of
  the print chamber**, the glass **arching over it**, and **several robot styli
  hanging in the chamber ready to print matter**.
- Then a **scale cue**: it must read as something delivered on a truck and
  assembled, and **the kid has to be able to push its box**.

**Rounds 5–7, same day** — Ian did the volume arithmetic and the machine was
about **13× the carton**. Machine shrunk, crate grown; see the printer section.

## The three-way material split

The strongest idea in the batch, now recorded in `props.md` §9:

**big dull plastic toy → small bright silver → long wood and blued steel.**

Three sizes, three materials, three finishes, three characters — legible with
the colour turned off. `prop_gun_lineup.png` exists to prove it, and it does.

## Conflicts with the existing docs — two resolved, one open

**RESOLVED — the sheriff's rifle.** `props.md` §9 had `cop_rifle` explicitly
*cut*, on the grounds that his firefight gun was the comically large pistol.
Ian reinstated it. **`props.md` has been updated**: `cop_rifle` is back as an L3
M14, and a new *"The three weapons must read apart"* section records the split.

**RESOLVED — Mom's rack.** Round 1's AUG was a bullpup with a charging handle,
and the script had her rack the gun **with her teeth** because the oven mitts
left her no fingers. The silver 9mm fixes the mechanism by construction — it has
a real slide, and the sheet gives it oversized rear serrations. **Superseded
2026-08-06:** the mitts are dead film-wide and the teeth gag went with them
(`style.md` § Characters, `script.md` `sq050-sh040`). She racks it one-handed
with bare fingers and painted nails. The serrations still earn their keep — they
now read as grip rather than as something to bite.

**STILL OPEN — `big_pistol` and "the comically large gun".** `guns-script.md`
has the 'Nam flashback and then *"out comes a comically large gun"* at
`sq050-sh020`. `props.md` now lays out three resolutions and recommends the
first: **the M14 *is* the comically large gun** — a full-length wood service
rifle in a suburban backyard, which lands the flashback in the same beat and
lets `nam_rifle` and `cop_rifle` collapse into one asset. Nothing in
`script.md` or `guns-script.md` has been rewritten pending that call.

**STILL OPEN — the printer's mechanism.** `props.md` §4 specifies *"it extrudes
downward onto a low bed at floor level — soft-serve, per `sq020-sh010`"*, and
`guns-script.md` writes the beat as *"the printer extrudes a machine gun like
soft-serve — one long continuous squeeze the boy snaps off the bed."*
**Nanoparticle materialisation plus a conveyor kills the soft-serve gag.** The
bell flick on the lyric survives; the extrusion does not. `sq010-sh060` and
`sq020-sh010` want rewriting if this design stands — and the conveyor does
answer §4's hard requirement that the machine produce a 1.8 m figure, by
carrying the object out as it builds instead of needing a 1.9 m chamber.

## Refs attached

`concept/boy/boy_v3_arcane_b-backyard-dusk.png` is the style target on every
call except the printer edit. Per sheet: `refs/santa/santa1.jpeg` (the moulded
face) and `refs/santa/8996346_IMG2486.jpeg` (the figure);
`refs/printer/images.jpeg`; `refs/3d printed gun/…cassette-futurism….webp`;
`refs/cop rifle/m14_lede.jpg`. `mom_gun` and `gun_lineup` ran on text alone.

---

## Shared preamble — every sheet except the printer edit

```
A PROP DESIGN SHEET for a 1993-set animated film. One object, presented for a
modeller to build from. Horizontal 4:3.

=== WHAT THIS IS FOR ===

This is a design document, not a mood piece. Somebody is going to hand-model
this object from this image, so the DESIGN MUST READ: every part, every join,
every mechanism clearly visible and clearly described in paint. Beauty is
second, legibility is first.

The attached illustration of the blond boy is the STYLE TARGET — same film,
same artist. Match its technique exactly: real dimensional form with every
surface visibly HAND-PAINTED in thick loaded directional gouache strokes, brush
marks left in. NO smooth digital gradients, NO airbrushed surfaces, NO soft
blended shading, NO plastic CG shine, NO ink outlines, NO line art. Take its
technique and palette ONLY — do not take its subject, its character, its pose,
its setting or its dramatic backlight.

=== PRESENTATION ===

The object sits alone, filling most of the frame, on a PLAIN FLAT WARM-GREY
FIELD. Empty background. No scenery, no room, no floor, no horizon, no
gradient, no vignette, no drop shadow, no cast shadow on the ground.

LIGHTING IS FOR CLARITY, not for drama: one warm key from the upper left giving
honest form and a clear lit/shadow split, with enough coloured bounce in the
shadow side that EVERY PART OF THE OBJECT STAYS READABLE. Shadows go saturated
teal, never grey and never black-crushed. Do not silhouette the object, do not
backlight it, do not throw half of it into darkness.

Matte throughout. Any gloss is a described material, never a rendering effect.

PALETTE — hue anchors at their saturated and deep extremes:
  paper-cream #f2e4cc   sand #d9c0a3        khaki #c2a878
  olive #8f7a3d         sky-teal #3fbdb3    terracotta #b0764a
  rust #c95f33          coral #f0a082       golden #eec078
  warm charcoal #42403b (never pure black)
1993 objects use the quieter set: charcoal-plastic #42403b,
faded-denim #7d94a8, mall-mauve #a98794, seafoam-grey #9db8ac.

NO mint and NO pale aqua-green anywhere — reserved elsewhere in this film.

=== PERIOD ===
1993, painted deadpan by a 1962 poster artist. The medium never acknowledges
the anachronism.
```

## Shared closing block — same scope

```
=== NO PEOPLE ===
No people, no hands, no fingers holding the object, no figures, no faces except
where the object itself has a moulded face. Nothing living.

=== AVOID ===
people, hands, figures, scenery, rooms, floors, horizons, backgrounds,
environmental context, dramatic backlighting, rim-lit silhouettes, half the
object lost in shadow, smooth digital gradients, airbrushed surfaces, soft
blended shading, plastic CG shine, photorealism, depth-of-field blur, low
contrast, grey or neutral shadows, ink outlines, line art, mint or aqua-green,
captions, labels, callout lines, arrows, dimension lines, measurement marks,
grids, watermarks, signatures.
```

---

## printer — round 1

```
=== THE OBJECT — the boy's 3D printer ===

A domestic 1993 desktop LASER PRINTER — unmistakably a beige Hewlett-Packard
LaserJet of that era — SCALED UP into a huge appliance the size of a tall
wardrobe. That joke is the entire design: it is shaped, coloured and detailed
exactly like the office printer everyone remembers, just enormous.

Keep every LaserJet cue and enlarge it:
- Warm beige and putty plastic, slightly yellowed with age, with softly rounded
  corners and broad flat body panels.
- Wide horizontal seams and panel gaps, a big front-hinged access door, and
  moulded ventilation louvre slots.
- A control panel with chunky mechanical buttons under a toggle guard, a small
  amber-green LCD strip, and a row of little indicator lights.
- Cassette-futurism detailing per the film: ribbon-cable looms, wood-grain
  veneer on the side panels, warm beige and amber rather than chrome and blue.

TWO THINGS MAKE IT NOT A PRINTER, and both must read clearly:

1. **IT MATERIALISES OBJECTS OUT OF THIN AIR.** Its upper body is a tall glass
   build chamber, and inside that chamber a swarm of glowing NANOPARTICLES
   hangs in empty space and coalesces into the object being made. Paint the
   swarm as a drift of fine bright motes, densest where the object is forming,
   thinning to nothing at the edges — the shape half-resolved, solid at the
   bottom and still a cloud of particles at the top. Nothing extrudes, nothing
   squeezes out of a nozzle, there is no filament and no print head. The object
   simply assembles itself out of the air. The particle glow is the only light
   the machine makes.
2. **THE OUTPUT SLIDES OUT OF THE SIDE ON A TRAY.** A wide motorised tray, like
   an enormous paper tray, is extended out from the side of the machine on
   visible rails, with a finished object lying on it. Show the tray fully open,
   the rails and their travel clearly visible, and the seam in the body panel it
   slides out of.

The build chamber must be TALL — it has to make a human-sized figure — so the
machine reads as a floor-standing appliance, well over head height.

Present it in a clear THREE-QUARTER VIEW that shows the front face, the control
panel, the glass chamber with its particle swarm, and the open side tray all at
once.
```

## printer — round 2, an EDIT of the approved image (superseded)

Ran as an edit rather than a re-roll because the look was approved. It kept
every material and detail it was told to, **but the result did not make spatial
sense**: the machine was open on one side, the finished object came out of the
other, and the camera was on a third. Superseded by round 3.

```
Edit the attached illustration (IMAGE 1). The look is approved — keep it.

KEEP EXACTLY AS THEY ARE: the beige HP-LaserJet body and its warm putty
plastic, the wood-veneer side panel, the control panel with all its chunky
buttons and its amber-green LCD strip, the indicator lights, the palette, the
visible gouache brushwork, the lighting, the flat warm-grey background, and the
glowing nanoparticle swarm that materialises the object out of thin air.

Change only the machine's ARCHITECTURE, in two ways:

1. **OPEN THE LEFT SIDE.** The left flank of the machine has no wall. The build
   volume is open straight out to the air on that side — you can see into the
   build area unobstructed. Keep a PARTIAL GLASS ENCLOSURE only: glass across the
   back and over the top of the build volume, with a clean cut edge where it
   stops. Not a sealed box. The right side, the base cabinet and the control
   panel stay solid and unchanged.

2. **REPLACE THE SLIDING TRAY WITH A CONVEYOR BELT.** A proper industrial
   conveyor runs out of that open left side: a wide belt over visible steel
   rollers, on a slim frame with legs, extending well past the body of the
   machine and out of frame. It exists to EXTEND THE MACHINE'S PRINTING RANGE —
   the object is built inside the open volume and carried out along the belt as
   it goes, so the machine can produce something far longer than itself. Show a
   long finished object lying along the belt, partway out, with the near end of
   it still inside the build volume and still half-resolved into nanoparticles.

The read should be: an open-sided machine that assembles things out of the air
and walks them out sideways on a belt.

Change nothing else. Do not restyle, do not relight, do not recolour, do not
reframe, do not smooth the brushwork, do not redesign the control panel.
```

## printer — round 3, a fresh generate (the keeper)

Ian's spec: the conveyor is the **whole floor of the print chamber**, the glass
cover **arches over it**, and **several robot styli hang in the chamber ready to
print matter**. Run fresh rather than as an edit, with the round-2 image
attached for materials and panel detailing only — explicitly *not* for layout.

The fix for the incoherence was to state the three sight lines as one
non-negotiable rule and make them agree: **the left end is open, the object
exits that same left end, and the camera is on the left looking into it.** Every
wrong alternative went into AVOID by name — an opening on the right, an object
exiting the right or the back, more than one opening.

```
A PROP DESIGN SHEET for a 1993-set animated film. One machine, presented for a
modeller to build from. Horizontal 4:3.

IMAGE 1 is the approved version of this machine. **Take its MATERIALS, COLOUR,
PANEL DETAILING and PAINT QUALITY exactly** — the warm beige and putty plastic,
the wood-veneer panel, the chunky mechanical buttons, the amber-green LCD strip,
the little indicator lights, the small hp badge, the visible gouache brushwork,
the flat warm-grey background and the lighting. **Do NOT take its layout** — the
architecture below replaces it completely.

IMAGE 2 is the film's style target. Match its painted technique: real
dimensional form, every surface visibly HAND-PAINTED in thick loaded directional
gouache strokes, brush marks left in. NO smooth digital gradients, NO airbrushed
surfaces, NO soft blended shading, NO plastic CG shine, NO ink outlines, NO line
art. Technique and palette only — not its subject, character or backlight.

=== READ THIS FIRST — THE LAST VERSION DID NOT MAKE SPATIAL SENSE ===

In the previous attempt the machine was open on one side while the finished
object came out of the other, and the camera was on a third. **This image must
be geometrically coherent. Three things have to agree, and they are the whole
brief:**

1. The machine's **LEFT END IS OPEN.**
2. The finished object **COMES OUT OF THAT SAME OPEN LEFT END.**
3. The **CAMERA IS ON THE LEFT**, three-quarters on, looking into the open left
   end and slightly down.

So we are looking straight into the open mouth of the machine, along the line
the work travels, and we can see all the way inside it. Nothing exits the right,
nothing exits the back. There is exactly one opening.

=== THE MACHINE ===

A 1993 beige HP LaserJet office printer, scaled up into a floor-standing
industrial machine. It reads as that printer's bigger cousin: same warm putty
plastic, same rounded corners, same broad panel seams and moulded louvre vents,
same wood-veneer flank.

**THE BODY IS AT THE RIGHT END.** The solid part of the machine — the base
cabinet, the electronics housing, the wood-veneer flank and the CONTROL PANEL
with its chunky buttons, amber-green LCD and indicator lights — is all massed at
the far RIGHT end of the object, furthest from camera. That is the head of the
machine. Keep it exactly as detailed as in IMAGE 1.

**THE CONVEYOR BELT IS THE ENTIRE FLOOR OF THE PRINT CHAMBER.** There is no
separate bed, no tray and no platform. A wide flat industrial belt on visible
steel rollers runs the full length of the machine — it begins inside, under the
body at the right, travels the whole chamber, and continues straight out
through the open left end on its own slim steel frame with legs, extending well
past the machine and toward camera. The object being printed is built directly
onto that moving belt and is carried out on it, which is how the machine makes
things far longer than itself.

**AN ARCHED GLASS HOOD COVERS THE CHAMBER.** A single curved transparent glass
canopy ARCHES OVER the belt from one long side to the other — a smooth
half-tunnel vault, like the lid of a printer or a chafing dish, with slim beige
frame ribs at intervals. It springs from the machine's side rails and covers the
chamber's length, but it **STOPS SHORT AT THE LEFT AND THE END IS FULLY OPEN**,
a clean cut mouth with a beige trim lip, so the belt and its work travel straight
out from under the arch. Partial enclosure only — never a sealed box, never a
door.

**SEVERAL ROBOT STYLI HANG IN THE CHAMBER.** Under the crown of the glass arch,
a row of four or five slender articulated ROBOT ARMS hangs DOWN from an overhead
rail, evenly spaced along the chamber, each tipped with a fine needle-like
STYLUS pointing at the belt below. They are poised and waiting — hanging at
slightly different heights and slightly different angles, like a row of dentist
arms or a spider's legs. Slim beige-and-charcoal segments, visible pivot joints,
thin ribbon cables looping up to the rail. They are the most characterful thing
inside the machine, and being able to count them matters.

**THE MATTER FORMS FROM THIN AIR.** Beneath the stylus tips a swarm of glowing
NANOPARTICLES hangs in empty space over the belt and coalesces into the object.
Paint the swarm as a drift of fine bright motes, densest right under the styli
where matter is forming and thinning to nothing outward. The object should read
half-made: solid and finished where it has already travelled out toward the open
left end, dissolving into loose particles at the end still under the styli.
Nothing extrudes, nothing squeezes from a nozzle, there is no filament and no
print head touching anything. The particle glow is the only light the machine
makes.

Lay a long object along the belt so the whole process reads left to right in one
look: **finished, out in the open air at the left → half-formed under the styli →
still a cloud of particles at the right.**

=== PRESENTATION ===

The machine sits alone, filling most of the frame, on a PLAIN FLAT WARM-GREY
FIELD. Empty background. No scenery, no room, no floor, no horizon, no gradient,
no vignette, no cast shadow on the ground.

LIGHTING IS FOR CLARITY, not drama: one warm key from the upper left giving
honest form and a clear lit/shadow split, with enough coloured bounce in the
shadow side that EVERY PART STAYS READABLE — especially inside the chamber,
which must not go dark. Shadows go saturated teal, never grey, never crushed.
Do not silhouette the machine and do not backlight it.

Matte throughout, except the glass, which is genuinely transparent — we must see
the styli and the particle swarm clearly through it, with only a couple of
restrained painted highlight streaks to say "glass".

PALETTE — hue anchors at their saturated and deep extremes:
  paper-cream #f2e4cc   sand #d9c0a3        khaki #c2a878
  olive #8f7a3d         sky-teal #3fbdb3    terracotta #b0764a
  rust #c95f33          coral #f0a082       golden #eec078
  warm charcoal #42403b (never pure black)
NO mint and NO pale aqua-green anywhere — reserved elsewhere in this film.

=== PERIOD ===
1993, painted deadpan by a 1962 poster artist.

=== NO PEOPLE ===
No people, no hands, no figures, no faces. Nothing living.

=== AVOID ===
an opening on the right, an object exiting the right side, an object exiting the
back, more than one opening, a sealed glass box, a hinged door, a flat glass lid,
a separate print bed or tray or platform, a nozzle, an extruder, a filament
spool, a print head touching the object, a dark unreadable interior;
people, hands, figures, scenery, rooms, floors, horizons, backgrounds,
dramatic backlighting, rim-lit silhouettes, smooth digital gradients, airbrushed
surfaces, soft blended shading, plastic CG shine, photorealism, depth-of-field
blur, low contrast, grey or neutral shadows, ink outlines, line art, mint or
aqua-green, captions, labels, callout lines, arrows, dimension lines, grids,
watermarks, signatures.
```

## printer — rounds 4–7, the scale correction

### The error

Round 4's scale sheet put a scale figure beside the machine for the first time,
and the moment it had a size, the packaging stopped working. Ian caught it:

- machine as drawn ≈ 1.8 m × 4 m × 1.2 m ≈ **8.6 m³**
- carton as drawn ≈ 1.0 × 0.8 × 0.8 ≈ **0.64 m³**

**About 13×.** The "it ships flat-packed in one carton" claim had been asserted
without ever doing the arithmetic.

### The fix

The mistake was letting the glass vault grow walk-in sized. **The chamber only
ever needs the cross-section of what it prints, not the length** — a 1.8 m figure
lying down needs maybe 0.6 m wide by 0.5 m tall, and the *belt travel* supplies
the length. Three bays of glass tunnel were doing work one hood does.

So: shrink the machine, grow the crate.

| | corrected |
|---|---|
| glass hood | ONE low continuous shell, chamber barely longer than wide |
| height | arch top at the boy's **shoulder**; it stands on slim legs |
| body | compact cabinet, chest height on the boy, household-appliance sized |
| conveyor | the only long part, an open skeleton carrying no volume, telescoping to a third of its length |
| crate | fridge-crate, **taller than the boy** — the largest single mass on the sheet |

That lands packed volume near 0.6 m³ into a ~1.3 m³ crate. Roughly 1.5–2×
instead of 13×, which nobody audits. The taller crate is better for the story
too: `sq010-sh045`'s lean-over-the-rim becomes a stretch he has to work for, and
four shoves makes more sense against something that size.

**Rejected alternatives.** Multiple crates solves it honestly but spends the
single-box beat the script is built on. Making the box a bag-of-holding is
on-theme for a film where matter appears from nothing, but it is a
cartoon-physics register and this style's whole move is deadpan serenity about
the impossible.

### The prompt that kept failing

**"One arch bay, not three" was ignored three rounds running.** Counting
instructions did not work; neither did banning "tunnel". What worked was
describing the hood as **a single object by analogy** — *the clear lid on an
office photocopier, the curved sneeze guard on a deli counter, one continuous
curved shell framed only at its outer rim* — plus a hard test the model could
apply to its own output: *"if you can count more than one arch shape, the
drawing is wrong."* Then banning `repeating arches, a row of ribs, multiple
bays, a vaulted tunnel, a cathedral roof`.

Round 6 also came back wearing a real **HP logo and the word LaserJet**. Named
and banned; gone in round 7.

### Scale sheet — `prop_printer_scale.png`

```
A PROP DESIGN SHEET for a 1993-set animated film — a SCALE AND PACKAGING sheet.
Horizontal 4:3.

IMAGE 1 is the approved design of this machine. **Keep it exactly** — the same
arched glass hood over the conveyor, the same row of hanging robot styli, the
same open left end, the same beige HP-LaserJet body and wood-veneer flank at the
right end with its chunky buttons and amber-green LCD, the same materials, the
same palette, the same gouache brushwork, the same flat warm-grey field and the
same clear even lighting. Nothing about the design changes.

IMAGE 2 is the film's style target. Match its painted technique: real
dimensional form, every surface visibly hand-painted in thick loaded directional
gouache strokes, brush marks left in. No smooth digital gradients, no airbrushed
surfaces, no soft blended shading, no plastic CG shine, no ink outlines, no line
art.

=== WHAT THIS SHEET IS FOR ===

The previous sheet showed the machine floating with nothing to size it against,
so it read bench-sized. **This sheet exists to answer two questions: how big is
it, and how did it get here.** It must show that this is a mail-order appliance
that arrived on a truck in ONE carton a child could shove across a driveway, and
that it assembles into something much longer than the box it came in.

=== LAYOUT — TWO STUDIES SIDE BY SIDE ===

Two studies on one sheet, generous even margins, clear empty background between
them. No panel lines, no dividers, no boxes, no captions, no labels, no numbers,
no dimension lines, no arrows, no text of any kind anywhere on the sheet.

**LEFT STUDY — ASSEMBLED.** The machine as approved in IMAGE 1, side-on
three-quarter, fully set up with its conveyor extended. Standing beside it, a
SCALE SILHOUETTE (described below) of a CHILD.

**THE MACHINE IS SMALL AND LOW.** Earlier versions drew it as a walk-in tunnel
with a volume many times that of its shipping carton, which made nonsense of the
packaging. Corrected:

- The glass vault is **ONE SHORT ARCH BAY** on two frame ribs — a compact hood
  over a chamber barely longer than it is wide. Three hanging styli, not five.
- The whole machine is **LOW**: the top of the glass arch reaches only to about
  the CHILD'S SHOULDER. It stands on slim legs.
- The solid beige body with the control panel is a compact cabinet, chest height
  on the child, no bigger than a household appliance.
- The **conveyor is the only long part and it is an open skeleton** — slim steel
  rails, rollers and thin folding legs with daylight straight through, running
  out through the open left end. It carries almost no volume. Give it visible
  TELESCOPING SECTIONS with collars and knuckle-jointed legs so it obviously
  collapses to a third of its length.

Read left to right: long skinny open belt, then the small low glass hood, then
the compact body at the right end. **A small machine with a long thin leg.**

**RIGHT STUDY — BOXED.** The single cardboard shipping carton it arrived in,
closed and sitting square on the ground, with the SAME scale silhouette of the
same child standing beside it in the same pose. Both studies at exactly the same
scale, both figures exactly the same height, so the two can be compared directly.

=== THE SCALE SILHOUETTE ===

A completely FLAT, FEATURELESS SILHOUETTE of a child, standing straight and
facing forward, filled in one solid flat neutral warm grey with no interior
detail whatsoever — no face, no eyes, no hands, no clothing, no shading, no
outline. A blank cut-out shape, the way an architect puts a scale figure on a
drawing. It is a measuring stick, not a character, and it must never read as a
person in the scene.

The child is small — the top of its head reaches just under the top edge of the
carton.

=== THE PROPORTIONS — THIS IS THE POINT OF THE SHEET ===

**THE WHOLE POINT OF THIS SHEET IS THAT THE MACHINE PLAUSIBLY CAME OUT OF THE
CARTON.** A viewer should be able to look at the two and believe it. So:

- The CARTON is BIG — a fridge crate, **clearly TALLER THAN THE CHILD**, its top
  edge above the top of their head, so leaning over the open rim would be a real
  stretch. Deep and wide, but plainly shovable across a floor by someone
  determined. It is the largest single mass on the sheet.
- The MACHINE'S SOLID PARTS — the beige body and the small glass hood together —
  must look like **LESS THAN THE VOLUME OF THAT CRATE**, obviously so. The arch
  reaches only to the child's shoulder; the body is a chest-height cabinet.
- The CONVEYOR is long but is an OPEN SKELETON carrying no volume, and it visibly
  telescopes and folds, so it accounts for the length without needing the space.
- The assembled machine is still longer than the crate is wide — that is fine and
  true, because the length is all belt.

If the assembled machine looks like it could not possibly fit in the crate, the
sheet has failed.

=== THE CARTON ===

Plain corrugated cardboard in warm sand and khaki, honest and new. Taped seams
down the centre with visible packing tape, reinforced corners, a couple of
staples. Slightly bowed sides and one dented corner from the journey. Simple
printed shipping marks treated as PURELY GRAPHIC MARKS — bars, blocks and
arrow-like glyphs — with no readable letterforms or words anywhere. A few loose
white packing peanuts on the ground at its base.

=== PRESENTATION ===

Both studies alone on a PLAIN FLAT WARM-GREY FIELD. Empty background, no
scenery, no room, no floor line, no horizon, no gradient, no vignette, no cast
shadows on the ground.

Lighting for CLARITY, not drama: one warm key from the upper left, honest form,
a clear lit and shadow split, and enough saturated teal coloured bounce in the
shadows that every part stays readable — especially inside the print chamber,
which must not go dark. Glass genuinely transparent, with only a couple of
restrained painted highlight streaks.

PALETTE — hue anchors at their saturated and deep extremes:
  paper-cream #f2e4cc   sand #d9c0a3        khaki #c2a878
  olive #8f7a3d         sky-teal #3fbdb3    terracotta #b0764a
  rust #c95f33          coral #f0a082       golden #eec078
  warm charcoal #42403b (never pure black)
NO mint and NO pale aqua-green anywhere — reserved elsewhere in this film.

=== PERIOD ===
1993, painted deadpan by a 1962 poster artist.

=== AVOID ===
a short squat machine, a machine as tall as it is long, a small dome, a machine
similar in size to the carton, a rendered or detailed or painted human being, a real child, a face, eyes,
hands, hair, clothing on the scale figure, shading or outlines on the scale
figure, more than one carton, an opening on the right of the machine, an object
exiting the right side, a sealed glass box, a hinged door, a separate print bed
or tray, a nozzle, an extruder, a filament spool, a dark unreadable interior,
scenery, rooms, floors, horizons, backgrounds, dramatic backlighting, rim-lit
silhouettes, smooth digital gradients, airbrushed surfaces, soft blended
shading, plastic CG shine, photorealism, depth-of-field blur, low contrast, grey
or neutral shadows, ink outlines, line art, mint or aqua-green, readable words or letterforms, brand names, logotypes, captions, labels, callout lines, arrows, dimension lines, grids,
watermarks, signatures.
```

### Hero — `prop_printer.png`

```
A PROP DESIGN SHEET for a 1993-set animated film. One machine, presented for a
modeller to build from. Horizontal 4:3.

IMAGE 1 is the approved version of this machine. **Take its MATERIALS, COLOUR,
PANEL DETAILING and PAINT QUALITY exactly — but NOT its size or its proportions,
which are corrected below** — the warm beige and putty plastic,
the wood-veneer panel, the chunky mechanical buttons, the amber-green LCD strip,
the little indicator lights, the small hp badge, the visible gouache brushwork,
the flat warm-grey background and the lighting. **Do NOT take its layout** — the
architecture below replaces it completely.

IMAGE 2 is the film's style target. Match its painted technique: real
dimensional form, every surface visibly HAND-PAINTED in thick loaded directional
gouache strokes, brush marks left in. NO smooth digital gradients, NO airbrushed
surfaces, NO soft blended shading, NO plastic CG shine, NO ink outlines, NO line
art. Technique and palette only — not its subject, character or backlight.

=== THE SIZE — THIS IS THE CORRECTION, READ IT FIRST ===

IMAGE 1 shows this machine at its **CORRECT AND FINAL SIZE AND CONFIGURATION**,
standing beside a scale figure of a child. **Copy its size, its proportions and
its layout exactly.** This new image is the same machine, drawn larger in frame
and in a hero three-quarter view, with the printing process running.

Everything about the machine's design in IMAGE 1 is right and must carry over
unchanged:

- **THE GLASS IS ONE SINGLE SMOOTH HOOD — THIS KEEPS COMING BACK WRONG.**
  Think of the clear plastic lid on an office photocopier, or the curved sneeze
  guard on a deli counter: **ONE continuous curved shell, edge to edge, with a
  frame only around its outside rim.** There are NO repeating arches. NO row of
  ribs marching down its length. NO series of bays. NO vaulted tunnel. NO
  cathedral. If you can count more than one arch shape, the drawing is wrong.
  The chamber under it is barely longer than it is wide.
- **IT IS LOW.** The whole machine is waist-to-chest height on an adult. The top
  of the glass arch is about the height of a kitchen counter, sitting on slim
  legs. Nobody could walk into this. Nobody could climb inside it.
- **THREE HANGING STYLI, not five** — the chamber is small now and only fits
  three.
- **THE SOLID BODY IS COMPACT** — the beige end carrying the control panel is a
  chest-height cabinet about as deep as it is wide, no bigger than a small
  household appliance.
- **THE BELT IS THE ONLY LONG PART, AND IT IS ALL AIR.** A slim open steel
  conveyor frame on thin folding legs runs out through the open left end and
  extends well past the machine. It is a skeleton — rails, rollers and legs with
  daylight straight through it, carrying almost no volume. Give it **visible
  TELESCOPING SECTIONS with collars and pinch-bolts, and knuckle joints in the
  legs**, so it plainly collapses to a third of its length.

The read: **a small low machine with a long skinny leg.** The chamber is the
size of a picnic cooler; the belt is what makes it long. Everything solid about
this machine must look like it would fit in a large cardboard box, because it
does — that is settled and IMAGE 1 is the proof. Do not make it bigger again, do
not add arch bays, do not turn it back into a tunnel.

=== READ THIS FIRST — THE LAST VERSION DID NOT MAKE SPATIAL SENSE ===

In the previous attempt the machine was open on one side while the finished
object came out of the other, and the camera was on a third. **This image must
be geometrically coherent. Three things have to agree, and they are the whole
brief:**

1. The machine's **LEFT END IS OPEN.**
2. The finished object **COMES OUT OF THAT SAME OPEN LEFT END.**
3. The **CAMERA IS ON THE LEFT**, three-quarters on, looking into the open left
   end and slightly down.

So we are looking straight into the open mouth of the machine, along the line
the work travels, and we can see all the way inside it. Nothing exits the right,
nothing exits the back. There is exactly one opening.

=== THE MACHINE ===

A 1993 beige HP LaserJet office printer, scaled up into a floor-standing
industrial machine. It reads as that printer's bigger cousin: same warm putty
plastic, same rounded corners, same broad panel seams and moulded louvre vents,
same wood-veneer flank.

**THE BODY IS AT THE RIGHT END.** The solid part of the machine — the base
cabinet, the electronics housing, the wood-veneer flank and the CONTROL PANEL
with its chunky buttons, amber-green LCD and indicator lights — is all massed at
the far RIGHT end of the object, furthest from camera. That is the head of the
machine. Keep it exactly as detailed as in IMAGE 1.

**THE CONVEYOR BELT IS THE ENTIRE FLOOR OF THE PRINT CHAMBER.** There is no
separate bed, no tray and no platform. A wide flat industrial belt on visible
steel rollers runs the full length of the machine — it begins inside, under the
body at the right, travels the whole chamber, and continues straight out
through the open left end on its own slim steel frame with legs, extending well
past the machine and toward camera. The object being printed is built directly
onto that moving belt and is carried out on it, which is how the machine makes
things far longer than itself.

**ONE SINGLE SMOOTH GLASS HOOD COVERS THE CHAMBER** — a low curved shell over
the belt from one long side to the other, framed only around its outer rim, like
a photocopier lid. One arch shape and no more. It springs from the machine's side rails and covers the
chamber's length, but it **STOPS SHORT AT THE LEFT AND THE END IS FULLY OPEN**,
a clean cut mouth with a beige trim lip, so the belt and its work travel straight
out from under the arch. Partial enclosure only — never a sealed box, never a
door.

**SEVERAL ROBOT STYLI HANG IN THE CHAMBER.** Under the crown of the glass arch,
a row of THREE slender articulated ROBOT ARMS hangs DOWN from an overhead
rail, evenly spaced across the short chamber, each tipped with a fine needle-like
STYLUS pointing at the belt below. They are poised and waiting — hanging at
slightly different heights and slightly different angles, like a row of dentist
arms or a spider's legs. Slim beige-and-charcoal segments, visible pivot joints,
thin ribbon cables looping up to the rail. They are the most characterful thing
inside the machine, and being able to count them matters.

**THE MATTER FORMS FROM THIN AIR.** Beneath the stylus tips a swarm of glowing
NANOPARTICLES hangs in empty space over the belt and coalesces into the object.
Paint the swarm as a drift of fine bright motes, densest right under the styli
where matter is forming and thinning to nothing outward. The object should read
half-made: solid and finished where it has already travelled out toward the open
left end, dissolving into loose particles at the end still under the styli.
Nothing extrudes, nothing squeezes from a nozzle, there is no filament and no
print head touching anything. The particle glow is the only light the machine
makes.

Lay a long object along the belt so the whole process reads left to right in one
look: **finished, out in the open air at the left → half-formed under the styli →
still a cloud of particles at the right.**

=== PRESENTATION ===

The machine sits alone, filling most of the frame, on a PLAIN FLAT WARM-GREY
FIELD. Empty background. No scenery, no room, no floor, no horizon, no gradient,
no vignette, no cast shadow on the ground.

LIGHTING IS FOR CLARITY, not drama: one warm key from the upper left giving
honest form and a clear lit/shadow split, with enough coloured bounce in the
shadow side that EVERY PART STAYS READABLE — especially inside the chamber,
which must not go dark. Shadows go saturated teal, never grey, never crushed.
Do not silhouette the machine and do not backlight it.

Matte throughout, except the glass, which is genuinely transparent — we must see
the styli and the particle swarm clearly through it, with only a couple of
restrained painted highlight streaks to say "glass".

PALETTE — hue anchors at their saturated and deep extremes:
  paper-cream #f2e4cc   sand #d9c0a3        khaki #c2a878
  olive #8f7a3d         sky-teal #3fbdb3    terracotta #b0764a
  rust #c95f33          coral #f0a082       golden #eec078
  warm charcoal #42403b (never pure black)
NO mint and NO pale aqua-green anywhere — reserved elsewhere in this film.

=== PERIOD ===
1993, painted deadpan by a 1962 poster artist.

=== NO PEOPLE ===
No people, no hands, no figures, no faces. Nothing living.

=== AVOID ===
an opening on the right, an object exiting the right side, an object exiting the
back, more than one opening, a sealed glass box, a hinged door, a flat glass lid,
a separate print bed or tray or platform, a nozzle, an extruder, a filament
spool, a print head touching the object, a dark unreadable interior, a long tunnel, three or more arch bays, a walk-in
machine, a machine tall enough to stand inside, a machine larger than a
household appliance, more than three styli, repeating arches, a row of ribs,
multiple bays, a vaulted tunnel, a cathedral roof, brand names, logotypes,
real-world trademarks, an HP logo, the word LaserJet, readable lettering on the
body;
people, hands, figures, scenery, rooms, floors, horizons, backgrounds,
dramatic backlighting, rim-lit silhouettes, smooth digital gradients, airbrushed
surfaces, soft blended shading, plastic CG shine, photorealism, depth-of-field
blur, low contrast, grey or neutral shadows, ink outlines, line art, mint or
aqua-green, captions, labels, callout lines, arrows, dimension lines, grids,
watermarks, signatures.
```

## santa — round 2 (round 1 superseded)

```
=== THE OBJECT — the vintage blow-mould Santa lawn decoration ===

A 1960s hollow blow-moulded plastic Santa Claus lawn ornament, about a metre
tall, exactly the kind in the attached photographs.

**THE LAST ATTEMPT PAINTED A TIDY LITTLE PORTRAIT OF SANTA. THAT IS THE
FAILURE.** This is not a face. It is a CHEAP PLASTIC MOULDING OF ONE, made in a
factory by the thousand and decorated fast by somebody who was not looking
closely. Every note below serves that.

THE MOULDING: thick cream-yellow plastic, translucent enough to glow faintly,
aged and unevenly discoloured. The features are shallow MOULDED RELIEF — a
beard of stiff sculpted curls, moulded brows, a moulded moustache, a bulbous
moulded nose. The surface is smooth, hard and slightly waxy, and it catches
light the way plastic does, not the way skin does.

THE PAINT, AND THIS IS THE POINT: the colour is slapped ON TOP of that relief in
flat, cheap, opaque dabs, and **IT DOES NOT LINE UP WITH THE MOULDING.** Push
this hard enough to see it instantly:
- The red mouth is painted clearly CROOKED and clearly OFF to one side of the
  moulded lips, overlapping the moulded beard at one corner and leaving bare
  plastic showing at the other.
- The two round red cheek dots are at OBVIOUSLY different heights and different
  sizes.
- One blue eye is painted wide of its moulded socket, so the plastic shows
  through on one side and the paint runs onto the moulded lid on the other.
- Edges of every painted patch are blunt, thick and slightly ragged — a fat
  brush, one pass, no care.

The result is a **SMILE THAT IS PLAINLY WRONG** — still cheerful, still meant
kindly, but visibly misaligned, like a mask assembled a fraction out of true. Do
NOT make it a leer, a grin, a snarl or a horror face. It is a nice Santa,
decorated badly, and that is worse.

THE BODY: hollow moulded plastic. Glossy red suit with moulded white fur trim at
cuffs, hem and hat; a moulded black belt with a square buckle; moulded mittens; a
sack of toys. The red has faded hard and unevenly on the sun-facing side and the
white has gone yellow-cream. **PRONOUNCED MOULD SEAM LINES run vertically down
both sides of the whole figure, head included** — sharp raised ridges of flash
where the two halves of the mould met, never cleaned off. A round cut hole in the
base for a light bulb, and a stubby fabric power cord. **Two or three strips of
old grey DUCT TAPE** patch a crack in the body and hold something at the base,
grimy at the edges and lifting at one corner.

**THE HEAD ROTATES INDEPENDENTLY OF THE BODY — SHOW THIS.** A clean horizontal
joint at the collar: a moulded collar ring with a visible circular seam and a
distinct step, exactly like a jar lid, so the head can be turned on it. Make that
ring unmistakable, and let a thin dark gap show in the joint.

PRESENT AS TWO STUDIES SIDE BY SIDE, generous even margins, empty background
between them:
- LEFT: the whole figure, three-quarter view, standing.
- RIGHT: the head and collar alone, larger, TURNED ABOUT 40 DEGREES to one side
  relative to the body's facing so the rotation reads clearly, with the collar
  joint ring and the mould seam both plainly visible. This head must read as a
  hollow plastic shell, not as a portrait.
```

## kid_gun

```
=== THE OBJECT — the boy's printed machine gun ===

A boy's fantasy of a machine gun, printed by the machine in his garage. This is
the film's signature prop. The design note is simple: **IT IS ABSURDLY
OVERDONE.** A ten-year-old designed it by adding every cool part he could think
of and then adding more, and the printer built exactly what he asked for.

It must read as a TOY, not a weapon — chunky, over-scaled, moulded in plastic
with soft rounded edges and thick slab sides, with visible mould seams and a
faint sheen. Nothing on it looks machined or lethal.

PILE ON THE PARTS, and make every one of them oversized:
- A long barrel inside a perforated cooling shroud with big round holes.
- A huge curved BANANA MAGAZINE, far too long, sweeping down and forward.
- A full shoulder STOCK with a thick moulded cheek rest.
- A SCOPE on top, comically large, mounted on a riser too tall for it.
- A carrying handle, a vertical foregrip, a bipod folded underneath.
- A drum-fed side canister that does not connect to anything.
- Chunky toggle switches under guards, and a couple of blinking indicator lamps.
- Ribbon cable looms and moulded panel greebles — cassette futurism, warm beige
  and amber rather than chrome and blue.

**THE BELLS AND WHISTLES ARE LITERAL.** A small brass BELL is bolted to the
receiver, and a real tin WHISTLE is mounted beside it. They are functional and
plainly attached, and they are the funniest thing on the object.

Body colour is warm charcoal plastic with beige and sand panels and one or two
hot rust-orange accent stripes moulded in, the way a toy is coloured.

A cheap rectangular sticker reading NOT A TOY is slapped crooked on the side of
the receiver — the one piece of lettering allowed in this image, printed
off-register with its red plate shifted a hair off the black, already scuffing
at one corner.

Present it as a clean side profile, filling the frame, so every part reads.
```

## mom_gun — round 2, the silver 9mm

```
=== THE OBJECT — Mom's gun ===

A SILVER 9mm SEMI-AUTOMATIC PISTOL. Sleek, European, expensive-looking and
completely serious — the exact opposite of the boy's overdone plastic toy.
Think the sidearms carried by the villains in a 1988 action film.

- BRIGHT POLISHED SILVER throughout: stainless steel and nickel, mirror-bright
  on the flats of the slide and softly brushed on the frame, so the two silvers
  read as different metals. It is the shiniest object in this film.
- A squared, purposeful SLIDE with clean machined serrations at the rear, a
  crisp ejection port, and a low-profile front and rear sight.
- **The slide is the important part** — it must read as a separate piece that
  travels back along the frame, with a clear gap line between slide and frame,
  because it gets racked. Make the rear serrations big and obviously grippable.
- A slim frame, a squared trigger guard, a magazine release button, a safety
  lever, and the butt of a magazine flush in the grip.
- Grip panels in black checkered plastic — the only dark note on the object.
- Precise machined joins, tight panel lines, no decoration, no engraving, no
  lettering, no decals. Its whole character is that it is UNCLUTTERED and
  well-made.
- Honest handling wear: the bright finish very slightly softened at the muzzle
  and along the high edges. Nothing damaged.

Present it as a clean side profile, filling the frame.
```

## cop_gun

```
=== THE OBJECT — the sheriff's rifle ===

A standard-issue American service rifle of the early Cold War era: an M14, and
specifically the WOOD one. Its whole job in this film is to look completely
different from the other two weapons — where the boy's is chunky moulded plastic
and Mom's is sleek black polymer, this is WOOD AND BLUED STEEL, and it looks
like it was issued to somebody a long time ago.

- A full-length one-piece WALNUT STOCK running most of the weapon: warm
  red-brown, honestly grained, hand-oiled, with a real sheen where hands have
  worn it and dings and dents along the bottom edge.
- Blued steel barrel and receiver in deep warm charcoal, worn to bright silver
  at the edges, the muzzle and the wear points.
- A perforated metal handguard, a flash suppressor at the muzzle, a front sight
  post in a protective ring, and a rear aperture sight.
- A straight box magazine of modest size, nothing dramatic.
- A wooden pistol grip formed as part of the stock rather than a separate
  polymer grip — no modern grip shape anywhere.
- A worn canvas sling in olive drab, with brass hardware gone dull.
- Honest, dignified age: no rust, no damage, nothing broken. This is a
  well-maintained old rifle.

Nothing tactical, nothing modern, no rails, no optics, no plastic.

Present it as a clean side profile, filling the frame.
```

## gun_lineup — round 2, rebuilt around the pistol

```
=== THE SHEET — all three weapons, one scale, for comparison ===

THREE weapons stacked one above another on a single sheet, ALL AT THE SAME
SCALE and all in plain flat SIDE PROFILE facing the same direction. Generous
even margins, clear empty background between them, no panel lines, no dividers,
no boxes, no captions, no labels, no numbers, no text of any kind.

The entire purpose of this sheet is that the three read as COMPLETELY DIFFERENT
OBJECTS from silhouette alone, and from material alone. Push that contrast.

TOP — THE BOY'S. Absurdly overdone, a child's fantasy printed for real. Chunky
over-scaled moulded PLASTIC with soft rounded edges, thick slab sides and
visible mould seams. Piled with parts, every one too big: a perforated barrel
shroud, an enormous curved banana magazine, a full stock with a moulded cheek
rest, a comically large scope on too tall a riser, a carrying handle, a vertical
foregrip, a folded bipod, a pointless drum canister, toggle switches under
guards, indicator lamps. A small brass BELL and a tin WHISTLE bolted to the
receiver. Warm charcoal plastic with beige and sand panels and hot rust accent
stripes. It is the longest and by far the bulkiest of the three.

MIDDLE — MOM'S. A SILVER 9mm SEMI-AUTOMATIC PISTOL, and it is TINY beside the
other two — a fraction of their length, which is the point. Bright polished
silver: mirror-bright stainless on the flats of the squared slide, softly
brushed nickel on the frame, so the two silvers read as different metals. Big
machined serrations at the rear of the slide, a clear gap line between slide and
frame, a slim squared trigger guard, black checkered grip panels as the only
dark note. No decoration, no lettering, no clutter. It is the smallest, the
brightest and the cleanest object on the sheet.

BOTTOM — THE SHERIFF'S. An early-Cold-War service rifle, the WOOD one — an M14.
A full-length one-piece WALNUT stock in warm red-brown, honestly grained and
hand-oiled, dinged along its bottom edge. Blued charcoal steel worn bright at
the edges and the muzzle. A perforated metal handguard, flash suppressor, front
sight post in a ring, rear aperture sight, a modest straight box magazine, a
wooden pistol grip formed from the stock itself, and a dull olive canvas sling.
Nothing tactical, nothing modern. Long, straight, thin and dignified.

Read down the sheet the three should go: BIG DULL PLASTIC TOY -> SMALL BRIGHT SILVER -> LONG WOOD AND BLUED STEEL.
The three differ in size, in material and in finish all at once.
```

## What came back

Ten calls. Every sheet landed on its first attempt at its own brief — a much
easier run than the locations, because a single object on a blank field gives
the model nothing to reinvent.

### Worth keeping

- **The design-sheet lighting recipe works.** "Light for clarity, not drama,
  with enough coloured bounce that every part stays readable" produced sheets a
  modeller can work from without losing the painted look.
- **The printer edit preserved everything it was told to** — body, wood veneer,
  control panel, LCD, palette, brushwork, lighting and the particle swarm all
  survived while the architecture changed underneath. Editing beats re-rolling
  whenever the look is already approved.
- **…but editing could not fix a layout that was incoherent to begin with.**
  Round 2 came back open on one side, ejecting from another, viewed from a
  third. **An edit prompt corrects local features; it will not re-reason about
  space.** Round 3 had to be a fresh generate with the round-2 image demoted to
  a materials-only reference, and the fix was stating the three sight lines as
  one rule that must agree — open end, exit end, camera — plus naming every
  wrong alternative in AVOID. First attempt, coherent.
- **Santa round 2 fixed the real problem.** Round 1 came back as a tidy painted
  portrait of Santa. Naming that failure explicitly — *"this is not a face, it is
  a cheap plastic moulding of one, decorated fast by somebody not looking
  closely"* — and then listing each misregistration separately (mouth crooked and
  off to one side, cheek dots at different heights and sizes, one eye wide of its
  socket, blunt ragged edges) got the off smile, the mould seams and the duct
  tape. **This is the one place in the film where off-register paint on a face is
  legal**, because Santa is an object, not a person.
- The `NOT A TOY` sticker came through off-register, the one piece of lettering
  deliberately allowed past the AVOID list.

### Known deviations, live

- **The printer's size is now settled** and `prop_printer_scale.png` is the
  authority: hood at the boy's shoulder, body chest height, crate taller than he
  is. If the hero and the scale sheet ever disagree again, the scale sheet wins.
- The object on the conveyor is a generic slab rather than anything the film
  actually prints. Fine for a design sheet, useless as a story beat — worth one
  version with the machine gun on the belt.
- The conveyor reads as a **roller** conveyor rather than a belt. Arguably
  better for the period and for the machine — but it is not what the prompt
  asked for, so note it before it becomes canon by accident.
- The LCD carries readable text (`READY - LONG PART ASSEMBLY`) despite the
  blanket ban on lettering. It is diegetic and it suits the machine; kept.
- On the lineup the three are close to but not exactly one scale. The boy's gun
  and the M14 come out similar in length — the boy's wins on bulk, not length.
