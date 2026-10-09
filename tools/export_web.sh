#!/bin/sh
# Builds the web version into build/web, packed for hosts that only serve
# common file types (see web/shell.html for how it's unpacked).
# Usage: tools/export_web.sh [path-to-godot]
set -e
GODOT="${1:-godot}"
cd "$(dirname "$0")/.."
rm -rf build/web && mkdir -p build/web
"$GODOT" --headless --export-release "Web" build/web/index.html
gzip -9 -c build/web/index.wasm | base64 -w 0 > build/web/index.wasm.gz.b64.txt
base64 -w 0 build/web/index.pck > build/web/index.pck.b64.txt
rm build/web/index.wasm build/web/index.pck
ls -la build/web
