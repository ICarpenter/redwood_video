"""Shared helpers for the redwood_video pipeline.

Stdlib only: this module runs under both system Python and Blender's
bundled Python (imported by new_shot.py inside Blender).
"""
from __future__ import annotations

import csv
import os
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path

FPS = 24
STATUSES = ("boarded", "blocked", "animated", "rendered", "comped", "final")
DEFAULT_BLENDER = "/Applications/Blender.app/Contents/MacOS/Blender"
_FIELDS = ["sq", "sh", "description", "start_frame", "end_frame",
           "duration", "assets", "status"]
_V_RE = re.compile(r"^v(\d{3})$")


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def shot_code(sq: str, sh: str) -> str:
    return f"sq{sq}_sh{sh}"


def shot_blend(sq: str, sh: str, root: Path | None = None) -> Path:
    root = root or project_root()
    return root / "shots" / f"sq{sq}" / f"sh{sh}" / f"sh{sh}.blend"


def render_dir(sq: str, sh: str, root: Path | None = None) -> Path:
    root = root or project_root()
    return root / "render" / shot_code(sq, sh)


@dataclass
class Shot:
    sq: str
    sh: str
    description: str
    start_frame: int
    end_frame: int
    assets: list[str] = field(default_factory=list)
    status: str = "boarded"

    @property
    def duration(self) -> int:
        return self.end_frame - self.start_frame + 1

    @property
    def code(self) -> str:
        return shot_code(self.sq, self.sh)


def read_shotlist(path) -> list[Shot]:
    path = Path(path)
    shots: list[Shot] = []
    seen: set[str] = set()
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != _FIELDS:
            raise ValueError(f"{path}: header must be {','.join(_FIELDS)}")
        for lineno, row in enumerate(reader, start=2):
            if any(row.get(k) is None for k in _FIELDS):
                raise ValueError(f"{path}:{lineno}: wrong number of columns")
            sq, sh = row["sq"].strip(), row["sh"].strip()
            for label, val in (("sq", sq), ("sh", sh)):
                if not (len(val) == 3 and val.isdigit()):
                    raise ValueError(
                        f"{path}:{lineno}: {label} must be a 3-digit string, got {val!r}"
                    )
            try:
                start = int(row["start_frame"])
                end = int(row["end_frame"])
            except ValueError:
                raise ValueError(
                    f"{path}:{lineno}: start_frame/end_frame must be integers"
                ) from None
            if end < start:
                raise ValueError(f"{path}:{lineno}: end_frame {end} < start_frame {start}")
            duration = row["duration"].strip()
            if duration:
                try:
                    duration_val = int(duration)
                except ValueError:
                    raise ValueError(
                        f"{path}:{lineno}: duration must be an integer, got {duration!r}"
                    ) from None
                if duration_val != end - start + 1:
                    raise ValueError(
                        f"{path}:{lineno}: duration {duration} != end-start+1 ({end - start + 1})"
                    )
            status = row["status"].strip()
            if status not in STATUSES:
                raise ValueError(
                    f"{path}:{lineno}: status {status!r} not one of {'|'.join(STATUSES)}"
                )
            code = shot_code(sq, sh)
            if code in seen:
                raise ValueError(f"{path}:{lineno}: duplicate shot {code}")
            seen.add(code)
            assets = [a.strip() for a in row["assets"].split(";") if a.strip()]
            shots.append(Shot(sq, sh, row["description"].strip(), start, end,
                              assets, status))
    return shots


def beat_to_frame(beat: float, bpm: float, fps: int = FPS) -> int:
    return round(beat * 60.0 / bpm * fps)


def next_version(render_shot_dir) -> str:
    d = Path(render_shot_dir)
    if not d.is_dir():
        return "v001"
    nums = [int(m.group(1)) for p in d.iterdir() if (m := _V_RE.match(p.name))]
    return f"v{max(nums, default=0) + 1:03d}"


def find_blender() -> str:
    cand = os.environ.get("BLENDER") or shutil.which("blender") or DEFAULT_BLENDER
    if not (shutil.which(cand) or os.path.exists(cand)):
        raise FileNotFoundError(f"Blender not found at {cand}; set $BLENDER")
    return cand
