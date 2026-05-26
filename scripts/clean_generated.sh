#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$ROOT_DIR"

rm -rf build .pytest_cache
rm -f cache.vcd
find . -name "__pycache__" -type d -prune -exec rm -rf {} +
find . -name ".DS_Store" -type f -delete
find waves -type f \( -name "*.vcd" -o -name "*.fst" \) -delete 2>/dev/null || true

echo "[clean_generated] removed generated build/test/wave/cache artifacts"
