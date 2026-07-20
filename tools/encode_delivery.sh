#!/usr/bin/env bash
# Encode a rendered PNG sequence + audio into delivery masters.
# Usage: tools/encode_delivery.sh <frames_dir> <audio_file> <name>
# Produces delivery/<name>_prores.mov and delivery/<name>_h264.mp4
set -euo pipefail
REDWOOD_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

command -v ffmpeg >/dev/null 2>&1 || {
  echo "error: ffmpeg not found — brew install ffmpeg" >&2; exit 1; }

usage="usage: tools/encode_delivery.sh <frames_dir> <audio_file> <name>"
frames="${1:?$usage}"
audio="${2:?$usage}"
name="${3:?$usage}"
[ -d "$frames" ] || { echo "error: $frames is not a directory" >&2; exit 1; }
[ -f "$audio" ] || { echo "error: $audio not found" >&2; exit 1; }

mkdir -p "$REDWOOD_ROOT/delivery"

ffmpeg -y -framerate 24 -pattern_type glob -i "$frames/*.png" -i "$audio" \
  -c:v prores_ks -profile:v 3 -pix_fmt yuv422p10le \
  -c:a pcm_s16le -shortest \
  "$REDWOOD_ROOT/delivery/${name}_prores.mov"

ffmpeg -y -framerate 24 -pattern_type glob -i "$frames/*.png" -i "$audio" \
  -c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p \
  -c:a aac -b:a 320k -movflags +faststart -shortest \
  "$REDWOOD_ROOT/delivery/${name}_h264.mp4"

echo "delivery/${name}_prores.mov"
echo "delivery/${name}_h264.mp4"
