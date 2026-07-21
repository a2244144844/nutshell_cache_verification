#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
WORKSPACE_ROOT="$ROOT_DIR"

source "$SCRIPT_DIR/env.sh"

# Activate venv so CMake finds Python 3.11 instead of Homebrew 3.14
if [ -f "$WORKSPACE_ROOT/.venv/bin/activate" ]; then
  source "$WORKSPACE_ROOT/.venv/bin/activate"
fi

OUT_DIR="$ROOT_DIR/build/picker_cache"
rm -rf "$OUT_DIR"
mkdir -p "$ROOT_DIR/build"

picker export "$ROOT_DIR/rtl/dut/Cache.v" \
  --fs "$ROOT_DIR/rtl/dut/Test.v" \
  -w cache.vcd \
  --sim verilator \
  --tdir "$OUT_DIR" \
  --autobuild true \
  -c
