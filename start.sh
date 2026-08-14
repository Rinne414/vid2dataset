#!/usr/bin/env bash
# Linux / macOS start entry — double-click in a file manager, or: ./start.sh
set -euo pipefail
cd "$(dirname "$0")"

echo "=========================================="
echo " vid2dataset"
echo " Linux / macOS start"
echo "=========================================="

if [[ -x "./vid2dataset" ]]; then
  exec "./vid2dataset" app
fi

if [[ -x "./venv/bin/python" ]]; then
  exec "./venv/bin/python" -m vid2dataset app
fi

if [[ -x "./.venv/bin/python" ]]; then
  exec "./.venv/bin/python" -m vid2dataset app
fi

echo
echo "Cannot start yet."
echo
echo "Install once, then run this script again:"
echo "  python3 -m venv venv"
echo "  ./venv/bin/pip install -U pip"
echo "  ./venv/bin/pip install -e ."
echo
echo "Optional NVIDIA GPU (Linux):"
echo "  ./venv/bin/pip install torch --index-url https://download.pytorch.org/whl/cu126"
echo
exit 1
