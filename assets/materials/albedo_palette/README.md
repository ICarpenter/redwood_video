# albedo_palette/ — a record, not a system

**Kept deliberately when the dab painter was deleted, 2026-08-06.** Colour is
being started from scratch. This folder is here so the work behind the
2026-08-04 palette is not lost, and nothing reads it.

| file | what it is |
|---|---|
| `albedo_palette.json` | 96 swatches — 14 colour families plus neutrals and a 5-strong bold set, each family in five shades (pale / light / base / dark / deep), with `hex`, `rgb8` and a one-line `role` for every one |
| `albedo_palette.png` | the picker sheet — the same 96 as an image, which is the readable version |

**Where the colours came from is in the JSON's `meta`,** and it is the most
valuable thing here: a colour census of `refs/styles/` and the 60s/80s
reference sets — 31 images, 2.48M pixels — plus the caveat that green is only
1.4% of the saturated pixels in those refs, so olive, green and sage were
derived rather than measured.

**The generator is gone.** `tools/albedo_palette.py` and
`tools/palette_common.py` built these and were deleted with the rest of the dab
tooling; recover them from git history (`git log -- tools/albedo_palette.py`)
if the maths is ever wanted. The `index` field only meant something to the
index-map encoding the dab painter used — as a palette, ignore it and read the
hex.

**The prose version is canon**, not this: `docs/treatment/style.md` § Palette
carries the core swatches and the 1993 annex with their roles and the
reasoning, and that is the document to argue with. This is the long tail
underneath it. The palette was always guidance rather than rules — no tool ever
enforced it, and none should.

The tilt half of this pair (`tilt_palette/`) was **not** kept: it indexed facet
normals for the dab mechanism specifically, so it died with it.
