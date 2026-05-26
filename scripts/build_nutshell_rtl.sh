#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

source "$SCRIPT_DIR/env.sh"

cd "$ROOT_DIR/upstream/NutShell"
mill -i generator.test.runMain top.TopMain --target-dir build/rtl BOARD=sim CORE=inorder --split-verilog
