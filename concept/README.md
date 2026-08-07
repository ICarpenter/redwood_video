# concept/

Generated concept art, and the exact prompt that produced each image.

Not part of the pipeline — nothing in `tools/` reads this directory, and no layout
scene links it. It exists so a look can be argued about with a picture instead of a
paragraph, and so a good frame can be reproduced or nudged later instead of
re-guessed.

## Rules

- **Every image ships with its prompt.** One `<image>.prompt.md` per image (or per
  batch, when one prompt produced several variants), holding the prompt verbatim
  plus the refs that were attached to the call.
- **Note where an image departs from `docs/treatment/style.md`.** The style is
  locked; concept art is allowed to argue with it, but the argument has to be
  written down or the folder quietly becomes a second style doc.
- **Concept art is not canon.** `docs/treatment/style.md` is. If an image wins,
  update the doc — don't leave the image to speak for itself.
- Images are git-LFS (`.gitattributes` covers `*.png`). Commit explicit paths.

## Contents

### `boy/` — the boy, 2026-08-05

Three passes, generated with Nano Banana Pro (Gemini). All used the same subject
refs from `refs/boy/` (jeans / bowlcut child / Black Sabbath tee) and the two
desert-patio prints from `refs/styles/`.

| image | prompt | what it is |
|---|---|---|
| `boy_v1_muted-sullen.png` | `boy_v1_muted-sullen.prompt.md` | First pass. **Superseded** — still has the off-register blush dots and the sullen face, and the build is too soft. |
| `boy_v2_joy-flat-gouache.png` | `boy_v2_joy-flat-gouache.prompt.md` | **The one that matches the locked style.** Flat, unmodelled, matte, chalked back. Blush gone, Christmas-morning joy carried by the mouth, wiry long-necked build. Judged too muted. |
| `boy_v3_arcane_a-sunset-field.png`, `boy_v3_arcane_b-backyard-dusk.png` | `boy_v3_arcane.prompt.md` | High-contrast painted-3D pass, Arcane-leaning. **Crosses three locked rules on purpose** — modelled form, saturated shadows, rim light. See the warning in its prompt file. |

The character decisions that came out of this run — no blush dot on flesh, wiry
build with long neck and colt legs, heavy lids over a huge toothy grin — are
recorded in `docs/treatment/style.md` § Characters. The v2/v3 surface question is
**not** settled; it wants an A/B on the sq020-sh020 look-dev frame.

### `boy/` — modelling references, 2026-08-05/06

Derived from `boy_v3_arcane_b-backyard-dusk.png` and then from each other. Flat,
shadowless and orthographic on purpose: these are plates to sculpt over, not
frames, so they set the locked look aside the way `boy_modelsheet.prompt.md`
already does.

| image | prompt | what it is |
|---|---|---|
| `boy_modelsheet.png` + `_front` / `_side` crops | `boy_modelsheet.prompt.md` | Two-view ortho model sheet. Loaded in `assets/chars/cast.blend` as image empties in `boy_modeling_sculptref`. **The canon for the boy's wardrobe** — his shoe is one solid black mass, low collar, no white midsole. |
| `boy_hands_anatomy.png` | `boy_hands_feet.prompt.md` § Sheet 1 | Six hand cells — flat back, flat palm, edge, rest, fist, spread. The sculpting plate. |
| `boy_hands_grips.png` | `boy_hands_feet.prompt.md` § Sheet 2 | Six grips, taken from what the film actually asks of him: pistol grip and foregrip (the printed machine gun, `sq020`/`sq030`/`sq060`), flat push and hooked pull (the box, `sq010-sh040/045`), overhand rail grip (the fence, `sq080-sh040`), pointing. |
| `boy_shoe_ortho.png` | `boy_hands_feet.prompt.md` § Sheet 3 | Six ortho views of the sneaker, shoe alone with no cuff. **Post-processed** — the model captions every view and will not stop, so the captions are painted out after generation. Method is in the prompt file. |
| `boy_foot_poses.png` | `boy_hands_feet.prompt.md` § Sheet 4 | Stride and jump poses with the jean cuff, for animation rather than modelling. Cell 2 is meant to be a heel strike and is not — pose that one by hand. |

The prompt file's **"What came back"** section records which instructions this
model obeys and which it ignores however they are worded. Read it before
re-running any of these.

### `boy/` — expression sheets, 2026-08-06

Eighteen expressions and a mouth chart, all keyed to shots the film actually
contains — the list comes out of `docs/treatment/script.md`, not an emotion
wheel, and `boy_expressions.prompt.md` carries the cell → shot map. Anchored to
`boy_modelsheet_head.png`, a crop of the front model sheet (crop only, no
generation).

| image | prompt | what it is |
|---|---|---|
| `boy_expr_getting.png` | `boy_expressions.prompt.md` § Sheet 1 | sq010–sq020, the boy in his element: neutral, the devious grin (`sq010-sh050` is a whole shot of it), wonder over the box rim, the shove, doing arithmetic, the bead. **Captions painted out.** |
| `boy_expr_caught.png` | § Sheet 2 | sq020–sq070, what happens *to* him: pew, caught mid-aim, told off, savoring, the shared oh-no, blast-dazed. **Captions painted out.** |
| `boy_expr_motion.png` | § Sheet 3 | motion and range: impatient glee, mid-dive panic, the look, sprint whoop, plus blink and jaw-wide as rig utilities. |
| `boy_mouth_chart.png` | § Sheet 4 | Nine lower-face crops — the mouth shape vocabulary, which is where most of his acting lives. |

Loaded in `assets/chars/cast.blend` as `boy_modeling_sculptref_faces`, a 2×2
board on +X mirroring the hands/feet board on −X.

**Two departures from `style.md`, both argued in the prompt file:** the sheets
carry face outlines (§ Characters forbids linework on faces — that is a rule
about final frames, and a reference plate has to be unambiguous), and the eyes
act on the peak beats rather than staying sleepy throughout (§ Characters treated
as guidance here, Ian's call 2026-08-06). Neither is a look decision.

### `mom/` — the mom, 2026-08-06

First pass, ten calls. Built against `boy_v3_arcane_b-backyard-dusk.png` as both
the style target *and* the family reference — the requirement was that she read
as unmistakably that boy's mother, so the prompt names the six shared features
(jaw, grin, lids, build, blond, the rounded mass on top) individually rather
than asserting a relation. In the output it is the **heavy hooded lids** that
carry it.

| image | prompt | what it is |
|---|---|---|
| `mom_v1_arcane_a-garage-doorway.png` | `mom_v1_arcane.prompt.md` § Sheet A | **The hero.** The `sq020-sh040` scold — standing in the raking sun in the garage mouth, one finger up, the grin switched off. **Shows the retired oven mitts** — kept as is, see the note below. |
| `mom_v1_arcane_b-final-boss.png` | § Sheet B | Dual-wield at sunset, the grin back on, guns as flat silhouettes running off frame. |
| `mom_v1_faces.png` | § Sheet C | Six-cell expression board, every cell keyed to a shot that exists. |

Face **and hair** DNA is
`refs/mom/moms-new-haircut-mid-1990s-v0-tcgp7b5kkkce1.webp`; wardrobe is the
doc's 1988 mall-glam, not the photo's.

**These won, and `style.md` § Characters has been updated to match
(2026-08-06)** — the hairspray helmet is out and the curly bob is in, the
glasses are in, and her build, face and the switched-off-grin logic of the
scold are recorded there. The doc is canon again; this folder is just the
argument that moved it. The three Arcane crossings the boy's v3 makes —
modelled form, saturated shadows, rim light — are still crossings here and are
still not canon.

Two things worth knowing before re-running any of these. First, **the two-stage
edit pass is the technique that works** — get the frame close, then hand the
image back as the only ref with a short "change exactly these three things"
prompt. It fixed the finger wag and shoulder pads on Sheet A and the sky on
Sheet B without disturbing anything else, where re-rolling kept trading one
success for another. Second, **contrast never fully reached the boy's range**;
four rounds of escalating language got Sheet A most of the way and B and C
settled flatter. The prompt file's **What came back** section records the full
list, including what the model did unasked.

**⚠️ These three images show the oven mitts, which are dead as of 2026-08-06.**
Ian's call: she wore them on both hands in every shot and it made her read as a
housewife, which she is not — **she goes to work**, the shoulder pads and
pleated trousers were already saying so, and the mitts were fighting them. She
bakes; it is something she does, not what she is. Her hands are bare and
capable — long slender fingers, hard well-kept nails — and **she racks a slide
with her fingers**, so the teeth gag at `sq050-sh040` went with the mitts.

The images are **kept exactly as they are** — they are good, and they won the
argument that moved `style.md`. Everything downstream of them is updated:
`style.md` § Characters, `script.md` (three shots), `guns-script.md` (three
beats), `props_v1.prompt.md`, and the Sheet A/B/C prompts below, so a re-run
does not put the mitts back. The one surviving pair is set dressing —
`property_v1.prompt.md` hangs quilted mitts on a hook by the stove, which is
exactly the "she bakes, it is not her identity" reading and should stay.

### `mom/` — modelling references, 2026-08-06

Built mitt-free from the hero and the expression board. Flat, shadowless and
orthographic — plates to sculpt over, not frames, so the refs' painted-3D
treatment is deliberately discarded. Her hands are a subject in their own right
here, which is the whole reason the mitts came off.

| image | prompt | what it is |
|---|---|---|
| `mom_modelsheet.png` + `_front` / `_side` crops | `mom_modelsheet.prompt.md` § Sheet 1 | Two-view ortho model sheet, calibrated to **1.70 m** per `tools/guides.py:55`. The side crop is flopped — she came back facing left both rounds. |
| `mom_hands_anatomy.png` | § Sheet 2 | Six hand cells. Wiry working hands — tendons, knuckles, no padding — finished with immaculate painted nails. That contradiction is the character. |
| `mom_hands_grips.png` | § Sheet 3 | Six grips keyed to her shots: the wag (`sq020-sh040`), pistol grip, **racking the slide two-handed** (`sq050-sh040`, the beat that replaced the teeth gag), the casual dual-wield carry (`sq080-sh010`), the sweet-tea pour (`sq070-sh040`), hand on hip. **Panel dividers filled out** after generation. |
| `mom_shoe_ortho.png` | § Sheet 4 | Six ortho views of her flat court shoe, 23.1 cm. **Captions painted out**, and the **top view is 21% short** — scale it 1.26× if you use it as its own plate. |

Loaded in `assets/chars/cast.blend`, scene `mom_modeling`, into Ian's existing
`mom_modeling_sculptref` plus a new `mom_modeling_sculptref_detail`.

**Every plate in that scene is now at true scale (2026-08-06).** The three
concept plates predate the model sheet and were at arbitrary sizes; they have
been measured against its calibration and rescaled, so all of them show her at
**1.70 m** with the full-body ones standing on z = 0. The blockout measured
1.409 m because it was copied in from the boy — Ian is rebuilding it, and the
plates were left at canon rather than dragged down to meet it. The one thing
still parked oddly is the front plate, off-centre at x = −1.30 because
`momref_concept_finalboss` holds x = 0.

### `sheriff/` — the sheriff, 2026-08-06

Seven calls. **He is the only character who changes appearance across the film,
so the states are the design** — one sheet each, plus an expression board.
Anchored to two refs Ian named: `refs/cop/N150_0030_018.jpg` for the man (the
face, the hair, the heavy 1980s moustache) and `refs/cop/cops_shaking_hands.jpeg`
for the uniform (dark brown shirt with a **tan yoke** panel, tan tie, gold star
patches, black basketweave duty belt, tan trousers).

| image | prompt | what it is |
|---|---|---|
| `sheriff_v1_a-first-sighting.png` | `sheriff_v1.prompt.md` § Sheet A + A2 | **The hero.** `sq040-sh030/035` — beside the cruiser, campaign hat, **mirrored aviators**, uniform pressed. |
| `sheriff_v1_b-out-of-the-ditch.png` | § Sheet B | `sq040-sh060` onward, which is most of the film: **glasses gone, hat mangled, egg salad in the moustache**, uniform wrecked, M14 in one hand. |
| `sheriff_v1_c-flashback.png` | § Sheet C + C2 | `sq050-sh010` — total sepia, M1 helmet, flak jacket, M16A1. **Same body as the present-day man**, which is the point. |
| `sheriff_v1_faces.png` | § Sheet D + D2 | Six expressions keyed to real shots: pure bliss with the sandwich, stopped dead, "…Danny?", the salty mug, the twitch of recognition, hat off in apology. |

**Three character decisions came out of this run, all Ian's:** the moustache and
**mirrored aviators when we first see him**; the aviators **lost in the crash and
never seen again**, which buys the crash a visible cost and hides his eyes for
exactly as long as he is a threat; and **egg salad on his face** afterwards,
turning the `egg_salad_sando` prop into a runner for free. None of it is in
`style.md` yet — his entry there is still one line about the car being his
anachronism.

**The build took two rounds, and the second one is the design.** Round 1 read as
an all-over fat man. Ian's correction: *naturally tall and wide-shouldered, with
bad posture and a gut, and a naturally big backside — hence the butt crack.* The
frame is a big man's and the softness is only in the belly and the seat, which is
what lets the same man read at twenty-three and at forty-five. **Round 1 is kept
in `round1/`** — its staging, uniform and expression beats were all right and only
the body was wrong. That folder also holds `sheriff_v1_faces_alt-drifted.png`, a
second expression attempt whose face went off model.

Two things were taken from the code rather than invented. `guide_assets.py`
`build_sheriff` gives him **a 0.30 m belly ball on a 1.8 m frame**, so he is a big
man and not the lean deputy in the photograph. And `build_sheriff_war`'s docstring
requires the flashback to use the **same silhouette**, so Sheet C is not a slim
young marine. ⚠️ The revised design lets the **gut be smaller in the flashback**
while the frame stays identical — a deliberate half-step away from that
docstring. If it stands, `sw_belly` wants shrinking in `guide_assets.py`.
Flagged, not changed.

**⚠️ Same three Arcane crossings** the boy's v3 and the mom's v1 make — modelled
form, saturated shadows, rim light — and still not canon. Contrast again fell
short of the boy's range, the ceiling the mom sheets already recorded.

**Round 1 needed three edit passes; round 2 needed one.** Fixing the build block
also fixed the flashback slimming itself down and the expression board captioning
itself — two faults that had each cost an edit. The prompt file's two "What came
back" sections record what every round got wrong, which is the most useful thing
in it. No model sheet yet; it derives from whichever sheet is accepted, the same
order the boy and the mom went.

### `property/` — the locations, 2026-08-06

Six locations × two times of day (mid-afternoon and sundown), twelve frames.
**Unlike the character sheets, these are not invented** — every one is painted
over a rendered structural blockout of `assets/envs/property/property.blend`, so
the architecture, the camera and the site are the real ones. The blockouts ship
alongside in `plates/`, and `property_v1.prompt.md` carries the exact camera
transforms, because **the cameras are not saved in the blend** — the render
script creates them at runtime and never writes the file.

| location | shots it serves |
|---|---|
| `establishing` | sq010 open, sq040 arrival, sq090 |
| `garage_tunnel` | sq010 (the box, the bench), sq020-sh020 |
| `backyard` | sq020–sq080 — the arena |
| `kitchen_sink` | sq040-sh020, sq050-sh030/035 — Mom's watching position |
| `corridor` | sq050 — the sheriff's crawl, Mom's kill-window wall |
| `front_porch` | sq010-sh010/020/030 — the screen-door slap |

Built to Ian's brief of **no humans and nothing at L3 hero fidelity**. Every L3
asset in `props.md` is banned by name in every prompt; everything present is
L1/L2 dressing lifted from `props.md` §5–§6 and `house.md`. Same three Arcane
crossings as the character sheets, and still not canon — but the flat sun disc
and the mint reservation are both honoured.

**Three findings worth carrying:**

1. **A grey blockout alone does not hold architecture.** Two frames came back as
   generic pitched-roof ranch cottages until the prompt *described the massing in
   words* — flat roof, fascia band, beam-end rhythm, carport tunnel, explicit
   bans on gable and ridge. Image plus text held it; image alone did not.
2. **Fix framing in the plate, not the prompt.** "Big sky" was won by re-shooting
   the plate cameras pitched up. Adjectives couldn't beat the framing.
3. **"Worn" reads as *ruined*.** The first pass came back derelict — peeling
   paint, rust streaks, broken concrete, junk in the dirt — which is both the
   wrong family and a straight violation of `style.md`'s **"subtle patina only"**.
   The fix was not an adjective but a stated human reason: *a decent home run by
   one parent who is out of hours*, so every flaw is a deferred job rather than
   neglect, surfaces are declared intact item by item, and belongings are stored
   rather than strewn. Ian's call, 2026-08-06; all twelve were regenerated, and
   it pulled the set closer to the locked flat-print look as a side effect.

### `props/` — the L3 hero props, 2026-08-06

Six sheets: `printer`, `santa`, and the three weapons plus a one-scale lineup.
**Lit differently from everything else in this folder on purpose** — these are
design documents somebody hand-models from, so they trade drama for legibility:
object alone on a flat field, key light for clarity, enough coloured bounce that
no part falls into darkness. That recipe is worth reusing for any prop sheet.

The strongest idea in the batch is Ian's three-way material split for the guns,
and the lineup sheet exists to prove it reads: **fat moulded plastic → short
black polymer geometry → long wood and blued steel.** Three silhouettes, three
characters, legible with the colour turned off.

Two rounds. Round 2 set Mom's gun as a **silver 9mm** (superseding a Steyr AUG,
kept as `prop_mom_gun_aug_superseded.png`), confirmed the sheriff's **M14**, and
opened the printer's left side onto a **conveyor belt** that extends its
printing range. **`docs/treatment/props.md` §9 has been updated** — `cop_rifle`
is reinstated as an L3 M14 and the material split is recorded there as canon.

`props_v1.prompt.md` still flags **two open questions**, neither edited into the
script: nanoparticle materialisation plus a conveyor **kills the printer's
soft-serve extrusion gag** in `guns-script.md`, and `big_pistol` vs *"out comes
a comically large gun"* needs a call — the doc recommends letting the M14 *be*
the comically large gun, which also collapses `nam_rifle` into it.

Rounds 3–4 rebuilt the printer around a conveyor that **is** the print chamber
floor, a glass vault arching over it, and a row of hanging robot styli — and
added `prop_printer_scale.png`, which puts the assembled machine, its shipping
carton and the boy in one frame at one scale. It recommends **one box, not
several**: the script already commits to one (four shoves, one lid, one rim, one
launch), and the conveyor ships folded inside it. That also retires §4's
≥1.9 m chamber requirement — a 1.8 m figure prints lying down and rides out.

Two lessons worth reusing:

- **Round 1's Santa came back as a tidy painted portrait of Santa.** Naming that
  failure outright — *"this is not a face, it is a cheap plastic moulding of one,
  decorated fast by somebody not looking closely"* — then listing each
  misregistration separately, is what produced the off smile, the mould seams and
  the duct tape.
- **An edit prompt corrects local features but will not re-reason about space.**
  The printer edit faithfully kept every material it was told to and still came
  back geometrically impossible. Fixing it needed a fresh generate with the old
  image demoted to a materials-only reference, plus the three sight lines stated
  as one rule that must agree — open end, exit end, camera.

### Clearance note

The Black Sabbath graphic is real album art. Fine for concept. If the tee survives
to final frames it probably wants an invented band with the same 1993 silhouette.
