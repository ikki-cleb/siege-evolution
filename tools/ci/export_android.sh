#!/usr/bin/env bash
# Builds the signed Android App Bundle (.aab) for Google Play.
# Signing comes from Codemagic's Android code signing (the upload key you
# uploaded there): Godot reads these GODOT_ANDROID_KEYSTORE_* variables.
#   BUILD_NUMBER (Codemagic) becomes the version code, so every upload is new.
set -euo pipefail
cd "$(dirname "$0")/../.."
export GODOT_ANDROID_KEYSTORE_RELEASE_PATH="${CM_KEYSTORE_PATH:?Android signing not set up in Codemagic}"
export GODOT_ANDROID_KEYSTORE_RELEASE_USER="${CM_KEY_ALIAS}"
export GODOT_ANDROID_KEYSTORE_RELEASE_PASSWORD="${CM_KEY_PASSWORD}"
# Each upload needs a higher version code than the last.
sed -i "s/^version\/code=.*/version\/code=${BUILD_NUMBER:-1}/" export_presets.cfg
# Godot's Gradle build needs the Android build template unpacked into android/.
TEMPLATES="$HOME/.local/share/godot/export_templates/${GODOT_VERSION:-4.7.2}.stable"
rm -rf android/build && mkdir -p android/build
unzip -q -o "$TEMPLATES/android_source.zip" -d android/build
echo "${GODOT_VERSION:-4.7.2}.stable" > android/.build_version
godot --headless --import
godot --headless --script tools/build_content.gd
mkdir -p build/android
godot --headless --export-release "Android" build/android/siege-evolution.aab
ls -la build/android
