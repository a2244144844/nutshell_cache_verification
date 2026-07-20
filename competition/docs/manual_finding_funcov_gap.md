# Manual Finding: Functional Coverage Gaps (2026-06-01)

## Discovery Context

After running `scripts/collect_coverage.sh 7 18`, the functional coverage report showed only **62% point coverage (57/91)**, significantly lower than expected. This was manually investigated by inspecting the aggregated Toffee coverage data.

**Resolution: COMPLETED (2026-06-01)** — All gaps closed. Final result: **91/91 points (100%), 98/98 bins (100%)**.

## Investigation Method

1. Ran `scripts/collect_coverage.sh 7 18` to regenerate coverage
2. Inspected `build/toffee_coverage_aggregated.json` for per-group/per-point breakdown
3. Cross-referenced `src/utils/toffee_coverage.py` for coverage model design
4. Identified root causes for each uncovered point

## Gap Summary (Before)

| Category | Uncovered Points | Root Cause |
|---|---|---|
| Tracker groups (model design) | 4 | Side-effect lambdas don't return bool, permanently "uncovered" |
| `cache_write_hit_x_wmask` | 26/48 | Random traffic covers only 22 of 48 wmask × offset combinations |
| `cache_probe_x_cache_state` | 4/6 | No tests for probes against valid/dirty cache lines |
| **Total** | **34/91** | |

## Detailed Findings

### 1. Tracker groups — model-level issue (4 points) ✅ RESOLVED

Three groups (`cache_req_tracker`, `cache_write_tracker`, `cache_probe_tracker`) used `_mark()` with lambdas that called state-capture functions (`_capture_req`, `_capture_write`, `_track_write`, `_capture_probe_req`). These functions performed side effects but **never returned True**, so the toffee marking system could never flag them as covered.

**Fix**: Added `return True` / `return False` to all four capture functions in `src/utils/toffee_coverage.py`.

### 2. cache_probe_x_cache_state — missing test stimulus + model issues ✅ RESOLVED

The coverage model defined cross-dimension bins (probe_hit/miss × empty/valid/dirty). Two issues found:

**Model issues fixed**:
- `probe_hit_empty` — physically unreachable (probe cannot hit an empty line). **Removed from model**.
- `probe_miss_*` — `_eval_probe_cross` checked the probed line's state, which for a miss is always empty. Fixed to check **overall cache state** (any dirty/valid lines present?).

**Tests added** (`tests/directed/test_coherence_probe.py`):
- `test_probe_hit_valid_state` — fill line, probe same addr → probe_hit (valid)
- `test_probe_hit_dirty_state` — fill + dirty line, probe same addr → probe_hit (dirty)
- `test_probe_miss_valid_state` — fill line A, probe line B → probe_miss with valid lines present
- `test_probe_miss_dirty_state` — fill + dirty line A, probe line B → probe_miss with dirty lines present

### 3. cache_write_hit_x_wmask — random coverage gaps ✅ RESOLVED

48 total combinations (6 wmask classes × 8 word offsets). All gaps closed via 44 directed tests in `tests/directed/test_write_hit_wmask.py`:

| Wmask Class | Covered Offsets |
|---|---|
| byte | 0, 1, 2, 3, 4, 5, 6, 7 |
| adjacent | 0, 1, 2, 3, 4, 5, 6, 7 |
| low_half | 0, 1, 2, 3, 4, 5, 6, 7 |
| high_half | 0, 1, 2, 3, 4, 5, 6, 7 |
| full | 0, 1, 2, 3, 4, 5, 6, 7 |
| sparse | 0, 1, 2, 3, 4, 5, 6, 7 |

### 4. cache_miss_x_addr_type — unreachable bin ✅ RESOLVED

`miss_mmio` bin removed from model: MMIO addresses never produce cache misses (MMIO bypasses cache entirely, routed through `io_mmio_req`).

## Resolution Summary

| Category | Status | Fix |
|---|---|---|
| 4 tracker points | ✅ Closed | Return True from capture functions |
| 4 probe × cache_state points | ✅ Closed | Fix `_eval_probe_cross` semantics + directed tests |
| 26 write_hit_x_wmask points | ✅ Closed | 44 directed tests for all 48 combos |
| 2 unreachable bins | ✅ Removed | `miss_mmio`, `probe_hit_empty` removed from model |

## Final Verification

```bash
source scripts/env.sh
bash scripts/collect_coverage.sh 7 18
# Result: 91/91 points (100%), 98/98 bins (100%)
# 18 groups all covered, 86 tests passed
```
