# guns — visual style candidates

**Status: OPEN — no style has been chosen.** Bigature Claymation is the most
developed candidate (workshopped 2026-08-02 from `refs/`), not the decision.
Script: `script.md` · Palette: `../../refs/palette.scss`

**How the decision gets made** — per the repo rule, by rendering and looking,
not by arguing: stage **one loaded test frame** (sq020-sh020 is ideal — boy,
printed gun with sticker, garage interior, Santa at the threshold: four
material families in one frame) and render it under each contending
treatment with its final light rig. Compare side by side.

## Shared givens (hold for any candidate)

These came from the refs and the script, not from any one style:

- **Tone:** slightly unsettling, **subtle patina only** — secondhand wear,
  never horror moves.
- **Setting: the early 90s — MCM is out of style.** The house is a 1962
  Palm Springs fantasy (flat roof, post-and-beam, glass walls) layered
  over with 80s/90s possessions: thrift-store hodgepodge, anachronism
  through necessity. Wardrobe canon: Mom in mall-glam armor (hairspray
  helmet, shoulder pads, pleated pants — supersedes the curler/housecoat
  look), the boy in bowl cut + baggies, the sheriff driving a boxy 80s
  Crown Victoria a decade out of date. Developed 2026-08-03 in
  `style-midcentury-print.md`; how each candidate *renders* the clash is
  its own business.
- **Palette:** the `refs/palette.scss` gradient (pale sky `#bcd2ee` →
  periwinkle `#9b7ede` → plum `#832161` → bordeaux `#52050a`) as the film's
  sky/grade arc, with **turquoise `#76e7cd` reserved as the accent** (the
  truck, the sweet tea).
- **Big-sky feel:** expansive, dramatic clouds throughout
  (`refs/sky_clouds/` is the vocabulary).
- **Clay carnage:** the script commits to it regardless of style ("clay
  everywhere," molten Play-Doh, clay divots, clay title card) — every
  candidate must give the destruction a clay read.
- Script consequence already applied and standing regardless of choice: the
  sheriff's noodle-gun beat (sq070-sh020) is cut.

---

# Candidate A — Bigature Claymation (developed)

## Thesis

The camera believes it is shooting live action — real lenses, smooth motion,
naturalistic sun, no miniature tricks. Everything in frame is honestly
handmade, at full scale, under a big painted theatre sky. The people are
polished living mannequins: clean, calm, a little too perfect. The unsettling
note comes entirely from that restraint plus patina on the world around them.

## The five castes

Every object in the film belongs to exactly one caste. No object may borrow
another caste's material behavior (see Physics law).

### 1. Flesh & flora — polished plasticine

People, animals, lawn, trees, flowerbed.

- Fully polished, Aardman-smooth surfaces. No fingerprints, no tool marks,
  no frame-to-frame boil. The surface is a living sculpture, not a
  re-sculpted one.
- Proportions near-realistic, lightly pushed. Silhouette comedy comes from
  wardrobe and grooming (hairspray helmet, bowl-cut dome, sheriff's belt-line),
  not from caricatured anatomy.
- **Faces:** sculpt morphs carry the acting (devious grin, final-boss Mom,
  "…Danny?"). Iris, brow, and blush are paint sitting *slightly*
  off-register on the sculpt — the blow-mold trick (`refs/santa/`).
- **Clothes:** sculpted clay masses, even off-body (the Sunday dress on the
  clothesline is sculpted clay). Printed graphics — the vintage band tee
  (`refs/boy/`) — are painted on, slightly off-register.
- **Hair:** sculpted clay masses. Bowl cut is one smooth dome. Mom's
  hairspray helmet is one massive sculpted dome. The mustache is a single
  form. No fibers, no flocking.
- Skin and clothing carry **no wear**. Patina never touches this caste.
- Character DNA from refs: boy — bowl cut + metal tee (`refs/boy/`);
  Mom — hairspray helmet, shoulder pads, pleated pants, mall-glam armor
  (`refs/mom/`, `refs/mom gun/`); sheriff — 70s–90s county lawman (`refs/cop/`).

### 2. Sets & terrain — earthy

House, garage, road, ditch, ground.

- Adobe, troweled plaster, packed dirt, organic texture. Hand-worked
  surfaces, but **no model-shop vocabulary**: no balsa grain, no foamcore
  edges, no exposed construction, no penciled layout lines.
- Architecture from `refs/house/` (the 1962 flat-roof glass pavilion per
  the setting given, pink kitchen) and `refs/garage interior/` (wood paneling reads as earthy
  hand-finished planks, not scribed sheet). Yard from `refs/backyard/`,
  `refs/clothesline/`.

### 3. Manufactured goods — diecast & molded

Vehicles, guns, the printer, appliances, decorations, housewares.

- Mechanical things are **diecast**: thick enamel paint chipping to silver
  metal, molded-in panel lines, visible screwheads, castings slightly soft.
  Master material sample: the patina'd teal C10 (`refs/old truck/`), which
  sits on the palette's turquoise swatch. Also `refs/cop_car/`,
  `refs/printer/`, `refs/cop rifle/`, `refs/mom gun/`.
- Decorations and housewares are **molded goods**: blow-mold hollow plastic
  (the Santa — `refs/santa/` — and the lawn flamingos), painted plaster
  (gnome), enamelware and ceramic (kitchen). Hollow things pop and shatter
  hollow; they never squash.
- This caste carries the heaviest patina: chips, yellowed whites, sticker
  residue, duct-tape repairs (the Santa's are already in the script).

### 4. Printed objects — extruded clay

Everything the printer makes: the machine gun, the action figures.

- Soft-serve extrusion; FDM layer lines read as **coil-pottery striations**.
  Printed things are visibly clay *by manufacture*.
- These are the only **soft manufactured** objects in the world, which
  concentrates all squash/droop/melt/splatter comedy on the boy's creations
  by law: the scolded barrel droop, the xylophone head-pops, molten
  Play-Doh, clay divots — all lawful, all this caste (plus flesh-caste clay
  puffs and smoldering hair).
- Figure design language: discount-Americana vintage action figures
  (`refs/3d printed dummies/` — off-brand wrestler / mullet commando).
  The printed gun's design: toy-scaled cassette-futurism with literal bells
  and whistles (`refs/3d printed gun/`).

### 5. Effects — light, not matter

Muzzle flashes, fire, all smoke (including the sq070 aftermath drift), the
mushroom cloud.

- Glowing fluid-sim / geometry-node objects, like stage pyro. The one caste
  that is not a handmade solid — it is allowed to break the diorama because
  theatre lighting always does.
- The mushroom cloud (with its one-frame bald eagle) is this caste's
  showcase.

## Sky & light

- The sky is a **painterly theatre-set backdrop**: the shared big-sky
  clouds, brush-painted, running the shared palette gradient across the
  film.
- One warm "stage sun" key matching the backdrop's hour. Naturalistic
  direction and softness; no product-table lighting.

## Patina law

Universal secondhand wear on the built world (castes 2–3): chips, yellowing,
residue, repairs. Never on flesh, clothes, or hair (caste 1). Fresh prints
(caste 4) are new — their wear is earned on screen by gunfire.

**The sweet-tea pitcher is the single lawfully pristine object in the film.**
The script already calls it "the only pristine object in the wreckage"
(sq070-sh040); the style enforces the gag.

## Physics law

**Strict castes, no exceptions.**

- Clay (castes 1 and 4) squashes, droops, melts, splatters.
- Diecast dents, chips, and *bends* — it never droops.
- Molded hollow goods crack, pop, and shatter — they never squash.
- Earthy surfaces crater and crumble.

## Banned list (within this candidate)

Rejected on purpose during development; if A wins, do not reintroduce:

- Tilt-shift / miniature-faking DOF
- Stepped or on-2s "stop-motion" animation
- Surface boil, animated fingerprints, tool-mark flicker
- Exposed model construction (foamcore, glue, stands in frame)
- Real cloth and fiber/flocked hair
- Glass doll eyes
- Photographic skies
- Caste violations for a gag

## Production notes (Blender / EEVEE)

- All five material families are EEVEE-friendly: SSS clay, painted plaster,
  chipped enamel, emission FX. The claymation add-on covers caste 1/4
  surfacing.
- Sculpted clothes and hair mean **no cloth sim and no hair system**.
- The painterly sky lives on world-space backdrop geometry (dome/cyc), so
  free camera moves keep working — no camera projections anywhere in this
  style, which keeps the camera-driven layout pipeline unconstrained.

---

# Candidate B — Toy Box Americana (sketch)

The whole world is a secondhand vintage toy. People are rotocast vinyl with
sculpted hair and swivel-joint articulation, each as if from a different toy
line (boy — flocked-hair kid figure; Mom — doll line; sheriff — 70s Mego
cop); the house is playset plastic with decal windows; vehicles are diecast
with real paint chips; the Santa is literally the blow-mold ref. Clay is
reserved for the printer's output and all destruction (satisfying the shared
clay-carnage given). Limited articulation is the *animation language* —
swivel-wrist aim sweeps, stiff gopher-pops — an animation economy for a solo
pipeline. Shot like an 80s toy commercial: macro lens, tabletop sweep.
Patina does the unsettling: yellowed vinyl, sticker residue, one eye printed
off-register. The "NOT A TOY" runner becomes the style's thesis statement.

- **Pros:** strongest alignment with what `refs/` actually contains; the
  cheapest great-looking materials in CG (plastics) — EEVEE-native; rigging
  and animation economy.
- **Cons/risks:** lives or dies on lighting — reads as "default render of a
  toy" if the macro-tabletop light isn't nailed.

# Candidate C — Painted Americana 3D-for-2D (sketch)

Projection-painted fills on simple 3D plus geometry-node / grease-pencil
strokes — but aimed at **mid-century American illustration** (Little Golden
Books, UPA, Charley Harper, roadside postcards) rather than Moebius. The
most art-directable frames of the three.

- **Pros:** every frame can be a picture-book plate; flattens render cost.
- **Cons/risks:** heaviest per-shot 2D labor for one person across 40 shots;
  and camera projections structurally fight this repo's core rule — the
  camera is the only framing authority, and projections punish exactly the
  free moves the layout pipeline is built around. Mitigation is painting
  onto simple 3D and reserving true projections for statics, but that's a
  constraint tax on every shot.

# Back pocket (modifiers, not styles)

- **VHS broadcast finish:** 4:3 moments, chroma bleed, tracking wobble on
  the flashback, timestamp on "toy commercial" beats. Stackable on any
  winner; decide late.
- **County-fair shooting gallery:** the destructible figures as flat
  painted-tin targets that spin/flip when hit — usable as the printed-figure
  subsystem inside any candidate (the chorus head-pop xylophone run reads
  perfectly as a target row).
