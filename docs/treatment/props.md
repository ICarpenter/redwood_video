# guns — props, vehicles & set dressing (asset catalog)

Every non-character object the film needs, what fidelity it has to reach,
how to get it there, and whether it moves. Characters are a separate pass.

Site logic: `site.md` · Architecture: `house.md` · Shot beats: `script.md` ·
Style law: `style.md` · Registry: `../../tools/guides.py` · Refs: `../../refs/`

**A ✓ after an asset name means an L0 guide already exists** in
`tools/guides.py` and can be blocked into a layout scene today. Everything
without one has to be created. **new** marks an asset this catalog adds that
no document previously called for.

---

## 1. The elevation ladder

Everything is built as a primitive first and refined upward. Two things stay
separate, because conflating them is what makes asset budgets rot:

- **Rung = the requirement.** Set by the camera. Not negotiable per asset.
- **Technique = the route.** Set by cost. Freely swappable.

| Rung | Holds at | What it means |
|---|---|---|
| **L0 guide** | animatic only | Mass + scale + flat palette color. Blockable. 28 prop guides already exist. |
| **L1 background** | 8 m and beyond | Correct silhouette, correct stratum + palette family, no detail that survives a push-in. |
| **L2 mid** | 2–8 m | Real detail, real patina. Holds at conversational distance. |
| **L3 hero** | close-up | Hand-modeled, hand-painted, print wear authored per `style.md`. |

**Routes to a rung** — all four land at different ceilings:

| Route | Realistic ceiling | Use when |
|---|---|---|
| Scripted primitive (`guide_assets.py`) | L0–L1 | The thing is a box, a cylinder, or a flat. |
| Polyhaven / free CC0 | L1–L2 | It exists and it's generic (plants, tools, cans). |
| **Purchase** | L2 | A good asset exists and costs less than a day (vehicles, appliances). |
| **Hyper3D / Hunyuan generation** | L2 | Nothing exists to buy and the form is chunky, not precise. |
| Hand-modeled | L3 | It gets a close-up or it carries a gag. |

Bought and generated geometry arrive at **the same rung** — both need retopo
and a repaint into the print look before a shot renders. `pipeline.md` already says so.
Neither ever arrives at L3. With modest spend the rule is: **buy when a good
asset exists, generate when it doesn't, hand-build when the camera gets close.**

**Promotion rule: an asset moves up a rung only when a rendered frame proves
it needs to.** That is the repo's verify-by-looking law applied to budget.
Ship everything at L1, render the sequence, promote what looks thin.

## 2. Where an asset lives

`house.md` invariant 4 already says *anything that changes state on camera is
a prop, not set*. One clause extends it to cover dressing:

| Home | Rule | Cost |
|---|---|---|
| **Guide** (`props.blend`) | Per-shot position matters, **or** it changes state on camera | A build function + a registry entry |
| **Set dressing** (`property.blend`) | It sits in one world-space spot, identically, in every shot | Nothing — the property is already linked everywhere |
| **Mini set** (`assets/envs/<name>/`) | A cluster pulled into one or two shots and placed away from the property | One file, instanced on demand |

This split matters: it keeps roughly forty things — paint cans, shelving,
plants, fences, garage junk, mailbox — out of the registry entirely. They
never need per-shot placement, so they get modeled straight into
`property.blend` at L1 and are finished forever.

**Watch the weight.** `property.blend` is linked into every layout scene, so
dressing it costs every shot. Keep dressing on its own sub-collections
(`dressing_garage`, `dressing_yard`, `dressing_kitchen`) so a wide can exclude
what it can't see.

## 3. Animation policy

**No prop in this film requires an armature.** Every motion in the script
resolves to one of six mechanisms, listed in ascending cost. Do not reach past
the cheapest one that works.

| # | Mechanism | Covers |
|---|---|---|
| 1 | Rigid keyframe | The default. Most props, most shots. |
| 2 | Hinge empty | Parent the instance to an Empty on the hinge line, rotate the Empty. Already the documented pattern in `guides.py`. |
| 3 | Parts hierarchy + drivers | Wheels, gantry travel, a pistol slide. |
| 4 | Variant swap | The `santa` → `santa_torso` + `santa_head` precedent. Intact→wrecked, dress→ventilated, tire→flat, figure→headless. |
| 5 | Shape key | Reserved. One asset uses it (the butterfly). |
| 6 | Sim / FX | Fracture, particles, mushroom cloud, muzzle flashes, packing peanuts. |

**Deformation is TBD** (2026-08-05) — see *Deformation* under Motion in
`style.md`. How far the flat/angular print treatment carries droop, squash,
melt or splatter has to be seen moving before it can be specced. Consequences
for this catalog:

- **Nothing here is specced to deform.** Every asset resolves to mechanisms
  1–4 and 6. If the tests bring deformation back, it gets added to specific
  assets then, from evidence.
- **The armature finding survives either outcome.** Droop and squash are
  shape keys or sims, not rigs. The single asset that could conceivably want
  a bone chain is the machine gun's barrel, and a shape key covers it.
- **`sq020-sh040` is unaffected.** The scolded barrel-droop was never what
  that shot is doing — see *Open questions*.

**The assets that need real mechanism work** — everything else in the catalog
is mechanism 1 or 2:

printer · cruiser · delivery_truck · machine_gun · rosco · hubcap ·
clothesline · bbq · action figures · butterfly. Plus five hinge empties
(screen door, casement leaf, back door leaf, cruiser door, gun cabinet),
which cost minutes each.

---

## 4. Delivery & print chain

Cassette futurism: CRT phosphor, chunky rockers under toggle guards, ribbon
cable looms, reel-to-reel feedstock, dot-matrix output, wood-grain veneer side
panels, big mechanical buttons. Warm beige and amber, not chrome and blue.

| Asset | Lives | Closest look | Rung | Route | Motion |
|---|---|---|---|---|---|
| `printer` ✓ | guide | **sq010-sh060** — his nose is almost on it | **L3** | hand | Gantry + head + bed + panel lights. The film's biggest mechanism. |
| `delivery_truck` ✓ | guide | sq010-sh020, mid/far, never stops | L2 | buy (step-van) | Wheels, roll door, the package launch |
| `box` ✓ / `box_open` ✓ | guide | sq010-sh040/045, close | L2 | primitive + hand | Rigid; variant swap on the tear-open |
| `not_a_toy_sticker` | **new** — graphic | sq010-sh045 peel, sq020-sh020 slap | **L3 artwork** | hand (2D) | None — three placements of one artwork |
| `packing_peanuts` | dressing + particles | sq010-sh040 trailing, sh045 everywhere | L1 | primitive | Particle scatter |
| `printer_bench`, feedstock drums | dressing | sq010-sh060 background | L1 | primitive | — |
| `porch_mat` | dressing | sq010-sh020 — the package lands on it | L1 | primitive | — |

**Printer design brief.** The one asset with a hard functional requirement: it
must plausibly extrude a **1.8 m human-sized action figure** (`sq020-sh050`)
and a machine gun that lands on the floor (`sq020-sh020` — "picks the gun up
off the garage floor"). That means a **portal/gantry frame with a vertical
build volume ≥ 1.9 m**, open-fronted, with the output face aimed at the
garage's **rear** door so figures slide out toward the backyard. It extrudes
downward onto a low bed at floor level — soft-serve, per `sq020-sh010`. The
extrusion itself is a build modifier or shape key riding a curve, not a sim.

---

## 5. Garage

**Canon set here: the boy's father is a dead veteran** — same war as the
sheriff, different unit, they never met. The sheriff does not know this
family. This buys three things at no story cost: the war-surplus junk in the
garage has a reason to exist, it explains why this kid knows what a *firing
squad* is, and the inherited-violence undertone runs under the whole film
without anyone ever saying a word about it.

**Mom knows the sheriff the way anyone knows a county sheriff** — she voted
for him. That is the entire basis of her recognition in `sq070-sh030`, and it
is funnier than friendship, because the horror lands on her.

The camera looks into this room properly twice — `sq010-sh045`'s reverse
through the passthrough and `sq020-sh020`'s three beads on the garage junk.
Everything here is **dressing at L1** unless noted; the cluster within ~4 m of
the printer earns L2.

### The father's remnants

| Asset | Rung | Route | Note |
|---|---|---|---|
| `footlocker` | L2 | primitive + L2 decal | Olive drab, stenciled name worn to illegibility. The name is never resolved. |
| `war_surplus_junk` | L1 | buy/free | Ammo cans, canteen, entrenching tool, a mess kit. **This is the boy's toy box** — it is why he knows the pose. |
| `folded_flag_case` | L2 | primitive | Triangle case, high on a shelf. Small, unmissable. |
| `father_photo` | L1 geo / **L3 art** | hand (2D) | Framed on the pegboard. Never in close-up — it works better half-seen. |
| `dress_uniform` | L1 | generate | Garment bag on a nail. |
| `unfinished_project` | L1 | primitive | Something half-built on the bench under a dust sheet. Nobody moved it. |

### Christmas

| Asset | Rung | Route | Note |
|---|---|---|---|
| `xmas_boxes` | L1 | primitive | Labeled cartons, tinsel spilling out of one. |
| `aluminum_tree` + color wheel | L1 | generate | 1962 object in a 1993 pile — the hodgepodge law in one prop. |
| `light_strings` | L1 | primitive | Tangled, on a nail. |
| `plastic_reindeer` | L2 | generate | **Santa's sibling** — reuse the Santa's blow-mold material exactly. |

### Posters & signage

Graphics jobs, not modeling jobs: L1 geometry carrying L2/L3 artwork.

| Asset | Rung | Note |
|---|---|---|
| `campaign_sign` | L1 geo / L2 art | **"RE-ELECT SHERIFF ——", sun-bleached, in the junk.** Plants `sq070-sh030` for the price of one flat. |
| `pinup_calendar` | L1 / L2 art | Auto-parts calendar, wrong month, wrong year. |
| `band_poster` | L1 / L2 art | Matches the boy's tee (`refs/boy/`). |
| `beer_mirror` | L1 | Novelty sign, faintly reflective. |

### Electronics & hobby

| Asset | Rung | Route | Note |
|---|---|---|---|
| `tv` | L2 | generate | Wood-veneer portable on a shelf. Reads cassette-futurism next to the printer. |
| `cb_radio` | L1 | generate | The father's. Ties the war junk to the hobby bench. |
| `boombox` | L2 | buy | Also wanted in the kitchen — build once, place twice. |
| `broken_vcr`, tape stacks | L1 | primitive | — |
| `workbench`, `vise`, `pegboard` | L1 | primitive | Pegboard carries painted tool shadows with no tool in them. |
| `rc_plane` / model kit | L1 | generate | Half-built. |
| `fishing_gear`, tackle box | L1 | buy/free | — |
| `bicycle` | L1 | buy/free | The boy's. |
| `lawnmower`, `paint_cans`, `coffee_can_of_screws`, `extension_cord`, `shop_shelving` | L1 | free/primitive | Standard garage kitbash. One purchase covers most of it. |

---

## 6. Yard

| Asset | Lives | Closest look | Rung | Route | Motion |
|---|---|---|---|---|---|
| `santa` ✓ | guide | **sq020-sh044 dedicated CU**; **sq070-sh050 fills foreground** | **L3** | hand | Slump; variant→`santa_torso`+`santa_head` ✓ |
| `santa_charred` | **new** variant | sq070-sh050 foreground | **L3** | hand | Post-blast state |
| `bbq` | **new** guide | sq060-sh020 — the hiss insert | **L2→L3** | buy + resculpt | None, then fracture. Forest-green kettle, `refs/BBQ/` |
| `propane_tank` | sub-object of `bbq` | sq060-sh020 | L2 | — | The puncture is the beat |
| `old_truck` | **dressing** | sq050-sh030 mid; sq060-sh014 mid | L2 | buy C10 + resculpt | **None.** Parked forever; impacts are FX. No longer the ricochet surface (moved to the passthrough) — it keeps the sheriff's cover and Mom's sightline break |
| `clothesline` ✓ | guide | sq060-sh020, sq070-sh010 | L2 | primitive + hand | Falls in the blast |
| `sunday_dress` | **new** guide | sq060 — takes a hit, her aim changes | L2 | hand | Variant → ventilated |
| `laundry` (sheets) | dressing | sq050-sh020 sightline blocker | L1 | primitive | — |
| `lawn_flamingos` | **new** guide | sq060 — beheaded one per beat | L2 | generate | Variant → headless |
| `garden_gnome` | **new** guide | sq060 — takes cover behind the birdbath | L2 | generate | Rigid |
| `birdbath` | dressing | sq060 mid | L1 | buy/free | — |
| `back_fence` | dressing | **sq080-sh040 — they vault it** | L2 | primitive | — |
| `treeline` | dressing | far, every backyard wide | L1 | buy/free | — |
| `manzanita` | dressing | sq080-sh040 mid | L2 | buy | Twisted red bark — best silhouette value in the yard |
| `succulents` (agave, aloe, prickly pear) | dressing | scattered, mid | L1 | buy/free | — |
| `foundation_bushes` | dressing | mid | L1 | buy/free | — |
| `pots_planters` | dressing | north end by the truck | L1 | generate | — |
| `flower_pot` | **new** guide | sq030-sh030 catches the arm — *[IF TIME]* | L2 | primitive | Variant → arm-in-pot |
| `window_box` | dressing | sq040-sh020 under the west sill | L1 | primitive | South leaf only — north half is Mom's exit |
| `mailbox` + post + `culvert` | dressing | sq020-sh020 — he draws a bead on it | L1 | primitive | — |
| `patio_table` ✓, `folding_chair` ✓ | guide | sq070-sh040 mid | L2 | buy | Chair goes over in sq080-sh030 |
| `tea_pitcher` ✓ | guide | **sq070-sh040 — tight on it** | **L3** | hand | None. **The one lawfully pristine object — the gag is the finish** |
| `tea_glass` ✓ | guide | sq070-sh040 | L2 | primitive | — |
| `trash_cans`, `hose_reel`, `watering_can` | dressing | mid | L1 | free | — |
| `yard_charred` | **new mini set** | sq070–sq080, every shot | L2 | hand + decals | See below |

### `yard_charred` — the architectural finding

From `sq060-sh030` onward the backyard is scorched, but the yard lives in
`property.blend`, which is linked at identity into every scene and ships **one
static state**. There is no way to char it per shot.

Solution follows the `trench` precedent: **an additive overlay mini set**
(`assets/envs/yard_charred/`) — scorch decals, charred grass patches, the
downed clothesline, debris — instanced into `sq070` and `sq080` shots and
placed over the clean yard. Additive, so it never fights the identity rule,
and one file covers nine shots.

---

## 7. Cop car & the sandwich

**The cruiser is a boxy 80s Crown Victoria** — settled 2026-08-05, matching
`style.md`'s canon ("a decade out of date" in 1993). That means the
**1979–1991 LTD Crown Victoria** (the square Panther body), not the 1992–97
aero car — the aero car would be brand new in 1993 and the canon says it
isn't.

**`refs/cop_car/` is half on-canon.** It holds a genuinely good three-angle
set (side, ¾ front, ¾ rear) of a **County Sheriff Crown Victoria in a desert
setting** — white with a gold-and-black stripe, star decal, "Emergency 911",
period lightbar, dust on the rockers. Livery, graphics, lightbar and
environment are all directly usable and save real work. But that car is the
**1992–97 aero body**, so it is the wrong generation for the silhouette. The
rest of the folder — 1960s Plymouth Fury/Belvedere/Satellite and a 1960 Ford
Fairlane — is two decades off and is mood only.

**Action: source a 1979–91 square-body Crown Vic, then dress it with the
livery from the existing three-angle set.**

| Asset | Lives | Closest look | Rung | Route | Motion |
|---|---|---|---|---|---|
| `cruiser` ✓ | guide | sq040-sh030 mid; sh044, sh060 mid | L2 | **buy** + repaint | Wheels, suspension slew, window down |
| `cruiser_interior` | **new** | **sq040-sh035 & sh042 — both INTERIOR** | **L3** | hand | Wheel, column shifter, radio handset |
| `cruiser_door` ✓ | guide | sq040-sh060 mid | L2 | primitive | Hinge → falls off |
| `hubcap` ✓ | guide | sq040-sh050 — rolls into the yard | L2 | primitive | Rolls; then skeet-shot |
| `lightbar` | sub-object | sq040-sh030 | L2 | buy | Static, emissive |
| `tire_blown` | variant | sq040-sh040 | L1 | primitive | Swap on the PANG |
| `egg_salad_sando` ✓ | guide | **sq040-sh035 two-handed in frame; sh042 again** | **L3** | hand | Rigid + one squeezed variant |
| `sheriff_hat` / `hat_mangled` | guide | sq070-sh030 — comes off in apology | L2 | hand | Variant swap |

**`cruiser_interior` is a second build, not a detail pass.** Two of the film's
interior shots live in it and both are close: dash, bench seat, wheel, column
shifter, radio and coiled handset, shotgun rack, dangling air freshener,
coffee cup, clipboard. Budget it like a small set.

---

## 8. The action figures

Five designs. Each takes a hero trope and reveals the inner asshole. All are
printer output: **extruded wet pigment, piped-paint striations, visibly made
of paint that never fully dried.** Fresh prints are *perfectly* registered and
fully saturated — too perfect, which is the "NOT A TOY" note. Their wear is
earned on screen by gunfire.

| # | Figure | The trope | The reveal | Silhouette anchor |
|---|---|---|---|---|
| 1 | **The Barbarian** | Conan | Flexing at nobody. Entirely self-satisfied. | Broadsword, bare bulk |
| 2 | **The Soldier** | GI hero | Dumbass. Helmet askew, safety on, no idea. | Mullet + bandolier |
| 3 | **The Space Captain** | Star hero | Chestful of medals he awarded himself. Preening chin. | Ray gun, hand on hip |
| 4 | **The Champion** | Wrestler | Sore winner — pointing at a man already down. | Belt + cape |
| 5 | **The Frontier Marshal** | Gunslinger | Noble squint is over a parking dispute; hand already on his gun. | **Hat — the best read at 15 m** |

**The Soldier's head is the one that matters.** `sq040-sh064` drops it in
close-up at the sheriff's feet, facing him, and he has to read it as a man he
knew. That head is **L3**; the other four heads and all five bodies are L2.

**Poses for `sq030-sh010`'s firing squad**, distributing the script's three
named poses across the five:

- **Captain** — mid-friendly-wave (preening, of course he's waving)
- **Champion** — holding the tiny white flag (ironic, and he hates it)
- **Soldier** — blindfolded with a cigarette, and doesn't realise why
- **Barbarian** and **Marshal** — just standing there being smug. They are the
  silhouette anchors at either end of the line.

| Asset | Rung | Route | Motion |
|---|---|---|---|
| `action_figure` ✓ ×5 bodies | L2 | **generate** + resculpt | Rigid. Posed at build time — no rig |
| `figure_head` ×5 | L2 (**soldier L3**) | hand | Detachable; fracture |
| `figure_arm` | L2 | hand | The flowerbed runner *[IF TIME]* |
| `white_flag`, `cigarette`, `blindfold` | L1 | primitive | — |
| fragment set | L2 | fracture in-file | Xylophone pops, molten burst |

Generation is a good fit here — chunky toy forms are exactly what it handles
well. **Faces need hands.**

---

## 9. Guns

| Asset | Lives | Closest look | Rung | Route | Motion |
|---|---|---|---|---|---|
| `machine_gun` ✓ | guide | **sq020-sh010 — soft-serve extrusion, bell flick** | **L3** | hand | Trigger, bell. Muzzle flash is FX. No deformation specced — see §3 |
| `rosco` ✓ | guide | **sq050-sh040 — drawn, spun, racked with teeth** | **L3** | hand | Slide travel (one rigid part) |
| `cop_rifle` | **reinstated 2026-08-06** | sq050-sh020 onward — the sheriff's firefight gun | **L3** | hand | Recoil only |
| `big_pistol` ✓ | guide | sq050-sh020 mid | L2 | hand | Recoil only — **see the open question below** |
| `gun_cabinet` ✓ | guide | **sq050-sh040 close, from behind her** | L2 + **L3 sign** | hand | Door hinge |
| `arsenal_contents` | sub-collection | sq050-sh040 | L1 | primitive | Rack of long guns, shell boxes — silhouettes only |
| `nam_rifle` | **new** | sq050-sh010, sepia, 2 s | L1 | buy/free | M16A1 per `refs/cop rifle/`, **or reuse `cop_rifle`** — see below |
| `sheriff_duty_sidearm` | wardrobe | holstered, mid | L1 | primitive | — |
| `shotgun_rack` | part of `cruiser_interior` | sq040-sh035 | L1 | primitive | — |

**The machine gun** is toy-scaled cassette futurism with **literal bells and
whistles** — a real bell and a real whistle mounted on it, because the boy
flicks the bell on the lyric. It wears the NOT A TOY sticker from `sq020-sh020`
to the end of the film, weathering as it goes.

**LIVE LAUGH LOAD.** The sign goes on the pantry/arsenal. Framing is the
problem: `sq050-sh040` is shot **from behind Mom**, so a sign flat on the wall
is masked by her. **Recommendation: mount it on the inside face of the door**,
so it swings toward camera as she opens it — the flip *is* the gag, and it
solves the sightline instead of fighting it. Wall-mounted above the cabinet is
the fallback if the door angle can't be made to work. Either way this needs a
blocking test before the cabinet is built past L1.

## The three weapons must read apart — set 2026-08-06

The armory is designed as a **three-way material split**, so the shooters are
told apart by silhouette and finish alone, with the colour turned off:

| | weapon | material read |
|---|---|---|
| **The boy** | `machine_gun` | **big dull moulded plastic.** Absurdly overdone — a kid added every part he could think of and the printer built it. Scope on too tall a riser, banana magazine, full stock, carrying handle, foregrip, bipod, a pointless drum canister, and the literal bell and whistle. Chunky, soft-edged, mould-seamed, unmistakably a toy. |
| **Mom** | `rosco` | **small bright silver.** A sleek **silver 9mm semi-automatic pistol** — mirror-bright stainless slide, brushed nickel frame, black checkered grips, no decoration at all. The smallest and shiniest object in the film, and the only bright metal. Its slide is what she racks with her teeth. |
| **The sheriff** | `cop_rifle` | **long wood and blued steel.** An **M14**: full-length one-piece walnut stock, warm red-brown and hand-oiled, blued charcoal steel worn bright at the edges, perforated handguard, dull olive canvas sling. Nothing tactical, nothing modern, nothing plastic. |

Concept sheets for all three, plus a one-scale lineup proving the read, are in
`concept/props/`.

**`cop_rifle` is reinstated — Ian's call, 2026-08-06.** It was previously cut on
the grounds that his firefight gun is the comically large pistol and nothing in
`script.md` gave him a rifle. That is overruled: the sheriff carries an **M14**,
and the wood is what separates him visually from the other two shooters.

**Open — what happens to `big_pistol`.** `guns-script.md` has the 'Nam flashback
trigger and then *"out comes a comically large gun"* at `sq050-sh020`. Three ways
to resolve it, none chosen yet:

1. **The M14 *is* the comically large gun.** A full-length wood service rifle
   hauled out in a suburban backyard is comically large, and it lands the
   flashback in the same beat — the rifle he kept from the war. This also lets
   `nam_rifle` and `cop_rifle` collapse into one asset instead of two, which is
   the cheapest outcome and the tidiest story.
2. **He has both** — the oversized pistol is the comedy reveal, the M14 is what
   he actually fights with. Costs an extra hero asset and muddies the silhouette
   split.
3. **Keep the pistol as the reveal and drop the M14.** Contradicts the call
   above.

Option 1 is the recommendation. Nothing in `script.md` or `guns-script.md` has
been rewritten pending that decision.

---

## 10. Everything else

Things the seven areas didn't cover.

| Asset | Lives | Closest look | Rung | Route | Motion |
|---|---|---|---|---|---|
| `title_card` ✓ | guide | **sq090 — fills the frame** | **L3** | hand | Settles out of an overshoot. Hand-painted; the final round lands as a **wet splat**, the last unauthorized pigment in the film |
| `bullet_hole` ✓ | guide | sq090 | L2 | primitive | — |
| `mushroom_cloud` ✓ | guide | sq060-sh030 | L2 | FX sim | The Paint FX showcase — a giant graphic paint-plume in stacked flat shapes |
| `bald_eagle` | **new** | **one frame** inside the cloud | L2 | generate | None. Seen for 1/24 s — **silhouette is the entire asset** |
| `butterfly` | **new** guide | sq050-sh020 — runner 2/3 | L2 | generate | **The only shape-key asset in the film** (wing flap) |
| `screen_door` ✓ | guide | sq010-sh030 — the ♪ door-slap | L2 | primitive | Hinge empty |
| `casement_leaf` ✓ | guide | sq050-sh035 through the glass | L2 | primitive | Hinge empty |
| `back_door_leaf` ✓ | guide | sq060-sh012 behind Mom | L2 | primitive | Hinge empty |
| Kitchen dressing | dressing | **sq050-sh040 holds a mid-shot across it** | L2 | buy + generate | Fridge with clippings, wall phone with a long cord, dish rack, canisters, 1993 clutter |
| `nam` | **new mini set** | sq050-sh010, 2 s, sepia | **L1 — hold the line** | primitive + free | Sandbags, ammo crates, jungle cards. **Two seconds. Do not build a war.** |
| `swamp_cooler`, `tv_aerial` | dressing (roof) | sq070-sh010 aerial | L1 | primitive | Already specced in `house.md` |
| Porch dressing | dressing | sq010-sh020/030 | L1 | primitive | Chair, wind chime, milk crate |
| `squibs` ✓ | `assets/fx/` | throughout | — | exists | — |
| `paint_divots` | FX | sq080-sh030/040 | L2 | particles | Wet splats chasing their heels |
| `scorch_decals` | part of `yard_charred` | sq070+ | L2 | hand | — |
| Sky backdrop | look-dev | every exterior | L2 | hand | Painterly theatre cyc per `style.md`. Not a prop, but it is an asset and nothing is scheduled for it |

---

## 11. Build order

Ordering is forced by one fact: **the style is not locked**, and `style.md`
names `sq020-sh020` as the test frame that decides it — boy, printed gun with
sticker, garage interior, Santa at the threshold. **Nothing else in this
catalog can be surfaced until that frame is rendered and judged.**

1. **Test-frame four** — `machine_gun` (L3), `not_a_toy_sticker` (L3 artwork),
   `santa` (L3), and enough garage interior dressing to fill the frame behind
   them (L2 in the near cluster, L1 beyond). Each to its own target rung with
   final surfacing, because the point is to judge the surfacing. This unlocks
   every other look decision in the film.
2. **`printer`** — the largest mechanism, and it carries four shots.
3. **The five figures** — they appear across eight shots and gate all of
   `sq030`. Generate the bodies in one batch.
4. **`cruiser` + `cruiser_interior` + `egg_salad_sando`** — `sq040` is the
   hottest section in the film and all of it is here.
5. **Yard dressing at L1, everywhere, in one pass** — then render `sq060` and
   `sq070` and promote only what looks thin.
6. **`yard_charred`** — once the clean yard is final.
7. **Everything else**, driven by the promotion rule.

## 12. Open questions

- **`sq020-sh040` is a character moment, not a gag** (settled 2026-08-05).
  **Mom is permissive and has one sharp line**, and that shot is where the
  audience learns it. The story is told by her face and by how she and the
  boy physically deal with each other — not by a prop doing a trick. The
  barrel droop was decoration on top of it, and losing it costs nothing;
  a prop animating under her wag would actively *pull the eye off her face*,
  which is the one thing the shot cannot afford. **`script.md` should drop
  the ♪-synced droop from its sh040 row** and describe the performance
  instead. No replacement gag is wanted.
- **The noodle-gun cut now rests on a suspended law.** `script.md`'s
  `sq070-sh020` row justifies the cut with *"diecast can't droop under
  `style.md`'s physics law"* — and that law is TBD as of today. The cut
  itself stands; only its stated reason is stale. Worth a look when the
  movement tests come back, in case the beat is wanted after all.
- ~~**Tire discrepancy.**~~ **Resolved 2026-08-05 — front left, shot down the
  garage passthrough.** The round comes in the rear door and out the front,
  crosses the driveway heading east, and takes the northbound cruiser square
  on its left flank; because the car drives *into* the line rather than the
  line chasing the car, it lands on the front axle. He veers left, and left is
  west, which is the ditch. `shotlist.csv` had the tire right all along and
  wins as source of truth. **The ricochet no longer bounces off the old
  truck** — `site.md` updated, and the truck keeps its two real jobs (the
  sheriff's cover, breaking Mom's sightline). `script.md` and `guns-script.md`
  updated. `story.md` still reads "back tire" and was left alone deliberately:
  it is labelled the author's near-verbatim draft 1, a record rather than a
  living spec.
- **LIVE LAUGH LOAD placement** needs a blocking test before the cabinet
  builds past L1 (see §9).
- **Mint is the reserved accent** and `style.md` spends it on exactly two
  things: **the old C10** and **the sweet tea**. The delivery truck is not on
  that list. Recommend it take rust or orange from the albedo palette so the
  reservation stays meaningful — a reserved colour is only reserved if it goes
  unspent everywhere else. The two trucks never share a frame, so this is
  cheap either way.
- **`guns-script.md` vs `script.md`** disagree on the gun cabinet: prose says
  a framed sign flips to reveal an arsenal, the shot table says she opens a
  cabinet. The pantry-with-a-sign resolution above splits the difference —
  fold it back into both docs.

## 13. What this catalog decided

- The father is a **dead veteran, unrelated to Danny**. The sheriff does not
  know the family; Mom knows him as an elected official she voted for.
- The five action figures, their reveals, and their firing-squad poses.
- The cruiser is a **boxy 80s Crown Victoria**.
- The prose-only props — flamingos, gnome, birdbath — are **in**.
- **No prop needs an armature** — and that holds whichever way the
  deformation tests land, because droop and squash are shape keys or sims.
  One asset (the butterfly) uses a shape key today.
- Charring is an **additive overlay mini set**, not a property variant.
- `sq020-sh040` is **a character moment carried by performance**, and no prop
  animates in it.
