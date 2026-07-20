#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
WORKSPACE_ROOT="$(cd "$ROOT_DIR/.." && pwd)"
STAGE_INDEX="${1:-1}"
MCP_PORT="${UCAGENT_MCP_PORT:-5002}"
BACKEND_ARGS="${UC_ENV_CMD_BACKEND_EX_ARGS:--m gpt-5.4-mini --ephemeral}"

cd "$REPO_ROOT"

if [ -f "$WORKSPACE_ROOT/.venv/bin/activate" ]; then
  source "$WORKSPACE_ROOT/.venv/bin/activate"
fi

UCAGENT_CMDLINE_START_MCP=1 \
UC_ENV_CMD_BACKEND_EX_ARGS="$BACKEND_ARGS" \
ucagent "$ROOT_DIR" Cache \
  --config "$ROOT_DIR/configs/ucagent_track1_cache.yaml" \
  --backend codex \
  --exit-on-completion \
  --mcp-server-no-file-tools \
  --mcp-server-host 127.0.0.1 \
  --mcp-server-port "$MCP_PORT" \
  --force-stage-index "$STAGE_INDEX" \
  --no-embed-tools \
  -s
