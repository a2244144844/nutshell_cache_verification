# Test Points

Date: 2026-05-26

This document lists the first verification targets for the selected Cache DUT.

## Implemented Smoke Points

Implemented in:

```text
tests/smoke/test_cache_basic.py
```

Environment modules used by the smoke:

```text
src/env/cache_env.py
src/monitor/cache_monitor.py
src/scoreboard/cache_scoreboard.py
src/utils/simplebus.py
```

Runnable with:

```sh
competition/track1_nutshell_cache/scripts/run_smoke.sh
```

Current checks:

| ID | Point | Status |
| --- | --- | --- |
| `SMK-001` | Reset releases and Cache becomes request-ready. | Implemented |
| `SMK-002` | First normal read to a cold line misses and emits a memory `READ_BURST`. | Implemented |
| `SMK-003` | Memory `READ_LAST` response refills the line and returns CPU `READ_LAST`. | Implemented |
| `SMK-004` | User metadata is preserved from request to response. | Implemented |
| `SMK-005` | Second read to the same address hits and emits no memory request. | Implemented |
| `SMK-006` | Full-mask write hit returns `WRITE_RESP`. | Implemented |
| `SMK-007` | Read-after-write hit returns the updated data. | Implemented |

## Next Directed Points

| ID | Point | Goal |
| --- | --- | --- |
| `DIR-001` | Byte/half/word write masks | Implemented in `tests/directed/test_write_masks.py`; checks partial updates inside a 64-bit word. |
| `DIR-002` | Different word offsets in the same line | Implemented in `tests/directed/test_word_offsets.py`; checks independent hit writes/reads for `addr[5:3]`. |
| `DIR-003` | Refill with multiple beats | Implemented in `tests/directed/test_refill_beats.py`; checks 8-beat refill order from a nonzero word offset. |
| `DIR-004` | Replacement into invalid ways | Confirm invalid way is preferred before random victim replacement. |
| `DIR-005` | Dirty victim writeback | Implemented in `tests/directed/test_dirty_writeback.py`; fills a 4-way set, dirties the victim candidates, and checks writeback/refill sequencing on the fifth conflicting access. |
| `DIR-006` | MMIO bypass | Use an MMIO address and verify request routes through `io_mmio_*`. |
| `DIR-007` | Flush behavior | Assert `io_flush` during in-flight or idle states and check recovery. |
| `DIR-008` | Coherence probe hit/miss | Drive `io_out_coh_req_*` and validate probe response. |
| `DIR-009` | Response backpressure | Implemented in `tests/corner/test_backpressure.py`; deasserts `io_in_resp_ready` after the refill launches and verifies the CPU response stays valid until ready returns high. |
| `DIR-010` | Memory request backpressure | Implemented in `tests/corner/test_backpressure.py`; deasserts `io_out_mem_req_ready` long enough to prove the memory request stays asserted and stable until ready returns high. |

## Regression Result

```text
scripts/run_regression.sh -> 7 passed in 0.14s
```

## Random Coverage Bootstrap

Implemented in:

```text
tests/random/test_random_cache.py
src/generator/cache_random.py
src/utils/cache_coverage.py
```

Runnable with:

```sh
competition/track1_nutshell_cache/scripts/collect_coverage.sh
competition/track1_nutshell_cache/scripts/run_random.sh
```

Current checks:

| ID | Point | Status |
| --- | --- | --- |
| `CRV-001` | Constrained random read/write traffic uses legal cache-line addresses and deterministic seed control. | Implemented |
| `CRV-002` | Random regression checks reads and writes against the reference model with write-mask handling. | Implemented |
| `CRV-003` | Functional coverage records command type, hit/miss proxy, write-mask class, word offset, and refill path. | Implemented |
| `CRV-004` | Coverage bootstrap now records the dirty miss/writeback/refill path through the closure stage. | Implemented |

Command results:

```text
scripts/collect_coverage.sh 7 18 -> 1 passed in 0.04s
scripts/run_regression.sh -> 7 passed in 0.14s
```

## Coverage Candidates

Functional coverage bins to add after the basic environment exists:

- Request command: read, write, read burst, write burst/write last, probe.
- Hit/miss result.
- Waymask selected: way 0, way 1, way 2, way 3.
- Write mask pattern: single byte, adjacent bytes, low/high word, full mask.
- Address class: normal memory, MMIO.
- State path: hit, clean miss refill, dirty miss writeback then refill, MMIO.
- Backpressure location: CPU response, memory request, memory response.
- Flush timing: idle, after request accept, during miss handling.

## Bug Injection Evidence

Implemented in:

```text
tests/injected_bug/run_bug_injection.py
docs/bug_tracking.md
```

Runnable with:

```sh
competition/track1_nutshell_cache/scripts/run_bug_injection.sh
competition/track1_nutshell_cache/scripts/run_bug_injection.sh --disable-bug
```

Current checks:

| ID | Point | Status |
| --- | --- | --- |
| `BUG-001` | Corrupted reference-model expected data is detected by `CacheScoreboard.check_read_response()`. | Implemented |

Command results:

```text
tests/injected_bug/run_bug_injection.py -> exit 1
  BUG-001 mode=enabled: corrupting reference-model read_word() flips bit 0 at addr 0x80000000
  BUG-001 expected_data=0x1122334455667789, actual_data=0x1122334455667788
  AssertionError: BUG-001 detected by scoreboard.check_read_response: reference-model corruption made the expected read data 0x1122334455667789 while the DUT returned 0x1122334455667788 at addr 0x80000000
tests/injected_bug/run_bug_injection.py --disable-bug -> exit 0
  BUG-001 mode=disabled: clean reference-model read_word() at addr 0x80000000
  BUG-001 recovery path: bug injection disabled, scoreboard checks passed.
scripts/run_regression.sh -> 7 passed in 0.14s
```

## Reproducibility Entry

Runnable with:

```sh
competition/track1_nutshell_cache/scripts/reproduce.sh
```

Current one-command result:

```text
scripts/clean_generated.sh && scripts/reproduce.sh -> PASS
```

## Directed Test Commands

Run only directed tests:

```sh
competition/track1_nutshell_cache/scripts/run_directed.sh
```

Run smoke plus directed tests:

```sh
competition/track1_nutshell_cache/scripts/run_regression.sh
```
