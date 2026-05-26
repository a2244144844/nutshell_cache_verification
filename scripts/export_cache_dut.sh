#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$ROOT_DIR/../.." && pwd)"

if [ -f "$REPO_ROOT/.venv/bin/activate" ]; then
  source "$REPO_ROOT/.venv/bin/activate"
fi

source "$SCRIPT_DIR/env.sh"

OUT_DIR="$ROOT_DIR/build/picker_cache"
rm -rf "$OUT_DIR"
mkdir -p "$ROOT_DIR/build"

picker export "$ROOT_DIR/rtl/dut/Cache.v" \
  --fs "$ROOT_DIR/rtl/dut/Test.v" \
  -w cache.vcd \
  --sim verilator \
  --tdir "$OUT_DIR" \
  --autobuild true
