# Shared environment for redwood_video shell tools. Source, don't execute:
#   . "$(dirname "$0")/env.sh" || exit 1
REDWOOD_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BLENDER="${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}"
if ! command -v "$BLENDER" >/dev/null 2>&1 && [ ! -x "$BLENDER" ]; then
  echo "error: Blender not found at $BLENDER (set \$BLENDER)" >&2
  return 1
fi
export REDWOOD_ROOT BLENDER
