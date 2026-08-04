# guns — shot-by-shot script (DRAFT 3 — punch-up integrated)

Story: `story.md` · Lyrics/structure: `lyrics.md` · Section frames:
`../sections.csv` · Ending CONFIRMED: "Not the Santa" — the song dies dead
on the last chorus hit (bar 111); everything after is audio tail.

Bars counted from 0 · 1 bar ≈ 1.7s ≈ 40.85 frames · frames are song-global
(cut points snap to beats via `../beatmap.csv`). Durations rounded to 0.1s.
**♪ = music/lyric sync** · **[IF TIME]** = first to cut if a section runs hot.

**Retimed 2026-08-02** against markers placed by ear on the actual recording
(`edit/edit.blend` → `../sections.csv`). The old chart ran one bar late
throughout, so every section moved ~41 frames earlier. Every section is now a
whole number of bars and every cut lands on a bar line.

The music enters at **frame 81** (bar 2) — the track opens with ~3.3s of
silence. **Picture still starts at frame 1:** `sq010-sh010`'s sunrise plays
over that lead-in, which is why this table's intro reads bars 0–18 while
`../sections.csv` reads 2–18. The two are describing different things — the
picture and the song.

## Runner ledger

- **BUTT-CRACK TRILOGY (confirmed):** debut sq040-sh060 → butterfly
  sq050-sh020 → holding-pants sprint sq080-sh040.
- **"NOT A TOY" sticker:** peeled off the box and pocketed (sq010-sh040) →
  slapped onto the fresh machine gun (sq020-sh020). It wears it through all
  the carnage.
- **Flowerbed arm [IF TIME]:** arm lands in the flower pot (sq030-sh030) →
  Mom absentmindedly waters it (sq040-sh020). Never referenced again.

## sq010 — INTRO · bars 0–18 · frames 1–735 · 30.6s

| sh | bars | frames | dur | shot |
|----|------|--------|-----|------|
| 010 | 0–4 | 1–163 | 6.8s | Wide: sun rises over the rural house. Pedal steel yawns. Long and lazy — let the world breathe. |
| 020 | 4–6 | 164–245 | 3.4s | Delivery truck never stops — the big package spirals out like a football and sticks the landing on the porch mat. [IF TIME: simplify to truck pulling away] |
| 030 | 6–9 | 246–368 | 5.1s | Boy comes through the screen door on a straight arm **already running** takes the porch steps in one jump and pulls up hard over the package. ♪ door-slap on the beat. |
| 040 | 9–11 | 369–449 | 3.4s | Boy SHOVES the big box up the drive and in through the garage FRONT door — four shoves not one slide he loads up drives and rocks back off it. Packing peanuts already trailing. |
| 045 | 11–13 | 450–531 | 3.4s | REVERSE — from the back yard, looking in through the open rear door: the passthrough established, road beyond. He works the lid **the flaps come open** and he leans in over the rim to look. Then he peels the big "NOT A TOY" sticker off and pockets it — deliberately. |
| 050 | 13–15 | 532–613 | 3.4s | CLOSE UP: the devious grin. Hold it. |
| 060 | 15–18 | 614–735 | 5.1s | Printer boots and warms up little chugs and wiggles — and he cannot keep still in front of it: leans in cranes round one side then the other and ends up bouncing with his nose almost on it. ♪ warm-up chunks in time as verse 1 approaches. |

## sq020 — VERSE 1 · bars 18–38 · frames 736–1552 · 34.0s

| sh | bars | frames | dur | shot |
|----|------|--------|-----|------|
| 010 | 18–22 | 736–899 | 6.8s | The machine gun prints like soft-serve — one continuous extrusion the boy snaps off. Bells and whistles are LITERAL: he flicks the tiny bell — ding. ♪ "the product's movin'" as it plops off the bed. |
| 020 | 22–26 | 900–1062 | 6.8s | He picks the gun up off the garage floor and comes up with it slaps the "NOT A TOY" sticker on and then draws a bead on three separate things — garage junk the yard the mailbox holding each one — before the big swing round to his LEFT. |
| 030 | 26–29 | 1063–1185 | 5.1s | He brings the gun up onto his shoulder and starts play-shooting the Santa — six jerks he makes himself no muzzle flash he is going "pew". Then MOM'S SHADOW falls across him — full villain silhouette — and he freezes mid-aim. |
| 040 | 29–32 | 1186–1307 | 5.1s | Reveal: curlers, housecoat, oven mitts, sweetest face in the county — finger wagging. ♪ wags on beats; the clay gun barrel DROOPS a little more with each wag, scolded. The warning lands: do NOT shoot the Santa. |
| 044 | 32–33 | 1308–1348 | 1.7s | HARD CUT — CLOSE UP on the vintage Santa by the garage's back door: duct-tape repairs, mismatched paint. It has survived incidents before. **THE SETUP** (and it's already parked in the eventual line of fire). |
| 046 | 33–34 | 1349–1389 | 1.7s | REACTION — the boy's eyes flick from Mom to the Santa and back. He heard her. He is also, visibly, doing arithmetic. |
| 050 | 34–36 | 1390–1471 | 3.4s | Printer again: human-sized action figure slides out — discount-Americana visage (off-brand wrestler / mullet commando energy). |
| 060 | 36–38 | 1472–1552 | 3.4s | Boy hauls it out the garage's REAR door into the backyard, past the Santa at the threshold; more figures under his arm. |

## sq030 — CHORUS 1 · bars 38–46 · frames 1553–1878 · 13.6s

| sh | bars | frames | dur | shot |
|----|------|--------|-----|------|
| 010 | 38–40 | 1553–1634 | 3.4s | Firing squad reveal: one figure posed mid-friendly-wave, one already holding a tiny white flag, one blindfolded with a cigarette. ♪ "Who got the bag?" |
| 020 | 40–42 | 1635–1716 | 3.4s | Boy squares up, cocks it, savors it. ♪ "Who is your plug?" |
| 030 | 42–46 | 1717–1878 | 6.8s | **OBLITERATION.** Heads pop left-to-right in beat order like a xylophone run across "I got the guns." Clay everywhere. [IF TIME: one arm arcs into Mom's flower pot.] |

## sq040 — VERSE 2 · bars 46–64 · frames 1879–2614 · 30.7s — HOTTEST SECTION

Starts on **verse_2_intro** (a 4-bar instrumental lead-in, 46–50, frames
1879–2042) and runs into **verse_2** from frame 2043; the seam lands one frame
before `sh030` ends, i.e. effectively on the `sh030`/`sh035` cut. It no longer
reaches the end of verse 2 — the war flashback (`sq050-sh010`) now starts at
2615, two bars early, so the last two bars of verse 2 belong to sq050.

**The `verse_2` marker looks about a bar late.** "When a law man keeps a
knockin'" is audibly under way by frame ~2003, which is why `sh030` cuts in
there rather than at the marker. Nothing downstream depends on the two
agreeing — shots need not align to sections mid-sequence — but if the marker
gets moved back a bar, `verse_2_intro` becomes 3 bars and this note is stale.

| sh | bars | frames | dur | shot |
|----|------|--------|-----|------|
| 010 | 46–47 | 1879–1920 | 1.8s | Carnage continues; a figure's head balloons and bursts, molten Play-Doh. |
| 020 | 47–49 | 1921–2002 | 3.4s | Kitchen window: Mom admires his thoroughness, winces at his aim. [IF TIME: absentmindedly waters the new arm in the flower pot.] |
| 030 | 49–50 | 2003–2043 | 1.7s | Sheriff's cruiser ambles down the rural road. Wide, unhurried, nothing wrong yet. ♪ "when a law man keeps a knockin'." |
| 035 | 50–52 | 2044–2124 | 3.4s | INTERIOR: he's driving with his knee, two-handing an egg salad sandwich, pure bliss. The sandwich is the point — establish how much it matters before it is threatened. |
| 040 | 52–53 | 2125–2165 | 1.7s | PANG — a stray ricochet blows the back tire. ♪ blowout on the beat. |
| 042 | 53–54 | 2166–2206 | 1.7s | INTERIOR REACTION — the car is already going and he does not care: both hands go to the SANDWICH. Priorities, established. |
| 044 | 54–55 | 2207–2247 | 1.7s | Cut back outside: the cruiser slews into the drainage ditch, hubcap flying off, and coasts to a final rest just past the house. |
| 050 | 55–57 | 2248–2329 | 3.4s | [FIRST CUT IF TIGHT] Boy still shredding; the cruiser's hubcap rolls all the way into the yard — he skeet-blasts it without looking. |
| 060 | 57–58 | 2330–2369 | 1.7s | Sheriff climbs carefully out the window — the door falls off AFTER. **BUTT CRACK DEBUT (runner 1/3).** |
| 062 | 58–59 | 2370–2410 | 1.7s | His head pops up over the lip of the trench like a gopher — hat and all — and stops dead. |
| 064 | 59–60 | 2411–2451 | 1.7s | REVERSE on his eyeline: a blasted-off action-figure head drops in from the yard, bounces twice on the grass and rolls to a stop facing him. |
| 066 | 60–64 | 2452–2614 | 6.8s | Back on the sheriff. A shudder runs through him, his back arches, and the camera SNAPS in to his face as he mouths it: "…Danny?" ♪ the zoom hits on the beat. |

## sq050 — CHORUS 2 · bars 64–74 · frames 2615–3023 · 17.0s

**Starts 2 bars before the chorus does.** `chorus_2` is frames 2696–3023; the
war flashback cuts in at 2615, over the tail of verse 2, so the sepia punch
lands before the downbeat rather than on it. Deliberate — the flashback is
triggered by the sheriff finding Danny at the end of `sq040-sh060`, and it
plays through the chorus hit rather than waiting for it.

| sh | bars | frames | dur | shot |
|----|------|--------|-----|------|
| 010 | 64–68 | 2615–2777 | 6.8s | War flashback — two seconds of sepia clay 'Nam, triggered by Danny. Face puckers into the salty marine mug. ♪ "Who got the bag?" |
| 020 | 68–70 | 2778–2858 | 3.4s | Comically large gun out; determined army crawl. **A butterfly lands on the crack (runner 2/3).** |
| 030 | 70–71 | 2859–2911 | 2.2s | Window POV — Mom sees: disheveled armed man creeping along her house. |
| 035 | 71–72 | 2912–2940 | 1.2s | REVERSE through the glass onto her face. The sweetness drains out of it. She has already decided. |
| 040 | 72–74 | 2941–3023 | 3.5s | From BEHIND her: she opens the gun cabinet beside the window, draws Rosco, SPINS to camera and racks the slide with her TEETH (oven mitts). ♪ rack lands on "I got the guns." |

## sq060 — SOLO · bars 74–86 · frames 3024–3513 · 20.4s — THE SETPIECE

| sh | bars | frames | dur | shot |
|----|------|--------|-----|------|
| 010 | 74–77 | 3024–3146 | 5.1s | **THREE-WAY FIREFIGHT.** The boy breaks across the yard under fire and dives; the sheriff tracks him the whole way, firing. ♪ gunfire phrases with the guitar. |
| 012 | 77–79 | 3147–3227 | 3.4s | The instant the boy hits the dirt — REAR on Mom, planted on the back stoop, blasting away at the sheriff. She has been the third gun all along. |
| 014 | 79–82 | 3228–3350 | 5.1s | Back on the sheriff, camera looking WEST past him toward the house. **Mom is visible 20 m down the lens behind him, Rosco up, returning fire through the kitchen's north window** — muzzle flash after muzzle flash out of his flank. He is still firing north at the boy when he registers it, and swings the gun onto the house. The swing rakes straight across the propane BBQ. |
| 020 | 82–84 | 3351–3431 | 3.4s | The spray rakes the propane BBQ. Hiss. **All three freeze — one shared "oh no" look across the yard.** |
| 030 | 84–86 | 3432–3513 | 3.4s | **MUSHROOM CLOUD** — for exactly one frame it resolves into a bald eagle. Everyone blasted off their feet, slow-mo clay pinwheel. ♪ detonation on the solo's final accent. |

## sq070 — VERSE 3 · bars 86–102 · frames 3514–4166 · 27.2s

| sh | bars | frames | dur | shot |
|----|------|--------|-----|------|
| 010 | 86–89 | 3514–3636 | 5.1s | AERIAL hover over the charred backyard — scorched grass the flattened clothesline the boy flat on his back out on the middle of it. **Mom comes out through the kitchen window she has been shooting out of all firefight — over the sill and straight down the yard to her son.** She is the only thing moving. Quiet under the verse. (No blast column: it swallowed the frame at any size that read. The sheriff is 10.8 m north of the boy and cannot be held here as well as the back door — he is sh020's shot.) |
| 020 | 89–92 | 3637–3758 | 5.1s | OVER THE SHERIFF'S SHOULDER. He props himself up on the grass and — a twitch of recognition — finally sees who he has been trading fire with. A boy. And his mother. This was never a war. ♪ "the kid are lying in a slump." (Noodle-gun gag CUT 2026-08-02 — diecast can't droop under `style.md`'s physics law.) |
| 030 | 92–96 | 3759–3922 | 6.8s | REVERSE onto him past Mom and the boy. He gets up and crosses to them — and **she works out who he is**: head up off her son, freeze, a double-take, and it lands. THEN the mangled hat comes off in apology and it goes out of her — she is still laughing when we cut. All good fun after all. |
| 040 | 96–99 | 3923–4044 | 5.1s | Tight on the sweet-tea pitcher — the only pristine object in the wreckage — then PUSH OUT to reveal a table set up in the charred yard facing the garage: the sheriff sitting screen-left Mom centre-left handing him a glass the boy on the right. |
| 050 | 99–102 | 4045–4166 | 5.1s | REVERSE out of the garage: the charred Santa fills the foreground the tea tableau small beyond him. He slumps over — and his head pops off and rolls out across the grass toward them. **THE PAYOFF.** |

## sq080 — CHORUS 3 · bars 102–111 · frames 4167–4534 · 15.3s — THE ENDING

| sh | bars | frames | dur | shot |
|----|------|--------|-----|------|
| 010 | 102–104 | 4167–4247 | 3.4s | Mom's face goes final boss. She takes BOTH guns off the tea table — his and the boy's — and comes up dual-wielding, oven mitts still on. Push in onto her face. ♪ "Who got the bag?" |
| 020 | 104–105 | 4248–4288 | 1.7s | Two-shot square onto the two and a half metres between them — **with Mom planted dead centre between them dual-wielding**. Boy and sheriff exchange ONE look past her. She does not move. That is the beat. |
| 030 | 105–107 | 4289–4370 | 3.4s | She unloads; they bolt WEST past the table and straight up the yard for the back fence his chair going over behind him clay divots exploding at their heels. She barely has to turn — they run right past her. ♪ the hook changes owners — SHE'S "got the guns" now. |
| 040 | 107–111 | 4371–4534 | 6.8s | **FINAL IMAGE:** wide up the yard from just behind Mom — the two of them running away west into the sunset under heavy fire out of our own eyeline divots chasing them across the grass and rounds banging off the fence. **The boy OVERTAKES him at ~4405 and vaults the fence first at 4450; the sheriff is still short of it and gets over at 4478 one-handed (runner 3/3).** They go into the treeline and the desert and mountains beyond. ♪ song dies dead on bar 111's hit — **SMASH TO BLACK** with it. |

## sq090 — TAIL (audio only) · bars 111–~117 · frames 4535–~4780 · ~10.2s

| sh | bars | frames | dur | shot |
|----|------|--------|-----|------|
| 010 | 111–~117 | 4535–~4780 | ~10.2s | Black. Hand-sculpted clay title card settles out of an overshoot… holds… and takes one last stray bullet hole at 4700. Fade with the ring-out — exact out-point picked in the edit. |

## Tally & density notes

- **40 shots** across 9 sequences; sh-numbering gaps ready for inserts.
- Most punch-ups ride EXISTING shot time as choreography or design detail
  (xylophone pops, firing-squad poses, duct-taped Santa, eagle-frame,
  dual-wield) — near-zero pacing cost.
- The ones that cost real time, in cut-first order if a section runs hot:
  1. sq040-sh050 hubcap skeet (whole shot) · 2. sq010-sh020 package
  football (simplify) · 3. flowerbed arm (both beats).
- **sq040 (verse 2) is the hottest section** — sandwich two-parter + hubcap
  + Danny + crack debut in 20 bars. The animatic decides what survives.
- Chorus escalation intact: boy owns the hook (1) → grown-ups crash in (2)
  → Mom owns it (3) and ends the film mid-sprint.
- NEXT: boards per sequence (Storypencil) → animatic proves the pacing →
  survivors become rows in `../shotlist.csv`.
