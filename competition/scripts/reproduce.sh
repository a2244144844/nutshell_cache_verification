#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$ROOT_DIR"

echo "[reproduce] 1/4 normal regression"
"$SCRIPT_DIR/run_regression.sh"

echo "[reproduce] 2/4 coverage collection"
"$SCRIPT_DIR/collect_coverage.sh" "${CACHE_RANDOM_SEED:-7}" "${CACHE_RANDOM_STEPS:-18}"

echo "[reproduce] 3/4 bug injection expected failure"
set +e
"$SCRIPT_DIR/run_bug_injection.sh"
bug_status=$?
set -e
if [ "$bug_status" -eq 0 ]; then
  echo "[reproduce] ERROR: bug injection unexpectedly passed" >&2
  exit 1
fi
echo "[reproduce] observed expected bug-injection failure: exit $bug_status"

echo "[reproduce] 4/4 bug injection recovery path"
"$SCRIPT_DIR/run_bug_injection.sh" --disable-bug

echo "[reproduce] PASS"
