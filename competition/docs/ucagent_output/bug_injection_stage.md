# Bug Injection Stage Output

Date: 2026-05-26

## Changed Files

- `tests/injected_bug/run_bug_injection.py`
- `docs/bug_tracking.md`
- `docs/test_points.md`
- `docs/ai_collaboration_report.md`
- `docs/verification_plan.md`
- `docs/ucagent_operation_plan.md`
- `README.md`
- `top.md`

## Commands Run

```sh
source scripts/env.sh && /Users/zzy/Workspace/ucagent/.venv/bin/python tests/injected_bug/run_bug_injection.py
source scripts/env.sh && /Users/zzy/Workspace/ucagent/.venv/bin/python tests/injected_bug/run_bug_injection.py --disable-bug
scripts/run_regression.sh
```

## Exact Results

- `tests/injected_bug/run_bug_injection.py` exited with code `1`.
- The failure was intentionally triggered by a corrupted reference-model expected value and was detected by `CacheScoreboard.check_read_response()`.
- Failure evidence:

  ```text
  BUG-001 mode=enabled: corrupting reference-model read_word() flips bit 0 at addr 0x80000000
  BUG-001 expected_data=0x1122334455667789, actual_data=0x1122334455667788
  AssertionError: BUG-001 detected by scoreboard.check_read_response: reference-model corruption made the expected read data 0x1122334455667789 while the DUT returned 0x1122334455667788 at addr 0x80000000
  ```

- `tests/injected_bug/run_bug_injection.py --disable-bug` exited with code `0`.
- Recovery evidence:

  ```text
  BUG-001 mode=disabled: clean reference-model read_word() at addr 0x80000000
  BUG-001 expected_data=0x1122334455667788, actual_data=0x1122334455667788
  BUG-001 recovery path: bug injection disabled, scoreboard checks passed.
  ```

- `scripts/run_regression.sh` passed with `7 passed in 0.14s` on the latest local recheck after output wording cleanup.

## Remaining Risks

- The injected fault is reference-model-only, so it validates detection wiring and reporting rather than a live RTL mutation.
- The harness currently covers a single controlled mismatch; additional injected bugs could expand coverage of other scoreboard and monitor paths.
- The direct regression remains clean, but the bug harness must stay outside `scripts/run_regression.sh` so the main suite does not inherit the intentional failure mode.
