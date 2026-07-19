"""Create every missing shot .blend listed in docs/shotlist.csv.

Usage: python3 tools/build_shots.py [--dry-run] [--force]
"""
import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shotlib


def plan_builds(shots, root, force=False):
    return [
        s for s in shots
        if force or not shotlib.shot_blend(s.sq, s.sh, root).exists()
    ]


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--force", action="store_true",
                   help="rebuild shots that already exist (asks for confirmation; OVERWRITES existing work)")
    args = p.parse_args(argv)

    root = shotlib.project_root()
    shots = shotlib.read_shotlist(root / "docs" / "shotlist.csv")
    todo = plan_builds(shots, root, args.force)
    if args.force:
        existing = [s for s in shots if shotlib.shot_blend(s.sq, s.sh, root).exists()]
        if existing and not args.dry_run:
            print("--force will OVERWRITE these existing shot files from the template:")
            for s in existing:
                print(f"  {s.code}")
            try:
                answer = input(f"type yes to rebuild {len(existing)} existing shot(s): ")
            except EOFError:
                answer = ""
            if answer.strip() != "yes":
                print("aborted")
                return
    if len(todo) < len(shots):
        print(f"skipping {len(shots) - len(todo)} existing shot(s)")
    if not todo:
        print("nothing to build")
        return
    if args.dry_run:
        for s in todo:
            print(f"would build {s.code} [{s.start_frame}-{s.end_frame}]")
        return

    blender = shotlib.find_blender()
    for s in todo:
        print(f"building {s.code} ...")
        cmd = [
            blender, "--background",
            str(root / "tools" / "shot_template.blend"),
            "--python-exit-code", "1",
            "--python", str(root / "tools" / "new_shot.py"),
            "--", "--sq", s.sq, "--sh", s.sh,
        ]
        if args.force:
            cmd.append("--force")
        subprocess.run(cmd, check=True)
    print(f"built {len(todo)} shot(s)")


if __name__ == "__main__":
    main()
