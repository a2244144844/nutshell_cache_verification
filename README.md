# Track1 NutShell Cache Verification Workspace

This workspace is for the CCF Track1 UCAgent competition task: verifying the NutShell Cache with UCAgent-assisted, human-reviewed verification engineering.

## Reviewer Quick Start (3 Commands)

1. **Reproduce**: `make reproduce`
   - Expected: `[reproduce] PASS` (regression + coverage + bug injection + recovery)

2. **Coverage Reports**:
   - RTL: `open build/reports/rtl_coverage.html` — Line 100.0% | Branch 100.0% | Toggle 88.4% | Expr 100.0%
   - Funcov: `open build/reports/cache_coverage.html` — 18 groups, 91 points, 98 bins, all 100%

3. **Key Documents** (recommended reading order):

   | Doc | Purpose |
   |-----|---------|
   | `docs/ai_collaboration_report.md` | AI-human collaboration log, defects table, prompt strategy, 17 stages |
   | `docs/verification_plan.md` | Phased verification plan with current status |
   | `docs/coverage_waiver_rationale.md` | Per-line waiver analysis (15 categories, 48 waived lines/expressions) |
   | `docs/gap_analysis_first_prize.md` | First-prize gap analysis and improvement action plan |

## Current Status

- UCAgent and Claude Code CLI are available on this machine.
- 18 UCAgent stages (0-17) completed through `configs/ucagent_track1_cache.yaml` with Claude Code backend.
- The selected DUT is Picker's Cache example RTL copied to `rtl/dut/Cache.v`.
- Picker exports the selected DUT as Python class `DUTCache`.
- `make test-smoke` passes the first reset/read/write smoke test.
- Structured verification environment under `src/env`, `src/monitor`, `src/scoreboard`, `src/utils`, and `src/generator`.
- 84 tests across smoke, directed, corner, random, and multi-seed random suites.
- Directed tests cover: partial write masks, word offsets, refill beats, replacement, MMIO bypass, flush, coherence probe, write miss, clean eviction, dirty writeback, read-burst hit, write-miss dirty eviction, and PREFETCH.
- `make test-directed` passes with `81 passed`.
- `make test` passes with `84 passed`.
- `make coverage-multi` passes with Toffee functional coverage: 18 groups, 91 points, 98 bins, all 100% covered.
- RTL coverage: **Line 1359/1359 (100.0%) | Branch 471/471 (100.0%) | Toggle 24947/28227 (88.4%) | Expr 137/137 (100.0%)**.
- 48 lines/expressions waived across Categories A-O (see `docs/coverage_waiver_rationale.md`).
- Toggle waiver: 3,280 misses waived Categories T-A~T-F (see `docs/toggle_coverage_waiver.md`).
- `make reproduce` is the one-command reproducibility entry and passes from a cleaned generated-artifact state.
- Bug-injection evidence recorded in `docs/bug_tracking.md`; kept out of normal regression suite.

## UCAgent Integration Status

All 18 configured UCAgent stages (0-17) are complete with artifacts under `docs/ucagent_output/`. The competition workflow is defined in `configs/ucagent_track1_cache.yaml`. Integration plan: see `docs/ucagent_operation_plan.md`.

## Working Directories

```text
./
├── LICENSE
├── Makefile
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

All planned verification work is complete:

1. Line coverage: 1359/1359 (100.0%), 21 lines waived (Categories A-K, D).
2. Branch coverage: 471/471 (100.0%), 23 branches waived (Categories L-N).
3. Expr coverage: 137/137 (100.0%), 6 expressions waived (Category O).
4. Toggle coverage: 24947/28227 (88.4%), 3,280 toggles waived (Categories T-A~T-F, documentation-based).
5. Functional coverage: 18 groups, 91 points, 98 bins, all 100% covered.
6. Bug-injection harness preserved outside normal regression path; `make test` remains clean at `84 passed`.
7. Full reproducibility entry `make reproduce` validated and passes.

## Template-Aligned Report Set

The UCAgent template-style integrated Markdown deliverables are under:

```text
unity_test/
```

The files `unity_test/Cache_basic_info.md`, `unity_test/Cache_verification_needs_and_plan.md`, `unity_test/Cache_functions_and_checks.md`, `unity_test/Cache_line_coverage_analysis.md`, `unity_test/Cache_bug_analysis.md`, and `unity_test/Cache_test_summary.md` consolidate the detailed process records from `docs/`.

## Reproducibility

Run the main reproducibility entry from this workspace:

```sh
make reproduce
```

It runs normal regression, coverage collection with seed `7` and `18` transactions by default, the expected-failure bug injection, and the disabled-bug recovery path. Generated build, cache, Python bytecode, and wave artifacts can be removed with:

```sh
make clean
```

Latest validation:

```text
make clean && make reproduce -> PASS
```
