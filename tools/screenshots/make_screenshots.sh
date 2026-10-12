#!/usr/bin/env bash
# Makes the store screenshots from the real game, framed with captions:
#   store/screenshots/ios-6.9/   1320x2868 (iPhone 6.9")
#   store/screenshots/android/   1080x2160 (phone, the game's own 1:2 shape)
#   store/screenshots/feature-graphic.png (Google Play, 1024x500)
# Needs Godot and xvfb-run (both in the cloud sessions). Takes a few minutes.
set -euo pipefail
cd "$(dirname "$0")/../.."
godot --headless --import > /dev/null 2>&1 || true
for size in "ios-6.9 1320 2868" "android 1080 2160"; do
  read -r name w h <<< "$size"
  raw="build/screenshots/raw_$name"
  save_dir="$(mktemp -d)"  # a fresh save, so the shots don't depend on yours
  XDG_DATA_HOME="$save_dir" xvfb-run -a -s "-screen 0 1400x3000x24" \
    godot --resolution "${w}x${h}" --script tools/screenshots/capture.gd -- "$raw"
  python3 tools/screenshots/frame.py "$raw" "store/screenshots/$name" "$w" "$h"
done
