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
make export
```

Then run the dirty-writeback test:

```sh
source scripts/env.sh && /Users/zzy/Workspace/ucagent/.venv/bin/python -m pytest tests/directed/test_dirty_writeback.py -v
```

Or run the full regression to see the blast radius:

```sh
make test
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

make export
make test
```

Recovery result: the restored RTL is covered by the latest clean regression, `scripts/run_regression.sh -> 37 passed`.

---

## Bug ID

`BUG-003`

## Injected Fault

Address corruption — flips bit 20 of every CPU request address before the DUT sees it. An `AddrCorruptingEnv` wrapper intercepts `drive_cpu_request()` and `send_cpu_request()` to modify the address transparently.

## Trigger

```sh
source scripts/env.sh && .venv/bin/python tests/injected_bug/bug_003_address_corruption.py
```

## Detection Path

After dirtying a line via write-hit, a conflicting address triggers eviction. The DUT issues a writeback with the corrupted address, but the scoreboard's `check_dirty_writeback_refill()` validates the writeback address against the original (uncorrupted) victim address — causing an assertion failure.

## Failure Evidence

```text
BUG-003 mode=enabled: flipping addr bit 20 on all CPU requests
AssertionError: BUG-003 detected: address corruption caused writeback
address mismatch (bit 20 flipped).
```

## Cleanup / Recovery

```sh
source scripts/env.sh && .venv/bin/python tests/injected_bug/bug_003_address_corruption.py --disable-bug
```

Recovery: `--disable-bug` uses the normal `CacheEnv` (no address corruption), writeback address matches scoreboard expectation. Exit 0.

---

## Bug ID

`BUG-004`

## Injected Fault

Dirty-bit loss — a corrupted reference model (`DirtyForgettingModel`) deliberately clears the dirty flag after `write_word()`. The model believes the line is clean, but the DUT correctly tracks it as dirty. On eviction, the DUT performs a writeback but the model expects a clean eviction.

## Trigger

```sh
source scripts/env.sh && .venv/bin/python tests/injected_bug/bug_004_dirty_bit_loss.py
```

## Detection Path

Fills 4 ways, dirties one line via write-hit (model forgets dirty), then accesses a 5th conflicting address. The DUT performs a dirty writeback, but the model expects clean eviction. The test detects the unexpected `WRITE_BURST`/`WRITE_LAST` in the memory request stream and raises `AssertionError`.

## Failure Evidence

```text
BUG-004 mode=enabled: reference model forgets dirty status after write
AssertionError: BUG-004 detected: DUT performed dirty writeback but
reference model (corrupted) expected clean eviction.
```

## Cleanup / Recovery

```sh
source scripts/env.sh && .venv/bin/python tests/injected_bug/bug_004_dirty_bit_loss.py --disable-bug
```

Recovery: `--disable-bug` uses the clean `ReferenceCacheModel` (dirty status preserved), scoreboard validates dirty writeback correctly. Exit 0.

---

## Bug ID

`BUG-005`

## Injected Fault

Refill order scramble — memory response beats are reversed before being sent to the DUT. The DUT expects critical-word-first order (beats starting from the requested word offset), so scrambled beats land data in wrong word positions.

## Trigger

```sh
source scripts/env.sh && .venv/bin/python tests/injected_bug/bug_005_refill_scramble.py
```

## Detection Path

A READ request with word offset 3 is sent. The refill beats are reversed (scrambled), causing data to land in wrong word positions. The DUT returns the word at the requested offset, but the data is wrong because the refill order was incorrect. `scoreboard.check_read_response()` detects the data mismatch.

## Failure Evidence

```text
BUG-005 mode=enabled: refill beats scrambled (reversed order)
BUG-005 expected_data=0x5000000000000003, actual_data=0x5000000000000004
AssertionError: BUG-005 detected by scoreboard.check_read_response:
scrambled refill order caused data mismatch.
```

## Cleanup / Recovery

```sh
source scripts/env.sh && .venv/bin/python tests/injected_bug/bug_005_refill_scramble.py --disable-bug
```

Recovery: `--disable-bug` sends beats in correct critical-word-first order, data matches reference model. Exit 0.

---

## Bug ID

`BUG-006`

## Injected Fault

Race condition — a CPU READ request and a coherence PROBE request are driven simultaneously in the same cycle. The internal arbiter must serialize the two requests. If one request is dropped or produces corrupted data, the test detects it.

## Trigger

```sh
source scripts/env.sh && .venv/bin/python tests/injected_bug/bug_006_race_condition.py
```

## Detection Path

A cache line is filled first. Then both `io_in_req_valid` (CPU READ to a different address) and `io_out_coh_req_valid` (PROBE to the filled line) are asserted together. The test steps cycle-by-cycle, monitoring both `io_in_resp_*` (CPU response) and `io_out_coh_resp_*` (probe response). If either response is missing after 300 cycles, the test raises `AssertionError` for request drop or deadlock.

## Failure Evidence

```text
BUG-006 mode=enabled: simultaneous CPU READ + coherence PROBE in same cycle
AssertionError: BUG-006 detected: CPU response never arrived —
race condition caused request drop or deadlock.
```

## Cleanup / Recovery

```sh
source scripts/env.sh && .venv/bin/python tests/injected_bug/bug_006_race_condition.py --disable-bug
```

Recovery: `--disable-bug` runs the CPU READ and PROBE sequentially (no race), both operations complete correctly. Exit 0.

---

## Bug Detection Summary

| Bug ID | Fault Type | Injection Method | Detection Mechanism | Detected? |
|--------|-----------|-----------------|-------------------|-----------|
| BUG-001 | Reference-model data corruption | Python model bit-flip in `read_word()` | `scoreboard.check_read_response()` | Yes |
| BUG-RTL-001 | RTL state-machine bypass | Modified `Cache.v:615` transition | `test_dirty_writeback.py` IndexError on empty write_reqs | Yes |
| BUG-003 | Address corruption | `AddrCorruptingEnv` flips addr bit 20 | `scoreboard.check_dirty_writeback_refill()` addr mismatch | Yes |
| BUG-004 | Dirty-bit loss | `DirtyForgettingModel` clears dirty after write | Unexpected writeback in mem request stream | Yes |
| BUG-005 | Refill order scramble | Reversed refill beat sequence | `scoreboard.check_read_response()` data mismatch | Yes |
| BUG-006 | CPU+probe race | Simultaneous io_in_req + io_out_coh_req | Response timeout / drop detection | Yes |
