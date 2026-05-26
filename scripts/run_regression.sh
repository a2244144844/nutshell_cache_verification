#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$ROOT_DIR/../.." && pwd)"

"$SCRIPT_DIR/export_cache_dut.sh"

if [ -f "$REPO_ROOT/.venv/bin/activate" ]; then
  source "$REPO_ROOT/.venv/bin/activate"
fi

source "$SCRIPT_DIR/env.sh"
export PYTHONPATH="$ROOT_DIR:${PYTHONPATH:-}"

python -m pytest "$ROOT_DIR/tests/smoke" "$ROOT_DIR/tests/directed" "$ROOT_DIR/tests/corner" -q
