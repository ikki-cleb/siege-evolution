#!/usr/bin/env bash
# Exports the Xcode project for iOS (Godot can't sign for the App Store by
# itself on CI; Codemagic's xcode-project tools build and sign the .ipa).
#   APPLE_TEAM_ID  your 10-character Apple Developer team id (Codemagic env)
#   BUILD_NUMBER   (Codemagic) becomes the build number, so every upload is new.
set -euo pipefail
cd "$(dirname "$0")/../.."
sed -i '' "s/^application\/app_store_team_id=.*/application\/app_store_team_id=\"${APPLE_TEAM_ID:?set APPLE_TEAM_ID in Codemagic}\"/" export_presets.cfg
sed -i '' "s/^application\/version=.*/application\/version=\"${BUILD_NUMBER:-1}\"/" export_presets.cfg
godot --headless --import
godot --headless --script tools/build_content.gd
mkdir -p build/ios
godot --headless --export-release "iOS" build/ios/SiegeEvolution.ipa
ls -la build/ios
