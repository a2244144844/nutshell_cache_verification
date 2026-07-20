# Stage 20: First-Prize Gap Closure — P2 Items

Date: 2026-05-31 | Backend: Claude Code CLI | Source: `docs/gap_analysis_first_prize.md`

## Summary

Executed all 3 P2 items from the first-prize gap analysis: env.sh portability check (P2-11), cross-dimension coverage groups (P2-10), and requirements traceability matrix (P2-9). These add polish and documentation depth to the first-prize submission.

## Verification Gate

- `scripts/run_regression.sh` → **38 passed**
- `scripts/run_directed.sh` → **27 passed**
- All P2 changes are additive — no regressions

## Results

### P2-11: env.sh Portability Check

Added fail-fast existence guards for critical toolchain paths in `scripts/env.sh`:
- `PICKER_HOME`: hard error if missing (required for DUT build)
- `JAVA_HOME`: warning if missing (only needed for Chisel/Scala builds)

The paths are already portable (derived from `$ROOT_DIR`), so the fix is purely a fail-fast guard that provides clear diagnostic messages.

### P2-10: Cross-Dimension Coverage Groups

Added 3 cross-dimension functional coverage groups combining independent dimensions to prove multi-axis verification:

| Cross Group | Dimensions | Bins | Implementation |
|-------------|-----------|------|----------------|
| `cache_write_hit_x_wmask` | write_mask_class × word_offset | 48 (6 masks × 8 offsets) | `cache_coverage.py` + `toffee_coverage.py` |
| `cache_miss_x_addr_type` | hit_miss × addr_class (normal/mmio) | 4 | `cache_coverage.py` + `toffee_coverage.py` |
| `cache_probe_x_cache_state` | probe_hit/miss × cache state (empty/valid/dirty) | 6 | `cache_coverage.py` + `toffee_coverage.py` |

**Python-level** (`cache_coverage.py`): Extended `EXPECTED_BINS` with 3 cross-dimension bin sets and updated `record()` to compute `write_hit_x_wmask`, `miss_x_addr_type`, and `probe_x_cache_state` bins automatically. Uses `_line_dirty` dict for probe state tracking.

**Toffee-level** (`toffee_coverage.py`): Added 3 cross-dimension `CovGroup`s (`cache_write_hit_x_wmask`, `cache_miss_x_addr_type`, `cache_probe_x_cache_state`) plus 3 tracker groups (`cache_req_tracker`, `cache_write_tracker`, `cache_probe_tracker`). State-tracking helpers (`_capture_req`, `_capture_write`, `_capture_probe_req`, `_eval_probe_cross`) capture DUT pin state across cycles to evaluate cross-dimension conditions. Consolidated wmask classification into `@staticmethod _classify_wmask`.

Total functional coverage: 12 → 15 groups, 31 → 58+ points, 37 → 95 bins.

**Key technical challenge**: The DUT's `io_out_coh_resp_bits` has only `cmd` and `rdata` pins — no `addr`. Probe address must be captured from `io_out_coh_req_bits_addr` (request side) via `_capture_probe_req` and stored in `_last_probe_addr` for use in `_eval_probe_cross`.

### P2-9: Requirements Traceability Matrix (RTM)

Created `docs/requirements_traceability_matrix.md` mapping every verification requirement to its test, coverage group, and status:

| Section | Requirements | Coverage |
|---------|-------------|----------|
| Core Cache | SMK-002~007 | `refill_path` + `cmd_type` groups |
| Write Mask & Word Offset | DIR-001~002 | `write_mask_class` + `word_offset` groups |
| Refill & Replacement | DIR-003~005, DIR-011~013, DIR-020 | `refill_path` all 6 bins |
| MMIO & Flush | DIR-006~007, DIR-016~017 | `addr_class.mmio` + `flush_timing` |
| Coherence Probe | DIR-008, DIR-014, DIR-021 | `probe_result` |
| Backpressure | DIR-009~010 | `backpressure_loc` |
| Read Burst & Prefetch | DIR-015, DIR-018~019, DIR-022 | (structural coverage) |
| Random Verification | CRV-001~005 | All 37→95 bins |
| Bug Injection | BUG-001, BUG-RTL-001, BUG-003~006 | 7 bugs with --disable-bug |
| Coverage Waivers | Categories A~O + T-A~T-F | 48 lines + 3,280 toggle |

Includes final coverage summary (Line 100%, Branch 100%, Expr 100%, Toggle 88.4%, Funcov 100%) and test execution summary (6 suites, ~60s full reproduce).

## Files Changed

| File | Change |
|------|--------|
| `scripts/env.sh` | P2-11: added PICKER_HOME/JAVA_HOME existence checks |
| `src/utils/cache_coverage.py` | P2-10: added 3 cross-dimension bin sets (58 bins) to EXPECTED_BINS + recording logic |
| `src/utils/toffee_coverage.py` | P2-10: added 3 cross-dimension CovGroups + 3 tracker groups with state-tracking helpers |
| `docs/requirements_traceability_matrix.md` | P2-9: created RTM (10 requirement sections, all tests + coverage groups + waiver categories) |
| `docs/test_points.md` | Added Stage 20 section with cross-dim coverage + RTM + env.sh entries |
| `docs/ai_collaboration_report.md` | Added Stage 20 entry for P2-9/10/11 |

## Scoring Impact

| Dimension | Before (after P1) | After (P0+P1+P2) | Delta |
|-----------|-------------------|-------------------|-------|
| 覆盖率达标 (15pts) | 13-15 | 14-15 | +1 |
| 工程规范 (20pts) | 18-20 | 19-20 | +1 |
| **Total (100pts)** | **88-99** | **90-100** | **+2** |
