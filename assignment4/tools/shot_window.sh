#!/bin/bash
# Capture one real window on DISPLAY=:1.
# Usage: shot_window.sh <title-substring> <output.png>
set -euo pipefail
export DISPLAY=:1
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/tmp/runtime-ubuntu}"
title="${1:?title}"
out="${2:?out}"
id=""
for _ in 1 2 3 4 5 6 7 8 9 10; do
  id=$(xdotool search --name "$title" | tail -1 || true)
  if [[ -n "$id" ]]; then
    break
  fi
  sleep 0.4
done
if [[ -z "$id" ]]; then
  echo "window not found: $title" >&2
  xdotool search --name "." getwindowname %@ >&2 || true
  exit 1
fi
xdotool windowactivate --sync "$id"
# Keep the whole window inside the 1920x1200 desktop.
xdotool windowmove "$id" 24 48
if [[ -n "${3:-}" ]]; then
  w="${3%x*}"
  h="${3#*x}"
  xdotool windowsize "$id" "$w" "$h"
fi
sleep 0.5
xdotool windowactivate --sync "$id"
sleep 0.3
eval "$(xdotool getwindowgeometry --shell "$id")"
# Clamp to the screen so scrot does not clip the bottom edge.
if (( Y < 0 )); then Y=0; fi
if (( X < 0 )); then X=0; fi
if (( X + WIDTH > 1920 )); then WIDTH=$((1920 - X)); fi
if (( Y + HEIGHT > 1200 )); then HEIGHT=$((1200 - Y)); fi
rm -f "$out"
scrot -a "${X},${Y},${WIDTH},${HEIGHT}" -F "$out"
echo "saved $out id=$id ${WIDTH}x${HEIGHT} at ${X},${Y}"
file "$out"
