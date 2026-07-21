#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
WORKSPACE_ROOT="$ROOT_DIR"

"$SCRIPT_DIR/export_cache_dut.sh"

source "$SCRIPT_DIR/env.sh"
export PYTHONPATH="$ROOT_DIR:${PYTHONPATH:-}"

"$WORKSPACE_ROOT/.venv/bin/python" -m pytest "$ROOT_DIR/tests/smoke" "$ROOT_DIR/tests/directed" "$ROOT_DIR/tests/corner" -q
