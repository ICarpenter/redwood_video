# guns — the house (modeling spec)

Turns the greybox house in `assets/envs/property/property.blend` into the
real set: **the 1962 flat-roof desert-modern pavilion the setting canon
demands** (`style.md` shared givens, developed in `style-midcentury-print.md`),
on the exact footprint the greybox already occupies. Site logic: `site.md`.
Shot beats: `script.md`. Refs: `refs/house/`, plus
`refs/styles/il_fullxfull.5572769945_bsf5.webp` — the house's self-image.

The ref that resolves "flat roof" into a real building is
`refs/house/f1b1fc07-….image.webp`: a desert tract house — near-flat roof,
deep white fascia on a wide cantilevered overhang, masonry walls, swamp
cooler squatting on the roof. That is this house's bones. The Eichler ref
supplies the cladding and beam vocabulary; the catalog plans (6141/6144/6146)
supply window pattern, the three-lite front door, and catalog-illustration
proportions; `pinkkitchen2.jpg` is the 1962 kitchen, `Kitchen1.jpg` the 1993
clutter that sits on top of it.

## Hard invariants (from the pipeline, not negotiable here)

1. **The footprint is frozen.** House `x −7…5, y −4…5`, garage
   `x −13…−7, y −3…3`, porch deck `x −5…1, y −6.4…−4`, back stoop
   `x −4…−1, y 5…6.2`. Blocking and ~40 shot cameras assume these masses.
2. **Every existing opening keeps its exact plan position, sill, and head.**
   Openings may gain frame styling; they may not move, shrink, or change
   datum. New openings are allowed (flagged below) but must pass the
   re-render check.
3. The property stays linked at identity; ground datum `z = 0`; all house
   objects stay inside the `property` collection; preview cameras stay out.
4. **Anything that changes state on camera is a prop, not set.** The
   clothesline already established this law (it must fall, so it lives in
   `props.blend` and is instanced per shot). Doors and window sashes obey
   the same law — see *Functional elements*.
5. Verify by rendering and looking (preview cams + the shot list at the
   end), never by trusting the numbers.
6. Work happens by hand-editing `property.blend` in Blender (it is
   hand-maintained; `blockout_property.py` refuses to touch it). Blender
   closed before any headless render pass. Commit the blend by explicit
   path (git-LFS), with a snapshot commit before the first edit.

## Massing & dimensions

All metres, world space. Existing numbers marked ▸ are unchanged from the
greybox; everything else is the flat-roof adaptation.

### House block

| element | dimension |
|---|---|
| ▸ shell footprint | `x −7…5` (12.0) × `y −4…5` (9.0) |
| ▸ wall thickness | 0.25 |
| ▸ wall top (plate) | `z 3.2` — kept, so the eave line barely moves |
| roof | flat slab `z 3.2…3.35`, tar-and-gravel top |
| fascia | continuous band `z 3.2…3.6` (0.4 deep), the MCM signature move |
| overhang | roof + fascia cantilever **0.75** past the wall on east, north, and west free faces; south only where the garage isn't |
| beams | post-and-beam expression: 0.10 × 0.25 section, running east–west (spanning y), underside at `z 2.95`; ends punch through the east and west fascia by 0.15. Module ≈ 1.35 so beams land on both existing porch posts (x −4.7 and 0.7); set the exact array in-file |
| interior ceiling | `z 2.95` between exposed beams (visible in sq050-sh040) |
| ▸ gable roof | **deleted** — `house_roof` (ridge 5.2) goes away; see *What changes on screen* |

### Porch (east, onto the road)

| element | dimension |
|---|---|
| ▸ deck | `x −5…1, y −6.4…−4`, top `z 0.5` — now reads as a raised concrete/terrazzo slab |
| steps | **new** — two treads, 0.25 risers, full run `x −3…0` on the east edge (the boy takes them in one jump, sq010-sh030); doormat zone in front of the door |
| canopy | the main roof plane continues east over the deck to `y −6.6` between `x −5.2…1.2` — one flat plane at `z 3.2…3.6` replacing the separate 3.0 porch roof (underside rises 0.2; posts lengthen to meet it) |
| ▸ posts | at x −4.7 and 0.7, slimmed to 0.12 square steel-profile posts, `z 0.5…3.2` |
| breeze-block screen | **new, optional dress** — one 2.0 × 2.4 panel closing the porch's south end (`x = −5` plane); pure Palm Springs signature, frame-left in sq010-sh030. Keep clear of the door path |

### Garage (south, the passthrough)

| element | dimension |
|---|---|
| ▸ shell | `x −13…−7, y −3…3`, wall top 2.9 |
| roof/fascia | flat slab `z 2.9…3.0`, fascia band `z 2.9…3.25`, overhang 0.6 east/south/west — the fascia line steps down 0.35 where it meets the house; the step is the composition beat where the two masses read as one building |
| ▸ passthrough | opening `x −12.4…−7.6` (4.8 w) × `z 0.1…2.4` both ends — frozen; the road→print→killing-field sightline is the film's spatial engine |
| door leaves | glass-paneled sectional doors (mustard-ranch ref), modeled **parked open** — panels and track visible overhead inside the tunnel from sq010-sh045's reverse. Never rigged, never closed; the script never closes them |

### Roofscape (the 1993 layer)

- **Swamp cooler** on the house roof, NW quadrant (~`(−4, 3)`): 0.9 × 0.9 ×
  0.8 box on a low curb + duct. It is canon-flavored dilapidation
  (`style-midcentury-print.md`) and it buys back silhouette lost with the
  ridge.
- **TV aerial** mast at the SE corner, ~1.8 above the deck: 1993 rural, thin
  silhouette interest in the wides.
- Two scupper-and-downspout drops on the fascia (north and south faces).
- One fascia board on the east face replaced with bare plywood — the
  flagship "dilapidation is content" beat.

## Elevations — openings are frozen, treatments are new

Head datum stays 2.4 everywhere (back door 2.55). Frames go thin
aluminum-or-painted-wood MCM profiles; the fat casing/sill greybox trim
goes away except as slim head/jamb reveals.

**EAST (front, y = −4, faces the road).** Porch spans x −5…1.
- ▸ `front_south` `x −6.00…−4.20`, sill 1.2 → picture window, single lite.
- ▸ `front_north` `x 1.99…3.79`, sill 1.2 → picture window.
- **New:** clerestory ribbon above it, `x 1.4…4.6, z 2.6…3.05` — the band
  one sheet of aluminum foil later sunshades. New cut: needs the re-render
  check on sq010 shots.
- ▸ front door `x −2.4…−1.4`, `z 0.5…2.5`: MCM slab with three staggered
  lites, painted the accent color (the 6141 ref's orange door, translated
  to the palette — terracotta/rust family; **never mint**).
- Screen door in front of it — a prop; see *Functional elements*.

**NORTH (x = 5, the corridor).** The sheriff's crawl and Mom's kill-window.
- ▸ `kitchen_north` casement pair `y 1.60…4.20`, sill 1.2, head 2.4 —
  **person-sized and functional**, see below. Mom spots him through it
  (sq050-sh030), is seen through its glass (sh035), fires through it
  (sq060-sh014).
- ▸ `north_east` `y −2.8…−1.4` → fixed lite.
- Cladding: this wall carries the clearest grooved-siding read — it gets
  raked morning light down its whole length.

**WEST (y = 5, the backyard).** The massacre-watching face; dusk key.
- ▸ `kitchen_west` casement pair `x 1.40…4.20`, sill 1.2 — the window Mom
  watches through (sq040-sh020) and climbs out of (sq070-sh010): each leaf's
  clear opening ≥ 1.25 wide × 1.2 tall, genuinely passable.
- Window box hung under the *south leaf's* half of the sill — the flower
  pot the arm lands in ([IF TIME] runner) waters here. South half only:
  the north half is the sill Mom vaults in sq070-sh010, and the exit path
  stays clear.
- ▸ back door `x −3.40…−2.20`, `z 0.45…2.55`: half-glass slab door onto the
  stoop (Mom's sq060-sh012 firing position is planted in front of it).
- ▸ `west_south` `x −6.4…−5.2`, sill 1.5 → fixed, obscure glass (bathroom).
- The wall band `x −2.2…1.4` between door and casements stays solid —
  the gun-cabinet-adjacent interior needs wall, and full glass here would
  expose shell interior the film never dresses.

**SOUTH (x = −7).** Mostly eaten by the garage (y −3…3).
- ▸ `south_west` `y 3.4…4.6`, sill 1.2 → fixed lite.

## Interior scope

**The kitchen is the only house interior the film shoots** (sq050-sh040
holds a mid-shot across it). It is the whole west half (partition at
`y 0…0.25`, kept). Build to mid-shot depth, 1962 bones first:

- Counter run along the west wall, sink centered under `kitchen_west` —
  Mom-at-the-sink is the watching position; counter continues around the
  NW corner under `kitchen_north`.
- **Pink tile** counter + backsplash, white slab-front cabinets
  (`pinkkitchen2.jpg`), painted block or plaster walls, terrazzo-look
  floor.
- Exposed ceiling beams continue inside at `z 2.95`.
- Clear wall space beside `kitchen_north` (toward the NE corner) for the
  `gun_cabinet` prop — it stays a prop in `props.blend`.
- The 1993 stratum (white fridge wearing clippings, boombox, clutter —
  `Kitchen1.jpg` energy) is set dressing, separate objects, so the
  hodgepodge law ("every lived-in frame carries at least one post-1980
  object") can be satisfied per shot.
- East half of the house: empty shell, painted `interior`; add one cased
  1.2 m opening in the partition (~`x −0.5`) so the plan is truthful if a
  camera ever crosses. Nothing else.

**Garage interior is its own dressing pass** (wood paneling per
`refs/garage interior/`, the printer bench, junk) — not this spec. This
spec only guarantees its envelope: the tunnel, parked-open doors, and
clean interior wall/ceiling surfaces to dress against.

## Functional elements — the state law

The property is linked at identity everywhere, so a linked object cannot
change pose per shot. **The house ships one static state; every stateful
leaf is a separately-instanced prop** (each leaf its own collection with
origin on the hinge line, so a per-shot angle is just the instance's
rotation — same mechanism as every other guide).

| element | static state in the house | prop leaf | shots that stage the prop |
|---|---|---|---|
| kitchen casements ×2 | **baked open ~62°** (rural summer; matches today's set; correct for the firefight and the climb-out) | `casement_leaf` (glazed sash, hinge-origin) | sq050-sh035 needs *through the glass*: stage one leaf at ~15–20° over her face. sq040-sh020 likewise if the closed read wins the frame |
| screen door | **absent** from the set (invisible at distance) | `screen_door` — wood frame + mesh, spring-hinge origin, opens outward | sq010-sh010/020/030 (the ♪ door-slap is sh030's animation) |
| front door | baked **open inward** ~80° — dark doorway reads, boy's exits stay unobstructed | reuse leaf only if a shot ever needs it moving | — |
| back door | baked **closed** | `back_door_leaf` | sq060-sh012 (open behind Mom on the stoop), any stoop beat that wants it |
| garage sectionals | parked open, static forever | — | — |
| gun cabinet | not in the house (wall space reserved) | existing `gun_cabinet` | sq050-sh040 |

If staging leaves per shot chafes in practice, the fallback is variant
swap-collections (like `santa` → `santa_torso`), not library overrides —
overrides fight every tool in the repo.

## Surfaces & material zones

Model now, shade later: the style is **not locked** (Bigature Claymation
vs Mid-Century Print — the sq020-sh020 test frame decides). So the model
carries clean, zoned material slots that both candidates can bind to.
Geometry stays neutral: **no modeled siding grooves, no modeled tile** —
both candidates draw surface pattern in the shader/paint layer (dabs or
plaster), and modeled grooves would fight the print candidate's flatness.

| slot | covers | Claymation (caste 2 earthy unless noted) | Mid-Century Print (core swatches only — annex is illegal on architecture) |
|---|---|---|---|
| `MAT_siding` | main wall cladding | troweled plaster, hand-finished, subtle patina | paper-cream, whisper+soft dabs, painted groove suggestion |
| `MAT_fascia` | fascia bands, beam ends | painted plaster, chips at corners | paper-cream (lighter drift); the one plywood patch board in sand |
| `MAT_block` | breeze-block, plinth course | adobe block | paper-cream w/ painted joints |
| `MAT_roof_gravel` | roof decks | packed grit | sand/khaki |
| `MAT_glass` | all panes | thin glass, existing alpha treatment | flat graphic fill + painted diagonal gleam (no raytrace, per style law) |
| `MAT_frames` | window/door frames, tracks | painted wood | paper-cream drift |
| `MAT_door_accent` | front door, garage door rails | chipped enamel (caste 3 — a manufactured slab) | terracotta/rust accent |
| `MAT_deck` | porch slab, steps, stoop | smoothed concrete | paper-cream/sand |
| `MAT_interior` | shell interior, ceiling, partition | painted plaster, light (headless-render lesson: never dark) | paper-cream |
| `MAT_kitchen_tile` | counters, backsplash | glazed ceramic (caste 3) | dusty-rose |
| `MAT_kitchen_cab` | cabinet faces | painted wood | paper-cream |
| `MAT_terrazzo` | kitchen floor, entry | polished aggregate | paper-cream + painted fleck dots |
| `MAT_metal_93` | swamp cooler, aerial, downspouts | diecast (caste 3), heaviest patina | charcoal-plastic legal (post-1980 objects) |

Patina is content in both candidates: chips/yellowing (claymation) or
misregistration/fade (print) on the built world only. The dilapidation
menu (plywood fascia board, foil clerestory, swamp cooler) is modeled or
placed geometry, style-independent. **Mint appears nowhere on this
building, ever.**

## Modeling techniques

- **Rebuild, don't boolean-patch.** Replace the boolean-cut greybox shell
  with planned wall segments: solid strips with openings built into the
  topology, quads, mitered corners, real reveals. The greybox stays in the
  file on a hidden `_greybox` sub-collection until the re-render check
  passes, then dies.
- One object per architectural system: shell, roof+fascia, beam array,
  porch, stoop, each window unit, doors, garage shell, kitchen built-ins,
  roofscape junk. Origins at sensible local points; transforms applied.
- **Window/door units as in-file collections, instanced** where repeated
  (fixed lite ×5 at three widths, casement unit ×2). Prop leaves
  (screen door, casement leaf, back door leaf) are built here but *live*
  in `props.blend` via `guide_assets.py` conventions, hinge at origin.
- Bevel modifier, weight-limited, ~1.5 cm — enough for a dab-lit or
  clay-lit edge to catch, small enough to stay architectural.
- Beam array via Array modifier off one beam; count/offset set to the
  porch-post module.
- Budget: shell+roof+beams ≤ 20k tris; units 1–2k each; whole building
  ≤ 60k. Flat shading wants simple geometry — the blockout-economics note
  in `style-midcentury-print.md` is the law here.
- Keep greybox object names on 1:1 replacements (`house`, `garage`,
  `win_kitchen_north_*`, …) so nothing downstream that greps names breaks;
  new elements get the same lowercase_snake convention.
- Materials: rebind the palette-named greybox materials where the zone
  matches (`house`→`MAT_siding` rename is fine); keep the `window` alpha
  treatment working in EEVEE until the style lands.

## UV & painting prep

Both candidates paint by hand (Ucupaint dab kit, or plaster/patina maps),
so UVs are cut for painting, not for photo textures:

- Non-overlapping UVs per object; seams on inside corners, under fascia,
  behind downspouts — never mid-elevation.
- **Axis-aligned, consistently oriented islands** (world-up = UV-up):
  the print candidate's tilt dabs are tangent-space, and a rotated island
  rotates every dab's direction with it. One orientation rule now saves
  re-painting later.
- Uniform texel density: hero elevations ≈ 3.5 px/cm at 4K per elevation
  map (house N/E/W each own a 4K; S+garage share one; roof, deck, interior,
  kitchen at 2K). Flat gouache and plaster both carry at this density.
- Instanced window units intentionally share paint across instances;
  unique wear, if a shot demands it, comes from realizing that one
  instance late — don't pre-realize.
- No second UV channel, no bakes: tangent tilt dabs need none. (The
  object-space Gindy variant stays in the back pocket and would demand
  unique UVs — another reason not to pre-overlap anything.)

## What changes on screen — and the re-render check

The one deliberate silhouette change: **ridge 5.2 → fascia 3.6** (+ swamp
cooler to ~4.3). Every wide framed against the gable will breathe
differently; sq010-sh010's sunrise-over-the-house is the film's opening
frame and the most exposed. Reframing, if needed, is lawful — camera only.

Render and eyeball, before/after, at minimum:

1. The six preview cams in `property.blend` (site/intro/backyard/kitchen/
   road/sidecorridor).
2. `sq010-sh010` (roofline hero), `sh030` (porch, steps, screen door),
   `sh045` (passthrough reverse).
3. `sq020-sh030`/`sh040` (garage + Mom's doorway silhouette),
   `sh044` (Santa at the rear threshold).
4. `sq040-sh020` (west casement from outside).
5. `sq050-sh030`/`sh035`/`sh040` (north window POV, through-glass, kitchen
   interior with gun-cabinet wall).
6. `sq060-sh012` (stoop + back door), `sh014` (muzzle flash out of the
   north window past the truck).
7. `sq070-sh010` (aerial — roof reads at its largest), `sh040`/`sh050`
   (truce table facing the garage, reverse past the Santa).
8. `sq080-sh040` (final wide west — house is frame-edge but the fascia
   line leads the eye).

## Out of scope

Terrain undulation, the road/ditch, fence/treeline, the old truck, BBQ,
all cast/prop guides, garage interior dressing, and every shader decision
the test frame owns. The stale `site.md` note listing the porch as "Mom's
firing position, final shot" predates the west-sunset ending revision —
fix it there, not here.

## Decisions taken here (revisit only with a render in hand)

- Casements ship baked open; through-the-glass beats stage a leaf prop.
- Clerestory goes above `front_north` (east face) — the only new opening.
- Sills all keep greybox datums; no floor-to-ceiling glass anywhere (the
  self-image poster's glass wall is the house's *fantasy*; the built
  reality per the desert-tract ref is walls with windows — and the film
  only ever dresses the kitchen behind them).
- Porch canopy joins the main roof plane (underside 3.0 → 3.2).
- Breeze-block panel is dress, cuttable if it crowds sq010-sh030.
