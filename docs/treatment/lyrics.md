# guns — lyrics & song structure

141 BPM, 4/4, 150 bars, 4:15. Bars counted from 0 at song start (the
`start_bar`/`end_bar` columns in `../sections.csv` use this same convention;
note `../beatmap.csv`'s bar column is 1-indexed — its bar 1 is this bar 0).

## Structure

Frames below are **measured off the recording**, not derived from the written
chart — they come from the timeline markers hand-placed in `edit/edit.blend`
on 2026-08-02 and copied into `../sections.csv`. The chart this table used to
carry ran one bar late against the actual take: every section landed on
beatmap bar N while the file claimed N+1.

| Section  | Bars    | Frames    | Length |
|----------|---------|-----------|--------|
| *(lead-in silence)* | 0–2 | 1–80 | 3.3s |
| Intro    | 2–18    | 81–735    | 27.3s  |
| Verse 1  | 18–38   | 736–1552  | 34.0s  |
| Chorus 1 | 38–46   | 1553–1878 | 13.6s  |
| Verse 2 intro | 46–50 | 1879–2042 | 6.8s |
| Verse 2  | 50–66   | 2043–2695 | 27.2s  |
| Chorus 2 | 66–74   | 2696–3023 | 13.7s  |
| Solo     | 74–86   | 3024–3513 | 20.4s  |
| Verse 3  | 86–102  | 3514–4166 | 27.2s  |
| Chorus 3 | 102–111 | 4167–4534 | 15.3s  |
| Tail (audio only) | 111–150 | 4535–6124 | 66.2s |

Every section boundary is a downbeat and every section is a whole number of
bars. Two corrections the old chart got wrong: the track opens with **3.3s of
silence** before the music enters at frame 81 (bar 2) — picture still starts
at frame 1 and plays the sunrise over it — and verse 2 is preceded by a 4-bar
instrumental lead-in (**Verse 2 intro**) that the old chart folded into the
verse.

(The song ends dead on the last chorus hit at bar 111; bars 111–150 are
just the audio ringing out. Picture ends with a title card early in the
tail — the exact out-point gets picked in the edit.)

## Lyrics

### Verse 1
In the heartland, they are strugglin'
and rebelion, has been discussed
I say hey man, the products movin'
And in the dead hand, they all trust

### Chorus
Who got the bag?
Who is your plug?
I got the guns
if peace of mind is what you want

### Verse 2
when a law man, keeps a knockin'
with the question, of his luck
will a warrant, keep him breathing
or is a bullet, too quick to duck

### Verse 3
down in Austin, a rifle taken
given by him, who needed a bump
stocks are rising, not surprising
the kid are lying, in a slump

(Chorus repeats after each verse; instrumental solo between chorus 2 and
verse 3.)
