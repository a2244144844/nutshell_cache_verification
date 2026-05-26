# Verification Plan

## Objective

Verify the NutShell Cache design using a UCAgent-assisted and human-reviewed verification flow. The target result is a reproducible verification environment with structured Toffee components, constrained random tests, functional coverage, scoreboard checks, and bug-detection evidence.

Important status clarification:

- The executable Cache verification environment is already progressing through Picker/Python/Codex work.
- The Cache task now has UCAgent-orchestrated audit, backpressure, CRV/coverage, dirty-writeback closure, and bug-injection evidence stages.
- `docs/ucagent_operation_plan.md` defines how to turn the current work into a UCAgent-visible workflow with stage contracts, output files, and journal evidence.
- `docs/ucagent_output/stage_audit.md`, `docs/ucagent_output/backpressure_stage.md`, `docs/ucagent_output/crv_coverage_stage.md`, `docs/ucagent_output/dirty_writeback_stage.md`, and `docs/ucagent_output/bug_injection_stage.md` are the current Cache-specific UCAgent output artifacts.

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
- Current supervised result: `scripts/collect_coverage.sh 7 18` passed with `1 passed in 0.04s`; `scripts/run_regression.sh` passed with `7 passed in 0.14s`
- Known gap: none in the current functional-coverage bootstrap set.

Dirty writeback closure result:

- Stage: `dirty_writeback_coverage_closure`
- Output: `docs/ucagent_output/dirty_writeback_stage.md` and `docs/coverage_report.md`
- Current supervised result: `scripts/collect_coverage.sh 7 18` passed with `1 passed in 0.04s`; `scripts/run_regression.sh` passed with `7 passed in 0.14s`
- Coverage delta: `dirty_miss_writeback_refill` moved from `0` to `1`.

Bug-injection evidence result:

- Stage: `bug_injection_evidence`
- Output: `docs/ucagent_output/bug_injection_stage.md` and `docs/bug_tracking.md`
- Current supervised result: `tests/injected_bug/run_bug_injection.py` exited with code `1` with the expected scoreboard failure; `tests/injected_bug/run_bug_injection.py --disable-bug` exited with code `0`; `scripts/run_regression.sh` passed with `7 passed in 0.14s`

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
- Next action: complete the final report package and reproducibility cleanup.

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
- `scripts/run_directed.sh` and `scripts/run_regression.sh` provide directed-only and smoke-plus-directed commands.
- Current directed result: `scripts/run_directed.sh` passes with `3 passed`.
- Current regression result: `scripts/run_regression.sh` passes with `7 passed`.
- Current UCAgent audit result: `configs/ucagent_track1_cache.yaml` stage `cache_regression_audit` passes and records `docs/ucagent_output/stage_audit.md`.

## Phase 3: CRV And Coverage Closure

Tasks:

- Implement constrained random traffic.
- Add directed tests for miss/hit, replacement, dirty writeback, MMIO, flush, and burst paths.
- Build functional coverage points and coverage bins.
- Iterate on coverage gaps.

Target coverage:

- Functional coverage: as close to 100% as practical, with 90%+ as the first milestone.
- Line coverage: collect if available from the RTL simulation flow, with the GitLink task reference mentioning 96%+ effective line coverage.

Deliverables:

- `tests/random/`
- `tests/corner/`
- `docs/coverage_report.md`
- `scripts/collect_coverage.sh`

Current result:

- `src/generator/cache_random.py` provides deterministic constrained random read/write traffic.
- `src/utils/cache_coverage.py` records command type, hit/miss proxy, write-mask class, word offset, and refill path bins.
- `tests/random/test_random_cache.py` passes through `scripts/collect_coverage.sh 7 18`.
- `tests/directed/test_dirty_writeback.py` closes the dirty-victim writeback/refill gap with a 4-way set conflict and validates the writeback/refill sequence.
- `docs/coverage_report.md` records the full coverage bootstrap. Covered bins include read/write commands, hit/miss proxy, write-mask classes, all word offsets, and `dirty_miss_writeback_refill`.
- UCAgent stages `crv_coverage_bootstrap` and `dirty_writeback_coverage_closure` record these results in `docs/ucagent_output/crv_coverage_stage.md` and `docs/ucagent_output/dirty_writeback_stage.md`.
- Next action: complete the final report package and reproducibility cleanup.

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
- The normal `scripts/run_regression.sh` suite remains clean with `7 passed in 0.14s`.

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
- `README.md`, `docs/ai_collaboration_report.md`, and `docs/coverage_report.md` have been iterated across multiple UCAgent stages and remain the final-deliverable candidates.
- Final report packaging and submission-ready review are still in progress.
