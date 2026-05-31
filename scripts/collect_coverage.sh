#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$ROOT_DIR/../.." && pwd)"

"$SCRIPT_DIR/export_cache_dut.sh"

source "$SCRIPT_DIR/env.sh"
export PYTHONPATH="$ROOT_DIR:${PYTHONPATH:-}"

export CACHE_RANDOM_SEED="${1:-7}"
export CACHE_RANDOM_STEPS="${2:-18}"
export CACHE_COVERAGE_JSON="$ROOT_DIR/build/cache_random_coverage.json"
export TRACK1_CACHE_ROOT="$ROOT_DIR"

REPORT_DIR="$ROOT_DIR/build/reports"

# Clean previous coverage artifacts
rm -rf "$ROOT_DIR/build/coverage"
mkdir -p "$ROOT_DIR/build/coverage"
rm -rf "$REPORT_DIR"
mkdir -p "$REPORT_DIR"

# Run full test suite and generate Toffee HTML report with funcov + line coverage
"$REPO_ROOT/.venv/bin/python" -m pytest "$ROOT_DIR/tests/" -q \
  --toffee-report \
  --report-dir "$REPORT_DIR" \
  --report-name cache_coverage.html \
  --report-dump-json

# Also generate a Markdown coverage summary from legacy collector
"$REPO_ROOT/.venv/bin/python" - <<'PY'
import json
import os
from pathlib import Path

from src.utils.cache_coverage import EXPECTED_BINS, CacheCoverageCollector

root = Path(os.environ["TRACK1_CACHE_ROOT"])
summary_path = root / "build" / "cache_random_coverage.json"
toffee_path = root / "build" / "toffee_coverage_aggregated.json"
toffee_dir = root / "build" / "coverage"
report_path = root / "docs" / "coverage_report.md"
seed = int(os.environ.get("CACHE_RANDOM_SEED", "7"))
steps = int(os.environ.get("CACHE_RANDOM_STEPS", "18"))

data = json.loads(summary_path.read_text(encoding="utf-8"))
collector = CacheCoverageCollector()
collector.load_summary(data["summary"])
summary = collector.summary()

def aggregate_toffee_coverage(coverage_dir):
    files = sorted(coverage_dir.glob("*.json"))
    if not files:
        return None
    aggregated = {}
    for path in files:
        data = json.loads(path.read_text(encoding="utf-8"))
        for group_name, group in data.items():
            target_group = aggregated.setdefault(group_name, {
                "name": group.get("name", group_name),
                "points": [],
            })
            point_map = {point["name"]: point for point in target_group["points"]}
            for point in group.get("points", []):
                target_point = point_map.get(point["name"])
                if target_point is None:
                    target_point = {
                        "name": point["name"],
                        "bins": [],
                    }
                    target_group["points"].append(target_point)
                    point_map[point["name"]] = target_point
                bin_map = {bin_data["name"]: bin_data for bin_data in target_point["bins"]}
                for bin_data in point.get("bins", []):
                    target_bin = bin_map.get(bin_data["name"])
                    if target_bin is None:
                        target_bin = {"name": bin_data["name"], "hints": 0}
                        target_point["bins"].append(target_bin)
                        bin_map[bin_data["name"]] = target_bin
                    target_bin["hints"] += int(bin_data.get("hints", 0) or 0)
    return aggregated

def load_toffee_summary(data):
    if not data:
        return None
    groups = len(data)
    points = 0
    bins = 0
    covered_points = 0
    covered_bins = 0
    details = []
    for group_name, group in sorted(data.items()):
        group_points = group.get("points", [])
        group_bins = 0
        group_covered_bins = 0
        group_covered_points = 0
        for point in group_points:
            points += 1
            point_bins = point.get("bins", [])
            point_covered = False
            for bin_data in point_bins:
                bins += 1
                group_bins += 1
                hints = int(bin_data.get("hints", 0) or 0)
                if hints > 0:
                    covered_bins += 1
                    group_covered_bins += 1
                    point_covered = True
            if point_covered:
                covered_points += 1
                group_covered_points += 1
        details.append((group_name, group_covered_points, len(group_points), group_covered_bins, group_bins))
    return {
        "groups": groups,
        "points": points,
        "bins": bins,
        "covered_points": covered_points,
        "covered_bins": covered_bins,
        "details": details,
    }

toffee_data = aggregate_toffee_coverage(toffee_dir)
if toffee_data:
    toffee_path.write_text(json.dumps(toffee_data, indent=2) + "\n", encoding="utf-8")
else:
    toffee_data = json.loads(toffee_path.read_text(encoding="utf-8")) if toffee_path.exists() else None

toffee = load_toffee_summary(toffee_data)

# Parse line coverage from the dumped toffee report JSON
toffee_report_json = root / "build" / "reports" / "toffee_report.json"
line_coverage = None
if toffee_report_json.exists():
    try:
        tr_data = json.loads(toffee_report_json.read_text(encoding="utf-8"))
        lc = tr_data.get("coverages", {}).get("line")
        if lc and lc.get("total", 0) > 0:
            line_coverage = lc
    except Exception:
        pass

lines = []
lines.append("# Coverage Report")
lines.append("")
lines.append(f"- HTML report: `build/reports/cache_coverage.html`")
if line_coverage:
    hints = line_coverage.get("hints", 0)
    total = line_coverage.get("total", 0)
    pct = (hints / total * 100) if total > 0 else 0
    lines.append(f"- **Line coverage (RTL)**: {hints}/{total} lines ({pct:.1f}%)")
lines.append(f"- Random seed: `{seed}`")
lines.append(f"- Random steps: `{steps}`")
if toffee:
    lines.append(
        f"- **Toffee funcov**: {toffee['groups']} groups, "
        f"{toffee['points']} points, {toffee['bins']} bins"
    )
    lines.append(
        f"- **Marked Points**: {toffee['covered_points']}/{toffee['points']} "
        f"({toffee['covered_points'] * 100 // max(1, toffee['points'])}%)"
    )
    lines.append(
        f"- **Covered Bins**: {toffee['covered_bins']}/{toffee['bins']} "
        f"({toffee['covered_bins'] * 100 // max(1, toffee['bins'])}%)"
    )
lines.append("")

for bin_name, expected_bins in EXPECTED_BINS.items():
    lines.append(f"## {bin_name.replace('_', ' ').title()}")
    lines.append("")
    lines.append("| Bin | Count | Status |")
    lines.append("| --- | ---: | --- |")
    counts = summary.get(bin_name, {})
    for bin_value in expected_bins:
        count = counts.get(bin_value, 0)
        status = "covered" if count else "gap"
        lines.append(f"| `{bin_value}` | {count} | {status} |")
    lines.append("")

if toffee:
    lines.append("## Toffee Group Summary")
    lines.append("")
    lines.append("| Group | Points | Bins | Status |")
    lines.append("| --- | ---: | ---: | --- |")
    for group_name, covered_points, total_points, covered_bins, total_bins in toffee["details"]:
        status = "covered" if covered_bins == total_bins else "gap"
        lines.append(
            f"| `{group_name}` | {covered_points}/{total_points} | "
            f"{covered_bins}/{total_bins} | {status} |"
        )
    lines.append("")

lines.append("## Gaps And Next Actions")
lines.append("")
gaps = []
if summary.get("refill_path", {}).get("dirty_miss_writeback_refill", 0) == 0:
    gaps.append("- Dirty miss writeback/refill path not observed.")
if toffee and toffee["covered_bins"] < toffee["bins"]:
    gaps.append("- Toffee functional coverage still has uncovered bins; inspect the Toffee group summary above.")
if not gaps:
    gaps.append("- No functional-coverage gaps remain in the Toffee model.")
if summary.get("write_miss", {}).get("clean", 0) == 0 or summary.get("write_miss", {}).get("dirty", 0) == 0:
    gaps.append("- Legacy random-collector write-miss bins may show gaps because the constrained-random bootstrap focuses on write hits; directed tests close these paths in the Toffee model.")
lines.extend(gaps)
lines.append("")

report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Coverage report written to {report_path}")
PY

echo ""
echo "Reports:"
echo "  HTML (funcov + line): $REPORT_DIR/cache_coverage.html"
if [ -d "$REPORT_DIR/line_dat" ]; then
    echo "  Line coverage (LCOV):  $REPORT_DIR/line_dat/index.html"
fi
echo "  Markdown:               $ROOT_DIR/docs/coverage_report.md"

# ── Generate RTL-level branch coverage HTML from code_coverage.json ──
echo ""
echo "Generating RTL coverage HTML..."
RTL_SRC="$ROOT_DIR/build/picker_cache/Cache.v"
if [ -f "$RTL_SRC" ]; then
  "$REPO_ROOT/.venv/bin/python" "$SCRIPT_DIR/generate_rtl_coverage_html.py" \
    -i "$REPORT_DIR/line_dat/code_coverage.json" \
    -o "$REPORT_DIR/rtl_coverage.html" \
    --rtl "$RTL_SRC"
else
  "$REPO_ROOT/.venv/bin/python" "$SCRIPT_DIR/generate_rtl_coverage_html.py" \
    -i "$REPORT_DIR/line_dat/code_coverage.json" \
    -o "$REPORT_DIR/rtl_coverage.html"
fi
echo "  RTL coverage (Branch/Line/Toggle/Expr): $REPORT_DIR/rtl_coverage.html"
