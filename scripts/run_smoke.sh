#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
WORKSPACE_ROOT="$(cd "$ROOT_DIR/.." && pwd)"

"$SCRIPT_DIR/export_cache_dut.sh"

if [ -f "$WORKSPACE_ROOT/.venv/bin/activate" ]; then
  source "$WORKSPACE_ROOT/.venv/bin/activate"
fi

source "$SCRIPT_DIR/env.sh"
export PYTHONPATH="$ROOT_DIR:${PYTHONPATH:-}"

python -m pytest "$ROOT_DIR/tests/smoke" -q
