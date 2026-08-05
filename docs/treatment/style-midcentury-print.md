# Mid-Century Print — style candidate (standalone)

**Status: CANDIDATE — developed 2026-08-03, deliberately outside `style.md`
until it earns its slot with a test render.** It competes with the candidates
in `style.md` under the same rule: stage the loaded test frame
(sq020-sh020 — boy, printed gun, garage interior, Santa at the threshold),
render it under this treatment with its final light rig, and compare side by
side. If it wins or places, merge it into `style.md` then.

Refs: `refs/styles/` (Palm Springs / desert-modern poster art — two gouache
prints, three flat-vector prints). Tools evaluated: Ucupaint (free, layered
texture painting), Deep Paint Pro (~$40, gouache/pastel brushes + presets).
Technique ref: `~/blender/add-ons/cody-gindy-kettle-patreon-02.blend`
(painted-normals demo, examined 2026-08-03 — paid content, kept outside
the repo).

## Relationship to style.md

This is Candidate C's aesthetic family (mid-century American illustration)
with C's two economic problems removed: the style is **stroke-free** (no
grease-pencil linework, no Line Art modifier, no per-shot 2D labor) and uses
**no camera projections** (dome sky + world-space grain keep the
camera-authority rule unconstrained).

It **renegotiates two shared givens** from `style.md`:

1. **Palette.** This candidate does not inherit the `refs/palette.scss`
   gradient arc. It brings its own MCM palette (below). The turquoise
   accent reservation *transfers intact* — mint stays reserved for the
   truck and the sweet tea.
2. **Clay carnage → paint carnage.** The script's destruction beats keep
   their shape but remap medium: "clay everywhere" becomes *paint
   everywhere*. Same beats, same reads, different substance.

All other givens hold: slightly unsettling tone, subtle patina only
(translated below), big-sky feel (as poster clouds).

It also **contributes one given up** to film canon (developed
2026-08-03): the 1993 setting — recorded in `style.md`'s shared givens
so it holds under any candidate.

## Thesis

The film is a mid-century American print come to life — flat matte gouache
shapes, no linework anywhere, long graphic shadows, big poster skies. The
world is *printed*: every surface is registered color on paper.

The unsettling note comes from the medium misbehaving. Everything the boy's
printer creates, and every act of violence, is **wet paint** in a dry
printed world — pigment the print never authorized. Creation and
destruction are the same substance, and the pristine print gets
progressively ruined by it.

## The setting — 1993, film canon

The film is set in the early 90s, when mid-century modern is thirty
years out of style. The house is a 1962 Palm Springs fantasy — flat
roof, deep fascia, post-and-beam, walls of glass
(`refs/styles/il_fullxfull.5572769945_bsf5.webp` is the house's
self-image) — inherited, not chosen. Three decades of necessity have
layered 80s/90s possessions over the bones: thrift-store hodgepodge,
hand-me-downs, anachronism through necessity.

The print expresses it deadpan: the whole film is drawn as the poster of
the house's self-image, and 1993 just sits in it, rendered serenely.
**The medium never acknowledges the anachronism** — a 1962 poster artist
forced to draw a boombox draws it with the same loving flatness as the
butterfly roof. This hands the shared "slightly unsettling" given a
second engine: every frame is slightly wrong-in-time.

The setting itself is film canon — it holds under any style candidate
and is recorded in `style.md`'s shared givens. This doc covers only how
the print expresses it.

## The two strata — what the world is made of

Every object in the lived-in world belongs to one of two strata:

- **The 1962 stratum** — architecture and built-ins: flat roof, deep
  fascia and overhangs, glass walls, breeze-block screen, terrazzo, the
  pink kitchen (`refs/house/`). Plus the mint C10 — a period-coherent
  relic. This stratum wears the core MCM palette.
- **The 1980s–90s stratum** — everything the family added out of
  necessity: the hand-me-down plaid recliner, particle-board shelving,
  the 27-inch CRT, boombox, VCR, cordless phone, the boy's printer, all
  wardrobe, the sheriff's Crown Vic. This stratum can draw on the 1993
  annex swatches (below); core MCM swatches sit on it happily too.

**Aim for at least one post-1980 object in every lived-in frame.** The
architecture dressed pure reads as a period piece, which is the one
thing this setting isn't — the film never shows the clean 1962 poster,
only 1993 wearing it.

**Dilapidation is content, not medium.** The print stays flat and clean
while *depicting* wear: a fascia board replaced with bare plywood, dead
patches in the lawn, aluminum foil sunshading one clerestory, a swamp
cooler squatting on the flat roof, the duct-taped blow-mold Santa
(already canon). Era makes no difference to how wear reads — a thrifted
1985 recliner fades and misregisters exactly like a 1962 breeze block,
because the wear belongs to the print, not to the object's decade.

Maybe (a story/set call, not a style call): a drained, cracked pool —
the most on-theme failed-fantasy set piece available if a beat ever
wants one.

## The shading machine

The unifying technique — proven by the Gindy kettle file — is
**hand-painted normal dabs**: brush strokes painted into the normal
channel, each dab one flat color = one flat facet catching light as a
single plane. The surface *looks* hand-laid gouache but shades
physically, so the grain reacts to every light change — the look holds
AND the world stays lit. Adapted for this film as **tangent-space tilt
dabs** on a quantized palette (Gindy paints absolute object-space
normals; tangent tilts need no per-asset bake and deform correctly on
characters).

- **`MCM_Toon`** — flat painted albedo in, painted shading out. The tilt
  map perturbs the normal; diffuse is left **soft and physical**.
  **Banding is dead film-wide (decided 2026-08-04, by test — see
  `assets/materials/tilt_dab_test/`).** The terminator breaks along
  stroke shapes because the *dabs* break it, and shadow color runs
  through the **global shadow tint** (shadows shift hue, not just value).
  - **Why banding had to go.** Banding and tilt dabs are competing
    mechanisms, not complementary ones. A hard `ColorRamp` step means a
    3–14° tilt only changes the output within a narrow band around the
    threshold; everywhere else the tilted and untilted normals land in
    the same band and shade identically. Measured on the mint C10: with
    banding on, dabs are invisible across the lit surface and read only
    along the terminator, leaving flat interiors. With banding off, the
    same map gives all-over gouache grain. The treatment previously
    guessed banding might be redundant — it is the reverse, banding made
    the *dabs* redundant. The dabs are the look, so banding loses.
  - **Consequence: the engine is no longer forced.** `Shader to RGB` was
    the only EEVEE-only node in the stack. Without it `MCM_Toon` is
    engine-agnostic and Cycles is back on the table — see Production
    notes.
- **The tilt palette** (replaces the old procedural `MCM_Grain` noise —
  dabs killed it). A swatch = direction × lean, encoded as a
  tangent-space normal color; flat blue = no tilt. Crucially the two
  palettes are **independent axes**: a dab is an (albedo × tilt) pair
  chosen at the moment it is laid down — any colour with any tilt, no
  fixed pairing — and one surface uses several tilts of the same albedo.
  Neighboring dabs disagreeing slightly about direction is the entire
  gouache effect.
  - **12 directions, universal film-wide** — one hand paints the movie.
    No per-asset bakes; the same swatches serve every object.
  - **Magnitude tiers are the material axis:** whisper (~3°), soft
    (~7°), medium (~14°), strong (~25°). **Any tier is available on any
    surface.** Tier is a call made at the brush — the earlier per-family
    table (stucco / terrain / diecast / characters) was deleted
    2026-08-04, because it was guessing at assignments before anything
    had been painted. See
    `docs/superpowers/specs/2026-08-04-tilt-dab-painter-design.md`.
  - **How tiers read at distance — measured 2026-08-04 on the C10.**
    Whisper (3°) is barely visible in an 85 mm closeup at 2.8 m; medium
    (14°) reads clearly on a full-truck hero wide. So a surface painted
    all-whisper goes flat at shot distance: reach for whisper when the
    grain should only be felt up close, and for medium or strong when a
    wide has to carry it. Measured with uniform procedural scatter —
    real hand-laid dabs are denser and more deliberate and may read a
    step stronger.
  - **Albedo drift:** each palette swatch carries five drift variants
    (warm / cool / dusk / pale / deep) for dab-level color variation.
  - **Distance scaling:** step tilt magnitude down with the depth
    bands — far layers whisper or nothing. Painterliness reads as a
    foreground privilege, exactly like the refs' flat backgrounds.
- **What albedo carries:** placed color variation (paint the drift
  swatches directly, or Ucupaint layers for whole regions: a warm patch
  on a wall, a darker pass at a roofline, painted occlusion accents
  under eaves). What it shouldn't carry is directional shading or faked
  relief — light direction belongs to the render and facets to the tilt
  map. Painted into albedo instead, either one stops responding when the
  sun moves, and reacting to light is the entire point of the technique.
- **The world is matte.** Specular sits at zero film-wide so that wet
  paint is the only gloss anywhere; that contrast is what makes the FX
  read as a foreign substance rather than as highlights.
- **Glass is a graphic fill** — windows and truck glass render as flat
  poster fills with a painted diagonal gleam shape. A real reflection
  would put a photographic window into a painted world.
- **Structural darkening is painted, not rendered.** Render AO adds a
  soft procedural gradient that flat shapes can't absorb; placed by
  hand into albedo it stays a shape.
- **Depth is graphic, not atmospheric:** distant layers step toward
  paper/sky tone in discrete bands (the refs' mountains) via an optional
  distance-banding input on `MCM_Toon`. Mist would do it as a gradient,
  and the refs do it as steps.

## Palette

Sampled from `refs/styles/` (headless pixel census, 2026-08-03). Hexes are
starting swatches — the test frame tunes them.

| swatch | hex | role |
|---|---|---|
| paper-cream | `#f2e4cc` | light base: walls, concrete, highlights, clouds |
| sand | `#d9c0a3` | ground, road, mid-value neutrals |
| khaki | `#c2a878` | dry grass, secondary ground |
| olive | `#8f7a3d` | lawn, foliage masses |
| sky-teal | `#3fbdb3` | the daytime sky; deep and slightly desaturated |
| terracotta | `#b0764a` | roofs, brick, furniture accents |
| rust | `#c95f33` | hot accents: mountains, the cop car's pop |
| dusty-rose | `#d8a8a8` | sunset transition, distant warmth |
| coral | `#f0a082` | the sunset sky |
| golden | `#eec078` | sun disc, golden-hour wash |
| **mint (reserved)** | `#76e7cd` | **the truck and the sweet tea** — held back from everything else so it lands |

- **Mint stays distinct from the teal sky** by hue and value: sky-teal is
  deep and dusty, mint pale and saturated. That separation is what lets
  mint work as a signal — spent anywhere else, it stops being one.
- **The color arc is the MCM day:** teal-sky daytime → warm ochre
  afternoon → coral/golden sunset for the finale (the gouache sunset ref
  is the finale's sky).
- **Light:** one hard sun per scene, angled for long diagonal poster
  shadows. Cast shadows are crisp graphic shapes, tinted by the global
  shadow control.

### The 1993 annex

Four swatches for the 1980s–90s stratum, mixed dusty so they sit quietly
inside the gouache world:

| swatch | hex | role |
|---|---|---|
| charcoal-plastic | `#42403b` | electronics, tires, the CRT, cop-car trim — warm charcoal, never pure black |
| faded-denim | `#7d94a8` | the boy's baggies; denim anywhere |
| mall-mauve | `#a98794` | Mom's wardrobe, the afghan, the couch |
| seafoam-grey | `#9db8ac` | 90s kitchenware, a windbreaker |

What the annex is for:

- These are the 1993 stratum's colours. They read as *added later*
  precisely because the sky, the terrain, and the architecture never
  wear them.
- Kept to a minority of any frame. The core swatches carrying the
  majority is what makes the annex land as intrusion rather than as
  simply the palette.
- Each annex swatch carries the same drift variants as a core swatch and
  paints at any dab tier, exactly like a core swatch.
- **No collision with mint:** seafoam-grey is grayed nearly to neutral
  and faded-denim is grayed blue, while mint stays pale *and* saturated
  — the same separation that holds it apart from the teal sky.

All of the above is the *intent* behind these swatches — why they exist
and what they're for — not a checklist. Both palettes in the dab painter
are freeform: every swatch is one click away, and guidance is there to
be used or overruled at the brush.

## Sky

A painted backdrop dome, so free camera moves keep working: flat poster
clouds — cream shapes with one or two internal tone steps — redrawn from
the `refs/sky_clouds/` vocabulary, one dome variant per time-of-day. Two or
three flat cloud cards at different depths add parallax on big moves. When
the sun is visible it is a flat disc, no glow, no bloom.

## Characters

UPA-flat — Little Golden Books people — wearing the same `MCM_Toon` shader
as the world, 2-band, mottled, matte:

- **Faces are flat shapes, not sculpts:** dot/wedge eyes, graphic brows,
  mouth as a cut shape. No linework on a face. Acting is carried by
  silhouette, pose, and holds.
- **One print artifact rides on people:** the off-register **blush
  dot** — period-correct Golden Books misregistration, and the project's
  off-register signature surviving on flesh. It only reads as a print
  artifact while it's the only one, so people otherwise stay cleanly
  registered.
- **Hair is a solid graphic mass** — bowl cut is one shape, Mom's
  hairspray helmet is one huge sculpted mass, the mustache is a single
  form.
- **Wardrobe is flat fills.** The boy's band-tee graphic gets to be
  off-register: the tee is a print within the print.
- **The decade rides the silhouette** (setting canon, expressed flat):
  - **Mom — 1988 mall-glam armor, all film:** the hairspray helmet,
    shoulder-padded blouse in mall-mauve, pleated high-waist pants.
    Supersedes the earlier curler/housecoat look; `refs/mom/` remains
    the face/energy DNA, and the oven mitts survive as kitchen props.
    The silhouette is pre-armored for the final-boss turn — no costume
    change needed.
  - **Boy:** bowl cut over a faded-denim baggy silhouette, cuffs
    pooling over the sneakers, band tee as above.
  - **Sheriff:** the man reads timeless county lawman; his anachronism
    is the car (see the two strata) — a boxy 80s LTD Crown Victoria, a
    decade out of date even in 1993, cream body with the rust pop the
    palette already assigns (`refs/cop_car/`).
- Character DNA still comes from `refs/boy/`, `refs/mom/`, `refs/cop/` —
  wardrobe and grooming silhouettes, translated to flat shapes.
- **Flesh reads better calmer than the world.** Tangent-space tilts
  deform correctly with the rig, so grain survives animation — but a
  brushy face competes with the acting, which silhouette and holds are
  already carrying. Keeping skin quieter than its surroundings also
  makes the world look brushier by contrast. Guidance, not a tier
  assignment: every tier is available anywhere.

## Motion

- **Camera: smooth and cinematic.** Existing layout and camera work carry
  through unchanged.
- **Characters: limited animation** — strong holds, snappy transitions.
  Fast actions use **painted smears**: the smear frame is literally a
  brushstroke shape, plus optional speed-line cards.
- **Objects don't droop, sag, or melt as behavior.** That vocabulary is
  the claymation candidate's, and it's most of what distinguishes the two
  candidates' reads — borrowing it here blurs both. Destruction in this
  world is splatter and graphic effects.
- **Script consequence if this candidate wins:** the scolded barrel-droop
  beat depends on droop physics and needs a graphic restaging (a dribble
  of wet paint from the muzzle, a hung-head pose from the boy) or a cut —
  same category as the standing noodle-gun cut.

## Paint FX — creation and destruction

The one wet subsystem in a dry world. Wet paint is the only gloss in the
film: saturated, deeper-hued, with slow drips.

- **Creation:** the printer extrudes glossy wet pigment. Layer lines read
  as *piped-paint striations* — printed things are visibly made of paint
  that never fully dried.
- **Gunfire:** muzzle flashes are flat comic starburst cards stamped on
  2s. Impacts splatter wet paint onto surfaces (dynamic paint / decal
  splats). Implementation pattern proven in the kettle file's flames:
  painted cards + a geo-nodes flipbook (Scene Time drives a random card
  pick per frame) — the same rig serves flashes and starbursts.
- **The head-pop xylophone run:** figures burst into splats with starburst
  stamps — the county-fair shooting-gallery idea from `style.md`'s back
  pocket merges in for free.
- **Wounds dry into patina:** fresh hits are glossy splats; over
  subsequent shots they dry into matte, misregistered stains. Damage
  literally becomes print wear — destruction and patina are one mechanism.
- **Big beats:** molten Play-Doh → pooling molten pigment; the mushroom
  cloud → a giant graphic paint-plume in stacked flat shapes, one-frame
  bald eagle as a print stamp; clay title card → splat card.

## Print wear — how age reads

Secondhand wear reads as **print wear**: slightly off-register color fills
on old objects (the truck's chips become misregistered plates), sun-faded
hues, paper-tone ghosting at edges. Fresh printed objects are *perfectly*
registered, fully saturated — too perfect, which is the "NOT A TOY" note.

Print wear stays on the built world; people keep their clean registration
(blush dot excepted), so wear reads as the world aging *around* them.

**The sweet-tea pitcher stays pristine:** the one thing in the film with
zero misregistration and full saturation. It out-prints the world around
it, which is only legible while nothing else does.

## Production notes (Blender / EEVEE)

- **Engine: genuinely open, and now a free choice.** Killing banding
  (2026-08-04) removed `Shader to RGB`, the only EEVEE-only node in the
  stack, so `MCM_Toon` runs unmodified in both engines and nothing about
  the look forces the decision any more. The kettle demo itself renders
  in Cycles. What still differs is shadow character and bounce fill —
  and physical bounce may *fight* the art-directed global shadow tint,
  which is now the **only** real tiebreak.
  - **Measured 2026-08-04 (C10, identical shader, both engines):** EEVEE
    holds dab contrast crisp and graphic; Cycles' bounce fill lifts the
    shadow side and visibly *dilutes* the dab read, and ground bounce
    pushes warm colour up onto the body. For a style whose entire
    identity is the dab grain, that leans **EEVEE** — not because
    anything forces it now, but because physical bounce washes out the
    look. If Cycles is wanted for the 3090 farm, it needs clamped/limited
    diffuse bounces to compete. Confirm on the sq020-sh020 frame.
  - Render cost is not the tiebreak: Ian's PC with one or two RTX 3090s
    is available as a Cycles farm, and the style is cheap in either
    engine (diffuse-only, no glass, no reflections).
- **The style is cheap by construction.** No raytraced reflections, no AO
  pass, no bloom, no cloth sim, no hair systems, no specular outside wet
  paint — every one of those is an aesthetic choice made for the look,
  which happens to also cost nothing. Frames render extremely fast.
- **The dab painter** (`tools/addons/redwood_dabpaint.py`, designed
  2026-08-04 — `docs/superpowers/specs/2026-08-04-tilt-dab-painter-design.md`):
  one native brush stroke sets both channels, because the painted image
  isn't colour at all. It stores `R = albedo swatch index`,
  `G = tilt swatch index`, and two film-wide 256×1 LUTs resolve those
  indices into the real colour and the real tangent normal. One image
  means Ctrl+Z is correct by construction; regenerating a palette
  recolours every dab in the film; and any albedo composes with any
  tilt, so the two axes are independent with no pair table. Both
  palettes are freeform — pick a swatch, paint, change either, keep
  painting.
- **Generated, not hand-managed:** `tools/tilt_palette.py` (built
  2026-08-03) is the tilt swatch registry and emits the palette
  artifacts into `assets/materials/tilt_palette/` — picker sheet, JSON,
  LUT, swatch icons. `tools/albedo_palette.py` is its counterpart for
  colour. Retune → rerun → nothing repainted (old swatches stay valid,
  new ones append; only *reordering* would invalidate painted pixels).
  `tilt_palette.json` still carries a per-family tier table from before
  legality was dropped — that field is vestigial and nothing reads it.
- **Routes tried and rejected 2026-08-04**, recorded so they don't get
  retried: two-pass painting (normals, then colour) defeats the
  technique, because the dab boundaries stop coinciding; the Ucupaint
  layer-pair kit works but needs a layer switch before *every dab*; a
  scratch-image "commit dab" operator desynced undo and outlined every
  stroke in black. Full reasoning in the design doc.
- **Object-space variant in the back pocket** (Gindy's original: bake
  object-space normals, overpaint sampling from the bake — full
  resculpting-by-paint): rigid hero props only, unique UVs required. It
  can't go on deforming meshes — the bake is in object space, so it's
  wrong the moment the mesh moves.
- **Noir-window trick** (stolen from the kettle file): painted
  window-light texture + a light-path shadow-ray gag casts painted
  mullion shadows — a direct fit for the garage interior.
- **Value-check toggle:** a compositor HSV with saturation dropped to 0
  for black-and-white value studies — the kettle file shipped saved in
  that state; keep it as a one-click check while lighting.
- **Blockout economics:** flat shading *wants* simplified geometry, and
  the pipeline already has blockout-grade geometry everywhere. The
  distance from the current animatic to final frames is shorter under this
  candidate than any other.
- **Tools:** Ucupaint (free) stays installed for layered *region* work —
  it is not the dab painter; Deep Paint Pro (~$40) for gouache/pastel
  brushes and material presets to dissect. Both are conveniences — the
  core machine is vanilla nodes. **To verify: Deep Paint's Blender 5.x
  compatibility** (it claims 3.6+).
- **No camera projections.** Dome sky + world-space grain keep the
  camera-driven layout pipeline unconstrained. A projection would make
  the camera a shading authority as well as a framing one, and
  `docs/layout.md` depends on it being only the latter.

## What this style doesn't do — and why

Not prohibitions. These are the choices that make it one style rather
than several, each one buying something specific. If a shot ever wants
to spend one, that's worth doing on purpose rather than by drift.

- **Outlines / linework** (Freestyle, Line Art, grease pencil) —
  stroke-free is what separates this from Candidate C and its per-shot
  2D labor. The shapes have to hold on colour alone.
- **Raytraced reflections/refractions, render AO, bloom/glow** — each
  one lays a smooth photographic gradient over a world built from flat
  registered shapes.
- **Diffuse poster banding / `Shader to RGB` quantization** — dropped
  2026-08-04 on measurement: it suppresses the tilt dabs everywhere but
  the terminator, and the dabs are the look. Doesn't touch the separate
  distance-banding of colour toward paper/sky tone under "Depth".
- **Smooth CG gradients inside a shape** — shading variation comes from
  light plus tilt dabs. A painted or procedural gradient fills the same
  space with none of the hand in it.
- **Photographic textures** — the world is registered colour on paper,
  and a photograph is the one thing that can't be.
- **Camera projections** — see production notes: the camera stays a
  framing authority only.
- **Soft-body droop/melt as behavior** — the claymation candidate's
  vocabulary. Molten *aftermath* is wet-paint FX and welcome; solid
  objects deforming as a gag is the other film.
- **Specular outside wet paint** — gloss is the signal that something is
  wet and doesn't belong. Spread it around and the FX stop reading.
- **Mint outside the truck and the sweet tea** — a reserved colour is
  only reserved if it goes unspent everywhere else.
- **Memphis patterns, airbrush gradients, neon hues** — the 80s/90s
  stratum is drawn in the same serene gouache as everything else. An
  era-differentiated graphic language would let the frame acknowledge
  the anachronism, and the deadpan depends on it never doing that.
- **Annex swatches on sky, terrain, or architecture** — see the annex
  above: they read as *added later* only because those three never wear
  them.

## Maybes (decide late, by test render)

- **Motion blur** — prints don't blur, but the solo's fast action may want
  it. Test with and without.
- **DOF** — same: poster flatness argues no, cinematic camera may argue
  yes on close-ups.
- **Comic onomatopoeia** ("BLAM" cards) — period-plausible and
  music-video-friendly, but a big tonal move.
- **VHS broadcast finish** — the `style.md` back-pocket modifier stacks on
  this candidate too if wanted.

## Pinned state (2026-08-04 — resume later this week)

Done:

- This treatment, developed and revised through the tilt-dab discovery.
- `tools/tilt_palette.py` + generated picker sheet and JSON in
  `assets/materials/tilt_palette/` (sheet verified by eye: flat column
  uniform, whisper near-flat, strong row cycling hue around the clock).
- Kettle demo filed at `~/blender/add-ons/cody-gindy-kettle-patreon-02.blend`;
  extracted textures + color re-render examined.
- The 1993 setting layer (2026-08-03): serene-print era clash, the
  two-strata content split, the 4-swatch annex, Mom's mall-glam
  replacement of the curler look, the sheriff's boxy Crown Vic. Setting
  canon recorded in `style.md` shared givens.
- **Tilt-dab proof, 2026-08-04 — the technique is validated and banding
  is dead.** `assets/materials/tilt_dab_test/` (mint 1963 C10,
  `MCM_Toon`, paintable tilt + albedo maps, Blender palettes built from
  the swatch JSON, sun turntable). Run tablet-free with procedurally
  stamped dab maps. Findings: banding suppresses dabs everywhere but the
  terminator, so it's out film-wide; the engine is consequently
  unforced; and whisper is too gentle to read at shot distance, so tier
  choice is a per-surface judgement rather than a fixed assignment.
  Ucupaint 2.4.9 installed and enabled.
- **Per-family dab-tier assignments dropped, 2026-08-04.** The stucco /
  terrain / grass / diecast / characters tier table is deleted — tier is
  a freeform choice at the brush. Its last home is a vestigial field in
  `tilt_palette.json`.
- **Dab painter built and painting, 2026-08-04** —
  `tools/addons/redwood_dabpaint.py`, designed in
  `docs/superpowers/specs/2026-08-04-tilt-dab-painter-design.md`. One
  stroke sets both channels; undo is correct by construction because
  there is only ever one image. `tools/albedo_palette.py` ships with it:
  15 bases x 5 drifts, 90 swatches. Confirmed working in the UI on a
  plane in `tilt_dab_test.blend`.

Next, in order:

1. **Settle the albedo palette.** The 90 swatches are a first guess made
   to get the machinery working. Near-neutral bases (charcoal-plastic,
   seafoam-grey) produce six near-identical drifts, and warm/cool only
   mean what they say near the neutral axis. Cheap to change *now* —
   nothing is painted, and reordering the palette repaints every existing
   dab once something is.
2. **Paint one asset** — the truck or the Santa — with the painter, to
   feel the workflow on a real surface. Watch for index fringing at dab
   boundaries early rather than late. Blocked on the tablet.
3. **Stage the sq020-sh020 test frame** and A/B: EEVEE vs Cycles (both
   now open — banding is dead, so nothing forces the engine), motion
   blur, DOF, and how the tiers actually read at shot distance — this
   candidate vs Bigature, side by side.

Open verify items:

- ~~Blender color-pick behavior on Non-Color images.~~ **Closed
  2026-08-04** by building the swatches as real Blender *palettes*
  (`tilt_DIECAST_legal`, `tilt_ALL` in the test file) straight from
  `tilt_palette.json`'s `rgb8`, stored as raw floats. Clicking a palette
  swatch writes the exact intended byte into a Non-Color image. Never
  type hex (the field assumes sRGB) and never eyedropper the sheet (it
  samples display-transformed pixels) — both silently corrupt the
  encoding. This trap is why the dab painter sets `brush.color` itself
  from the palette JSON instead of leaving colour picking to the hand;
  the test file's hand-built palettes are superseded by its swatch grid,
  and `tilt_DIECAST_legal` is a leftover of the dropped tier table.
- Deep Paint's Blender 5.x compatibility (claims 3.6+).
- ~~Whether Ucupaint mask/alpha painting writes with correct values into
  Non-Color normal-channel overrides.~~ **CLOSED 2026-08-04 — it works.**
  Confirmed in the UI on a test plane: one Solid Color layer with an image
  mask, Color channel Source = Custom Color (rust) and Normal channel
  Source = Custom Color (`#804af3`, `h06_strong`). Painting the mask white
  drove *both* channels from one stroke. Measured across sun azimuths, the
  untilted mint base held constant at ~0.42 luminance while the painted
  patch swung 0.43 → 0.04 — a tilt that is genuinely live, not a colour
  swap. Ucupaint 2.4.9 on Blender 5.1.2. Two gotchas found en route:
  - **The Normal channel defaults to Bump mode.** In Bump it reads the
    swatch as a *height*, not a tangent normal, and fails silently — a
    headless run gave a constant result across flat/whisper/soft/medium/
    strong and across directions, with no error. It must be switched to
    **Normal Map**. (Internally: `override` is the bump slot, `override_1`
    is the normal-map slot.)
  - **The Ucupaint kit probably cannot be script-generated.** Building a working
    ypaint stack from Python failed repeatedly — colour worked but the
    Normal output rendered black through `set_input_default_value`,
    `check_all_channel_ios(yp_node=...)`, a hard reset, and an explicit
    Geometry normal. The tree is assembled by UI-driven update callbacks;
    `override_1_color` has no update callback and is merely a mirror of a
    node input socket. Together with the layer-switch-per-dab cost, this
    is why the Ucupaint route was dropped entirely rather than re-scoped
    to a hand-authored template — the technique was sound, the
    ergonomics weren't.
- The noir-window trick comes from the Cycles kettle file and leans on
  a light-path gag — verify it (or an equivalent gobo approach) in
  EEVEE if EEVEE wins the engine A/B.
