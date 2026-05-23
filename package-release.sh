#!/usr/bin/env bash
# Package dist/TekServeLocal for GitHub Releases (README download button).
set -euo pipefail
cd "$(dirname "$0")"

SRC="dist/TekServeLocal"
OUT="TekServeLocal-Linux.tar.gz"

if [[ ! -f "$SRC/TekServeLocal" ]]; then
  echo "Run ./build.sh first. $SRC/TekServeLocal not found."
  exit 1
fi

rm -f "$OUT"
tar -czf "$OUT" -C dist TekServeLocal

echo "Release package ready:"
echo "  $OUT"
echo ""
echo "Upload to GitHub:"
echo "  gh release create v1.0.0 TekServeLocal-Linux.tar.gz --title v1.0.0"
