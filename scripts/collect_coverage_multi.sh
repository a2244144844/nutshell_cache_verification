#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
WORKSPACE_ROOT="$ROOT_DIR"

"$SCRIPT_DIR/export_cache_dut.sh"

source "$SCRIPT_DIR/env.sh"
export PYTHONPATH="$ROOT_DIR:${PYTHONPATH:-}"

# Multi-seed configuration
export CACHE_RANDOM_SEEDS="${CACHE_RANDOM_SEEDS:-7,13,42,99,256,31,77,128,512,1023}"
export CACHE_RANDOM_STEPS="${CACHE_RANDOM_STEPS:-200}"

REPORT_DIR="$ROOT_DIR/build/reports"

# Clean previous coverage artifacts
rm -rf "$ROOT_DIR/build/coverage"
mkdir -p "$ROOT_DIR/build/coverage"
rm -rf "$REPORT_DIR"
mkdir -p "$REPORT_DIR"

echo "=== Stage 13: Multi-Seed Toggle Coverage Collection ==="
echo "Seeds: $CACHE_RANDOM_SEEDS"
echo "Steps per seed: $CACHE_RANDOM_STEPS"
echo ""

# Run full test suite (smoke + directed + multi-seed random) in single pytest process
"$WORKSPACE_ROOT/.venv/bin/python" -m pytest \
  "$ROOT_DIR/tests/smoke/" \
  "$ROOT_DIR/tests/directed/" \
  "$ROOT_DIR/tests/corner/" \
  "$ROOT_DIR/tests/random/test_random_multi_seed.py" \
  -q \
  --toffee-report \
  --report-dir "$REPORT_DIR" \
  --report-name cache_coverage.html \
  --report-dump-json

echo ""

# Generate RTL coverage HTML
if [ -f "$REPORT_DIR/line_dat/code_coverage.json" ]; then
    "$WORKSPACE_ROOT/.venv/bin/python" "$SCRIPT_DIR/generate_rtl_coverage_html.py" \
      -i "$REPORT_DIR/line_dat/code_coverage.json" \
      -o "$REPORT_DIR/rtl_coverage.html"
    echo "RTL coverage HTML: $REPORT_DIR/rtl_coverage.html"
else
    echo "WARNING: code_coverage.json not found, skipping HTML generation"
fi

echo ""
echo "Reports:"
echo "  HTML (funcov + line): $REPORT_DIR/cache_coverage.html"
echo "  RTL coverage:          $REPORT_DIR/rtl_coverage.html"

# Print toggle coverage summary
if [ -f "$REPORT_DIR/line_dat/code_coverage.json" ]; then
    echo ""
    echo "=== Coverage Summary ==="
    "$WORKSPACE_ROOT/.venv/bin/python" - <<'PY'
import json
from pathlib import Path

path = Path("build/reports/line_dat/code_coverage.json")
data = json.loads(path.read_text())
udata = data.get("uncovered", {}).get("data", {})

totals = {"line": [0, 0], "branch": [0, 0], "toggle": [0, 0], "expr": [0, 0]}
for file_path, file_cov in udata.items():
    for mod_name, mod_data in file_cov.get("modules", {}).items():
        t = mod_data.get("total", {})
        m = mod_data.get("miss", {})
        for k in totals:
            totals[k][0] += t.get(k, 0)
            totals[k][1] += t.get(k, 0) - m.get(k, 0)

for k, label in [("line", "Line"), ("branch", "Branch"), ("toggle", "Toggle"), ("expr", "Expr")]:
    t, h = totals[k]
    pct = (h / t * 100) if t > 0 else 100.0
    print(f"  {label:>8s}: {h}/{t} = {pct:.1f}%")
PY
fi
