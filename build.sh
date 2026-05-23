#!/usr/bin/env bash
# Build TekServe Local for Linux (folder app in dist/TekServeLocal/).
set -euo pipefail
cd "$(dirname "$0")"

if ! python3 -c "import tkinter" 2>/dev/null; then
  echo "tkinter is required. Install it, then re-run:"
  echo "  Debian/Ubuntu: sudo apt install python3-tk python3-dev"
  echo "  Fedora:          sudo dnf install python3-tkinter"
  echo "  Arch:            sudo pacman -S tk"
  exit 1
fi

echo "Installing build dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements-build.txt

echo "Building TekServe Local..."
python3 -m PyInstaller tekserve_local.spec --noconfirm --clean

if [[ ! -f dist/TekServeLocal/TekServeLocal ]]; then
  echo "Build failed: dist/TekServeLocal/TekServeLocal not found."
  exit 1
fi

echo ""
echo "Build complete:"
echo "  dist/TekServeLocal/TekServeLocal"
echo ""
echo "Run: ./dist/TekServeLocal/TekServeLocal"
echo "Release archive: ./package-release.sh"
