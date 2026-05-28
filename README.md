# Track1 NutShell Cache Verification Workspace

This workspace is for the CCF Track1 UCAgent competition task: verifying the NutShell Cache with UCAgent-assisted, human-reviewed verification engineering.

## Current Status

- UCAgent and Codex CLI are available on this machine.
- UCAgent/Codex and UCAgent/Claude Code linkage has been verified separately and now has Cache-specific audit, backpressure, CRV/coverage, dirty-writeback, bug-injection, final-report, flush, and coherence-probe stage evidence.
- The GitLink competition environment repository has been cloned under `upstream/env-xs-ov-00-nutshell-cache`.
- The selected DUT is Picker's Cache example RTL copied to `rtl/dut/Cache.v`.
- Picker exports the selected DUT as Python class `DUTCache`.
- `scripts/run_smoke.sh` passes the first reset/read/write smoke test.
- The first reusable Python verification skeleton exists under `src/env`, `src/monitor`, `src/scoreboard`, and `src/utils`.
- Directed tests now cover partial write masks, same-line word offsets, full 8-beat refill order, invalid-way replacement priority, MMIO bypass, flush behavior (including needFlush de-assertion), coherence probe hit/miss (including full release sequence), read-burst hit, write miss, clean eviction, dirty-victim writeback/refill, and write-miss dirty eviction closure.
- `scripts/run_directed.sh` currently passes directed tests with `26 passed in 5.10s`.
- `scripts/run_regression.sh` currently passes smoke, directed, corner, and random tests with `30 passed in 5.43s`.
- `scripts/collect_coverage.sh 7 18` passes the full coverage collection run with `30 passed` and the Toffee functional coverage model reports 12 groups, 31 points, and 37 bins all 100% covered.
- Verilator RTL line coverage: **1359/1364 (99.6%)** with 5 remaining waived lines (4 Category J D-cache ports + 1 residual).
- `scripts/reproduce.sh` is the one-command reproducibility entry and passes from a cleaned generated-artifact state.
- The first Cache-specific UCAgent audit stage completed and generated `docs/ucagent_output/stage_audit.md`.
- The UCAgent backpressure, CRV/coverage, dirty-writeback closure, bug-injection, final report packaging, flush behavior, coherence-probe, write-miss eviction replay, GenSpec, and line coverage closure stages completed and generated corresponding `docs/ucagent_output/*.md` artifacts.
- The bug-injection evidence is recorded in `docs/bug_tracking.md`; the intentional failure is kept out of the normal regression suite.

## UCAgent Integration Status

Current verification progress is real and reproducible. The project now has ten Cache-specific UCAgent stage artifacts covering audit, backpressure, CRV/coverage, dirty-writeback closure, bug-injection evidence, final report packaging, flush behavior, coherence probe, write-miss eviction replay, GenSpec, and line coverage closure (DIR-014/015/016).

- Existing work: Codex implemented and ran the Cache verification files in this workspace.
- Verified outside this workspace: `instruction.md` proves the local UCAgent -> Codex -> MCP `Complete` path can run.
- Verified inside this workspace: `configs/ucagent_track1_cache.yaml` ran the configured Cache stages through UCAgent/Codex or UCAgent/Claude Code, recorded stage journals, and called `Complete`.
- Ready for submission: configured UCAgent stages through coherence are complete, post-coherence directed tests are clean, regression is clean, and the reproducibility entry is validated.
- Config check passed: `ucagent --emulate-config --force-stage-index 1` recognized all stages and selected the backpressure stage.
- Final report packaging completed. See `docs/ucagent_output/final_report_stage.md`.
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
│   │   ├── coherence_probe_stage.md
│   │   ├── crv_coverage_stage.md
│   │   ├── dirty_writeback_stage.md
│   │   ├── final_report_stage.md
│   │   ├── flush_stage.md
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
│   ├── corner/
│   ├── directed/
│   ├── random/
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

## Verification Complete

All planned verification work is complete for the current submission package:

1. Line coverage closure completed: DIR-014 (probe hit full release), DIR-015 (read-burst hit), DIR-016 (needFlush de-assertion), and Category J waiver applied. RTL line coverage at 1359/1364 (99.6%).
2. Bug-injection harness preserved outside the normal regression path so `scripts/run_regression.sh` remains clean at `30 passed in 5.43s`.
3. Full reproducibility entry `scripts/reproduce.sh` validated and passes.

## Template-Aligned Report Set

The UCAgent template-style integrated Markdown deliverables are under:

```text
unity_test/
```

The files `unity_test/Cache_basic_info.md`, `unity_test/Cache_verification_needs_and_plan.md`, `unity_test/Cache_functions_and_checks.md`, `unity_test/Cache_line_coverage_analysis.md`, `unity_test/Cache_bug_analysis.md`, and `unity_test/Cache_test_summary.md` consolidate the detailed process records from `docs/`.

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
