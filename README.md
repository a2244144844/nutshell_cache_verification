# Track1 NutShell Cache Verification Workspace

This workspace is for the CCF Track1 UCAgent competition task: verifying the NutShell Cache with UCAgent-assisted, human-reviewed verification engineering.

## Current Status

- UCAgent and Codex CLI are available on this machine.
- UCAgent/Codex linkage has been verified separately and now has Cache-specific audit, backpressure, CRV/coverage, dirty-writeback, and bug-injection stage runs.
- The GitLink competition environment repository has been cloned under `upstream/env-xs-ov-00-nutshell-cache`.
- The selected DUT is Picker's Cache example RTL copied to `rtl/dut/Cache.v`.
- Picker exports the selected DUT as Python class `DUTCache`.
- `scripts/run_smoke.sh` passes the first reset/read/write smoke test.
- The first reusable Python verification skeleton exists under `src/env`, `src/monitor`, `src/scoreboard`, and `src/utils`.
- Directed tests now cover partial write masks, same-line word offsets, full 8-beat refill order, and dirty-victim writeback/refill closure.
- `scripts/run_regression.sh` currently passes smoke, directed, and corner tests with `7 passed in 0.14s`.
- `scripts/collect_coverage.sh 7 18` passes the CRV/coverage bootstrap with `1 passed in 0.04s` and now closes the dirty writeback gap.
- `scripts/reproduce.sh` is the one-command reproducibility entry and passes from a cleaned generated-artifact state.
- The first Cache-specific UCAgent audit stage completed and generated `docs/ucagent_output/stage_audit.md`.
- The UCAgent backpressure, CRV/coverage, dirty-writeback closure, and bug-injection stages completed and generated `docs/ucagent_output/backpressure_stage.md`, `docs/ucagent_output/crv_coverage_stage.md`, `docs/ucagent_output/dirty_writeback_stage.md`, and `docs/ucagent_output/bug_injection_stage.md`.
- The bug-injection evidence is recorded in `docs/bug_tracking.md`; the intentional failure is kept out of the normal regression suite.

## UCAgent Integration Status

Current verification progress is real and reproducible. The project now has five Cache-specific UCAgent stage artifacts and still needs the final-report stage before final submission.

- Existing work: Codex implemented and ran the Cache verification files in this workspace.
- Verified outside this workspace: `instruction.md` proves the local UCAgent -> Codex -> MCP `Complete` path can run.
- Verified inside this workspace: `configs/ucagent_track1_cache.yaml` ran `cache_regression_audit`, `backpressure_directed_tests`, `crv_coverage_bootstrap`, `dirty_writeback_coverage_closure`, and `bug_injection_evidence` through UCAgent/Codex, recorded stage journals, and called `Complete`.
- Ready for next stage: final report package and reproducibility cleanup.
- Config check passed: `ucagent --emulate-config --force-stage-index 1` recognized all 5 stages and selected the backpressure stage.
- Remaining gap: final report packaging still needs a dedicated pass.
- Integration plan: see `docs/ucagent_operation_plan.md`.

## Working Directories

```text
competition/track1_nutshell_cache/
├── LICENSE
├── README.md
├── top.md
├── configs/
│   └── ucagent_track1_cache.yaml
├── docs/
│   ├── ai_collaboration_report.md
│   ├── bug_tracking.md
│   ├── dut_selection.md
│   ├── interface_map.md
│   ├── nutshell_build_probe.md
│   ├── picker_installation.md
│   ├── source_inventory.md
│   ├── test_points.md
│   ├── ucagent_operation_plan.md
│   ├── ucagent_output/
│   │   ├── backpressure_stage.md
│   │   ├── bug_injection_stage.md
│   │   ├── crv_coverage_stage.md
│   │   ├── dirty_writeback_stage.md
│   │   └── stage_audit.md
│   └── verification_plan.md
├── rtl/
│   └── dut/
├── src/
│   ├── env/
│   ├── generator/
│   ├── monitor/
│   ├── scoreboard/
│   └── utils/
├── tests/
│   ├── smoke/
│   ├── random/
│   ├── corner/
│   └── injected_bug/
├── scripts/
│   ├── clean_generated.sh
│   ├── collect_coverage.sh
│   ├── reproduce.sh
│   ├── run_bug_injection.sh
│   ├── run_ucagent_stage.sh
│   ├── run_regression.sh
│   ├── run_directed.sh
│   └── run_smoke.sh
└── upstream/
    └── env-xs-ov-00-nutshell-cache/
```

## Immediate Next Step

Continue using UCAgent as the stage controller while expanding tests:

1. Complete the final report package and reproducibility cleanup.
2. Preserve the bug-injection harness outside the normal regression path so `scripts/run_regression.sh` remains clean.

## Reproducibility

Run the main reproducibility entry from this workspace:

```sh
scripts/reproduce.sh
```

It runs normal regression, coverage collection with seed `7` and `18` transactions by default, the expected-failure bug injection, and the disabled-bug recovery path. Generated build, cache, Python bytecode, and wave artifacts can be removed with:

```sh
scripts/clean_generated.sh
```

Latest validation:

```text
scripts/clean_generated.sh && scripts/reproduce.sh -> PASS
```
