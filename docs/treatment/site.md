# guns — the property (site plan)

Greybox layout: `assets/envs/property/property.blend`, bootstrapped by
`tools/blockout_property.py`. Massing only — it exists so boards, shot
cameras, and eventually the real set all agree on where things are. The
`.blend` is now **hand-maintained**: edit it in Blender. The tool has the
same positions baked in (so it doesn't lie) but refuses to overwrite the
file without `--force`; use `--out=<path>` for a throwaway preview build.

## Compass convention

| Axis | Direction | What's there |
|------|-----------|--------------|
| **+Y** | north | **BACKYARD** — the war |
| **−Y** | south | front yard, ditch, **ROAD** |
| **+X** | east | side corridor, sunrise |
| **−X** | west | garage/driveway side, sunset |
| +Z | up | |

The house **faces south** onto the road. The sun **rises in the east**
(opening shot) and **sets in the west** — so the final sprint runs *west*
down the road into the sunset, mirroring the sunrise. Nothing in the film
should contradict this without a reason.

## The three spaces

**ROAD (south, y ≈ −23…−17).** Dirt, running east–west. The sheriff
ambles in from the east; a drainage **ditch** runs the length of the north
shoulder (y ≈ −17…−14) — that's what he spins into. A **culvert** carries
the driveway across it, and the mailbox marks the crossing.

**HOUSE + GARAGE (centre).** House 12×9 m, gable roof, front porch facing
south (Mom fires from here in the final shot). Garage attached on the
**west**, its door facing south onto the driveway — the unboxing and the
printer live here, off the front of the property.

**BACKYARD (north, y ≈ +5…+27).** Contained by a back fence and treeline
so it reads as a yard, not prairie. The **BBQ and the Santa are clustered
tight by the back stoop** (west of centre) — so one propane blast catches
the whole cast *and* topples the Santa in a single beat. The boy's firing
position is centre; the firing squad lines up across the north end.

## The east side corridor — the layout's load-bearing idea

The garage sits on the **west**, leaving the **east side of the house as a
corridor** running from the backyard down to the road. It's not empty — the
old truck and the clothesline dress it — but it stays a clear *path*, and
it does double duty:

1. **The ricochet path.** A stray round off the boy's gun kicks off the
   **old truck**, now parked in the corridor near its road end, and zings
   south to blow out the sheriff's tire. The gag has a traceable line
   instead of a cheat. *(The exact bounce geometry is a boarding detail —
   the truck's job is to be the surface at the corridor mouth.)*
2. **The sheriff's crawl.** He climbs out of the ditch and army-crawls *up
   that same corridor* — past the truck, under the clothesline — to reach
   the backyard.

The **clothesline runs north–south along the corridor** (her floral dress
hangs here, ventilated in the firefight), which puts it straight in the
sightline of the **kitchen's east window**. The kitchen sits at the
north-east corner with windows on two walls — north into the backyard (she
watches the massacre) and east down the corridor (she spots the sheriff
creeping, past her own laundry). One room, both story beats, no contrivance.

## Key positions (metres)

| Element | Position | Notes |
|---------|----------|-------|
| House | x −7…5, y −4…5 | walls 3.2, ridge 5.2 |
| Garage | x −13…−7, y −3…3 | door faces south |
| Front porch | x −5…1, y −6.4…−4 | Mom's firing position, final shot |
| Kitchen windows | north wall x 1.4…4.2 · east wall y 1.6…4.2 | the two sightlines |
| Road centre | y ≈ −20 | sprint exits **west** |
| Ditch / crash | y −17…−14, crash ≈ x +10 | trench with culvert at driveway |
| Boy's position | (−2, 8.5) | fires north |
| Firing squad | y = 20, x −6…+6 | five figures |
| Old truck | x 11…14, y −3.1…1.5 | east corridor near the road; ricochet surface + crawl obstacle |
| BBQ + propane | x −6.7…−4.9, y 5.4…6.8 | beside the back stoop — the detonation |
| Santa | (−9.25, 5.05) | at the back stoop, inside the blast zone |
| Clothesline | x 8.6, y 5.8…14.8 | east side, runs N–S; in the kitchen east-window sightline |
| Back fence | y = 27 | treeline beyond |

## Status

Greybox massing, throwaway. Not yet designed: architectural character
(porch clutter, siding, roof pitch, junk), terrain undulation, the clay
look, interiors (only the kitchen window matters so far). Preview cameras
`cam_site`, `cam_intro`, `cam_backyard`, `cam_kitchen`, `cam_road`,
`cam_sidecorridor` live in the file, outside the linkable `property`
collection.
