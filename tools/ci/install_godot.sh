#!/usr/bin/env bash
# Installs Godot (headless editor) and its export templates on a Codemagic
# build machine (Linux for Android, macOS for iOS). Used by codemagic.yaml.
#   GODOT_VERSION  e.g. 4.7.2 (set in codemagic.yaml)
set -euo pipefail
VERSION="${GODOT_VERSION:-4.7.2}"
RELEASES="https://github.com/godotengine/godot/releases/download/${VERSION}-stable"
TEMPLATE_DIR_NAME="${VERSION}.stable"

if [[ "$(uname)" == "Darwin" ]]; then
  curl -sSL -o /tmp/godot.zip "$RELEASES/Godot_v${VERSION}-stable_macos.universal.zip"
  unzip -q -o /tmp/godot.zip -d /tmp/godot
  BIN="/tmp/godot/Godot.app/Contents/MacOS/Godot"
  DATA_DIR="$HOME/Library/Application Support/Godot"
else
  curl -sSL -o /tmp/godot.zip "$RELEASES/Godot_v${VERSION}-stable_linux.x86_64.zip"
  unzip -q -o /tmp/godot.zip -d /tmp/godot
  BIN="/tmp/godot/Godot_v${VERSION}-stable_linux.x86_64"
  DATA_DIR="$HOME/.local/share/godot"
fi
chmod +x "$BIN"
mkdir -p "$HOME/bin"
ln -sf "$BIN" "$HOME/bin/godot"
echo "$HOME/bin" >> "${CM_ENV_PATH_FILE:-/dev/null}" 2>/dev/null || true
export PATH="$HOME/bin:$PATH"

# Export templates (they include the Android build template and iOS template).
curl -sSL -o /tmp/templates.tpz "$RELEASES/Godot_v${VERSION}-stable_export_templates.tpz"
mkdir -p "$DATA_DIR/export_templates/$TEMPLATE_DIR_NAME"
unzip -q -o /tmp/templates.tpz -d /tmp/templates
cp -R /tmp/templates/templates/* "$DATA_DIR/export_templates/$TEMPLATE_DIR_NAME/"

# Android: tell Godot where Codemagic's Android SDK and Java live. (The
# settings file name changed between Godot versions, so write both names.)
if [[ "$(uname)" != "Darwin" ]]; then
  SETTINGS_DIR="$HOME/.config/godot"
  mkdir -p "$SETTINGS_DIR"
  for name in "editor_settings-4.tres" "editor_settings-${VERSION%.*}.tres"; do
    cat > "$SETTINGS_DIR/$name" <<SETTINGS
[gd_resource type="EditorSettings" format=3]

[resource]
export/android/android_sdk_path = "${ANDROID_SDK_ROOT:-${ANDROID_HOME:-}}"
export/android/java_sdk_path = "${JAVA_HOME:-}"
SETTINGS
  done
fi
godot --version
