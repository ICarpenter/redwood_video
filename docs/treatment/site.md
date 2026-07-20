# guns — the property (site plan)

Greybox layout: `assets/envs/property/property.blend`, bootstrapped by
`tools/blockout_property.py`. Massing only — it exists so boards, shot
cameras, and eventually the real set all agree on where things are. The
`.blend` is now **hand-maintained**: edit it in Blender. The tool has the
same positions baked in (so it doesn't lie) but refuses to overwrite the
file without `--force`; use `--out=<path>` for a throwaway preview build.

## The sun is the clock

The property runs along one line: the **road** at one end, the **backyard**
at the other, the **house** between. The sun turns that line into the
film's clock:

- **Sunrise is over the road** — the film opens at dawn as the delivery
  truck arrives. The road side is the EAST.
- **Sunset is over the backyard** — the firefight and the final sprint
  play out at dusk. The backyard is the WEST.

So the day *arcs from front-of-story to climax*: morning light on the
delivery, dying light on the carnage. The ending isn't "sprint into a
western sunset" — it's the two of them fleeing down the road at last light
while the sun sinks over the wrecked backyard behind them. Any shot that
contradicts this arc needs a reason.

*(Blend axes, for the technical record: road along −Y, backyard along +Y,
house at origin, +Z up. The greybox sun is keyed to the morning look —
raking in low from the road side; the firefight relights to the dusk key.)*

## The three spaces

**ROAD (south, y ≈ −23…−17).** Dirt, running east–west. The sheriff
ambles in from the east; a drainage **ditch** runs the length of the north
shoulder (y ≈ −17…−14) — that's what he spins into. A **culvert** carries
the driveway across it, and the mailbox marks the crossing.

**HOUSE + GARAGE (centre).** House 12×9 m, gable roof, front porch facing
the road (Mom fires from here in the final shot). The garage is attached on
the far side from the road and is a **passthrough**: a front door onto the
driveway/road and a rear door onto the backyard. This is the spatial engine
of the film — the boy hauls the delivered printer in the *front*, prints
inside, and carries the machine gun and the action figures out the *back*
into the backyard. The audience reads the whole supply chain in one
building: delivery → print → killing field.

**BACKYARD (y ≈ +5…+27).** Contained by a back fence and treeline so it
reads as a yard, not prairie. Right at the **garage's rear door**, where
the boy first carries his junk out, sit the **BBQ and the vintage Santa**,
clustered tight against the back of the house. The staging does triple
duty: the Santa is planted here *early* (established and exposed the moment
the passthrough starts moving), it's squarely in the eventual line of fire,
and one propane blast catches the whole cast *and* topples the Santa in a
single beat. The boy's firing position is centre; the firing squad lines up
across the far end.

## The east side corridor — the layout's load-bearing idea

The garage sits on the **west**, leaving the **east side of the house as a
corridor** running from the backyard down to the road. It's not empty — the
old truck and the clothesline dress it — but it stays a clear *path*, and
it does double duty:

1. **The ricochet bounce.** A stray round off the boy's gun kicks off the
   **old truck**, parked in the corridor near its road end, and zings out
   to blow the sheriff's tire. The truck is the surface that makes the gag
   a traceable line instead of a cheat.
2. **The sheriff's cover.** Crawling up the corridor, he ducks behind that
   same truck — which **breaks Mom's sightline from the kitchen window**.
   She spots him, he vanishes behind the truck, he pops out closer: the
   truck is what turns her "there's a man creeping" beat into a game of
   peekaboo with escalating dread.
3. **The crawl route.** Ditch → up the corridor → past the truck, under the
   clothesline → into the backyard. One continuous path.

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
| Garage | x −13…−7, y −3…3 | **passthrough** — front door (road, y −3) + rear door (backyard, y +3) |
| Front porch | x −5…1, y −6.4…−4 | Mom's firing position, final shot |
| Kitchen windows | back wall x 1.4…4.2 · corridor wall y 1.6…4.2 | the two sightlines |
| Road centre | y ≈ −20 | the escape route |
| Ditch / crash | y −17…−14, crash ≈ x +10 | trench with culvert at driveway |
| Boy's position | (−2, 8.5) | fires toward the firing squad |
| Firing squad | y = 20, x −6…+6 | five figures |
| Old truck | x 11…14, y −3.1…1.5 | corridor near the road; ricochet bounce + the sheriff's cover |
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
