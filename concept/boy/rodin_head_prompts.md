# boy — Rodin head-bust text-to-3D prompts

**Generated 2026-08-05 into `assets/chars/cast.blend`**, collection
`boy_modeling_rodin/boy_modeling_rodin_heads`.

**Settings: tier `Detail`, mesh_mode `Quad`, texture_mode `high`.** These are
only reachable because the BlenderMCP add-on was patched — it previously
hardcoded `Sketch`/`Raw`, which is what made every earlier attempt fail. See
"Add-on" below.

## Why heads

Full-body generation failed repeatedly (six attempts, image and text, both
tiers): legs fuse into cones or single blades, and the figure/ground read of the
concept art doesn't survive. Head-and-shoulders busts work, because the whole
mesh budget lands on the one region that carries the character.

**Geometry only.** These prompts deliberately carry no paint, colour, light or
style language — Ian repaints. Note that stripped to geometry the v2 and v3
concept prompts describe an identical boy; everything separating them is paint.
So the variation axis here is pose/proportion/form, not look.

## The constant

Every variant holds: large head, long thin neck, thick blond bowl cut as one
solid helmet mass with no strands, heavy droopy hooded eyelids, huge wide open
toothy grin with oversized front teeth, small wedge nose.

## The variants

| tag | object | what varies |
|---|---|---|
| A | `boy_head_A_baseline` | The original bust prompt verbatim — isolates the tier change |
| B | `boy_head_B_helmet` | Bowl cut hammered as one closed solid helmet: "no strands, no locks, no parting, no wisps" |
| C | `boy_head_C_pushed` | Extreme caricature — very large head, stalk neck, gigantic grin |
| D | `boy_head_D_headonly` | Head + neck only, no shoulders, so all resolution lands on the face |
| E | `boy_head_E_flat` | Flat planes / faceted graphic forms instead of realistic anatomy — tests whether Rodin can do the UPA look |

### A — baseline

```
A stylized cartoon 3D character head and shoulders bust: an 11-year-old boy with a
large head on a very long thin neck. Thick blond bowl-cut hair modelled as one
smooth solid helmet-shaped mass, a straight fringe cut square across the brow, the
ends curling under in a single continuous curved shape, no individual hair strands
and no separated locks. Heavy droopy hooded eyelids over small eyes, high thin
brows, a small simple wedge nose, large simple ears. A huge wide open toothy grin
stretching wider than the eyes, showing a full row of large oversized front teeth,
corners pulled up, chin tipped slightly back. Simple flat cheeks, no wrinkles, no
facial hair. Narrow sloping shoulders in an oversized boxy t-shirt collar. Clean
simple smooth geometry, plain matte untextured surface, no logos.
```
bbox_condition `[90, 85, 100]`

### B — helmet

```
A stylized cartoon 3D character head and shoulders bust of an 11-year-old boy. The
blond bowl-cut hair is one single thick solid helmet-shaped mass sitting on the
skull like an upturned bowl, with a hard straight fringe cut square across the brow
and the bottom edge curling under in one continuous curve. The hair is a simple
smooth closed shape: no individual strands, no separated locks, no parting, no
wisps. Beneath it, heavy droopy hooded eyelids over small eyes, high thin brows, a
tiny simple wedge nose, and an enormous wide open toothy grin stretching wider than
the eyes with a full row of big square front teeth. Long thin neck, narrow sloping
shoulders. Clean smooth simple geometry, plain matte untextured surface.
```
bbox_condition `[90, 85, 100]`

### C — pushed

```
A stylized cartoon 3D character head and shoulders bust with extremely exaggerated
caricature proportions: an 11-year-old boy with a very large round head balanced on
an extremely long, thin, stalk-like neck. Enormous thick blond bowl-cut hair as one
heavy solid helmet-shaped mass, oversized relative to the face, with a hard straight
fringe across the brow and the ends curling under in one continuous curve, no
individual strands. Very heavy droopy hooded eyelids almost closing the small eyes,
brows sitting high on the forehead, a tiny wedge nose, and a gigantic wide open
toothy grin stretching right across the face, far wider than the eyes, with huge
oversized square front teeth. Tiny narrow sloping shoulders. Clean smooth simple
geometry, plain matte untextured surface.
```
bbox_condition `[85, 80, 100]`

### D — head only

```
A stylized cartoon 3D character head only: an 11-year-old boy's head on a long thin
neck, cut off cleanly at the base of the neck with no shoulders and no body. Thick
blond bowl-cut hair as one smooth solid helmet-shaped mass covering the skull, hard
straight fringe cut square across the brow, bottom edge curling under in one
continuous curve, no individual strands. Heavy droopy hooded eyelids over small
eyes, high thin brows, small simple wedge nose, simple ears. A huge wide open toothy
grin far wider than the eyes, upper and lower rows of large square teeth visible,
deep open mouth cavity behind them, chin tipped slightly back. Smooth simple cheeks,
no wrinkles. Clean smooth simple geometry, plain matte untextured surface.
```
bbox_condition `[95, 90, 100]`

### E — flat / UPA

```
A stylized cartoon 3D character head and shoulders bust of an 11-year-old boy, built
from simple flat planes and bold graphic shapes rather than realistic anatomy, in the
style of 1950s mid-century flat cartoon design. The blond bowl-cut hair is one solid
geometric helmet shape with a hard straight fringe edge and a crisp curled-under
bottom rim, no strands. The face is simple and flat: broad flat cheek planes, heavy
droopy hooded eyelids as simple wedge shapes, brows as flat raised bars, a small
angular wedge nose, and a huge wide open grin cut across the face showing a flat row
of big square teeth. Large head, long thin neck, narrow shoulders. Clean smooth
simple geometry, faceted graphic forms, plain matte untextured surface.
```
bbox_condition `[90, 85, 100]`

## Gotchas worth keeping

- **Prompts are capped at 1024 characters.** Longer ones 400.
- **Busts import Z-up; full bodies import Y-up.** Full bodies need a −90° X
  rotation to stand; busts need none. Rotation mode also arrives as
  `QUATERNION`, so writing `rotation_euler` silently does nothing until you set
  `rotation_mode = 'XYZ'`.
- **`mesh_mode: Quad` does not survive the round trip.** The add-on downloads
  `.glb`, and glTF has no quad primitive, so results are 100% triangles measured.
  Real quads would need the FBX/OBJ download, which the importer doesn't fetch.
- **"Baggy jeans swamping thin legs" reliably generates a skirt or a cone.** Any
  full-body retry must say "two separate distinct trouser legs with a clear gap
  between them."

## Add-on

`~/blender/add-ons/blender-mcp/addon.py` (symlinked into Blender's addons dir)
previously hardcoded `tier="Sketch"`, `mesh_mode="Raw"`, `texture_mode="high"`
with no parameter or UI. Patched to read three new scene properties, defaulting
to `Detail`/`Quad`/`high`, with a "Generation Quality" box in the BlenderMCP
panel. Backup at `addon.py.pre-rodin-tier.bak`. Texture-mode values other than
`high` are **untested** against the API.
