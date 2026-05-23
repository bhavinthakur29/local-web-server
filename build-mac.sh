#!/usr/bin/env bash
# Build TekServe Local for macOS (.app bundle in dist/TekServeLocal.app).
set -euo pipefail
cd "$(dirname "$0")"

if ! python3 -c "import tkinter" 2>/dev/null; then
  echo "tkinter is required. Install it, then re-run:"
  echo "  brew install python-tk@3.13"
  echo "  # or: brew install tcl-tk"
  exit 1
fi

echo "Installing build dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements-build.txt

echo "Building TekServe Local..."
python3 -m PyInstaller tekserve_local.spec --noconfirm --clean

if [[ ! -d dist/TekServeLocal.app ]]; then
  echo "Build failed: dist/TekServeLocal.app not found."
  exit 1
fi

echo ""
echo "Build complete:"
echo "  dist/TekServeLocal.app"
echo ""
echo "Run: open dist/TekServeLocal.app"
echo "Release ZIP: ./package-release-mac.sh"
