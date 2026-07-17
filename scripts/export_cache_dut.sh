#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
WORKSPACE_ROOT="$(cd "$ROOT_DIR/.." && pwd)"

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
  --verbose \
  -c

# Picker 0.9.0's generated Python `purge` target uses GNU-only `mv -t`.
# On macOS the move silently fails and the generated wrapper is then deleted.
# Verbose mode keeps the package under UT_Cache; copy its runtime artifacts to
# the historical OUT_DIR layout expected by src/env/cache_env.py.
if [ -f "$OUT_DIR/UT_Cache/__init__.py" ]; then
  cp -R "$OUT_DIR/UT_Cache/." "$OUT_DIR/"
fi

if [ ! -f "$OUT_DIR/__init__.py" ]; then
  echo "ERROR: Picker Cache DUT export did not produce $OUT_DIR/__init__.py" >&2
  exit 1
fi
