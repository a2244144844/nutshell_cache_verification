#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$ROOT_DIR/../.." && pwd)"
SUMMARY_JSON="$ROOT_DIR/build/cache_random_coverage.json"

"$SCRIPT_DIR/export_cache_dut.sh"

if [ -f "$REPO_ROOT/.venv/bin/activate" ]; then
  source "$REPO_ROOT/.venv/bin/activate"
fi

source "$SCRIPT_DIR/env.sh"
export PYTHONPATH="$ROOT_DIR:${PYTHONPATH:-}"

export CACHE_RANDOM_SEED="${1:-7}"
export CACHE_RANDOM_STEPS="${2:-18}"
export CACHE_COVERAGE_JSON="$SUMMARY_JSON"
export TRACK1_CACHE_ROOT="$ROOT_DIR"

python -m pytest "$ROOT_DIR/tests/random" -q

python - <<'PY'
import json
import os
from pathlib import Path

from src.utils.cache_coverage import CacheCoverageCollector

root = Path(os.environ["TRACK1_CACHE_ROOT"])
summary_path = root / "build" / "cache_random_coverage.json"
report_path = root / "docs" / "coverage_report.md"
seed = int(os.environ.get("CACHE_RANDOM_SEED", "7"))
steps = int(os.environ.get("CACHE_RANDOM_STEPS", "18"))

data = json.loads(summary_path.read_text(encoding="utf-8"))
collector = CacheCoverageCollector()
collector.load_summary(data["summary"])
report = collector.render_markdown(
    seed=seed,
    steps=steps,
    commands_run=[
        f"scripts/collect_coverage.sh {seed} {steps}",
    ],
)
report_lines = [
    f"Coverage data file: `{summary_path}`",
    "",
    report,
]
report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
PY
