# property — v1, six locations x two times of day

**Generated 2026-08-06, Nano Banana Pro (`gemini-3-pro-image`) via the Gemini
API.** Sixteen calls for twelve keepers. Every frame is painted over a **rendered
structural blockout of `assets/envs/property/property.blend`**, so the
architecture, the camera and the site are the real ones, not invented.

| location | shots it serves | plate |
|---|---|---|
| `establishing` | sq010 open, sq040 arrival, sq090 | `plates/p_establishing.png` |
| `garage_tunnel` | sq010 (the box, the bench), sq020-sh020 | `plates/p_garage_tunnel.png` |
| `backyard` | sq020–sq080 — the arena | `plates/p_backyard.png` |
| `kitchen_sink` | sq040-sh020, sq050-sh030/035 — Mom's watching position | `plates/p_kitchen_sink.png` |
| `corridor` | sq050 — the sheriff's crawl, Mom's kill-window wall | `plates/p_corridor.png` |
| `front_porch` | sq010-sh010/020/030 — the screen-door slap | `plates/p_front_porch.png` |

Each exists as `prop_<location>_midafternoon.png` and `prop_<location>_sundown.png`
— the two ends of the film's colour arc.

## The plates — how to regenerate them

`tools/` does not build these and should not; nothing in the pipeline reads
`concept/`. They came from a throwaway script that opens `property.blend`
read-only, **creates cameras at render time and never saves the file**. Scene
`Scene`, EEVEE, 1440 × 1080, both sun lamps forced to
`rot=(52°, 0, −125°)`, `energy>=4.0` so form reads.

The cameras are not in the blend. These are the exact transforms — rotation X of
**90° looks along +Y**, above 90 pitches up:

| plate | location | rot XYZ (deg) | lens |
|---|---|---|---|
| establishing | (−26.0, −30.0, 6.50) | (93, 0, −36) | 38mm |
| backyard | (0.5, 14.5, 2.20) | (97, 0, 180) | 26mm |
| front_porch | (−2.2, −13.5, 1.70) | (95, 0, 0) | 30mm |
| corridor | (9.0, −12.0, 1.20) | (96, 0, 4) | 28mm |
| garage_tunnel | (−9.9, −6.2, 1.55) | (90, 0, 0) | 24mm |
| kitchen_sink | (2.8, 1.8, 1.62) | (92, 0, 0) | 24mm |

`property.blend` ships twelve cameras of its own. Only `cam_intro` and
`cam_sidecorridor` frame the structure usefully — **`cam_backyard` and
`cam_kitchen` both point away from the house** and return nothing but fence and
treeline, so they are background plates, not location angles. The six above are
new and deliberately pitched up for sky.

Live-geometry check before rendering: the scene holds `property > house` (live),
an **empty** `house_v2`, and an **excluded** `superseded`. `site_labels` is
already render-hidden. Render `Scene` as-is and it is correct.

## Refs attached to every call

| ref | role |
|---|---|
| `concept/property/plates/p_<location>.png` | **IMAGE 1 — STRUCTURE.** The blockout. Camera and architecture are not negotiable. |
| `concept/boy/boy_v3_arcane_b-backyard-dusk.png` | **IMAGE 2 — STYLE TARGET.** Technique, palette and light only. |

Labelled inline, each immediately before its image, prompt last — same handling
as `concept/mom/`.

## Constraints these were built under

Ian's brief: **no humans, and nothing at L3 hero fidelity.** Both are enforced in
every prompt.

- **No people at all.** Its own block plus a long AVOID clause. Held in all
  twelve.
- **No L3 heroes.** `props.md` §1 marks these hand-modelled close-up assets, and
  every one is banned by name: the `printer`, `machine_gun`, `rosco`, `santa` /
  `santa_charred`, `tea_pitcher`, `not_a_toy_sticker`, `cruiser_interior`,
  `egg_salad_sando`, `title_card`, the `gun_cabinet` L3 sign. `bbq` is
  **L2→L3** so it appears only as a plain kettle silhouette.
- Everything present is L1/L2 dressing lifted from `props.md` §5 (Garage) and §6
  (Yard), plus the kitchen dressing from `house.md`.
- A general fidelity clause holds all props at background/mid detail so nothing
  reads as a hero.

## Departures from the locked style

Same three `boy_v3_arcane.prompt.md` makes on purpose, for the same reason —
these have to sit beside the character sheets: **modelled form**, **saturated
coloured shadows**, **rim light**. `style.md` is still LOCKED as flat MCM print
and these are still an argument, not canon.

Two things the prompts *do* keep from the doc: **the sun is a flat disc with no
glow or bloom**, and **mint / pale aqua-green is banned outright** so the truck
and the sweet tea keep their reservation.

**Not yet checked:** several frames spend a lot of teal on walls and cabinetry.
It reads as sky-teal rather than reserved mint, but it wants an eye on it before
any of this informs a real surface.

---

## Shared preamble

Every one of the twelve prompts is this preamble, then a per-location block, then
the sky block, then a time-of-day block, then the shared closing block.
Reproduced once here; only the varying parts are repeated below.

```
A production concept illustration of a location from a 1993-set animated film.
Painted 3D, in the manner of Arcane: hand-painted textures over real dimensional
form, dramatic cinematic light, rich saturated colour. Horizontal 4:3.

=== READ THIS FIRST — WHAT THE TWO IMAGES ARE FOR ===

IMAGE 1 is an untextured 3D BLOCKOUT of this exact set, rendered from the exact
camera this illustration must use. It is the STRUCTURE and it is not negotiable:

- KEEP THE CAMERA EXACTLY. Same position, same lens, same horizon line, same
  perspective. Do not reframe, do not zoom, do not change the angle.
- KEEP THE ARCHITECTURE EXACTLY. Every wall, roof plane, beam, post, opening,
  window, door, step and slab stays exactly where it is, at exactly the
  proportions shown. Do not add or remove structure. Do not restyle the
  building.
- The blockout is grey and untextured ONLY because it is unfinished. Give every
  surface real material, colour, age and wear.

IMAGE 2 is the STYLE TARGET — a finished character concept from the same film.
Match its rendering exactly: the same artist, the same film, the same afternoon.
Take ONLY its technique, palette and light. Do not take its subject, and do not
put its character in this picture.

=== THE RENDER ===

Real dimensional form, hand-painted all over in thick loaded directional gouache
strokes. Brush marks left in and celebrated. You can count the strokes.
ABSOLUTELY NO smooth digital gradients, NO airbrushed surfaces, NO soft blended
shading, NO clean vector rendering, NO plastic CG shine. No ink outlines and no
line art — all definition comes from painted shape, value and edge.

Stroke direction wraps each form: strokes running along a beam, down a wall
plane, across the grain of a concrete slab. Where two colours meet the brush
edge stays visible — hand-made, slightly wavering, never a clean cut. Let loaded
edges ridge where they overlap and let dry patches scuff.

=== VALUE AND COLOUR ===

WIDE value range. Genuinely deep, near-black shadow masses against hot luminous
lit planes near white. Nothing sits safely in the middle.

- LIGHT is warm and saturated: golden and rust-orange, near-molten.
- SHADOW is deeply and openly COLOURED — never grey, never neutral, never just a
  darker version of the lit colour. Shadows drive hard into saturated deep teal
  and indigo.
- The picture lives on that hot/cold tension. One hard sun, no fill, crisp
  graphic cast shadows with hard painted edges thrown long across the ground.

PALETTE — hue anchors, taken to their saturated and deep extremes:
  paper-cream #f2e4cc   sand #d9c0a3        khaki #c2a878
  olive #8f7a3d         sky-teal #3fbdb3    terracotta #b0764a
  rust #c95f33          dusty-rose #d8a8a8  coral #f0a082
  golden #eec078        warm charcoal #42403b (never pure black)
The 1993 objects use a separate, quieter set so they read as ADDED LATER:
  charcoal-plastic #42403b   faded-denim #7d94a8
  mall-mauve #a98794         seafoam-grey #9db8ac

NO mint and NO pale aqua-green anywhere in the frame — that colour is reserved
for two specific objects elsewhere in this film and must not appear here.

=== THE WORLD — 1962 house, 1993 life ===

The building is a 1962 Palm Springs desert-modern fantasy — flat roof, deep
fascia, post-and-beam, walls of glass, breeze-block screens. It was INHERITED,
not chosen, and it is now thirty years out of style and worn: chalked paint,
sun-bleached surfaces, rust streaks, patched stucco, faded and cracked concrete.

Layered over those bones is thirty years of accumulated 1980s and early-90s
possessions — thrift-store hodgepodge, hand-me-downs, plastic and pressed wood
among the mid-century bones. That clash is the whole point of the design.

**Painted deadpan by a 1962 poster artist.** The medium never acknowledges the
anachronism — a 1962 illustrator forced to draw a boombox draws it with exactly
the same loving flatness as the house.

=== THIS LOCATION — the property from the road ===

The establishing shot of the whole property: a low mid-century ranch house with
a flat roof and deep fascia, its carport tunnel open straight through, seen
across a dry rural front yard from the dirt road.



DRESS THE FRAME with these, and only these:
- The dirt road running across the foreground, pale and dusty, with a shallow
  drainage ditch and a concrete culvert at the driveway mouth.
- A leaning galvanised mailbox on a weathered wooden post at the driveway.
- A cracked concrete driveway with weeds in the joints, running to the carport.
- Dry patchy lawn — olive and khaki, more dead than alive, worn to bare dirt in
  the traffic paths.
- Foundation bushes gone leggy along the base of the house, a few agave and
  prickly-pear succulents, and one twisted red-barked manzanita with the best
  silhouette in the yard.
- A rank of round-canopied trees behind the house and a low post-and-rail fence.
- Big dry mountains far behind, flat and simplified, going dusty violet.
- One old parked pickup truck on the drive, faded and sun-killed, sitting still
  and clearly parked forever.
- Two dented metal trash cans and a coiled hose on a reel against the wall.
```

## The sky block — shared by all twelve

```
=== THE SKY IS THE STAR OF THIS PICTURE ===

This is a BIG SKY film. Wherever sky is visible in the blockout, it is the most
dramatic, most designed element in the frame — treat it as the subject and the
architecture as the silhouette sitting under it.

CLOUDS — big, bold and architectural. Towering stacked formations built from a
few confident BLOCKED SHAPES with hard painted edges, the way a mid-century
poster artist draws a cloud: a flat body carrying one or two internal tone steps,
never a soft airbrushed puff, never wispy, never photographic. Scale them large
and let them tower — a handful of huge forms beats a sky full of small ones.
Their lit tops and edges catch hot molten gold; their bodies and undersides go
deep and saturated.

THE SUN IS A BALL — a flat, hard-edged DISC of pure light, painted as one clean
solid circle sitting in the sky. Graphic and deliberate, like a sticker on the
poster. NO glow, NO bloom, NO halo, NO god rays, NO lens flare, NO soft falloff
around it. Just the disc. Where the framing allows the sky, put the sun ball in
the picture and let it anchor the composition.
```

## Time of day — mid afternoon

```
=== TIME OF DAY — MID AFTERNOON ===

High hard sun, well up in the sky. The sky is DEEP SATURATED TEAL at the top of
the frame, cooling and deepening toward the zenith, and falling through warm
ochre and dusty rose down to the horizon haze. Big towering cumulus in bold
blocked cream shapes, hot gold along their lit tops, deep saturated teal-violet
in their shadowed undersides. The sun ball rides high and white-gold.

The light is hard, clean and near-overhead-ish: short-to-medium cast shadows
with crisp graphic edges, driving deep into saturated teal on the ground and the
walls. Lit planes go hot and pale; shadowed planes go dark and coloured. Maximum
clarity, maximum contrast, no haze on the foreground.
```

## Time of day — sundown

```
=== TIME OF DAY — SUNDOWN ===

The sun is LOW and sitting just above the horizon. The sky runs the film's full
arc from top to bottom: deep saturated teal and indigo overhead, falling through
hot coral and rust, down to a blazing molten golden band along the horizon.

Big dramatic cloud banks stacked across that gradient in bold blocked shapes,
their undersides catching hot coral and rust from below, their top edges rimmed
in hot gold, their bodies going deep violet-teal. This is the most saturated sky
in the film.

The sun ball sits low as a flat disc of pure molten gold, hard-edged and clean.

The light rakes in almost horizontally: VERY long, hard-edged shadows stretched
right across the ground toward camera, hot rim light burning along every top
edge, every post, every roof line and every leaf mass. Lit faces go near-white
gold; everything turned away from the sun drops into deep saturated teal and
indigo, nearly black. This is the most extreme contrast in the set.
```

## Closing block — shared by all twelve

```
=== ABSOLUTELY NO PEOPLE ===

This is an empty set. No people, no humans, no figures, no children, no adults,
no silhouettes of people, no hands, no faces, no reflections of people, no
animals. Nothing living. The location is completely unoccupied.

=== KEEP EVERYTHING AT BACKGROUND AND MID FIDELITY ===

Every object here is set dressing, not a hero prop. Render props as confident,
economical painted shapes with correct silhouette, correct material and honest
wear — the level of detail that holds at conversational distance. Do NOT render
any object as a jewel-like close-up hero with authored fine detail. If an object
would pull the eye away from the space itself, simplify it.

=== AVOID ===
people, humans, figures, children, adults, silhouettes of people, hands, faces,
animals, pets, birds;
a 3D printer, any machine or gun of any kind, firearms, rifles, pistols,
holsters, a blow-mold Santa Claus figure, a glass tea pitcher, a police car,
a car interior, lettered signs or stickers or decals with readable artwork,
a title card;
changing the camera, reframing, changing the lens, changing the architecture,
adding or removing walls or windows or roof planes, restyling the building,
straightening the perspective;
smooth digital gradients, airbrushed surfaces, soft blended shading, low
contrast, even mid-range values, pastel washes, washed-out colour, grey or
neutral shadows, ink outlines, line art, plastic CG shine, photorealism,
depth-of-field blur, lens flare, mint or aqua-green, text, labels, captions,
watermarks, signatures.
```

---

## Per-location blocks

### establishing

```
=== THE BUILDING — HOLD THIS FORM, THE LAST ATTEMPT REBUILT IT ===

The previous attempt replaced this house with a generic pitched-roof ranch. That
is the failure. The building in IMAGE 1 is a specific 1962 desert-modern house
and its form is fixed:

- The roof is DEAD FLAT. A single horizontal plane. It is finished with a DEEP
  FLAT FASCIA BAND running unbroken across the whole width of the building, like
  a thick ruled line. There is NO pitch, NO gable, NO ridge, NO hip, NO shingles,
  NO overhanging eave brackets, NO dormers, NO chimney stack.
- The whole building is LONG, LOW and HORIZONTAL — much wider than it is tall.
- On the left the mass is a carport/garage block whose opening runs STRAIGHT
  THROUGH the building as an open tunnel: you can see daylight, the back fence
  and the trees through it, out the far side.
- On the right a covered porch runs along the front, carried on slim SQUARE
  POSTS, with square BEAM ENDS projecting out past the fascia in a regular
  rhythm. Count them in the blockout and keep them.
- A decorative pierced concrete BREEZE-BLOCK SCREEN panel stands at the right end
  of the porch.
- Windows are wide, slim-framed picture windows set flush in flat stucco walls.
- A tall thin utility pole with a crossarm stands behind the right end.

Match the blockout's massing, roof line, opening positions and proportions
exactly. Add material, colour, age and wear — never new geometry.

=== THIS LOCATION — the property from the road ===

The establishing shot of the whole property: a low mid-century ranch house with
a flat roof and deep fascia, its carport tunnel open straight through, seen
across a dry rural front yard from the dirt road.



DRESS THE FRAME with these, and only these:
- The dirt road running across the foreground, pale and dusty, with a shallow
  drainage ditch and a concrete culvert at the driveway mouth.
- A leaning galvanised mailbox on a weathered wooden post at the driveway.
- A cracked concrete driveway with weeds in the joints, running to the carport.
- Dry patchy lawn — olive and khaki, more dead than alive, worn to bare dirt in
  the traffic paths.
- Foundation bushes gone leggy along the base of the house, a few agave and
  prickly-pear succulents, and one twisted red-barked manzanita with the best
  silhouette in the yard.
- A rank of round-canopied trees behind the house and a low post-and-rail fence.
- Big dry mountains far behind, flat and simplified, going dusty violet.
- One old parked pickup truck on the drive, faded and sun-killed, sitting still
  and clearly parked forever.
- Two dented metal trash cans and a coiled hose on a reel against the wall.


=== THE BUILDING — HOLD THIS FORM, THE LAST ATTEMPT REBUILT IT ===

The previous attempt replaced this house with a generic pitched-roof ranch. That
is the failure. The building in IMAGE 1 is a specific 1962 desert-modern house
and its form is fixed:

- The roof is DEAD FLAT. A single horizontal plane. It is finished with a DEEP
  FLAT FASCIA BAND running unbroken across the whole width of the building, like
  a thick ruled line. There is NO pitch, NO gable, NO ridge, NO hip, NO shingles,
  NO overhanging eave brackets, NO dormers, NO chimney stack.
- The whole building is LONG, LOW and HORIZONTAL — much wider than it is tall.
- On the left the mass is a carport/garage block whose opening runs STRAIGHT
  THROUGH the building as an open tunnel: you can see daylight, the back fence
  and the trees through it, out the far side.
- On the right a covered porch runs along the front, carried on slim SQUARE
  POSTS, with square BEAM ENDS projecting out past the fascia in a regular
  rhythm. Count them in the blockout and keep them.
- A decorative pierced concrete BREEZE-BLOCK SCREEN panel stands at the right end
  of the porch.
- Windows are wide, slim-framed picture windows set flush in flat stucco walls.
- A tall thin utility pole with a crossarm stands behind the right end.

Match the blockout's massing, roof line, opening positions and proportions
exactly. Add material, colour, age and wear — never new geometry.
```

### garage_tunnel

```
=== THIS LOCATION — the garage, looking straight through the open tunnel ===

A drive-through garage, both sectional doors parked permanently open, so the
space is a tunnel with daylight blazing at the far end and the backyard, fence
and treeline visible through it. Exposed beams overhead.

This room is a dead man's storage. The boy's father was a veteran and he is
gone; nobody has thrown any of it out, and nobody has moved the half-finished
job on the bench.



DRESS THE INTERIOR with these, and only these:
- Wood-panelled walls, oil-stained concrete floor, a bare hanging bulb.
- A heavy workbench along one wall with a vise bolted to it, and a pegboard
  above it that carries PAINTED TOOL SHADOWS WITH NO TOOLS IN THEM.
- Something half-built on the bench under a dust sheet. Nobody moved it.
- An olive-drab military footlocker, its stencilled name worn to illegibility.
- War-surplus junk treated as a child's toy box: ammo cans, a canteen, an
  entrenching tool, a mess kit.
- A folded flag in a triangular wooden case, high on a shelf. Small and
  unmissable.
- A garment bag holding a dress uniform, hanging on a nail.
- Cardboard Christmas cartons with tinsel spilling out of one, a 1962 aluminium
  Christmas tree with its colour wheel, tangled light strings on a nail, and a
  blow-mold plastic reindeer.
- A sun-bleached political campaign yard sign in the junk pile, its lettering
  faded past reading.
- An auto-parts pin-up calendar turned to the wrong month of the wrong year, a
  rock band poster, and a novelty beer mirror.
- A wood-veneer portable television on a shelf, a CB radio, a boombox, a broken
  VCR with stacks of tapes.
- A half-built model aeroplane kit, fishing rods and a tackle box, a child's
  bicycle, a lawnmower, paint cans, a coffee can of screws, a tangled extension
  cord, and steel shop shelving.
Crowd it. This room is full and it has been full for years.
```

### backyard

```
=== THE BUILDING — HOLD THIS FORM, THE LAST ATTEMPT REBUILT IT ===

The previous attempt replaced this wall with a small pitched-roof cottage. That
is the failure. The rear elevation in IMAGE 1 is fixed:

- The roof is DEAD FLAT, finished with a DEEP FLAT FASCIA BAND running unbroken
  across the entire width of the frame like a thick ruled line. NO pitch, NO
  gable, NO ridge, NO shingles, NO dormers.
- Beneath that fascia, a regular rhythm of square BEAM ENDS projects out through
  the wall plane at even spacing all the way across. They are the strongest
  feature of the elevation and they throw a repeating run of hard shadows down
  the stucco. Count them in the blockout and keep every one.
- The wall is one long, low, flat plane of stucco. The building is much wider
  than it is tall and it runs off both sides of the frame.
- On the left, a pair of casement windows stands OPEN OUTWARD, their glazed
  leaves swung out from the wall at an angle.
- On the right, a flush door with a low rectangular concrete STOOP SLAB on the
  ground in front of it.
- A slim square post stands at the far left, carrying the roof overhang.

Match the blockout's massing, roof line, beam rhythm and opening positions
exactly. Add material, colour, age and wear — never new geometry.

=== THIS LOCATION — the backyard, looking back at the house ===

The rear face of the house across the back lawn: the kitchen casement windows
standing open, the back door, a low concrete stoop, the deep roof overhang and
its beam ends, and the garage mass off to one side.



DRESS THE FRAME with these, and only these:
- A clothesline strung across the yard with sheets and laundry hanging still,
  including one floral Sunday dress.
- A domed charcoal kettle barbecue in forest green with a propane tank beside
  it, kept simple.
- A concrete birdbath, a scatter of pink plastic lawn flamingos, and one garden
  gnome.
- A metal patio table with a couple of folding lawn chairs in faded webbing.
- A window box hung under one half of the kitchen sill, planted and overgrown.
- Dented metal trash cans, a hose reel, a watering can lying on its side.
- Dry patchy lawn, olive and khaki, worn to bare dirt along the paths.
- Foundation bushes, agave and prickly pear, a twisted red-barked manzanita.
- A low back fence at the property line with a rank of round-canopied trees
  behind it, and dry mountains far beyond.


=== THE BUILDING — HOLD THIS FORM, THE LAST ATTEMPT REBUILT IT ===

The previous attempt replaced this wall with a small pitched-roof cottage. That
is the failure. The rear elevation in IMAGE 1 is fixed:

- The roof is DEAD FLAT, finished with a DEEP FLAT FASCIA BAND running unbroken
  across the entire width of the frame like a thick ruled line. NO pitch, NO
  gable, NO ridge, NO shingles, NO dormers.
- Beneath that fascia, a regular rhythm of square BEAM ENDS projects out through
  the wall plane at even spacing all the way across. They are the strongest
  feature of the elevation and they throw a repeating run of hard shadows down
  the stucco. Count them in the blockout and keep every one.
- The wall is one long, low, flat plane of stucco. The building is much wider
  than it is tall and it runs off both sides of the frame.
- On the left, a pair of casement windows stands OPEN OUTWARD, their glazed
  leaves swung out from the wall at an angle.
- On the right, a flush door with a low rectangular concrete STOOP SLAB on the
  ground in front of it.
- A slim square post stands at the far left, carrying the roof overhang.

Match the blockout's massing, roof line, beam rhythm and opening positions
exactly. Add material, colour, age and wear — never new geometry.
```

### kitchen_sink

```
=== THIS LOCATION — the kitchen, at the sink, looking out ===

The one interior the film shoots. A 1962 kitchen seen from just behind the sink:
the counter run under a pair of casement windows standing open onto the
backyard, exposed ceiling beams continuing indoors, the yard and fence and
treeline bright outside.



DRESS THE ROOM with these, and only these:
- Original 1962 bones, worn: pink ceramic tile counter and backsplash with
  grubby grout, white slab-front cabinets with simple hardware, painted block
  walls, a terrazzo-look floor.
- A deep enamel sink with a chrome tap, a dish rack, a scrubbed pot draining.
- The 1993 layer sitting on top of those bones, plainly added later: a white
  fridge wearing a crust of magnets, clippings and children's drawings; a
  boombox on the counter; a wall telephone with a long coiled cord; plastic
  storage canisters; a kettle; a calendar.
- A pair of quilted floral oven mitts hanging on a hook by the stove.
- Short cotton curtains pushed back at the window.
- Through the open windows: dry lawn, a low fence, round-canopied trees, dry
  mountains, big poster sky.
```

### corridor

```
=== THIS LOCATION — the narrow side corridor along the house ===

The tight gap between the long side wall of the house and the property line: the
wall's grooved siding running away from camera in raked light, its windows, the
deep roof overhang above, and an old parked pickup truck sitting in the open
ground beyond.



DRESS THE FRAME with these, and only these:
- Grooved vertical siding, chalked and sun-bleached, with rust streaks running
  from the fixings.
- A galvanised downspout and a run of gutter along the fascia.
- Gravel and dry dirt underfoot with weeds along the wall base.
- A hose reel on a bracket, two dented metal trash cans, a stack of old paint
  cans, a leaning sheet of plywood.
- Leggy foundation bushes and a few succulents.
- One old parked pickup truck beyond, faded and sun-killed, unmistakably parked
  forever and serving as a big simple block of shape in the mid-ground.
- A low fence and round-canopied trees past it, dry mountains far beyond.
```

### front_porch

```
=== THIS LOCATION — the covered front porch at eye level ===

The front entry seen straight on from the yard: a raised concrete porch slab
under a deep flat roof carried on square posts, the beam ends showing, the front
door standing open into a dark interior, a picture window to one side, and a
decorative concrete breeze-block screen to the other.



DRESS THE FRAME with these, and only these:
- A wood-framed screen door with sagging mesh, hanging slightly askew on its
  spring hinge in front of the open front door.
- The front door itself a mid-century slab with three staggered small lites,
  painted a chalked terracotta-rust accent.
- A worn bristle doormat, kicked crooked.
- A clerestory ribbon of small windows high on the wall above the picture
  window, with a sheet of aluminium foil taped over part of it as a sunshade.
- A metal porch chair with peeling paint, a stack of terracotta pots, a
  half-dead potted plant, a coiled garden hose.
- A milk crate holding junk, a child's bicycle leaned against a post.
- Brass house numbers and a simple wall sconce beside the door.
- Dry patchy lawn beyond the step, olive and khaki, worn to dirt on the path.
```

## What came back

Sixteen calls. What the model actually did:

| the model did this | the fix |
|---|---|
| **Rebuilt the house.** `establishing` and `backyard` came back as generic pitched-roof ranch cottages — gable, ridge, shingles — despite the blockout showing a flat roof and the prompt saying keep the architecture exactly. **A grey blockout alone does not hold architecture.** | A `THE BUILDING — HOLD THIS FORM` block that *describes the massing in words*: dead-flat roof, deep fascia band, the beam-end rhythm, the carport tunnel, the breeze-block screen, plus explicit bans on pitch/gable/ridge/shingles. Image **plus** text held it; image alone did not. The four v1 frames were discarded. |
| Painted the sky small and polite on the first pass | Fixed upstream in the **plate**, not the prompt — the exterior cameras were re-shot pitched up so sky occupies 40–60% of frame. Framing beats adjectives. |
| Put readable house numbers on the porch | `text` is already in AVOID and it did it anyway, small. Paint out if it matters; same fix as the boy's shoe-sheet captions. |
| **Painted the place derelict** — peeling paint, rust streaks running down walls, broken concrete, dead lawn, junk in the dirt. Wrong family. It also broke `style.md` film canon, which says **"subtle patina only"** in as many words. | A `THE WEAR IS SUBTLE` block, hoisted into the shared preamble and labelled the most important note on the page. It reframes every flaw as **a deferred job, not neglect** — one parent, out of hours, no shortage of pride. Surfaces are stated INTACT AND CLEAN item by item, belongings are *stored not strewn*, and a long dereliction clause went into AVOID. Closing line: **"When in doubt, make it cleaner."** All twelve were regenerated. |

**That last one is the note to keep.** "Worn", "aged" and "patina" are read by
this model as *ruined* unless the prompt spends real words saying otherwise, and
the fix is not an adjective — it is stating the human reason for each flaw. It
also pulled the whole set closer to the locked flat-print look as a side effect.

### What it did well without much fighting

- **The garage tunnel is the strongest frame in the set** and needed no second
  pass. The father's-remnants dressing all landed: flag case, footlocker, ammo
  cans, pegboard with painted tool shadows, dust-sheeted project, aluminium tree,
  reindeer, tangled lights, wood-veneer TV, boombox, bicycle, lawnmower.
- **Sun balls read exactly as specified** — flat hard-edged discs, no glow, no
  bloom, no rays — in every frame that shows sky.
- The interior (`kitchen_sink`) held its architecture first time. Only the
  exteriors rebuilt themselves.

### Known deviations, live

- The two times of day were generated independently, so a location's
  mid-afternoon and sundown frames **do not match each other shot-for-shot** in
  dressing placement. They are two paintings of one place, not a before/after
  pair. If a matched pair is wanted, generate one and *edit* it to the other time
  — the technique that worked throughout `concept/mom/`.
- Signs and posters in the garage came back carrying readable lettering despite
  `text` being in AVOID. The campaign sign is *supposed* to be bleached past
  reading — paint the lettering out, same method as the boy's shoe sheet.
- `corridor_sundown` drifted off its plate and reframed toward the driveway
  rather than holding the tight corridor. Re-run it against
  `plates/p_corridor.png` if the corridor read matters.
- No `yard_charred` state. Every frame is the clean pre-battle yard; sq070–sq080
  want their own pass over the overlay mini set once it exists.
