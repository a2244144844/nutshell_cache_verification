# Cache Bug Analysis

## Bug Summary

| Bug ID | Type | Detection |
| --- | --- | --- |
| `BUG-001` | Reference-model expected-data corruption | `CacheScoreboard.check_read_response()` detects data mismatch. |
| `BUG-RTL-001` | RTL dirty-writeback state-machine bypass | Dirty writeback directed test detects missing writeback request. |

## BUG-001: Reference Model Corruption

Injected fault:

```text
Reference-model read_word() flips bit 0 of expected refill data.
```

Trigger:

```sh
scripts/run_bug_injection.sh
```

Observed evidence:

```text
BUG-001 expected_data=0x1122334455667789, actual_data=0x1122334455667788
AssertionError: BUG-001 detected by scoreboard.check_read_response
```

Recovery:

```sh
scripts/run_bug_injection.sh --disable-bug
```

The recovery path exits cleanly and proves the failure is controlled by the injected fault.

## BUG-RTL-001: Dirty Writeback Bypass

Injected fault:

```text
CacheStage3 dirty-miss transition changed from:
  meta_dirty ? 4'h3 : 4'h1
to:
  4'h1
```

Effect:

- Dirty victim writeback state is skipped.
- Dirty victim data is silently dropped.
- Refill proceeds without the required `WRITE_BURST` / `WRITE_LAST` memory request.

Detection:

```text
tests/directed/test_dirty_writeback.py
```

Failure symptom:

```text
write_reqs is empty when the test expects at least one dirty writeback request.
```

Recovery:

- Restore the original RTL transition.
- Rebuild with `scripts/export_cache_dut.sh`.
- Rerun regression.

Latest clean regression:

```text
scripts/run_regression.sh -> 26 passed in 1.34s
```

## Bug Evidence Role

The bug analysis demonstrates two complementary detection modes:

- A Python-side reference/checker fault caught by the scoreboard.
- An RTL-side state-machine fault caught by a directed protocol/data-path test.

Both are excluded from the normal regression suite so the main verification flow remains clean.
