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

DIR-011 through DIR-013 were added after coherence-probe closure by another agent and are included in the clean regression and Toffee coverage closure. They are recorded as post-coherence direct agent work unless replayed through a later UCAgent stage.

## Execution Plan

1. Rebuild DUT wrapper with `scripts/export_cache_dut.sh`.
2. Run smoke, directed, and corner checks with `scripts/run_regression.sh`.
3. Run coverage collection with `scripts/collect_coverage.sh 7 18`.
4. Run bug-injection evidence with `scripts/run_bug_injection.sh` and recovery with `scripts/run_bug_injection.sh --disable-bug`.
5. Use `scripts/reproduce.sh` as the single submission-facing reproduction entry.

## Exit Criteria

| Criterion | Current Status |
| --- | --- |
| Directed suite clean | `scripts/run_directed.sh -> 23 passed in 1.05s` |
| Full regression clean | `scripts/run_regression.sh -> 26 passed in 1.34s` |
| Reproducibility entry clean | `scripts/clean_generated.sh && scripts/reproduce.sh -> PASS` |
| Toffee functional coverage closed | 12 groups, 31 points, 37 bins, all 100% covered |
| Bug evidence present | `BUG-001` and `BUG-RTL-001` documented |
