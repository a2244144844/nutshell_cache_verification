# UCAgent Operation Plan

Date: 2026-05-26

## Current Assessment

The current Cache verification workspace has real executable progress: Picker export works, Python tests drive the DUT, directed/corner/random tests pass, bug-injection evidence exists, and a VCD waveform has been generated. The workflow now has UCAgent-driven audit, backpressure, CRV/coverage, dirty-writeback closure, and bug-injection evidence stages; final packaging remains.

What is currently true:

- UCAgent/Codex integration has been verified separately in `instruction.md`.
- Cache-specific `cache_regression_audit`, `backpressure_directed_tests`, `crv_coverage_bootstrap`, `dirty_writeback_coverage_closure`, and `bug_injection_evidence` stages have run through UCAgent using `configs/ucagent_track1_cache.yaml`.
- Those stages generated `docs/ucagent_output/stage_audit.md`, `docs/ucagent_output/backpressure_stage.md`, `docs/ucagent_output/crv_coverage_stage.md`, `docs/ucagent_output/dirty_writeback_stage.md`, and `docs/ucagent_output/bug_injection_stage.md` and recorded regression, coverage, or injected-failure evidence.
- This Cache workspace was implemented by Codex in the shared repository, with human review and decisions recorded in `docs/ai_collaboration_report.md`.
- The current Cache tests are reproducible through shell scripts.

What is still missing for a strong Track1 submission:

- Earlier technical implementation stages were not originally launched through UCAgent.
- Final report packaging still needs a dedicated review pass.
- Any re-run of implementation stages should continue through the same `ucagent <workspace> Cache --backend codex` path.
- Reports must distinguish UCAgent-orchestrated work from direct Codex-assisted work.

Therefore, the next documentation and workflow goal is to make UCAgent the visible orchestrator of the verification process, while keeping Codex as the backend implementation agent.

## UCAgent Role In This Project

UCAgent should be used as the stage controller:

- Define the verification stages and expected deliverables.
- Feed each stage task to the Codex backend.
- Require journal updates for design assumptions, generated files, manual decisions, and test results.
- Mark each stage complete only after scripts/tests pass.
- Preserve final output files for review.

Codex should be used as the implementation backend:

- Inspect RTL and generated Picker wrappers.
- Edit source, test, script, and Markdown files.
- Run smoke, directed, regression, waveform, coverage, and bug-injection commands.
- Report findings back into UCAgent stage journals and final Markdown deliverables.

Human review remains mandatory:

- Correct DUT boundary decisions.
- Approve protocol assumptions.
- Decide which generated tests are meaningful.
- Identify and record AI misunderstandings.
- Decide when coverage or bug evidence is strong enough for submission.

## Proposed Stage Contract

The Cache competition task should be represented as these UCAgent stages.

| Stage | UCAgent Stage Name | Main Task | Required Output Files |
| --- | --- | --- | --- |
| 0 | `inventory_and_dut_boundary` | Read requirements, inventory sources, decide and justify selected DUT. | `docs/source_inventory.md`, `docs/dut_selection.md`, `docs/nutshell_build_probe.md` |
| 1 | `picker_export_and_interface_map` | Install/validate Picker, export selected Cache DUT, map interfaces and protocol constants. | `docs/picker_installation.md`, `docs/interface_map.md`, `scripts/export_cache_dut.sh` |
| 2 | `smoke_closure` | Build first reset/read/write smoke test and one-command runner. | `tests/smoke/test_cache_basic.py`, `scripts/run_smoke.sh`, `docs/test_points.md` |
| 3 | `structured_env_refactor` | Refactor prototype into env, monitor, scoreboard, and utils. | `src/env/cache_env.py`, `src/monitor/cache_monitor.py`, `src/scoreboard/cache_scoreboard.py`, `src/utils/simplebus.py` |
| 4 | `directed_cache_tests` | Add directed tests for write masks, word offsets, and full refill order. | `tests/directed/`, `scripts/run_directed.sh`, `scripts/run_regression.sh` |
| 5 | `backpressure_directed_tests` | Add memory/CPU response backpressure tests. | `tests/corner/test_backpressure.py`, `docs/ucagent_output/backpressure_stage.md` |
| 6 | `crv_coverage_bootstrap` | Add constrained random generator and first functional coverage collection. | `tests/random/`, `docs/coverage_report.md`, `docs/ucagent_output/crv_coverage_stage.md` |
| 7 | `dirty_writeback_coverage_closure` | Add dirty-victim writeback/refill coverage closure. | `tests/directed/test_dirty_writeback.py`, `docs/coverage_report.md`, `docs/ucagent_output/dirty_writeback_stage.md` |
| 8 | `bug_injection_evidence` | Add injected-bug tests and bug tracking evidence. | `tests/injected_bug/`, `docs/bug_tracking.md`, `docs/ucagent_output/bug_injection_stage.md` |
| 9 | `final_report_package` | Assemble final report and reproducibility instructions. | `README.md`, `docs/ai_collaboration_report.md`, `top.md` |

## UCAgent Run Template

The intended command should follow the local verified UCAgent/Codex linkage from `instruction.md`.

```sh
cd /Users/zzy/Workspace/ucagent
source .venv/bin/activate

UCAGENT_CMDLINE_START_MCP=1 \
UC_ENV_CMD_BACKEND_EX_ARGS="-m gpt-5.4-mini --ephemeral" \
ucagent /Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache Cache \
  --config /Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/configs/ucagent_track1_cache.yaml \
  --backend codex \
  --exit-on-completion \
  --mcp-server-no-file-tools \
  --mcp-server-host 127.0.0.1 \
  --mcp-server-port 5002 \
  --no-embed-tools \
  -s
```

The initial `configs/ucagent_track1_cache.yaml` file is an audit-stage config. It validated the existing regression through UCAgent and should now be expanded into the full multi-stage competition flow.

Initial audit result:

- Stage: `cache_regression_audit`
- Output file: `docs/ucagent_output/stage_audit.md`
- Regression result: `4 passed in 0.11s`
- UCAgent tool evidence: `SetCurrentStageJournal`, `Complete`, and `Exit` were called.
- Log interpretation note: the UCAgent log showed `Complete: true`, `Exit: true`, and Codex backend return code 0. The outer CLI command ended with code 1 after the Exit flow, so use the stage audit artifact and tool logs as the completion evidence.

## Running A Specific Future Stage

Use `--force-stage-index` through the helper script so new work starts from the intended stage instead of rerunning the audit stage.

```sh
cd /Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache

# Stage 1: backpressure implementation
scripts/run_ucagent_stage.sh 1

# Stage 2: CRV and coverage bootstrap
scripts/run_ucagent_stage.sh 2

# Stage 3: dirty writeback coverage closure
scripts/run_ucagent_stage.sh 3

# Stage 4: bug-injection evidence
scripts/run_ucagent_stage.sh 4
```

The helper uses `configs/ucagent_track1_cache.yaml`, starts the UCAgent MCP server, uses Codex as backend, and preserves the UCAgent requirement to call `SetCurrentStageJournal`, `Complete`, and then `Exit` for one-stage-at-a-time runs.

Configuration check:

- Command: `ucagent ... --emulate-config --force-stage-index 1`
- Result: UCAgent recognized the configured stages and selected `backpressure_directed_tests` as the current stage.
- Note: emulate mode uses a temporary workspace, so missing-output warnings are expected for files that the future stages will create.

## Current Config Shape

`configs/ucagent_track1_cache.yaml` currently contains these runnable stages:

- Stage 0: `cache_regression_audit`
- Stage 1: `backpressure_directed_tests`
- Stage 2: `crv_coverage_bootstrap`
- Stage 3: `dirty_writeback_coverage_closure`
- Stage 4: `bug_injection_evidence`

This is enough to keep implementation work on the UCAgent channel instead of direct Codex execution. Stages 0 through 4 have now been exercised through this channel.

Current exercised stages:

- Stage 0 `cache_regression_audit`: complete.
- Stage 1 `backpressure_directed_tests`: complete.
- Stage 2 `crv_coverage_bootstrap`: complete.
- Stage 3 `dirty_writeback_coverage_closure`: complete.
- Stage 4 `bug_injection_evidence`: complete.

The next intended work item is the final report package and reproducibility cleanup. Note that the previous stage 3 run advanced into the then-next stage after `Complete` despite the config instruction to call `Exit`; the overrun was stopped and out-of-scope bug-injection drafts were removed before Stage 4 was run deliberately.

## Reporting Rule

Every UCAgent-driven stage should leave a report entry with:

- UCAgent stage name.
- Codex backend actions.
- Files generated or edited.
- Commands run and exact result.
- Human decision or correction.
- Whether the stage called `Complete`.

This is the missing bridge between the current working verification code and the competition requirement that the project demonstrate UCAgent-assisted engineering.
