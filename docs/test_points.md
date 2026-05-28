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
| `DIR-004` | Replacement into invalid ways | Implemented in `tests/directed/test_invalid_way_replacement.py`; fills 3 of 4 ways, verifies 4th conflict uses the invalid way (no writeback, original data preserved). |
| `DIR-005` | Dirty victim writeback | Implemented in `tests/directed/test_dirty_writeback.py`; fills a 4-way set, dirties the victim candidates, and checks writeback/refill sequencing on the fifth conflicting access. |
| `DIR-006` | MMIO bypass | Implemented in `tests/directed/test_mmio_bypass.py`; verifies read/write to MMIO addresses route through `io_mmio_*`, never generate memory requests, and never hit in cache. |
| `DIR-007` | Flush behavior | Implemented in `tests/directed/test_flush_behavior.py`; asserts `io_flush[0]` (S1-S2 pipeline flush) during idle and in-flight states, verifies `io_empty` and cache recovery. `io_flush[1]` is gated by a D-cache assertion (`ro.B=false`). |
| `DIR-008` | Coherence probe hit/miss | Implemented in `tests/directed/test_coherence_probe.py`; drives `io_out_coh_req_*` with PROBE cmd and validates `io_out_coh_resp_*` response (cmd=0xc hit, cmd=0x8 miss). |
| `DIR-009` | Response backpressure | Implemented in `tests/corner/test_backpressure.py`; deasserts `io_in_resp_ready` after the refill launches and verifies the CPU response stays valid until ready returns high. |
| `DIR-010` | Memory request backpressure | Implemented in `tests/corner/test_backpressure.py`; deasserts `io_out_mem_req_ready` long enough to prove the memory request stays asserted and stable until ready returns high. |
| `DIR-011` | Write miss (cold write) | Implemented in `tests/directed/test_write_miss.py`; verifies CPU WRITE to a cold address triggers READ_BURST refill, merges write data with refill data, and returns WRITE_RESP. Tests full-mask, partial-mask, and 8-beat refill scenarios. |
| `DIR-012` | Clean eviction (no writeback) | Implemented in `tests/directed/test_clean_eviction.py`; fills 4 clean ways in a set, accesses a 5th conflicting address, and verifies clean victim replacement without writeback. Second test validates per-word data integrity on surviving lines. |
| `DIR-013` | Write miss with dirty eviction | Implemented in `tests/directed/test_write_miss_dirty_eviction.py`; fills 4 ways, dirties each, then sends a WRITE to a 5th conflicting address. Verifies dirty victim writeback (WRITE_BURST/LAST) precedes refill (READ_BURST), and partial-mask write data is correctly merged into the refilled line. |
| `DIR-014` | Probe hit full release sequence | Implemented in `tests/directed/test_coherence_probe.py`; extends the probe hit test to wait for the full 8-beat release data sequence on `io_out_coh_resp_*`. Covers lines 767-769, 795-797 (probe in s_idle) and 598-602, 865 (releaseLast counter in s_release). |
| `DIR-015` | Read-burst hit | Implemented in `tests/directed/test_read_burst_hit.py`; fills a line with known word data, sends READ_BURST, and verifies the hit response returns correct data. Covers lines 513 (hitReadBurst), 605 (respToL1Fire), 608-610 (respToL1Last), 771-772 (s_release transition), 800 (readBeatCnt), and 870 (respToL1Last increment). |
| `DIR-016` | Flush-during-miss needFlush de-assertion | Implemented in `tests/directed/test_flush_behavior.py`; asserts flush during an in-flight miss to set needFlush, then issues a follow-up request to trigger the clear condition (_T_5 & needFlush). Covers lines 558 (needFlush register) and 788 (needFlush <= 0). |

Replay note:

On `2026-05-27`, DIR-011 through DIR-013 were replayed through the UCAgent channel and recorded in `docs/ucagent_output/write_miss_eviction_replay_stage.md`. The implementation notes above remain as the historical record of the original direct-agent work.

## GenSpec Plan Review Artifact

The planning-only UCAgent stage for the corrected GenSpec flow is `docs/ucagent_output/genspec_flow_plan_stage.md`.

Command result:

```text
No GenSpec workflow command was run in this planning stage.
Recommended next command:
ucagent genspec_workspace Cache --config genspec_workspace/genspec_cache.yaml -hm --tui --mcp-server-no-file-tools --no-embed-tools --guid-doc-path /Users/zzy/Workspace/ucagent/examples/GenSpec/SpecDoc/dut_spec_template.md
```

## Regression Result

```text
scripts/run_directed.sh -> 26 passed in 5.10s
scripts/run_regression.sh -> 30 passed in 5.43s
scripts/collect_coverage.sh 7 18 -> 30 passed, RTL line coverage 1359/1364 (99.6%)
```

UCAgent replay evidence:

```text
source scripts/env.sh && /Users/zzy/Workspace/ucagent/.venv/bin/python -m pytest tests/directed/test_write_miss.py tests/directed/test_clean_eviction.py tests/directed/test_write_miss_dirty_eviction.py -q -> 7 passed in 0.58s
scripts/run_regression.sh -> 26 passed in 1.13s
scripts/collect_coverage.sh 7 18 -> 27 passed, 16 warnings in 3.52s
```

## Random Coverage Bootstrap

Implemented in:

```text
tests/random/test_random_cache.py
src/generator/cache_random.py
src/utils/cache_coverage.py
src/utils/toffee_coverage.py
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
| `CRV-005` | Toffee functional coverage records probe, MMIO, flush, clean eviction, clean write miss, and dirty write miss bins. | Implemented |

Command results:

```text
scripts/collect_coverage.sh 7 18 -> 30 passed, RTL line coverage 1359/1364 (99.6%)
scripts/run_regression.sh -> 30 passed in 5.43s
```

## Coverage Status

Covered functional coverage groups now include:

- Request command: read, write, and probe.
- Hit/miss proxy and refill path.
- Write mask pattern: single byte, adjacent bytes, low/high half, full mask, and sparse mask.
- Address class: normal memory and MMIO.
- State path: hit, clean miss refill, dirty miss writeback then refill, clean write miss, dirty write miss, clean eviction, and MMIO.
- Backpressure location: CPU response and memory request.
- Flush timing: idle and after request accept.

Toffee coverage result:

```text
12 groups, 31 points, 37 bins -> 100% covered
```

## Line Coverage Status

Verilator RTL line coverage is collected via `-c` flag in Picker export. Results are available in:
- HTML (funcov + line): `build/reports/cache_coverage.html`
- LCOV HTML: `build/reports/line_dat/index.html`
- Markdown: `docs/coverage_report.md`

Current line coverage:

```text
1359/1364 lines (99.6%) — after waiving 16 unreachable lines and covering 15 previously-uncovered lines
```

### Waiver Summary

Waivers are applied via `ignore_patterns` in `tests/conftest.py` (see `docs/coverage_waiver_rationale.md` for full rationale):

| Category | Lines | Count | Description |
|---|---|---|---|
| A, E | 263, 877, 901, 925, 949 | 5 | Assertion `$fwrite` failure messages — unreachable by design |
| B, G | 138, 411, 524, 2267, 2418 | 5 | D-cache forwarding signals — I-cache = always 0 |
| D | 2861-2862 | 2 | `io_flush[1]` pipeline kill — blocked by D-cache assertion |
| F | 240-241 | 2 | LFSR all-zero dead state — unreachable without corruption |
| J | 420, 460, 2276, 2316 | 4 | CacheStage3 D-cache ports — structurally unreachable in I-cache configuration |
| **Waived subtotal** | | **16** | (line 263 counted once for A+E) |
| `*Cache_top*` | entire file | — | Picker-generated DPI wrapper (not DUT code) |

### Remaining Uncovered Lines (5 lines, after category J waiver and DIR-014/015/016 coverage)

| Category | Lines | Count | Description |
|---|---|---|---|
| J | 420, 460, 2276, 2316 (2 of 4 waived) | 2 | CacheStage3 D-cache ports partially waived; 2 lines covered by directed tests |
| Residual | TBD | 3 | Remaining uncovered lines subject to further analysis |

## UCAgent Replay Artifact

The supplemental replay artifact for DIR-011 through DIR-013 is `docs/ucagent_output/write_miss_eviction_replay_stage.md`.

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
| `BUG-RTL-001` | RTL-level dirty-writeback state-machine bypass (`Cache.v:615`); `test_dirty_writeback.py` detects missing `WRITE_BURST`. | Implemented |

Command results:

```text
tests/injected_bug/run_bug_injection.py -> exit 1
  BUG-001 mode=enabled: corrupting reference-model read_word() flips bit 0 at addr 0x80000000
  BUG-001 expected_data=0x1122334455667789, actual_data=0x1122334455667788
  AssertionError: BUG-001 detected by scoreboard.check_read_response: reference-model corruption made the expected read data 0x1122334455667789 while the DUT returned 0x1122334455667788 at addr 0x80000000
tests/injected_bug/run_bug_injection.py --disable-bug -> exit 0
  BUG-001 mode=disabled: clean reference-model read_word() at addr 0x80000000
  BUG-001 recovery path: bug injection disabled, scoreboard checks passed.
scripts/run_regression.sh -> 26 passed in 1.34s
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
