# Bug Tracking

Date: 2026-05-26

## Bug ID

`BUG-001`

## Injected Fault

Corrupted reference-model `read_word()` logic flips bit `0` of the expected 64-bit refill data.

## Trigger

Run:

```sh
source scripts/env.sh && /Users/zzy/Workspace/ucagent/.venv/bin/python tests/injected_bug/run_bug_injection.py
```

The harness reads `0x80000000`, refills it with `0x1122334455667788`, then compares the DUT response against the corrupted reference model result `0x1122334455667789`.

## Detection Path

`env.scoreboard.check_read_response()` rejects the mismatched read response.

## Failure Evidence

Observed command result:

```text
BUG-001 mode=enabled: corrupting reference-model read_word() flips bit 0 at addr 0x80000000
BUG-001 expected_data=0x1122334455667789, actual_data=0x1122334455667788
AssertionError: BUG-001 detected by scoreboard.check_read_response: reference-model corruption made the expected read data 0x1122334455667789 while the DUT returned 0x1122334455667788 at addr 0x80000000
```

Command exit status: `1`

## Cleanup / Recovery

Disable the injected fault with:

```sh
source scripts/env.sh && /Users/zzy/Workspace/ucagent/.venv/bin/python tests/injected_bug/run_bug_injection.py --disable-bug
```

Recovery command result:

```text
BUG-001 mode=disabled: clean reference-model read_word() at addr 0x80000000
BUG-001 expected_data=0x1122334455667788, actual_data=0x1122334455667788
BUG-001 recovery path: bug injection disabled, scoreboard checks passed.
```

Recovery command exit status: `0`

---

## Bug ID

`BUG-RTL-001`

## Injected Fault

RTL-level corruption in `CacheStage3` state-machine decision (`rtl/dut/Cache.v` line 615): changed the dirty-writeback state transition from conditional (`meta_dirty ? 4'h3 : 4'h1`) to unconditional refill (`4'h1`). This forces the cache to skip the dirty-writeback state (`4'h3`) and proceed directly to refill (`4'h1`) on every miss, silently dropping dirty victim data.

## Trigger

Rebuild with the modified RTL:

```sh
scripts/export_cache_dut.sh
```

Then run the dirty-writeback test:

```sh
source scripts/env.sh && /Users/zzy/Workspace/ucagent/.venv/bin/python -m pytest tests/directed/test_dirty_writeback.py -v
```

Or run the full regression to see the blast radius:

```sh
scripts/run_regression.sh
```

## Detection Path

`test_dirty_writeback.py` line 61 expects at least one `WRITE_BURST`/`WRITE_LAST` memory request in `write_reqs` after a set-conflict miss evicts a dirty line. With the RTL bug, the cache skips writeback entirely, so `write_reqs` is an empty list — accessing `write_reqs[0]` raises `IndexError`.

## Failure Evidence

```text
tests/directed/test_dirty_writeback.py::test_dirty_victim_writeback_refills_on_set_conflict FAILED

write_reqs = [req for req in mem_requests if req.cmd in {sb.WRITE_BURST, sb.WRITE_LAST}]
read_reqs = [req for req in mem_requests if req.cmd in {sb.READ_BURST, sb.READ_LAST}]
>   victim_data = write_reqs[0].wdata
                  ^^^^^^^^^^^^^
E   IndexError: list index out of range

tests/directed/test_dirty_writeback.py:61: IndexError
```

Regression result with the bug active: `1 failed, 6 passed in 0.10s` — only `test_dirty_writeback` failed; all other tests (smoke, word-offsets, write-masks, refill-beats, backpressure) passed because they do not exercise the dirty-eviction path.

## Cleanup / Recovery

Restore the original RTL line and rebuild:

```sh
# Cache.v line 615 restored from:
#   wire [3:0] _state_T_3 = 4'h1; // BUG
# to:
#   wire [3:0] _state_T_3 = meta_dirty ? 4'h3 : 4'h1;

scripts/export_cache_dut.sh
scripts/run_regression.sh
```

Recovery result: the restored RTL is covered by the latest clean regression, `scripts/run_regression.sh -> 26 passed in 1.34s`.
