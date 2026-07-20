# Cache Verification Needs And Plan

## Verification Goal

Verify the selected NutShell Cache RTL through a reproducible Picker/Python/pytest flow, with UCAgent-visible stage evidence, functional coverage, directed corner tests, constrained random checks, scoreboard checks, and bug-detection evidence.

## Verification Needs

| Need | Planned Evidence |
| --- | --- |
| DUT export reproducibility | `scripts/export_cache_dut.sh` rebuilds Picker/Verilator/Python artifacts. |
| Basic read/write correctness | Smoke test checks reset, cold read miss/refill, read hit, write hit, and read-after-write. |
| Protocol timing | Directed tests check refill beats, backpressure, flush timing, and probe valid/ready ordering. |
| Data correctness | Scoreboard and reference model check read/write data and write-mask merges. |
| Replacement behavior | Directed tests cover invalid-way priority, clean eviction, dirty eviction, and writeback/refill sequencing. |
| MMIO and coherence paths | Directed tests cover MMIO bypass and probe hit/miss response commands. |
| Coverage closure | Random bootstrap plus Toffee coverage model records command, path, mask, MMIO, probe, flush, eviction, and write-miss bins. |
| Bug detection | Controlled reference-model corruption and RTL dirty-writeback bypass are both detected. |

## UCAgent Stage Plan

| Stage | Status | Output |
| --- | --- | --- |
| `cache_regression_audit` | Complete | `docs/ucagent_output/stage_audit.md` |
| `backpressure_directed_tests` | Complete | `docs/ucagent_output/backpressure_stage.md` |
| `crv_coverage_bootstrap` | Complete | `docs/ucagent_output/crv_coverage_stage.md` |
| `dirty_writeback_coverage_closure` | Complete | `docs/ucagent_output/dirty_writeback_stage.md` |
| `bug_injection_evidence` | Complete | `docs/ucagent_output/bug_injection_stage.md` |
| `final_report_package` | Complete and refreshed | `docs/ucagent_output/final_report_stage.md` |
| `coherence_probe_directed_test` | Complete | `docs/ucagent_output/coherence_probe_stage.md` |
| `flush_directed_test` | Complete | `docs/ucagent_output/flush_stage.md` |
| `line_coverage_100` | Complete | `docs/ucagent_output/line_coverage_100_stage.md` |
| `branch_coverage_closure` | Complete | `docs/ucagent_output/branch_coverage_closure_stage.md` |
| `toggle_coverage_improvement` | Complete | `docs/ucagent_output/toggle_coverage_improvement_stage.md` |
| `toggle_improvement_final` | Complete | `docs/ucagent_output/toggle_final_attempt_stage.md` |
| `toggle_waiver_docs` | Complete | `docs/ucagent_output/toggle_waiver_docs_stage.md` |

DIR-011 through DIR-013 were added after coherence-probe closure by another agent and are included in the clean regression and Toffee coverage closure. They are recorded as post-coherence direct agent work unless replayed through a later UCAgent stage.

DIR-017 (needFlush) and DIR-018 (respToL1Last) closed line coverage to 100% via Stage 11. DIR-019 (PREFETCH), DIR-020 (writeback counters), DIR-021 (internal probe), DIR-022 (state2) closed branch coverage to 100% via Stage 12. Multi-seed random traffic improved toggle coverage via Stage 13 (87.8%) and Stage 17 (88.4% final plateau). Stage 18 formalized toggle waivers in GenSpec documentation.

Line/branch waiver rationale in `docs/coverage_waiver_rationale.md`. Toggle waiver rationale in `docs/toggle_coverage_waiver.md`.

## Execution Plan

1. Rebuild DUT wrapper with `scripts/export_cache_dut.sh`.
2. Run smoke, directed, and corner checks with `scripts/run_regression.sh`.
3. Run coverage collection with `scripts/collect_coverage.sh 7 18`.
4. Run bug-injection evidence with `scripts/run_bug_injection.sh` and recovery with `scripts/run_bug_injection.sh --disable-bug`.
5. Use `scripts/reproduce.sh` as the single submission-facing reproduction entry.

## Exit Criteria

| Criterion | Current Status |
| --- | --- |
| Directed suite clean | `scripts/run_directed.sh -> 38 passed in 3.16s` |
| Full regression clean | `scripts/run_regression.sh -> 37 passed` |
| Reproducibility entry clean | `scripts/clean_generated.sh && scripts/reproduce.sh -> PASS` |
| Toffee functional coverage closed | 12 groups, 31 points, 37 bins, all 100% covered |
| RTL line coverage | 1359/1359 (100.0%), 42 lines waived (Categories A-N) |
| RTL branch coverage | 471/471 (100.0%) |
| RTL toggle coverage | 24947/28227 (88.4%), 3,280 toggles waived (Categories T-A–T-F, documentation-based) |
| RTL expr coverage | 137/137 (100.0%), 6 expressions waived (Category O) |
| Bug evidence present | `BUG-001` and `BUG-RTL-001` documented |
| Waiver rationale | `docs/coverage_waiver_rationale.md`, `docs/toggle_coverage_waiver.md` |
