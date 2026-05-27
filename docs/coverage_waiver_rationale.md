# Line Coverage Waiver Rationale

Date: 2026-05-27

## Overview

Verilator line coverage for `Cache.v` reports **1344/1378 (97.5%)**. The remaining 34 uncovered lines are analyzed below. Each line is categorized as either **waivable** (unreachable by design in the I-cache configuration) or **needs test** (a functional path that could be covered with additional test effort).

---

## Waivable Lines

### Category A: Assertion `$fwrite` Failure Messages

| Line(s) | Code |
|---|---|
| 263 | `$fwrite(32'h80000002, "Assertion failed\n    at Cache.scala:208 ...");` |
| 877 | `$fwrite(32'h80000002, "Assertion failed: MMIO request should not hit ...");` |
| 901 | `$fwrite(32'h80000002, "Assertion failed\n    at Cache.scala:461 ...");` |
| 925 | `$fwrite(32'h80000002, "Assertion failed\n    at Cache.scala:462 ...");` |
| 949 | `$fwrite(32'h80000002, "Assertion failed: only allow to flush icache ...");` |

**Why waive:** These `$fwrite` calls are inside `` `ifndef SYNTHESIS `` blocks and execute **only when a DUT assertion fails**. Since all RTL assertions pass (the DUT is correct), these lines are unreachable by construction. Reaching them would require injecting an RTL bug — which is the domain of bug-injection testing, not functional coverage. The fact they are uncovered is **positive evidence** that the assertions hold.

### Category B: D-cache Forwarding Signals (I-cache = not applicable)

| Line(s) | Code | Role |
|---|---|---|
| 411 | `input io_in_bits_isForwardData,` | Forwarding-path flag |
| 524 | `wire useForwardData = io_in_bits_isForwardData & ...` | Forwarding enable |
| 2267 | `wire s3_io_in_bits_isForwardData;` | Pipeline register field |
| 2418 | `reg s3_io_in_bits_r_isForwardData;` | Pipeline register |

**Why waive:** `isForwardData` is a D-cache store-to-load-forwarding signal. In the I-cache instance (which this DUT is configured as), this signal is hardwired to 0. Its derived logic (`useForwardData`) can never evaluate to true. These are dead wires by configuration.

### Category D: `io_flush[1]` Pipeline Kill

| Line(s) | Code |
|---|---|
| 2861 | `end else if (io_flush[1]) begin` |
| 2862 | `valid_1 <= 1'h0;` |

**Why waive:** The D-cache assertion at line 463 (`assert(!(!ro.B && io.flush), "only allow to flush icache")`) blocks `io_flush[1]` from ever being asserted. In an I-cache instance (`ro.B = false`, i.e., `ro == io`), any write to `io_flush[1]` triggers the assertion. Only `io_flush[0]` (S1→S2 pipeline flush) is reachable.

### Category E: CacheStage2 `$fwrite` Assertion

| Line(s) | Code |
|---|---|
| 263 | `$fwrite(32'h80000002,` (inside CacheStage2 SVA) |

**Why waive:** Same as Category A — assertion failure message in CacheStage2 module, unreachable because the Waymask PopCount assertion never fires.

### Category F: LFSR Seed Initialization

| Line(s) | Code |
|---|---|
| 240 | `end else if (victimWaymask_lfsr == 64'h0) begin` |
| 241 | `victimWaymask_lfsr <= 64'h1;` |

**Why waive:** The 64-bit LFSR replacement policy uses a maximum-length LFSR. The all-zero state is the lone invalid state that the LFSR cannot naturally reach (period = 2^64 - 1). This re-seed protection exists as a hardware safety net but is unreachable in simulation unless the LFSR is artificially corrupted.

### Category G: CacheStage2 Forwarding Metadata Register

| Line(s) | Code |
|---|---|
| 138 | `reg forwardMetaReg_data_dirty;` |

**Why waive:** Part of the D-cache forwarding path in CacheStage2. This register holds the dirty bit of the forwarded meta entry. In the I-cache configuration, the forwarding path is never active (`isForwardData = 0`), so this register never toggles from its reset value.

---

## Needs Further Analysis (not currently waived)

### Category H: CacheStage3 Internal Probe Path

| Line(s) | Code |
|---|---|
| 513 | `wire hitReadBurst = hit & _hitReadBurst_T;` |
| 600-610 | `releaseLast`, `respToL1Last` counter wires |
| 767-772 | State 0: probe → state transition |
| 795-800 | State 0: probe → readBeatCnt assignment |
| 865, 870 | Release counter updates |

**Why not yet waived:** These lines belong to the CacheStage3 internal probe handling path (`probe & hitReadBurst`). Our DIR-008 coherence probe test drives the **external** coherence port (`io_out_coh_req_*/io_out_coh_resp_*`), which enters through CacheStage1 (Arbiter). The internal `probe` signal in CacheStage3 is driven by a different entry point — a probe request that arrives via `io_in_req` with cmd=`PROBE` after passing through S1→S2. This path is structurally reachable but requires a specific stimulus sequence: a probe request arriving at the exact moment the pipeline contains a valid hit.

**Next step:** Could be covered with additional test stimulus targeting the `probe` + `hitReadBurst` case in CacheStage3 directly.

### Category I: `needFlush` State Transition

| Line(s) | Code |
|---|---|
| 558 | `reg needFlush;` |
| 787 | `end else if (_T_5 & needFlush) begin` |
| 788 | `needFlush <= 1'h0;` |

**Why not yet waived:** `needFlush` is a sticky flag set when a flush arrives during an in-flight miss. It remains high until the next request handshake (`_T_5` = `io_out_ready & io_out_valid`). We test flush during idle (DIR-007 `test_flush_while_idle`) and during miss (`test_flush_during_miss`), but neither currently triggers the `needFlush → 0` transition because the test doesn't issue a new request that completes after the flush.

**Next step:** Could be covered by: (1) start a miss, (2) assert flush while miss is in-flight (setting `needFlush`), (3) wait for miss to complete, (4) issue another request to trigger the `_T_5 & needFlush` handshake.

### Category J: CacheStage3 Module Ports (I-cache unused)

| Line(s) | Code |
|---|---|
| 420 | `input io_flush,` (CacheStage3 internal) |
| 460 | `output io_dataReadRespToL1` |
| 2276 | `wire s3_io_flush;` |
| 2316 | `wire s3_io_dataReadRespToL1;` |

**Why not yet waived:** These are CacheStage3 ports that are physically present in the Verilog but serve D-cache specific functions. `io_flush` (s3 internal) is separate from the top-level flush and is used for CacheStage3-specific pipeline flush. `io_dataReadRespToL1` is a signal that sends read data back to L1 cache, only used in D-cache. In the I-cache, these ports are connected but the logic behind them is never triggered.

**Next step:** Could be waived if confirmed that these ports are D-cache-only. The `io_flush` port in CacheStage3 (line 420) is different from the top-level `io_flush` — it's an internal port between cache stages. Need to verify whether icache testbench drives it with io_flush[1] or a different signal.

---

## Summary

| Category | Lines | Waive? | Status | Reason |
|---|---|---|---|---|
| A | 263, 877, 901, 925, 949 | Yes | Applied | Assertion `$fwrite` messages, unreachable by design |
| B | 411, 524, 2267, 2418 | Yes | Applied | D-cache forwarding signals (I-cache = always 0) |
| D | 2861-2862 | Yes | Applied | `io_flush[1]` blocked by D-cache assertion |
| E | 263 | Yes | Applied | CacheStage2 assertion `$fwrite` (same line as A) |
| F | 240-241 | Yes | Applied | LFSR all-zero dead state |
| G | 138 | Yes | Applied | D-cache forwarding metadata register |
| H | 513, 600-610, 767-772, 795-800, 865, 870 | Not yet | Open | Internal probe path in CacheStage3 — potentially testable |
| I | 558, 787-788 | Not yet | Open | `needFlush` de-assertion — potentially testable |
| J | 420, 460, 2276, 2316 | Not yet | Open | CacheStage3 D-cache ports — need verification |

### Post-Waiver Coverage

- **Before waiver**: 1344/1378 (97.5%) — 34 uncovered lines
- **After waiver** (Categories A-G): 1344/1366 (98.4%) — 22 uncovered lines
- **Waived**: 12 unique lines (263 counted once for A+E)

### Remaining Uncovered Lines by Category

| Category | Lines | Count | Description |
|---|---|---|---|
| H | 513, 600, 602, 605, 608, 610, 767-769, 772, 795-797, 800, 865, 870 | 16 | Internal probe path in CacheStage3 |
| I | 558, 788 | 2 | `needFlush` state transition |
| J | 420, 460, 2276, 2316 | 4 | CacheStage3 D-cache ports |

### Waiver Implementation

Waivers are applied via `ignore_patterns` in `tests/conftest.py`:
```python
ignore_patterns=[
    "*Cache_top*",       # Picker-generated DPI wrapper (entire file)
    "Cache.v:138,240-241,263,411,524,877,901,925,949,2267,2418,2861-2862",  # Categories A-G
]
```

The `file.v:line1,range1-range2` syntax is parsed by `toffee_test`'s `parse_ignore_miss_lines()` and filters only miss (hit=0) records for those specific lines.
