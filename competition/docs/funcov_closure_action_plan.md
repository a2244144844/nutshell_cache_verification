# Functional Coverage Closure Action Plan

## Goal

Raise functional coverage from 57/91 (62%) to 87/91 (96%), closing all reachable points.

**Status: COMPLETED (2026-06-01)** — Final result: **91/91 points (100%), 98/98 bins (100%)**.

## Baseline (2026-06-01)

- Points: 57/91 (62%), Bins: 64/99 (64%)
- After excluding 4 tracker points (model-design issue): 57/87 (65.5%)
- Line: 100%, Branch: 100%, Expr: 100%, Toggle: 86.9%

## Completed Actions

### A1: Fix tracker group `_mark` return values ✅

**File**: `src/utils/toffee_coverage.py`
**Target**: 4 points → covered, +4 points
**Result**: All 4 tracker functions (`_capture_req`, `_capture_write`, `_track_write`, `_capture_probe_req`) modified to return True on successful capture. All 3 tracker groups at 100%.

### A2: Add probe × cache_state cross coverage tests ✅

**File**: `tests/directed/test_coherence_probe.py`
**Target**: 4 → 5 points covered
**Result**: 10 probe tests pass. 5/5 probe_x_cache_state bins covered after removing `probe_hit_empty` (physically unreachable) and fixing `_eval_probe_cross` for probe_miss semantics.

Tests added:
- `test_probe_hit_valid_state` — fill line, probe same addr → probe_hit (valid state)
- `test_probe_hit_dirty_state` — fill + dirty line, probe same addr → probe_hit (dirty state)
- `test_probe_miss_valid_state` — fill line A, probe line B → probe_miss (valid lines present)
- `test_probe_miss_dirty_state` — fill + dirty line A, probe line B → probe_miss (dirty lines present)

### A3: Expand write_hit_x_wmask coverage ✅

**File**: `tests/directed/test_write_hit_wmask.py`
**Target**: 22 → 48 points covered
**Result**: 44 tests covering all 48 wmask × offset combinations. All tests pass.

Two rounds of test additions:
- **Round 1** (original plan): 26 tests for byte(1,2,5,6,7), adjacent(1,2,3,6,7), low_half(1,2,3,4,7), high_half(1,2,3,4,5), sparse(2,3,4,5,6,7)
- **Round 2** (gap closure): 18 tests for byte(3,4), adjacent(0,4,5), low_half(0,5,6), high_half(0,6,7), full(2,3,4,6,7), sparse(0,1)

### A4: Remove physically unreachable bins ✅

**File**: `src/utils/toffee_coverage.py`
- Removed `miss_mmio` from `cache_miss_x_addr_type` — MMIO never causes a cache miss (MMIO bypasses cache)
- Removed `probe_hit_empty` from `cache_probe_x_cache_state` — probe cannot hit a line that was never filled

Also synced `src/utils/cache_coverage.py` EXPECTED_BINS.

### A5: Fix `_eval_probe_cross` semantics for probe_miss ✅

**File**: `src/utils/toffee_coverage.py`
**Change**: For probe_miss bins, check overall cache state (any dirty/valid lines present?) instead of the probed line's state (which is always empty for a miss). For probe_hit bins, continue checking the specific hit line's state.

## Execution Order (Historical)

| # | Item | Files | Points | Status |
|---|---|---|---|---|
| 1 | Fix tracker `_mark` return values | `src/utils/toffee_coverage.py` | +4 | Done |
| 2 | Add probe × cache_state tests | `tests/directed/test_coherence_probe.py` | +4 | Done |
| 3 | Directed write_hit_x_wmask combos (round 1) | `tests/directed/test_write_hit_wmask.py` | +15 | Done |
| 4 | Directed write_hit_x_wmask combos (round 2) | `tests/directed/test_write_hit_wmask.py` | +18 | Done |
| 5 | Remove unreachable bins + fix probe_miss model | `src/utils/toffee_coverage.py` | -2 bins | Done |
| 6 | Verify with collect_coverage.sh | `scripts/collect_coverage.sh 7 18` | — | Done |

## Final Result (2026-06-01)

| Metric | Before | After | Notes |
|---|---|---|---|
| Points | 57/91 (62%) | **91/91 (100%)** | All points covered |
| Bins | 64/99 (64%) | **98/98 (100%)** | All bins covered (2 unreachable removed) |
| Line | 1359/1359 (100%) | 1359/1359 (100%) | Unchanged |
| Branch | 471/471 (100%) | 471/471 (100%) | Unchanged |

### Per-Group Breakdown

| Group | Points | Bins | Status |
|---|---|---|---|
| `cache_addr_class` | 1/1 | 2/2 | covered |
| `cache_backpressure` | 2/2 | 2/2 | covered |
| `cache_clean_eviction` | 1/1 | 1/1 | covered |
| `cache_cmd_type` | 2/2 | 3/3 | covered |
| `cache_coherence_probe` | 1/1 | 2/2 | covered |
| `cache_flush` | 1/1 | 2/2 | covered |
| `cache_hit_miss` | 2/2 | 2/2 | covered |
| `cache_miss_x_addr_type` | 2/2 | 3/3 | covered |
| `cache_probe_tracker` | 1/1 | 1/1 | covered |
| `cache_probe_x_cache_state` | 5/5 | 5/5 | covered |
| `cache_refill_path` | 3/3 | 4/4 | covered |
| `cache_req_accepted` | 1/1 | 1/1 | covered |
| `cache_req_tracker` | 2/2 | 2/2 | covered |
| `cache_word_offset` | 8/8 | 8/8 | covered |
| `cache_write_hit_x_wmask` | 48/48 | 48/48 | covered |
| `cache_write_mask_class` | 7/7 | 7/7 | covered |
| `cache_write_miss` | 2/2 | 3/3 | covered |
| `cache_write_tracker` | 2/2 | 2/2 | covered |

## Files Modified

| File | Change |
|---|---|
| `src/utils/toffee_coverage.py` | Fix tracker return values, remove 2 unreachable bins, fix `_eval_probe_cross` for probe_miss |
| `src/utils/cache_coverage.py` | Sync `EXPECTED_BINS` with model changes |
| `tests/directed/test_coherence_probe.py` | Add probe_hit_valid, probe_hit_dirty, probe_miss_valid, probe_miss_dirty directed tests |
| `tests/directed/test_write_hit_wmask.py` | Add 18 missing wmask × offset combos (44 tests total, 48/48 bins covered) |

## Verification

```bash
source scripts/env.sh
bash scripts/collect_coverage.sh 7 18
# Result: 91/91 points (100%), 98/98 bins (100%)
# 86 passed in 42.81s
```
