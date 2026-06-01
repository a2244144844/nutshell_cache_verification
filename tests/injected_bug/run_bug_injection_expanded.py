#!/usr/bin/env python3
"""Run all bug injection scenarios (BUG-003 through BUG-006).

Each bug is run in both injected and recovery modes.  The exit code reflects
whether ALL injected scenarios detected their faults and ALL recovery paths
passed cleanly.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

INJECTED_DIR = Path(__file__).resolve().parent
BUGS = [
    "bug_003_address_corruption.py",
    "bug_004_dirty_bit_loss.py",
    "bug_005_refill_scramble.py",
    "bug_006_race_condition.py",
]


def main() -> int:
    python = sys.executable
    failures: list[str] = []
    recovery_failures: list[str] = []

    for bug_file in BUGS:
        bug_path = INJECTED_DIR / bug_file
        bug_name = bug_file.replace(".py", "")

        # Run injected mode — expected to FAIL (exit != 0)
        proc = subprocess.run(
            [python, str(bug_path)],
            capture_output=True, text=True, timeout=120,
        )
        if proc.returncode == 0:
            failures.append(f"{bug_name}: injected mode did NOT fail (expected detection)")
        else:
            print(f"[PASS] {bug_name}: injected mode detected fault", flush=True)
            print(f"       {proc.stderr.strip().splitlines()[-1][:120] if proc.stderr.strip() else proc.stdout.strip().splitlines()[-1][:120]}", flush=True)

        # Run recovery mode — expected to PASS (exit == 0)
        proc = subprocess.run(
            [python, str(bug_path), "--disable-bug"],
            capture_output=True, text=True, timeout=120,
        )
        if proc.returncode != 0:
            recovery_failures.append(f"{bug_name}: recovery mode failed (expected clean pass)")
        else:
            print(f"[PASS] {bug_name}: recovery mode clean", flush=True)

    print(flush=True)
    if failures:
        print(f"DETECTION FAILURES ({len(failures)}):", flush=True)
        for f in failures:
            print(f"  - {f}", flush=True)
    if recovery_failures:
        print(f"RECOVERY FAILURES ({len(recovery_failures)}):", flush=True)
        for f in recovery_failures:
            print(f"  - {f}", flush=True)

    if not failures and not recovery_failures:
        print("All BUG-003 through BUG-006: detection + recovery PASS", flush=True)
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
