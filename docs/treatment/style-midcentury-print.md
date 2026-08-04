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
and is recorded in `style.md`'s shared givens. This doc legislates only
how the print expresses it.

## The two strata — content law

Every object in the lived-in world belongs to one of two strata:

- **The 1962 stratum** — architecture and built-ins: flat roof, deep
  fascia and overhangs, glass walls, breeze-block screen, terrazzo, the
  pink kitchen (`refs/house/`). Plus the mint C10 — a period-coherent
  relic. This stratum wears the core MCM palette.
- **The 1980s–90s stratum** — everything the family added out of
  necessity: the hand-me-down plaid recliner, particle-board shelving,
  the 27-inch CRT, boombox, VCR, cordless phone, the boy's printer, all
  wardrobe, the sheriff's Crown Vic. This stratum may draw on the 1993
  annex swatches (below); core MCM swatches remain legal on it.

**The hodgepodge law: every lived-in frame carries at least one
post-1980 object.** The architecture is never dressed pure — the film
never shows the clean 1962 poster, only 1993 wearing it.

**Dilapidation is content, not medium.** The print stays flat and clean
while *depicting* wear: a fascia board replaced with bare plywood, dead
patches in the lawn, aluminum foil sunshading one clerestory, a swamp
cooler squatting on the flat roof, the duct-taped blow-mold Santa
(already canon). Era makes no difference to print wear — the patina law
stays uniform; a thrifted 1985 recliner fades and misregisters exactly
like a 1962 breeze block.

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

- **`MCM_Toon`** — flat painted albedo in, poster shading out. The tilt
  map perturbs the normal; diffuse is then either quantized to 2–3
  poster bands (Shader-to-RGB) *or* left soft and physical — **A/B at
  the test frame**: with dabs carrying the painterly read, banding may
  be redundant. Either way the terminator breaks along stroke shapes,
  never a smooth CG gradient, and shadow color runs through the
  **global shadow tint** (poster shadows shift hue, not just value).
- **The tilt palette** (replaces the old procedural `MCM_Grain` noise —
  dabs killed it). A swatch = direction × lean, encoded as a
  tangent-space normal color; flat blue = no tilt. Crucially the two
  palettes are **independent axes**: a dab-kit entry is an
  (albedo × tilt) *pair*, and one surface uses several tilts of the same
  albedo — neighboring dabs disagreeing slightly about direction is the
  entire gouache effect.
  - **12 directions, universal film-wide** — one hand paints the movie.
    No per-asset bakes; the same swatches serve every object.
  - **Magnitude tiers are the material axis:** whisper (~3°), soft
    (~7°), medium (~14°), strong (~25°). Family legality: stucco /
    siding / cream surfaces = whisper+soft; terrain / road =
    soft+medium; grass & foliage = medium+strong with vertical-biased
    directions and elongated dabs; diecast = whisper, with strong
    reserved for crease accents; characters = whisper+soft only.
  - **Albedo drift:** each palette swatch carries 2–3 legal drift
    variants (warm / cool / dusk) for dab-level color variation.
  - **Distance scaling:** tilt magnitude steps down with the depth
    bands — far layers get whisper-or-nothing. Painterliness is a
    foreground privilege, exactly like the refs' flat backgrounds.
- **Albedo law:** albedo may contain placed color variation (Ucupaint
  layers: a warm patch on a wall, a darker pass at a roofline, painted
  occlusion accents under eaves) but **never directional shading** —
  light direction belongs to the render — and never faked relief:
  surface facets belong to the tilt map alone.
- **Matte is the world's law.** Specular is zero film-wide. The only gloss
  in the entire film belongs to wet-paint FX.
- **Glass is a graphic fill** — windows and truck glass render as flat
  poster fills with a painted diagonal gleam shape. No raytraced anything.
- **No render AO.** Structural darkening is painted into albedo, placed by
  hand.
- **Depth is graphic, not atmospheric:** distant layers step toward
  paper/sky tone in discrete bands (the refs' mountains) via an optional
  distance-banding input on `MCM_Toon`. No mist.

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
| **mint (reserved)** | `#76e7cd` | **the truck and the sweet tea. Nothing else, ever.** |

- **The mint law survives the teal world** by hue-and-value separation:
  sky-teal is deep and dusty; mint is pale and saturated. No other object
  may wear mint.
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

Annex law:

- Legal **only on post-1980 objects**; never on sky, terrain, or
  architecture.
- Never the majority of a frame — core MCM swatches keep majority rule
  everywhere.
- Each annex swatch carries drift variants and obeys the dab-tier family
  legality exactly like a core swatch.
- **The mint law survives the annex** the same way it survives the teal
  world: seafoam-grey is grayed nearly to neutral, faded-denim is grayed
  blue; mint stays pale *and* saturated. No collision.

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
- **One print artifact is allowed on people:** the off-register **blush
  dot** — period-correct Golden Books misregistration, and the project's
  off-register signature surviving on flesh. Otherwise people are always
  cleanly registered.
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
    is the car (see strata law) — a boxy 80s LTD Crown Victoria, a
    decade out of date even in 1993, cream body with the rust pop the
    palette already assigns (`refs/cop_car/`).
- Character DNA still comes from `refs/boy/`, `refs/mom/`, `refs/cop/` —
  wardrobe and grooming silhouettes, translated to flat shapes.
- **Dab tiers: whisper + soft only.** Tangent-space tilts deform
  correctly with the rig, so the grain survives animation; the gentle
  tiers keep flesh calm while the world around it gets brushier.

## Motion

- **Camera: smooth and cinematic.** Existing layout and camera work carry
  through unchanged.
- **Characters: limited animation** — strong holds, snappy transitions.
  Fast actions use **painted smears**: the smear frame is literally a
  brushstroke shape, plus optional speed-line cards.
- **No soft-body comedy.** Objects in this world do not droop, sag, or
  melt as behavior — that vocabulary belongs to the claymation candidate.
  Destruction is splatter and graphic effects only.
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

## Patina law — print wear

Secondhand wear reads as **print wear**: slightly off-register color fills
on old objects (the truck's chips become misregistered plates), sun-faded
hues, paper-tone ghosting at edges. Fresh printed objects are *perfectly*
registered, fully saturated — too perfect, which is the "NOT A TOY" note.

Print wear touches the built world only, never people (blush dot excepted).

**The sweet-tea pitcher is still the single lawfully pristine object:** the
only thing in the film with zero misregistration and full saturation. It
out-prints the world around it.

## Production notes (Blender / EEVEE)

- **Engine: EEVEE assumed, not settled — decide at the test frame.**
  The kettle demo itself renders in Cycles; the dab technique is
  engine-agnostic (painted normals shade identically everywhere), but
  the engines differ in shadow character and bounce fill — and physical
  bounce may *fight* the art-directed global shadow tint. The banded
  variant needs Shader-to-RGB (EEVEE-only); the soft-physical variant
  runs in either engine. Render the test frame in both and look. If
  banding wins, EEVEE is locked. Render cost is not the tiebreak:
  Ian's PC with one or two RTX 3090s is available as a Cycles farm,
  and the style is cheap in either engine (diffuse-only, no glass, no
  reflections).
- **The style bans most render cost by law:** no raytraced reflections, no
  AO pass, no bloom, no cloth sim, no hair systems, no specular outside
  wet paint. Frames render extremely fast.
- **The dab kit (Ucupaint):** one layer per (albedo × tilt) pair in use —
  Color channel override = the swatch, Normal channel override = the
  tilt color, and the *painted element is the layer's alpha*. One
  stroke writes both channels with different colors: Substance
  Painter's multi-channel brush, rebuilt out of palette law. The kit
  ships as a template and is appended per asset.
- **Generated, not hand-managed:** `tools/tilt_palette.py` (built
  2026-08-03) is the swatch registry and emits the palette artifacts —
  picker-sheet PNG + JSON with the per-family legality table, in
  `assets/materials/tilt_palette/`. Retune the tiers → rerun → nothing
  repainted (old swatches stay valid; new directions interleave). The
  future dab-kit builder imports its math from the same module.
- **Escalation path if the kit chafes:** (1) two-pass painting — normals
  then color; the kettle file's color maps are nearly flat, so pass two
  is cheap; (2) the layer-pair kit; (3) a small "commit dab" operator
  (paint a scratch image; stamp alpha×colorA into albedo and
  alpha×colorB into the tilt map; clear). Build (3) only if (1)/(2)
  prove annoying in real painting.
- **Object-space variant in the back pocket** (Gindy's original: bake
  object-space normals, overpaint sampling from the bake — full
  resculpting-by-paint): rigid hero props only, unique UVs required,
  never on deforming meshes.
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
- **Tools:** Ucupaint (free) for layered albedo painting; Deep Paint Pro
  (~$40) for gouache/pastel brushes and material presets to dissect. Both
  are conveniences — the core machine is vanilla nodes. **To verify: Deep
  Paint's Blender 5.x compatibility** (it claims 3.6+).
- **No camera projections anywhere.** Dome sky + world-space grain keep
  the camera-driven layout pipeline unconstrained.

## Banned list (within this candidate)

- Outlines / linework of any kind (Freestyle, Line Art, grease pencil)
- Raytraced reflections/refractions, render AO, bloom/glow
- Smooth CG gradients inside a shape (shading variation comes from light
  + tilt dabs, never from painted or procedural gradients)
- Photographic textures anywhere
- Camera projections
- Soft-body droop/melt comedy on objects (molten *aftermath* is lawful
  wet-paint FX; what's banned is solid objects deforming as behavior)
- Specular outside the wet-paint FX family
- Mint on anything but the truck and the sweet tea
- Memphis patterns, airbrush gradients, neon hues — the 80s/90s stratum
  is drawn in the same serene gouache as everything else; no
  era-differentiated graphic language
- Annex swatches on sky, terrain, or architecture

## Maybes (decide late, by test render)

- **Poster banding vs soft physical diffuse** — with tilt dabs carrying
  the painterly read, 2–3 band quantization may be redundant. A/B the
  test frame both ways; the kettle file argues soft-physical is enough.
- **Motion blur** — prints don't blur, but the solo's fast action may want
  it. Test with and without.
- **DOF** — same: poster flatness argues no, cinematic camera may argue
  yes on close-ups.
- **Comic onomatopoeia** ("BLAM" cards) — period-plausible and
  music-video-friendly, but a big tonal move.
- **VHS broadcast finish** — the `style.md` back-pocket modifier stacks on
  this candidate too if wanted.

## Pinned state (2026-08-03 — resume later this week)

Done:

- This treatment, developed and revised through the tilt-dab discovery.
- `tools/tilt_palette.py` + generated picker sheet and JSON in
  `assets/materials/tilt_palette/` (sheet verified by eye: flat column
  uniform, whisper near-flat, strong row cycling hue around the clock).
- Kettle demo filed at `~/blender/add-ons/cody-gindy-kettle-patreon-02.blend`;
  extracted textures + color re-render examined.
- The 1993 setting layer (2026-08-03): serene-print era clash, the
  two-strata content law, the 4-swatch annex, Mom's mall-glam
  replacement of the curler look, the sheriff's boxy Crown Vic. Setting
  canon recorded in `style.md` shared givens.

Next, in order (blocked on tablet):

1. **Paint one asset** — the truck or the Santa. Two-pass first (tilt
   dabs, then albedo drift) to feel the workflow before building the
   Ucupaint kit. Note the trade discovered en route: kit-painted color
   stays a live variable (overrides re-color painted dabs film-wide);
   two-pass bakes it. If palette flexibility matters, build the kit.
2. **Stage the sq020-sh020 test frame** and A/B: banding vs
   soft-physical diffuse, EEVEE vs Cycles (soft-physical only —
   banding can't leave EEVEE), motion blur, DOF — this candidate vs
   Bigature, side by side.

Open verify items:

- Blender color-pick behavior on Non-Color images (sample from the
  sheet, don't type hex — hex field assumes sRGB).
- Deep Paint's Blender 5.x compatibility (claims 3.6+).
- Whether Ucupaint mask/alpha painting writes with correct values into
  Non-Color normal-channel overrides (test on the first asset).
- The noir-window trick comes from the Cycles kettle file and leans on
  a light-path gag — verify it (or an equivalent gobo approach) in
  EEVEE if EEVEE wins the engine A/B.
