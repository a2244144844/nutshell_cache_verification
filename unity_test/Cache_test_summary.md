# Cache Test Summary

## Current Submission Result

| Command | Result |
| --- | --- |
| `scripts/run_directed.sh` | `26 passed in 5.10s` |
| `scripts/run_regression.sh` | `30 passed in 5.43s` |
| `scripts/collect_coverage.sh 7 18` | `30 passed, RTL line coverage 1359/1364 (99.6%)` |
| `scripts/clean_generated.sh && scripts/reproduce.sh` | `PASS` |

## Test Inventory

| Area | Count / Scope |
| --- | --- |
| Smoke | Reset, read miss/refill, read hit, write hit, read-after-write |
| Directed | DIR-001 through DIR-016 documented and implemented |
| Corner | CPU-response and memory-request backpressure |
| Random | Deterministic constrained random read/write bootstrap |
| Bug evidence | Reference-model corruption and RTL dirty-writeback bypass |
| Functional coverage | Toffee model: 12 groups, 31 points, 37 bins, 100% covered |
| RTL line coverage | Verilator: 1359/1364 lines (99.6%), 16 lines waived (Categories A-G + J) |

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
- Historical UCAgent stage artifacts preserve their stage-time command counts; current submission status is summarized here, in `README.md`, `docs/test_points.md`, and `docs/ucagent_output/final_report_stage.md`.
- RTL line coverage measured via Verilator: 1359/1364 (99.6%). Functional coverage closed through Toffee at 100%.
- DIR-011 through DIR-013 original implementation was direct-agent work; replayed through UCAgent (`docs/ucagent_output/write_miss_eviction_replay_stage.md`).
- DIR-014 through DIR-016 implemented through UCAgent stage 9 `line_coverage_closure` (`docs/ucagent_output/line_coverage_closure_stage.md`).
