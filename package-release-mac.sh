#!/usr/bin/env bash
# Package dist/TekServeLocal.app for GitHub Releases (README download button).
set -euo pipefail
cd "$(dirname "$0")"

APP="dist/TekServeLocal.app"
OUT="TekServeLocal-Mac.zip"

if [[ ! -d "$APP" ]]; then
  echo "Run ./build-mac.sh first. $APP not found."
  exit 1
fi

rm -f "$OUT"

# Ad-hoc sign so Gatekeeper is less strict for unsigned private builds.
if command -v codesign >/dev/null 2>&1; then
  codesign --force --deep --sign - "$APP" || true
fi

ditto -c -k --sequesterRsrc --keepParent "$APP" "$OUT"

echo "Release package ready:"
echo "  $OUT"
echo ""
echo "Upload to GitHub:"
echo "  gh release create v1.0.0 TekServeLocal-Mac.zip --title v1.0.0"
