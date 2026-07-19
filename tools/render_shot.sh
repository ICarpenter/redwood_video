#!/usr/bin/env bash
# Headless-render one shot to render/<code>/<version>/ as an image sequence (format comes from the shot blend's output settings).
# Usage: tools/render_shot.sh <sq> <sh> [vNNN]
set -euo pipefail
. "$(dirname "$0")/env.sh" || exit 1

usage="usage: tools/render_shot.sh <sq> <sh> [vNNN]"
sq="${1:?$usage}"
sh_="${2:?$usage}"
code="sq${sq}_sh${sh_}"
blend="$REDWOOD_ROOT/shots/sq${sq}/sh${sh_}/sh${sh_}.blend"
[ -f "$blend" ] || { echo "error: $blend not found" >&2; exit 1; }

ver="${3:-$(python3 -c "
import sys
sys.path.insert(0, '$REDWOOD_ROOT/tools')
import shotlib
print(shotlib.next_version('$REDWOOD_ROOT/render/$code'))
")}"
out="$REDWOOD_ROOT/render/$code/$ver/${code}_####"

echo "rendering $code -> render/$code/$ver/"
"$BLENDER" --background "$blend" \
  --render-output "$out" \
  --render-anim
echo "done: render/$code/$ver/"
