# UCAgent Operation Plan

Date: 2026-05-26

## Current Assessment

The current Cache verification workspace has real executable progress: Picker export works, Python tests drive the DUT, directed/corner/random tests pass, bug-injection evidence exists, and a VCD waveform has been generated. The workflow now has UCAgent-driven audit, backpressure, CRV/coverage, dirty-writeback closure, bug-injection evidence, final-report packaging, flush, coherence-probe, and a supplemental write-miss / eviction replay stage. The original write-miss and eviction implementation history remains recorded in the collaboration report as direct-agent work.

What is currently true:

- UCAgent/Codex integration has been verified separately in `instruction.md`.
- Cache-specific `cache_regression_audit`, `backpressure_directed_tests`, `crv_coverage_bootstrap`, `dirty_writeback_coverage_closure`, `bug_injection_evidence`, `final_report_package`, `flush_directed_test`, and `coherence_probe_directed_test` stages have run through UCAgent using `configs/ucagent_track1_cache.yaml`.
- A supplemental replay artifact, `docs/ucagent_output/write_miss_eviction_replay_stage.md`, records the 2026-05-27 UCAgent replay of DIR-011 through DIR-013.
- Those stages generated `docs/ucagent_output/stage_audit.md`, `docs/ucagent_output/backpressure_stage.md`, `docs/ucagent_output/crv_coverage_stage.md`, `docs/ucagent_output/dirty_writeback_stage.md`, `docs/ucagent_output/bug_injection_stage.md`, `docs/ucagent_output/final_report_stage.md`, `docs/ucagent_output/flush_stage.md`, and `docs/ucagent_output/coherence_probe_stage.md` and recorded regression, coverage, injected-failure, or directed-test evidence.
- This Cache workspace was implemented by Codex in the shared repository, with human review and decisions recorded in `docs/ai_collaboration_report.md`.
- The current Cache tests are reproducible through shell scripts.

What is still missing for a strong Track1 submission:

- Earlier technical implementation stages were not originally launched through UCAgent.
- Post-coherence write miss and eviction closure were performed by another agent and must be reported as such unless later replayed through a UCAgent stage. That replay now exists in `docs/ucagent_output/write_miss_eviction_replay_stage.md`, while the original implementation history remains direct-agent work.
- Any re-run of implementation stages should continue through the same `ucagent <workspace> Cache --backend codex` or approved UCAgent/Claude Code path.
- Reports must distinguish UCAgent-orchestrated work from direct Codex-assisted work.

Therefore, the documentation goal is to keep UCAgent as the visible orchestrator of stage work, while clearly labeling any direct Codex/Claude-agent work that was not replayed through UCAgent.

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
| 10 | `flush_directed_test` | Add flush behavior directed tests. | `tests/directed/test_flush_behavior.py`, `docs/ucagent_output/flush_stage.md` |
| 11 | `coherence_probe_directed_test` | Add coherence probe hit/miss directed tests. | `tests/directed/test_coherence_probe.py`, `docs/ucagent_output/coherence_probe_stage.md` |
| 12 | `final_submission_sync` | Refresh all docs after post-final directed closure. | `README.md`, `docs/test_points.md`, `docs/verification_plan.md`, `docs/ai_collaboration_report.md`, `docs/ucagent_output/final_report_stage.md`, `top.md` |
| 13 | `genspec_full` | Run official six-stage GenSpec flow on Cache RTL and existing docs. | `unity_test/Cache_spec.md`, `unity_test/Cache/CacheStage*.md`, `unity_test/Cache_functions_and_checks.md`, `unity_test/Cache_line_func_map.md`, `docs/ucagent_output/genspec_full_stage.md` |
| 14 | `line_coverage_closure` | Close remaining uncovered lines: DIR-014/015/016 + Category J waiver. | `tests/directed/test_read_burst_hit.py`, `docs/line_coverage_closure_plan.md`, `docs/ucagent_output/line_coverage_closure_stage.md` |

Supplemental replay artifact:

- `docs/ucagent_output/write_miss_eviction_replay_stage.md` records the UCAgent replay of DIR-011 through DIR-013 and preserves the original direct-agent implementation history.

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

# Stage 6: coherence probe directed test
scripts/run_ucagent_stage.sh 6

# Stage 7: flush directed test
scripts/run_ucagent_stage.sh 7
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
- Stage 5: `final_report_package`
- Stage 6: `coherence_probe_directed_test`
- Stage 7: `flush_directed_test`
- Stage 8: `write_miss_eviction_replay`
- Stage 9: `line_coverage_closure`

This is enough to keep implementation work on the UCAgent channel instead of direct Codex execution. Stages 0 through 9 have now been exercised through this channel.
The supplemental DIR-011 through DIR-013 replay artifact is recorded as stage 8.
The official GenSpec six-stage flow ran in a separate overlay workspace (`genspec_workspace/`) and is recorded in `docs/ucagent_output/genspec_full_stage.md`.

Current exercised stages:

- Stage 0 `cache_regression_audit`: complete.
- Stage 1 `backpressure_directed_tests`: complete.
- Stage 2 `crv_coverage_bootstrap`: complete.
- Stage 3 `dirty_writeback_coverage_closure`: complete.
- Stage 4 `bug_injection_evidence`: complete.
- Stage 5 `final_report_package`: complete.
- Stage 6 `coherence_probe_directed_test`: complete (via Claude Code backend).
- Stage 7 `flush_directed_test`: complete (via Claude Code backend).
- Stage 8 `write_miss_eviction_replay`: complete (UCAgent replay artifact; original DIR-011 through DIR-013 implementation remains direct-agent work).
- Stage 9 `line_coverage_closure`: complete (via Claude Code backend; DIR-014/015/016 + Category J waiver; line coverage 1359/1364 = 99.6%).

The current intended work item is final submission synchronization: update all top-level and mirror documents to the latest `30 passed` regression result, `26 passed` directed result, and 1359/1364 (99.6%) RTL line coverage, and clearly distinguish UCAgent-run stages from post-coherence direct agent work.

## MCP Server Connection

UCAgent can expose its verification tools via an MCP (Model Context Protocol) server, enabling any MCP-compatible client (Claude Code, Qwen, Codex, Gemini CLI, etc.) to interact with the verification workspace.

### Start the MCP Server

Run from the `competition/` directory:

```bash
printf '!import threading, time; threading.Thread(target=lambda: time.sleep(99999999), daemon=False).start()\nc\n' | \
  .venv/bin/ucagent . Cache --mcp-server --mcp-server-host 127.0.0.1 --mcp-server-port 5002 --human
```

The keep-alive thread is necessary because the MCP server runs as a daemon thread; without a non-daemon thread, the process exits immediately after initialization.

### One-Time DUT Directory Setup

Before first start, ensure the DUT directory exists under the workspace:

```bash
mkdir -p competition/Cache
cp competition/rtl/dut/Cache.v competition/rtl/dut/Cache.yaml competition/rtl/dut/Test.v competition/Cache/
touch competition/Cache/__init__.py
```

### MCP Client Configuration

Add to the MCP client's config file. For Claude Code, this goes in `.mcp.json` at the workspace root:

```json
{
  "mcpServers": {
    "ucagent": {
      "type": "http",
      "url": "http://127.0.0.1:5002/mcp"
    }
  }
}
```

### Available MCP Tools (26)

| Tool | Description |
|---|---|
| RoleInfo | Returns agent role info and basic guidance |
| CurrentTips | Returns tips for the current stage |
| Detail | Returns mission details with all stages |
| Status | Returns current mission status |
| Complete | Validates and completes current stage |
| Check | Validates current stage without advancing |
| GoToStage | Go to a specific stage by index |
| Exit | Exit agent after all stages complete |
| ReadTextFile | Read lines from a text file in workspace |
| PathList | List files and directories |
| GetFileInfo | Get file metadata (size, type, permissions) |
| SearchText | Search text in files (regex/wildcard) |
| FindFiles | Find files by pattern |
| EditTextFile | Edit or create text files |
| ReplaceStringInFile | Exact string replacement in files |
| CopyFile | Copy files within workspace |
| MoveFile | Move/rename files within workspace |
| CreateDirectory | Create directories |
| DeleteFile | Delete files or directories |
| RunTestCases | Execute test cases (pytest) |
| RunBashCommand | Run bash commands |
| WorkDiff | Show git diff for workspace |
| WorkCommit | Commit workspace changes |
| StageJournal | Get current stage journal |
| AllStageJournal | Get all stages' journals |
| SetCurrentStageJournal | Set current stage journal |

### Verify the Server

```bash
# Initialize MCP session
curl -s -X POST http://127.0.0.1:5002/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'

# The server responds with serverInfo: {"name":"UnityTest","version":"1.27.1"}
```

### Stop the Server

```bash
pkill -f "ucagent . Cache"
```

## Reporting Rule

Every UCAgent-driven stage should leave a report entry with:

- UCAgent stage name.
- Codex backend actions.
- Files generated or edited.
- Commands run and exact result.
- Human decision or correction.
- Whether the stage called `Complete`.

This is the missing bridge between the current working verification code and the competition requirement that the project demonstrate UCAgent-assisted engineering.
