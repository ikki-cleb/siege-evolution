#!/bin/bash
# Sets up a fresh Claude Code cloud session for Siege Evolution:
#   - installs Godot 4.7.2 (headless-capable) as `godot`
#   - installs the Web export templates (for tools/export_web.sh / export_itch.sh)
#   - imports the project so tests and content builds work immediately
# Safe to run repeatedly: every step is skipped if already done.
set -euo pipefail

# Only needed in cloud sessions; local machines have their own Godot.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

GODOT_VERSION="4.7.2"
GODOT_DIR="/opt/godot"
GODOT_BIN="$GODOT_DIR/Godot_v${GODOT_VERSION}-stable_linux.x86_64"
RELEASES="https://github.com/godotengine/godot/releases/download/${GODOT_VERSION}-stable"
TEMPLATES_DIR="$HOME/.local/share/godot/export_templates/${GODOT_VERSION}.stable"

# 1. Godot editor/runtime binary.
if [ ! -x "$GODOT_BIN" ]; then
  echo "Installing Godot ${GODOT_VERSION}..." >&2
  mkdir -p "$GODOT_DIR"
  curl -sSL -o "$GODOT_DIR/godot.zip" "$RELEASES/Godot_v${GODOT_VERSION}-stable_linux.x86_64.zip"
  unzip -q -o "$GODOT_DIR/godot.zip" -d "$GODOT_DIR"
  rm -f "$GODOT_DIR/godot.zip"
  chmod +x "$GODOT_BIN"
fi
ln -sf "$GODOT_BIN" /usr/local/bin/godot

# 2. Web export templates only (the full template pack is ~1 GB; we keep the web ones).
if [ ! -f "$TEMPLATES_DIR/web_nothreads_release.zip" ]; then
  echo "Installing Godot web export templates..." >&2
  mkdir -p "$TEMPLATES_DIR"
  curl -sSL -o /tmp/godot_templates.tpz "$RELEASES/Godot_v${GODOT_VERSION}-stable_export_templates.tpz"
  unzip -q -j -o /tmp/godot_templates.tpz 'templates/web*' 'templates/version.txt' -d "$TEMPLATES_DIR"
  rm -f /tmp/godot_templates.tpz
fi

# 3. Import assets and register script classes (creates the .godot/ cache).
cd "$CLAUDE_PROJECT_DIR"
godot --headless --import >/dev/null 2>&1 || true
# A second pass picks up resources that depend on the first (e.g. the font).
godot --headless --import >/dev/null 2>&1 || true

if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo "export GODOT=\"$GODOT_BIN\"" >> "$CLAUDE_ENV_FILE"
fi
echo "Siege Evolution session ready: godot $(godot --version 2>/dev/null | head -1)" >&2
