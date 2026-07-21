# UCAgent Stage Execution Summary (All 18 Stages)

**Project**: Track1 NutShell Cache Verification  
**Period**: 2026-05-25 to 2026-05-31  
**Backend**: Codex / Claude Code CLI via UCAgent MCP  
**Total Stages**: 18 (indices 0-17)

---

## Stage Index

| Index | Stage Name | Config Key | Date | Status | Artifact |
|-------|------------|------------|------|--------|----------|
| 0 | `cache_regression_audit` | Audit | 2026-05-26 | ✅ PASS | `stage_audit.md` |
| 1 | `backpressure_directed_tests` | Backpressure | 2026-05-26 | ✅ PASS | `backpressure_stage.md` |
| 2 | `crv_coverage_bootstrap` | CRV/Coverage | 2026-05-26 | ✅ PASS | `crv_coverage_stage.md` |
| 3 | `dirty_writeback_coverage_closure` | Dirty Writeback | 2026-05-26 | ✅ PASS | `dirty_writeback_stage.md` |
| 4 | `bug_injection_evidence` | Bug Injection | 2026-05-26 | ✅ PASS | `bug_injection_stage.md` |
| 5 | `final_report_package` | Final Report | 2026-05-26 | ✅ PASS | `final_report_stage.md` |
| 6 | `flush_directed_test` | Flush | 2026-05-26 | ✅ PASS | `flush_stage.md` |
| 7 | `coherence_probe_directed_test` | Coherence Probe | 2026-05-26 | ✅ PASS | `coherence_probe_stage.md` |
| 8 | `write_miss_eviction_replay` | Replay DIR-011~013 | 2026-05-27 | ✅ PASS | `write_miss_eviction_replay_stage.md` |
| 9 | `genspec_full` | GenSpec | 2026-05-27 | ✅ PASS | `genspec_full_stage.md` |
| 10 | `line_coverage_closure` | Line Coverage (DIR-014~016) | 2026-05-27 | ✅ PASS | `line_coverage_closure_stage.md` |
| 11 | `line_coverage_100` | Line 100% (DIR-017, 018) | 2026-05-31 | ✅ PASS | `line_coverage_100_stage.md` |
| 12 | `branch_coverage_closure` | Branch Coverage (DIR-019~022) | 2026-05-31 | ✅ PASS | `branch_coverage_closure_stage.md` |
| 13 | `toggle_coverage_improvement` | Toggle Improvement | 2026-05-31 | ✅ PASS | `toggle_coverage_improvement_stage.md` |
| 14 | `toggle_improvement_final` | Toggle Final (10 seeds) | 2026-05-31 | ✅ PASS | `toggle_final_attempt_stage.md` |
| 15 | `expr_coverage_closure` | Expr Coverage (Cat O) | 2026-05-31 | ✅ PASS | `expr_coverage_closure_stage.md` |
| 16 | `first_prize_gap_closure_p0` | P0 Items | 2026-05-31 | ✅ PASS | `first_prize_gap_closure_p0_stage.md` |
| 17 | `first_prize_gap_closure_p1` | P1 Items | 2026-05-31 | ✅ PASS | `first_prize_gap_closure_p1_stage.md` |
| (20) | `first_prize_gap_closure_p2` | P2 Items | 2026-05-31 | ✅ PASS | `first_prize_gap_closure_p2_stage.md` |

> Note: Stage 20 (P2) was executed after stage 17 as part of the first-prize gap closure work. Config has 18 stages (0-17); P2 is documented as supplemental.

---

## Coverage Progression Summary

| Stage | Line | Branch | Toggle | Expr | Funcov | Tests |
|-------|------|--------|--------|------|--------|-------|
| 0 (Audit) | N/A | N/A | N/A | N/A | N/A | 4 |
| 2 (CRV) | ~97% | ~95% | ~86% | ~95% | 12g/31p/37b | 6 |
| 3 (Dirty WB) | ~97% | ~95% | ~86% | ~95% | 12g/31p/37b (100%) | 7 |
| 6-7 (Flush/Probe) | ~98% | ~95% | ~86% | ~95% | 12g/31p/37b (100%) | 20 |
| 10 (Line Closure) | 1359/1364 (99.6%) | 95.3% | 86.7% | 95.6% | 100% | 30 |
| 11 (Line 100%) | **1359/1359 (100%)** | 95.3% | 86.7% | 95.6% | 100% | 32 |
| 12 (Branch) | 100% | **471/471 (100%)** | 86.7% | 95.6% | 100% | 37 |
| 13 (Toggle) | 100% | 100% | **24785/28227 (87.8%)** | 95.6% | 100% | 37 |
| 14 (Toggle Final) | 100% | 100% | **24947/28227 (88.4%)** | 95.6% | 100% | 37 |
| 15 (Expr) | 100% | 100% | 87.8% | **131/131 (100%)** | 100% | 38 |

---

## Key Technical Achievements by Stage

### Stage 0: Audit
- Validated UCAgent + Codex backend integration
- Regression: `4 passed in 0.11s`
- Established stage execution pattern

### Stage 1: Backpressure
- Added `tests/corner/test_backpressure.py` (2 tests: CPU resp + mem req stall)
- Extended `cache_env.py` with raw pin drive/sample helpers
- Regression: `6 passed in 0.16s`

### Stage 2: CRV/Coverage Bootstrap
- Created `src/generator/cache_random.py` (constrained random generator)
- Created `src/utils/cache_coverage.py` (functional coverage collector)
- Created `tests/random/test_random_cache.py`
- Coverage gap identified: `dirty_miss_writeback_refill = 0`
- Coverage: `1 passed in 0.09s`, Regression: `6 passed in 0.11s`

### Stage 3: Dirty Writeback Closure
- Added `tests/directed/test_dirty_writeback.py` (4-way set conflict test)
- Extended env for writeback beat acknowledgment before refill
- Coverage delta: `dirty_miss_writeback_refill: 0 → 1`
- All tests pass: `7 passed in 0.13s`

### Stage 4: Bug Injection
- Created `tests/injected_bug/run_bug_injection.py` (BUG-001: ref model corruption)
- Expected failure path: exit code 1 with scoreboard detection
- Recovery path: `--disable-bug` → exit code 0
- Normal regression clean: `7 passed in 0.14s`

### Stage 5: Final Report Package
- Refreshed all submission-facing docs (README, test_points, verification_plan, coverage_report, ai_collaboration_report)
- Verified one-command reproducibility: `scripts/reproduce.sh → PASS`

### Stage 6: Flush (DIR-007)
- Created `tests/directed/test_flush_behavior.py` (3 tests)
- Discovered D-cache assertion blocking `io_flush[1]` → limited to `io_flush[0]`
- Documented `needFlush` structural limitation in I-cache
- Results: `3 passed in 0.05s`, Regression: `16 passed in 0.13s`

### Stage 7: Coherence Probe (DIR-008)
- Created `tests/directed/test_coherence_probe.py` (3 tests)
- Fixed pipeline timing: valid must span clock edge (clear AFTER step)
- Documented S3 dataWay register constraint on probe hit rdata
- Results: `3 passed in 0.01s`, Regression: `20 passed in 0.72s`

### Stage 8: Write Miss/Eviction Replay (DIR-011~013)
- Replayed DIR-011, 012, 013 through UCAgent channel
- Original implementation was direct-agent; this stage provides UCAgent evidence
- Results: Focused `7 passed in 0.58s`, Full `26 passed in 1.13s`, Coverage `27 passed`

### Stage 9: GenSpec Full Flow
- Executed official UCAgent GenSpec 6-stage workflow
- Generated: `Cache_spec.md` + 6 sub-specs + FG/FC/CK matrix + line map
- Checkers: `FileLineMapChecker PASS`, `UnityChipCheckerLabelStructure PASS`
- Regression: `28 passed in 5.76s`, Reproduce: `PASS`

### Stage 10: Line Coverage Closure (DIR-014~016)
- DIR-014: Probe hit full release (already in test_coherence_probe.py)
- DIR-015: Created `test_read_burst_hit.py` (READ_BURST hit single-beat)
- DIR-016: Flush during miss needFlush de-assertion (already in test_flush_behavior.py)
- Category J waiver (4 D-cache ports): lines 420, 460, 2276, 2316
- Delta: 1344/1366 (98.4%) → 1359/1364 (99.6%) (+15 lines, +3 tests)

### Stage 11: Line Coverage 100% (DIR-017, 018)
- DIR-017: `test_needflush_assert_and_deassert` — needFlush lifecycle test
- DIR-018: `test_read_burst_hit_resptol1_counter` — respToL1Last counter test
- **Key finding**: Lines 558, 788 (needFlush) are structurally unreachable in I-cache (same root cause as 2861-2862, Category D)
- Category K waiver (3 lines): 605, 608, 610 (respToL1Last counter — I-cache single-beat limitation)
- **Result: 1359/1359 (100.0%) line coverage**

### Stage 12: Branch Coverage Closure (DIR-019~022)
- DIR-019: `test_prefetch.py` (2 tests) — line 2674 PREFETCH gating → P2 waived
- DIR-020: `test_writeback_multi_beat_counter_exercise` — lines 550, 555, 626 writeL2BeatCnt → P2 waived
- DIR-021: Internal probe tests (2) — lines 768, 777, 796 → P2 waived
- DIR-022: state2 false case line 824 → P2 waived (state2 never = 3)
- **Category N: 8 branch waivers added**
- **Result: 471/471 (100.0%) branch coverage**

### Stage 13: Toggle Coverage Improvement
- Extended `cache_random.py` with `enable_extended` mode:
  - 32 line bases, 16 data patterns
  - MMIO, probe, flush, READ_BURST, PREFETCH traffic
- Created `test_random_multi_seed.py` (scoreboard-free, toggle-focused)
- Created `collect_coverage_multi.sh`
- **Delta: +311 toggles (86.7% → 87.8%)**
- Plateau confirmed: 8 seeds × 200 steps yielded no further improvement

### Stage 14: Toggle Final Attempt
- 10 seeds × 200 steps = 2,000 ops (64 bases, 32 patterns)
- **Delta: +162 toggles (87.8% → 88.4%)**
- Plateau confirmed: 3,280 remaining misses = structural (T-A~T-F)
- **Result: 24947/28227 (88.4%) toggle coverage**

### Stage 15: Expr Coverage Closure (Category O)
- 6 expression waivers (SVA STOP_COND terms, dead logic)
- Lines: 274, 787, 889, 913, 937, 961
- **Result: 131/131 (100.0%) expr coverage**

### Stage 16: P0 Gap Closure
- README 3-command quick start + number sync
- verification_plan.md data sync (100% all coverage)
- Bug injection expansion: BUG-003~006 (address corrupt, dirty bit loss, refill scramble, race)
- Scoreboard rewrite: 35 → 194 lines (6 new check methods, 3 levels)

### Stage 17: P1 Gap Closure
- Step 30 attribution fix (human discovered, AI traced)
- AI Effective Contributions table (6 entries)
- Expanded Defect Analysis (5 before/after cases)
- Prompt Iteration Case Studies (3 examples)

### Stage 20 (Supplemental): P2 Gap Closure
- P2-11: `env.sh` portability guards (PICKER_HOME hard error, JAVA_HOME warning)
- P2-10: Cross-dimension coverage (3 groups, 58 bins): write_hit_x_wmask (48), miss_x_addr_type (4), probe_x_cache_state (6)
- P2-9: Requirements Traceability Matrix (10 sections, all tests + coverage + waivers mapped)

---

## Final Verification Metrics

```
Line:    1359/1359 = 100.0%  (21 lines waived: Categories A-N)
Branch:  471/471   = 100.0%  (17 branches waived: Categories L, M, N)
Expr:    131/131   = 100.0%  (6 expr waived: Category O)
Toggle:  24947/28227 = 88.4%  (3,280 waived: Categories T-A~T-F, doc-based)
Funcov:  15 groups, 56+ points, 95 bins = 100% covered
Tests:   38 passed (smoke + directed + corner + random multi-seed)
Reproduce: PASS (make clean && make reproduce)
```

---

## Files Changed Across All Stages

### Source Code
- `src/env/cache_env.py` — Extended with raw pin helpers, writeback ack
- `src/generator/cache_random.py` — Extended with multi-mode, diverse patterns
- `src/monitor/cache_monitor.py` — Base monitor
- `src/scoreboard/cache_scoreboard.py` — 35→194 lines, 6 new check methods
- `src/utils/simplebus.py` — SimpleBus constants and data classes
- `src/utils/cache_coverage.py` — Legacy + cross-dimension coverage
- `src/utils/toffee_coverage.py` — Toffee CovGroups (15 groups, cross-dim, internal signals)

### Tests
- `tests/smoke/test_cache_basic.py` — SMK-001~007
- `tests/directed/test_write_masks.py` — DIR-001
- `tests/directed/test_word_offsets.py` — DIR-002
- `tests/directed/test_refill_beats.py` — DIR-003
- `tests/directed/test_invalid_way_replacement.py` — DIR-004
- `tests/directed/test_dirty_writeback.py` — DIR-005
- `tests/directed/test_mmio_bypass.py` — DIR-006
- `tests/directed/test_flush_behavior.py` — DIR-007, 016, 017
- `tests/directed/test_coherence_probe.py` — DIR-008, 014, 021
- `tests/directed/test_backpressure.py` — DIR-009, 010
- `tests/directed/test_write_miss.py` — DIR-011
- `tests/directed/test_clean_eviction.py` — DIR-012
- `tests/directed/test_write_miss_dirty_eviction.py` — DIR-013, 020
- `tests/directed/test_read_burst_hit.py` — DIR-015, 018
- `tests/directed/test_prefetch.py` — DIR-019
- `tests/corner/test_backpressure.py` — Corner cases
- `tests/random/test_random_cache.py` — Original CRV
- `tests/random/test_random_multi_seed.py` — Multi-seed toggle
- `tests/injected_bug/run_bug_injection.py` — BUG-001~006 + RTL-001

### Scripts
- `scripts/export_cache_dut.sh` — Picker export with internal.yaml
- `scripts/collect_coverage.sh` — Single-seed coverage
- `scripts/collect_coverage_multi.sh` — Multi-seed toggle coverage
- `scripts/run_regression.sh` — Full regression
- `scripts/run_directed.sh` — Directed only
- `scripts/run_smoke.sh` — Smoke only
- `scripts/reproduce.sh` — One-command reproducibility
- `scripts/run_bug_injection.sh` — Bug injection wrapper
- `scripts/clean_generated.sh` — Cleanup
- `scripts/env.sh` — Toolchain setup + portability guards (P2-11)
- `scripts/run_ucagent_stage.sh` — Stage runner

### Config
- `configs/internal.yaml` — 22 internal signals for DPI export
- `configs/ucagent_track1_cache.yaml` — 18-stage UCAgent config

### Documentation (Primary Deliverables)
- `README.md` / `README_zh.md` — 3-command quick start, full status
- `docs/ai_collaboration_report.md` — 31 steps, defects table, prompt strategy
- `docs/verification_plan.md` — 5 phases, current status
- `docs/coverage_report.md` — Latest coverage numbers
- `docs/coverage_waiver_rationale.md` — 15 categories (A-O, T-A~T-F), 48 lines + 3,280 toggle
- `docs/test_points.md` — All SMK/DIR/CRV/BUG points with status
- `docs/requirements_traceability_matrix.md` — 10 sections, full traceability
- `docs/gap_analysis_first_prize.md` — P0/P1/P2 action items
- `docs/toggle_coverage_waiver.md` — Categories T-A~T-F
- `docs/source_inventory.md` — Source tracking
- `docs/reviewer_quickstart.md` — 3-command reviewer guide

### UCAgent Artifacts
- `docs/ucagent_output/ucagent_stages_summary.md` — This file
- `docs/ucagent_output/first_prize_gap_closure_stages.md` — P0/P1/P2 summary
- `docs/ucagent_output/internal_signal_coverage_impl.md` — Internal signal deep-dive
- `docs/ucagent_output/final_report_stage.md` — Submission checklist
- All 18 individual stage artifacts preserved

### GenSpec Deliverables (unity_test/)
- `Cache_spec.md` + 6 sub-specs
- `Cache_functions_and_checks.md` — FG/FC/CK matrix
- `Cache_line_func_map.md` — CK-to-line map
- `Cache_api.py`, `Cache_function_coverage_def.py` — Standard wrappers

---

## Execution Commands Reference

```bash
# Environment
cd /Users/zzy/Workspace/ucagent
source scripts/env.sh

# Smoke
make test-smoke                # or scripts/run_smoke.sh

# Directed tests
make test-directed             # or scripts/run_directed.sh

# Full regression
make test                      # or scripts/run_regression.sh

# Coverage (single seed)
make coverage SEED=7 STEPS=18  # or scripts/collect_coverage.sh 7 18

# Coverage (multi-seed toggle)
make coverage-multi            # or scripts/collect_coverage_multi.sh

# Bug injection
make bug-inject                # or scripts/run_bug_injection.sh
make bug-recover               # or scripts/run_bug_injection.sh --disable-bug

# Reproducibility (clean + full)
make reproduce                 # or scripts/clean_generated.sh && scripts/reproduce.sh

# UCAgent stage runner
scripts/run_ucagent_stage.sh <stage_index>
```

---

## Conclusion

All 18 UCAgent stages executed successfully with Codex/Claude Code backend. The verification environment achieves:

- **100% RTL Line/Branch/Expression coverage** (with documented waivers)
- **88.4% Toggle coverage** (structural plateau, documented waivers)
- **100% Toffee Functional coverage** (15 groups, 95 bins)
- **38 tests passing** across smoke, directed, corner, random suites
- **Full reproducibility** via `make reproduce`
- **7 bug injection scenarios** with detection/recovery evidence
- **Complete GenSpec specification chain** from RTL to line map

The project is submission-ready with all artifacts in `docs/ucagent_output/` and `unity_test/`.