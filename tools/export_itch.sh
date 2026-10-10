#!/bin/sh
# Builds a zip for itch.io (or any web host) at build/siege-evolution-web.zip.
# Upload it on itch.io as an HTML game, "played in the browser".
# Usage: tools/export_itch.sh [path-to-godot]
set -e
GODOT="${1:-godot}"
cd "$(dirname "$0")/.."
rm -rf build/itch && mkdir -p build/itch
"$GODOT" --headless --export-release "Web" build/itch/index.html
# Our page shell is written for Claude's artifact viewer, which adds the
# <!DOCTYPE>/<html> wrapper itself; a normal web host needs it in the file.
{ printf '<!DOCTYPE html>\n<html lang="en">\n<meta charset="utf-8">\n'; cat build/itch/index.html; printf '\n</html>\n'; } > build/itch/page.html
mv build/itch/page.html build/itch/index.html
rm -f build/siege-evolution-web.zip
(cd build/itch && zip -q -r ../siege-evolution-web.zip .)
ls -la build/siege-evolution-web.zip
