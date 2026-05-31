# Cache Test Summary

## Current Submission Result

| Command | Result |
| --- | --- |
| `scripts/run_directed.sh` | `37 passed` |
| `scripts/run_regression.sh` | `37 passed` |
| `scripts/collect_coverage.sh` | `37 passed, RTL line coverage 1359/1359 (100.0%), branch coverage 471/471 (100.0%)` |
| `scripts/collect_coverage_multi.sh` | Toggle coverage 24947/28227 (88.4%, Stage 17 final) |
| `scripts/clean_generated.sh && scripts/reproduce.sh` | `PASS` |

## Test Inventory

| Area | Count / Scope |
| --- | --- |
| Smoke | Reset, read miss/refill, read hit, write hit, read-after-write |
| Directed | DIR-001 through DIR-022 documented and implemented |
| Corner | CPU-response and memory-request backpressure |
| Random | Deterministic constrained random read/write bootstrap + multi-seed random (Stage 13/17) |
| Bug evidence | Reference-model corruption and RTL dirty-writeback bypass |
| Functional coverage | Toffee model: 12 groups, 31 points, 37 bins, 100% covered |
| RTL line coverage | Verilator: 1359/1359 lines (100.0%), 42 lines waived (Categories A-N) |
| RTL branch coverage | Verilator: 471/471 branches (100.0%) |
| RTL toggle coverage | Verilator: 24947/28227 toggles (88.4%), 3,280 toggles waived (Categories T-A–T-F, documentation-based) |

## UCAgent Evidence

| Artifact | Purpose |
| --- | --- |
| `docs/ucagent_output/stage_audit.md` | Initial UCAgent regression audit. |
| `docs/ucagent_output/backpressure_stage.md` | Backpressure implementation evidence. |
| `docs/ucagent_output/crv_coverage_stage.md` | Random and first coverage bootstrap evidence. |
| `docs/ucagent_output/dirty_writeback_stage.md` | Dirty writeback closure evidence. |
| `docs/ucagent_output/bug_injection_stage.md` | Controlled bug-injection evidence. |
| `docs/ucagent_output/final_report_stage.md` | Submission checklist and final documentation refresh. |
| `docs/ucagent_output/coherence_probe_stage.md` | Coherence probe directed stage evidence. |
| `docs/ucagent_output/flush_stage.md` | Flush behavior directed stage evidence. |
| `docs/ucagent_output/line_coverage_closure_stage.md` | Line coverage closure (DIR-014/015/016) stage evidence. |
| `docs/ucagent_output/line_coverage_100_stage.md` | Line coverage 100% closure (DIR-017/018, Stage 11) evidence. |
| `docs/ucagent_output/branch_coverage_closure_stage.md` | Branch coverage 100% closure (DIR-019–022, Stage 12) evidence. |
| `docs/ucagent_output/toggle_coverage_improvement_stage.md` | Toggle coverage improvement (multi-seed random, Stage 13) evidence. |

## Reproducibility

Primary command:

```sh
cd /Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache
scripts/reproduce.sh
```

Clean rebuild path:

```sh
scripts/clean_generated.sh
scripts/reproduce.sh
```

## Submission Notes

- The main regression excludes intentionally failing bug-injection runs.
- Historical UCAgent stage artifacts preserve their stage-time command counts; current submission status is summarized here, in `top.md`, `docs/test_points.md`, and `docs/ucagent_output/final_report_stage.md`.
- RTL line coverage: 1359/1359 (100.0%), branch coverage: 471/471 (100.0%), expr coverage: 137/137 (100.0%). Toggle coverage: 24947/28227 (88.4%), with 3,280 toggles waived (Categories T-A–T-F, documentation-based). Functional coverage closed through Toffee at 100%.
- DIR-011 through DIR-013 original implementation was direct-agent work; replayed through UCAgent (`docs/ucagent_output/write_miss_eviction_replay_stage.md`).
- DIR-014 through DIR-016 implemented through UCAgent stage 9 `line_coverage_closure` (`docs/ucagent_output/line_coverage_closure_stage.md`).
- DIR-017 (needFlush) and DIR-018 (respToL1Last) achieved line coverage 100% through UCAgent Stage 11.
- DIR-019 (PREFETCH), DIR-020 (writeback counters), DIR-021 (internal probe), and DIR-022 (state2) achieved branch coverage 100% through UCAgent Stage 12.
- Multi-seed random traffic (Stage 13) improved toggle coverage from 86.7% to 87.8%.
- Stage 17 max attempt (10 seeds × 200 steps, 64 addresses, 32 patterns) pushed toggle to 88.4% final plateau.
- Stage 18 formalized toggle waivers in GenSpec documentation (documentation-based, not in conftest.py).
- Waiver rationale documented in `docs/coverage_waiver_rationale.md` (line/branch/expr Categories A-O) and `docs/toggle_coverage_waiver.md` (toggle Categories T-A–T-F).
