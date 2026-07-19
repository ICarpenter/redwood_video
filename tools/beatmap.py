"""Generate docs/beatmap.csv: bar/beat -> seconds -> timeline frame.

Usage:
  python3 tools/beatmap.py --bpm 92 --length 214 [--beats-per-bar 4]
      [--fps 24] [--out docs/beatmap.csv]
"""
import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shotlib


def generate_rows(bpm, length_s, beats_per_bar=4, fps=shotlib.FPS):
    if bpm <= 0:
        raise ValueError(f"bpm must be positive, got {bpm}")
    if length_s < 0:
        raise ValueError(f"length must be >= 0, got {length_s}")
    rows = []
    beat = 0
    while True:
        t = beat * 60.0 / bpm
        if t > length_s:
            break
        rows.append({
            "bar": beat // beats_per_bar + 1,
            "beat": beat % beats_per_bar + 1,
            "time_s": round(t, 3),
            # timeline frame 1 = song time 0 (see docs/pipeline.md)
            "frame": shotlib.beat_to_frame(beat, bpm, fps) + 1,
        })
        beat += 1
    return rows


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--bpm", type=float, required=True)
    p.add_argument("--length", type=float, required=True,
                   help="track length in seconds")
    p.add_argument("--beats-per-bar", type=int, default=4)
    p.add_argument("--fps", type=int, default=shotlib.FPS)
    p.add_argument("--out", type=Path,
                   default=shotlib.project_root() / "docs" / "beatmap.csv")
    args = p.parse_args(argv)

    try:
        rows = generate_rows(args.bpm, args.length, args.beats_per_bar, args.fps)
    except ValueError as e:
        p.error(str(e))
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["bar", "beat", "time_s", "frame"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} beats to {args.out}")


if __name__ == "__main__":
    main()
