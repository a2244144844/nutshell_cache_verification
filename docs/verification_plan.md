# Verification Plan

## Objective

Verify the NutShell Cache design using a UCAgent-assisted and human-reviewed verification flow. The target result is a reproducible verification environment with structured Toffee components, constrained random tests, functional coverage, scoreboard checks, and bug-detection evidence.

Important status clarification:

- The executable Cache verification environment is already progressing through Picker/Python/Codex work.
- The Cache task now has UCAgent-orchestrated audit, backpressure, CRV/coverage, dirty-writeback closure, bug-injection evidence, final-report, flush, and coherence-probe stages, plus post-coherence directed-test closure work recorded in the AI collaboration log.
- `docs/ucagent_operation_plan.md` defines how to turn the current work into a UCAgent-visible workflow with stage contracts, output files, and journal evidence.
- `docs/ucagent_output/stage_audit.md`, `docs/ucagent_output/backpressure_stage.md`, `docs/ucagent_output/crv_coverage_stage.md`, `docs/ucagent_output/dirty_writeback_stage.md`, `docs/ucagent_output/bug_injection_stage.md`, `docs/ucagent_output/final_report_stage.md`, `docs/ucagent_output/flush_stage.md`, and `docs/ucagent_output/coherence_probe_stage.md` are the current Cache-specific UCAgent output artifacts.

## UCAgent Stage Overlay

To better match the Track1 requirement, each technical phase below should be mirrored by a UCAgent stage.

| Verification Phase | UCAgent Stage Evidence Needed |
| --- | --- |
| Source preparation | Stage journal records source inventory, DUT boundary decision, and human correction from full NutShell RTL to Picker Cache DUT. |
| Picker export | Stage output includes Picker command, generated wrapper location, and export pass/fail result. |
| Smoke closure | Stage output includes smoke test file, runner, command result, and manual acceptance notes. |
| Structured environment | Stage output includes env/monitor/scoreboard/utils files and review notes explaining component ownership. |
| Directed tests | Stage output includes directed tests, regression result, waveform path, and updated test-point table. |
| CRV/coverage | Stage output includes random generator, coverage model, coverage report, and coverage-gap closure notes. |
| Bug evidence | Stage output includes injected-bug tests, scoreboard failure evidence, and bug tracking report. |

The first audit pass has been run through:

```sh
ucagent /Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache Cache \
  --config /Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/configs/ucagent_track1_cache.yaml \
  --backend codex \
  --exit-on-completion
```

Audit result:

- Stage: `cache_regression_audit`
- Output: `docs/ucagent_output/stage_audit.md`
- Result at audit time: `scripts/run_regression.sh` passed with `4 passed in 0.11s`
- UCAgent evidence: Codex backend called `SetCurrentStageJournal`, `Complete`, and `Exit`.

Backpressure result:

- Stage: `backpressure_directed_tests`
- Output: `docs/ucagent_output/backpressure_stage.md`
- Current supervised result: `scripts/run_regression.sh` passed with `6 passed in 0.11s`

CRV/coverage result:

- Stage: `crv_coverage_bootstrap`
- Output: `docs/ucagent_output/crv_coverage_stage.md` and `docs/coverage_report.md`
- Current supervised result: `scripts/collect_coverage_multi.sh` passed with `37 passed`; `scripts/run_regression.sh` passed with `37 passed`
- Known gap: none — functional coverage at 12 groups, 31 points, 37 bins, all 100% covered.

Dirty writeback closure result:

- Stage: `dirty_writeback_coverage_closure`
- Output: `docs/ucagent_output/dirty_writeback_stage.md` and `docs/coverage_report.md`
- Current supervised result: `scripts/collect_coverage_multi.sh` passed with `37 passed`; `scripts/run_regression.sh` passed with `37 passed`
- Coverage delta: `dirty_miss_writeback_refill` moved from `0` to `1`; later expanded to 15 groups, 95 bins (including P2-10 cross-dimension coverage groups).

Bug-injection evidence result:

- Stage: `bug_injection_evidence`
- Output: `docs/ucagent_output/bug_injection_stage.md` and `docs/bug_tracking.md`
- Current supervised result: `tests/injected_bug/run_bug_injection.py` exited with code `1` with the expected scoreboard failure; `tests/injected_bug/run_bug_injection.py --disable-bug` exited with code `0`; 6 bug-injection tests total (BUG-001 through BUG-006); `scripts/run_regression.sh` passed with `37 passed`

## Phase 0: Workspace And Source Preparation

Status: source/workspace inventory completed; Picker installation completed; selected DUT copied, Picker export validated, first smoke test implemented, and the first structured Python verification environment skeleton created.

Tasks:

- Confirm local UCAgent/Codex availability.
- Collect competition instructions and source references.
- Clone the GitLink task environment repository.
- Fetch the NutShell Cache source reference.
- Install local Java runtime and Mill matching NutShell `.mill-version`.
- Generate NutShell RTL from the Chisel source.
- Decide the DUT wrapper boundary for Picker export.
- Copy Picker `example/Cache` RTL into the competition workspace.
- Validate Picker export and generated Python wrapper for the selected DUT.

Exit criteria:

- `docs/source_inventory.md` identifies all required sources and current gaps.
- A concrete selected DUT exists and can be exported by Picker.

Result:

- Workspace skeleton created.
- GitLink task template cloned.
- NutShell Cache source and documentation links verified as reachable.
- Local tool probe completed.
- Picker installed and validated with a small Adder export/import/run smoke test.
- Java runtime and Mill installed locally through `scripts/env.sh`.
- NutShell `BOARD=sim CORE=inorder` RTL generation completed as source-context exploration.
- Selected DUT boundary fixed at `rtl/dut/Cache.v`, copied from Picker `example/Cache/Cache.v`.
- `scripts/export_cache_dut.sh` validates Picker export and Python wrapper generation.
- First structured environment modules now wrap `DUTCache` access for reset, request driving, monitoring, and scoreboard checks.
- Current action: final documentation and submission package synchronization.

## Phase 1: DUT Understanding And Minimal Closure

Tasks:

- Read Cache documentation and `Cache.scala`.
- Extract top-level interfaces, transaction types, state machines, and major internal paths.
- Produce an interface map and feature/test-point list.
- Use the Picker-generated `DUTCache` wrapper.
- Run reset plus one basic read/write smoke test.

Deliverables:

- `docs/interface_map.md`
- `docs/test_points.md`
- `scripts/run_smoke.sh`
- `tests/smoke/`

Note: `docs/cache_architecture.md` was not created as a standalone document; the architecture description is incorporated into `docs/interface_map.md` and `docs/source_inventory.md`.

Current result:

- `docs/interface_map.md` created.
- `docs/test_points.md` created.
- `scripts/run_smoke.sh` created and passing.
- `tests/smoke/test_cache_basic.py` covers reset, read miss/refill, read hit, write hit, and read-after-write.
- Smoke now uses `src/env/cache_env.py`, `src/monitor/cache_monitor.py`, `src/scoreboard/cache_scoreboard.py`, and `src/utils/simplebus.py`.

## Phase 2: Structured Verification Environment

Tasks:

- Build Toffee-style environment structure.
- Implement Generator, Driver, Monitor, Scoreboard, and memory/reference model.
- Split tests into smoke, directed corner cases, random tests, and injected-bug tests.

Deliverables:

- `src/env/`
- `src/generator/`
- `src/monitor/`
- `src/scoreboard/`
- `src/utils/`
- `scripts/run_regression.sh`

Current result:

- `src/env/cache_env.py` provides the first reusable DUT wrapper, reset sequence, cycle stepping, CPU request driver, simple memory response handling, and monitor hooks.
- `src/monitor/cache_monitor.py` records CPU requests, CPU responses, and memory requests.
- `src/scoreboard/cache_scoreboard.py` checks current smoke-level read/write responses and memory request expectations.
- `src/utils/simplebus.py` centralizes SimpleBus command constants and request/response data classes.
- `tests/directed/test_write_masks.py` covers partial byte-mask writes on a cache hit.
- `tests/directed/test_word_offsets.py` covers independent hit writes/reads across all 8 word offsets in one cache line.
- `tests/directed/test_refill_beats.py` covers full 8-beat refill order from a nonzero word offset.
- `tests/directed/test_invalid_way_replacement.py` covers invalid-way replacement priority over random victim selection.
- `tests/directed/test_mmio_bypass.py` covers MMIO read/write routing through `io_mmio_*` and no-cache-hit behavior.
- `tests/directed/test_flush_behavior.py` covers flush behavior during idle and in-flight states, verifying `io_empty` and cache recovery (io_flush[0] only; io_flush[1] gated by D-cache assertion).
- `tests/directed/test_coherence_probe.py` covers coherence probe hit/miss responses through `io_out_coh_req_*` and `io_out_coh_resp_*`.
- `tests/directed/test_write_miss.py` covers clean write-miss refill and write-data merge behavior.
- `tests/directed/test_clean_eviction.py` covers clean victim replacement without writeback.
- `tests/directed/test_write_miss_dirty_eviction.py` covers write-miss dirty eviction, writeback-before-refill ordering, and partial-mask merge after refill.
- `scripts/run_directed.sh` and `scripts/run_regression.sh` provide directed-only and smoke-plus-directed commands.
- Current directed result: `scripts/run_directed.sh` passes with `27 passed`.
- Current regression result: `scripts/run_regression.sh` passes with `37 passed`.
- Current UCAgent result: 18 stages (0-17) completed through `configs/ucagent_track1_cache.yaml` with Claude Code backend; all stage artifacts under `docs/ucagent_output/`.

## Phase 3: CRV And Coverage Closure

Tasks:

- Implement constrained random traffic.
- Add directed tests for miss/hit, replacement, dirty writeback, MMIO, flush, and burst paths.
- Build functional coverage points and coverage bins.
- Iterate on coverage gaps.

Target coverage:

- Functional coverage: as close to 100% as practical, with 90%+ as the first milestone.
- Line coverage: collect if available from the RTL simulation flow, with the GitLink task reference mentioning 96%+ effective line coverage.
- Verilator RTL line coverage: enabled via `-c` flag in Picker export; results available in `build/reports/line_dat/index.html` (LCOV HTML) and `build/reports/cache_coverage.html` (toffee HTML).
- Line coverage waiver: `docs/coverage_waiver_rationale.md` documents all waived and pending lines; waivers applied via `ignore_patterns` in `tests/conftest.py`.

Deliverables:

- `tests/random/`
- `tests/corner/`
- `docs/coverage_report.md`
- `docs/coverage_waiver_rationale.md`
- `scripts/collect_coverage.sh`

Current result:

- `src/generator/cache_random.py` provides deterministic constrained random read/write traffic.
- `src/utils/cache_coverage.py` records command type, hit/miss proxy, write-mask class, word offset, and refill path bins.
- `src/utils/toffee_coverage.py` records the broader Toffee functional coverage model, including probe, MMIO, flush, clean eviction, clean write miss, and dirty write miss bins.
- `tests/random/test_random_cache.py` passes through `scripts/collect_coverage.sh 7 18`.
- `tests/directed/test_dirty_writeback.py` closes the dirty-victim writeback/refill gap with a 4-way set conflict and validates the writeback/refill sequence.
- `docs/coverage_report.md` records the full coverage bootstrap. Covered bins include read/write/probe commands, hit/miss proxy, write-mask classes, all word offsets, coherence probe, clean eviction, and `dirty_miss_writeback_refill`.
- Toffee functional coverage result: 12 groups, 31 points, 37 bins, all 100% covered.
- Verilator RTL line coverage: **1359/1359 (100.0%)** after applying Category A-K and D waivers (21 lines). See `docs/coverage_waiver_rationale.md` for full per-line analysis.
- Verilator RTL branch coverage: **471/471 (100.0%)** after applying Category L-N waivers (23 branches). See `docs/coverage_waiver_rationale.md`.
- Verilator RTL expr coverage: **137/137 (100.0%)** after applying Category O waiver (6 expressions).
- Verilator RTL toggle coverage: **24947/28227 (88.4%)** with 3,280 structural misses waived under Categories T-A~T-F (documentation-based). See `docs/toggle_coverage_waiver.md`.
- Line coverage waivers applied via `tests/conftest.py` using `ignore_patterns`: `*Cache_top*` (Picker-generated DPI wrapper) and `Cache.v:138,148,150,152,202-207,240-241,262,263,274,411,420,460,524,532,550,555,558,605,608,610,626,768,777,787,788,796,824,876,877,889,900,901,913,924,925,937,948,949,961,2267,2276,2316,2418,2674,2861-2862` (48 DUT lines/expressions: Categories A-O).
- UCAgent stages `crv_coverage_bootstrap`, `dirty_writeback_coverage_closure`, `line_coverage_closure`, `line_coverage_100`, `branch_coverage_closure`, `toggle_coverage_improvement`, `toggle_improvement_final`, `expr_coverage_closure`, and `toggle_waiver_docs` record coverage progress in `docs/ucagent_output/`.
- Toffee functional coverage result: 12 groups, 31 points, 37 bins, all 100% covered.
- Current action: first-prize gap closure per `docs/gap_analysis_first_prize.md`.

## Phase 4: Bug Injection And Detection Evidence

Tasks:

- Create controlled bug scenarios.
- Demonstrate detection through scoreboard, monitor checks, or assertions.
- Record trigger, symptom, root cause, fix, and rerun result.

Candidate injected bugs:

- Incorrect hit/miss decision.
- Wrong replacement way.
- Dirty bit update error.
- Writeback address/data mismatch.
- Refill data corruption.
- Response dropped under backpressure.

Deliverables:

- `tests/injected_bug/`
- `docs/bug_tracking.md`

Current result:

- `tests/injected_bug/run_bug_injection.py` injects a reference-model-only one-bit expected-data corruption.
- The default run trips `CacheScoreboard.check_read_response()` with expected `0x1122334455667789` versus actual `0x1122334455667788`.
- `--disable-bug` runs the same flow against the clean reference model and exits successfully.
- The normal `scripts/run_regression.sh` suite remains clean with `37 passed`.
- Bug injection expansion planned per `docs/gap_analysis_first_prize.md` P0-2 (BUG-003 through BUG-006).

## Phase 5: Final Report And Reproducibility

Tasks:

- Complete verification report.
- Complete AI collaboration report.
- Ensure one-command smoke/regression/coverage flows.
- Clean intermediate files.

Deliverables:

- `README.md`
- `docs/coverage_report.md`
- `docs/bug_tracking.md`
- `docs/ai_collaboration_report.md`
- final test report package.

Current result:

- `scripts/reproduce.sh` provides a one-command reproducibility entry: regression, coverage collection, expected-failure bug injection, and recovery path, validated with `scripts/clean_generated.sh && scripts/reproduce.sh -> PASS`.
- `scripts/clean_generated.sh` removes generated build, cache, Python bytecode, and wave artifacts.
- `scripts/run_bug_injection.sh` wraps the controlled bug-injection harness with `--disable-bug` recovery mode.
- `README.md`, `docs/ai_collaboration_report.md`, and `docs/coverage_report.md` have been iterated through the UCAgent stages and post-coherence directed-test closure.
- Final report packaging has been refreshed after the post-final directed tests. `docs/ucagent_output/final_report_stage.md` records the reviewed files, command results, submission checklist, and remaining risks.
- Latest validation: `scripts/run_directed.sh -> 27 passed`; `scripts/run_regression.sh -> 37 passed`; `scripts/collect_coverage_multi.sh -> 37 passed`; `scripts/reproduce.sh -> [reproduce] PASS`.
- RTL line coverage: **1359/1359 (100.0%)**.
- RTL branch coverage: **471/471 (100.0%)**.
- RTL expr coverage: **137/137 (100.0%)**.
- RTL toggle coverage: **24947/28227 (88.4%)**.
