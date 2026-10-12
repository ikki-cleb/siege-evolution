#!/usr/bin/env bash
# Adds the store billing plugins to the project before a phone export.
# They aren't kept in the repo (they're platform binaries); Codemagic fetches
# them on every build.
#   bash tools/ci/fetch_plugins.sh android   -> addons/GodotGooglePlayBilling
#   bash tools/ci/fetch_plugins.sh ios       -> ios/plugins/inappstore
#
# Each plugin comes from the latest GitHub release of its official repo. If a
# release's file names change, pin the exact download with the URL variables
# below (set them in Codemagic's environment variables):
#   BILLING_PLUGIN_URL   zip containing addons/GodotGooglePlayBilling
#   IOS_PLUGINS_URL      zip containing the inappstore plugin (.gdip + .xcframework)
set -euo pipefail
cd "$(dirname "$0")/../.."
PLATFORM="${1:?usage: fetch_plugins.sh android|ios}"

latest_asset() {  # repo, pattern -> download URL of the first matching asset
  curl -sSL "https://api.github.com/repos/$1/releases/latest" \
    | grep -o '"browser_download_url": *"[^"]*"' | cut -d'"' -f4 | grep -E "$2" | head -n 1
}

if [[ "$PLATFORM" == "android" ]]; then
  URL="${BILLING_PLUGIN_URL:-$(latest_asset godot-sdk-integrations/godot-google-play-billing '\.zip$')}"
  [[ -n "$URL" ]] || { echo "Couldn't find the Google Play Billing plugin; set BILLING_PLUGIN_URL"; exit 1; }
  curl -sSL -o /tmp/billing.zip "$URL"
  rm -rf /tmp/billing && unzip -q -o /tmp/billing.zip -d /tmp/billing
  ADDON="$(find /tmp/billing -type d -name GodotGooglePlayBilling | head -n 1)"
  [[ -n "$ADDON" ]] || { echo "The billing zip has no GodotGooglePlayBilling folder"; exit 1; }
  mkdir -p addons && rm -rf addons/GodotGooglePlayBilling && cp -R "$ADDON" addons/
  # Turn the plugin on (Godot only exports enabled editor plugins).
  if ! grep -q "GodotGooglePlayBilling/plugin.cfg" project.godot; then
    printf '\n[editor_plugins]\n\nenabled=PackedStringArray("res://addons/GodotGooglePlayBilling/plugin.cfg")\n' >> project.godot
  fi
  echo "Google Play Billing plugin added from $URL"
elif [[ "$PLATFORM" == "ios" ]]; then
  URL="${IOS_PLUGINS_URL:-$(latest_asset godot-sdk-integrations/godot-ios-plugins '\.zip$')}"
  [[ -n "$URL" ]] || { echo "Couldn't find the iOS plugins; set IOS_PLUGINS_URL"; exit 1; }
  curl -sSL -o /tmp/ios_plugins.zip "$URL"
  rm -rf /tmp/ios_plugins && unzip -q -o /tmp/ios_plugins.zip -d /tmp/ios_plugins
  GDIP="$(find /tmp/ios_plugins -name 'inappstore*.gdip' | head -n 1)"
  [[ -n "$GDIP" ]] || { echo "The iOS plugins zip has no inappstore .gdip"; exit 1; }
  mkdir -p ios/plugins
  cp -R "$(dirname "$GDIP")"/inappstore* ios/plugins/
  echo "StoreKit (inappstore) plugin added from $URL"
fi
