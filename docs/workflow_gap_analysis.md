# UCAgent Workflow Gap Analysis

Date: 2026-05-27

## Purpose

This document compares the current Track1 NutShell Cache verification workspace against the UCAgent standard workflow (11-stage verification + 6-stage GenSpec) to identify missing deliverables and structural gaps. The goal is to make the project fully aligned with UCAgent's recommended practice: **GenSpec first, then verification**.

For GenSpec Stage 1-2 planning, the current authoritative execution plan is [`docs/genspec_flow_plan.md`](docs/genspec_flow_plan.md).

## Reference Sources

| Source | URL |
| --- | --- |
| UCAgent GenSpec Workflow | https://ucagent.open-verify.cc/content/04_case/00_genspec/ |
| UCAgent Default 11-Stage Workflow | https://ucagent.open-verify.cc/content/03_develop/03_workflow/ |
| GenSpec Example Config | `examples/GenSpec/genspec.yaml` |
| GenSpec Spec Template | `examples/GenSpec/SpecDoc/dut_spec_template.md` |

## Current Project Status

- DUT: NutShell Cache (`rtl/dut/Cache.v`), exported via Picker as `DUTCache`
- Tests: 26 passed (smoke + directed + corner + random + bug injection)
- Coverage: Toffee 12 groups / 31 points / 37 bins (100%); RTL line coverage 1344/1366 (98.4%)
- UCAgent stages completed: Cache implementation stages plus supplemental write-miss/eviction replay and official GenSpec six-stage flow
- Reproducibility: `scripts/reproduce.sh` passes from clean state

## UCAgent Default 11-Stage Workflow Mapping

### Stage 1: Requirements Analysis and Verification Planning

| Item | Status |
| --- | --- |
| Expected output | `unity_test/Cache_verification_needs_and_plan.md` |
| Current file | `unity_test/Cache_verification_needs_and_plan.md` |
| Checker | `UnityChipCheckerMarkdownFileFormat` |
| Status | **PASS** — file exists and is structured |

### Stage 2: DUT Functional Understanding

| Item | Status |
| --- | --- |
| Expected output | `unity_test/Cache_basic_info.md` |
| Current file | `unity_test/Cache_basic_info.md` |
| Checker | `UnityChipCheckerMarkdownFileFormat` |
| Status | **PASS** — covers identity, interfaces, SimpleBus commands, constraints |

### Stage 3: Functional Specification Analysis (FG/FC/CK)

| Item | Status |
| --- | --- |
| Expected output | `unity_test/Cache_functions_and_checks.md` |
| Current file | `unity_test/Cache_functions_and_checks.md` |
| Checker | `UnityChipCheckerLabelStructure` (FG, FC, CK) |
| Status | **PASS** — has 5 FG groups and 45 CK labels after GenSpec functional-specification analysis |

Current FG/FC/CK structure:

| FG Group | FC Count | CK Count |
| --- | --- | --- |
| `FG-API` | 2 (HARNESS, SMOKE) | 9 |
| `FG-CORE-CACHE` | 3 (WRITE-MASK-OFFSET, REFILL-WRITE-MISS, REPLACEMENT-EVICTION) | 11 |
| `FG-MMIO-FLUSH-COH` | 3 (MMIO-BYPASS, FLUSH-BEHAVIOR, COHERENCE-PROBE) | 10 |
| `FG-BACKPRESSURE-CRV` | 2 (BACKPRESSURE, CRV-COVERAGE) | 8 |
| `FG-EVIDENCE` | 2 (BUG-INJECTION, REPORTING) | 7 |
| **Total** | **12** | **45** |

### Stage 4: Test Platform Infrastructure (DUT API + Fixtures)

| Item | Status |
| --- | --- |
| Expected output | `unity_test/tests/Cache_api.py` |
| Current file | `unity_test/tests/Cache_api.py` |
| Checker | `UnityChipCheckerDutCreation`, `UnityChipCheckerDutFixture`, `UnityChipCheckerEnvFixture` |
| Status | **PASS** — thin wrapper added over `src/env/cache_env.py` |

What exists:
- `src/env/cache_env.py` — `CacheEnv` class with reset, CPU request, memory response, MMIO, flush, probe helpers
- `tests/conftest.py` — pytest fixtures for `cache_env`, `mem_model`, `scoreboard`
- `src/scoreboard/cache_scoreboard.py` — read/write response checker
- `src/monitor/cache_monitor.py` — transaction recorder
- `src/utils/simplebus.py` — SimpleBus constants and data classes

Wrapper now provides:
- `create_dut(request=None, coverage=False, reset=True)`
- `cache_env` and `dut` pytest fixtures with lifecycle cleanup
- `api_cache_*` prefix helpers for reset, stepping, pin access, CPU requests, MMIO, memory response, and sampling

### Stage 5: Functional Coverage Model

| Item | Status |
| --- | --- |
| Expected output | `unity_test/tests/Cache_function_coverage_def.py` |
| Current file | `unity_test/tests/Cache_function_coverage_def.py` |
| Checker | `UnityChipCheckerCoverageGroup`, `UnityChipCheckerCoverageGroupBatchImplementation` |
| Status | **PASS** — thin wrapper added over `src/utils/toffee_coverage.py` |

What exists:
- `src/utils/cache_coverage.py` — records command type, hit/miss proxy, write-mask class, word offset, refill path bins
- `src/utils/toffee_coverage.py` — Toffee functional coverage model (12 groups, 31 points, 37 bins)

Wrapper now provides:
- `get_coverage_groups(dut)` returning Toffee `CovGroup` objects from `CacheCoverage`
- `create_coverage(dut)` for callers that need the full coverage object

### Stage 6: Basic API Implementation

| Item | Status |
| --- | --- |
| Expected output | `unity_test/tests/Cache_api.py` (API functions) |
| Current file | `unity_test/tests/Cache_api.py` |
| Checker | `UnityChipCheckerDutApi` |
| Status | **PASS** — `api_cache_*` prefix functions wrap the existing `CacheEnv` methods |

### Stage 7: Basic API Functional Tests

| Item | Status |
| --- | --- |
| Expected output | `unity_test/tests/test_cache_api_*.py` |
| Current state | Tests exist in `tests/smoke/`, `tests/directed/`, etc. but not in `test_cache_api_*` format |
| Checker | `UnityChipCheckerDutApiTest` |
| Status | **PARTIAL** — tests work but don't follow the standard `dut.fc_cover` marking convention |

### Stage 8: Test Framework Scaffolding

| Item | Status |
| --- | --- |
| Expected output | Placeholder test templates for uncovered CK points |
| Current state | All CK points have real implementations (no placeholders needed) |
| Checker | `UnityChipCheckerTestTemplate` |
| Status | **N/A** — all tests are implemented, scaffolding not needed |

### Stage 9: Full Verification Execution and Bug Analysis

| Item | Status |
| --- | --- |
| Expected output | `unity_test/Cache_bug_analysis.md` |
| Current file | `unity_test/Cache_bug_analysis.md` |
| Checker | `UnityChipCheckerTestCase` |
| Status | **PASS** — covers BUG-001 (reference model corruption) and BUG-RTL-001 (dirty writeback bypass) |

### Stage 10: Line Coverage Analysis and Improvement

| Item | Status |
| --- | --- |
| Expected output | `unity_test/Cache_line_coverage_analysis.md` |
| Current file | `unity_test/Cache_line_coverage_analysis.md` |
| Checker | `UnityChipCheckerTestCaseWithLineCoverage` |
| Status | **PASS** — 98.4% line coverage with waiver rationale |

### Stage 11: Verification Review and Summary

| Item | Status |
| --- | --- |
| Expected output | `unity_test/Cache_test_summary.md` |
| Current file | `unity_test/Cache_test_summary.md` |
| Checker | `UnityChipCheckerTestCase` |
| Status | **PASS** |

## GenSpec 6-Stage Workflow Mapping

### GenSpec Stage 1: Collect Existing Assets

| Item | Status |
| --- | --- |
| Expected output | `unity_test/Cache_spec.md` (main specification) |
| Current file | `unity_test/Cache_spec.md` |
| Checker | `MarkDownHeadChecker` |
| Status | **PASS** — generated by UCAgent GenSpec collect/augment stages |

What should be in `Cache_spec.md`:
- Design background (NutShell Cache role in RISC-V SoC)
- Terminology (SimpleBus, cache line, way, set, etc.)
- RTL source file inventory with `<ref_file>` tags
- Top-level interface table (all ports with direction, width, reset value)
- Functional description (cacheable traffic, MMIO bypass, flush, coherence probe)
- State machine description (CacheStage3 states)
- Configuration parameters
- Verification requirements summary
- Potential bug analysis

### GenSpec Stage 2: Augment with Code

| Item | Status |
| --- | --- |
| Expected output | `Cache_spec.md` enriched with RTL source analysis |
| Current file | `unity_test/Cache_spec.md` |
| Checker | `WalkFilesOneByOne` |
| Status | **PASS** — enriched through the augment-with-code stage |

### GenSpec Stage 3: Complete Sub-specs

| Item | Status |
| --- | --- |
| Expected output | `unity_test/Cache_spec_*.md` (sub-module specs) |
| Current file | `unity_test/Cache/` |
| Checker | `BatchMarkDownHeadChecker` |
| Status | **PASS** — six sub-specs generated |

Generated sub-specs:
- `unity_test/Cache/CacheStage1_spec.md`
- `unity_test/Cache/CacheStage2_spec.md`
- `unity_test/Cache/CacheStage3_spec.md`
- `unity_test/Cache/MetaDataArray_spec.md`
- `unity_test/Cache/DataArray_spec.md`
- `unity_test/Cache/Replacement_spec.md`

### GenSpec Stage 4: Human Check

| Item | Status |
| --- | --- |
| Expected output | `unity_test/Cache_spec_summary.md` |
| Current file | `unity_test/Cache_spec_summary.md` |
| Checker | `HumanChecker` |
| Status | **REVIEWED** — human_check summary generated; continuation was manually approved and resumed from stage 4 |

### GenSpec Stage 5: Functional Specification Analysis

| Item | Status |
| --- | --- |
| Expected output | `unity_test/Cache_functions_and_checks.md` |
| Current file | `unity_test/Cache_functions_and_checks.md` |
| Checker | `UnityChipCheckerLabelStructure` (FG, FC, CK) |
| Status | **PASS** — regenerated/validated by GenSpec with 5 FG groups and 45 CK labels |

### GenSpec Stage 6: Function-Line Map Generation

| Item | Status |
| --- | --- |
| Expected output | `unity_test/Cache_line_func_map.md` |
| Current file | `unity_test/Cache_line_func_map.md` |
| Checker | `FileLineMapChecker` |
| Status | **PASS** — `FileLineMapChecker` passed; all `Cache/Cache.v` lines are mapped or ignored |

What should be in `Cache_line_func_map.md`:
- Mapping from each CK label to specific `Cache.v` line numbers
- Traceability from functional coverage points to RTL code
- Gap analysis between documented functions and actual RTL paths

## Summary: Missing Deliverables

### High Priority (blocks standard workflow compliance)

| # | File | Source Stage | Effort |
| --- | --- | --- | --- |
| 1 | `unity_test/Cache_spec.md` | GenSpec 1-2 | **DONE** — generated by UCAgent GenSpec |
| 2 | `unity_test/tests/Cache_api.py` | Default 4, 6 | **DONE** — thin wrapper over `CacheEnv` |
| 3 | `unity_test/tests/Cache_function_coverage_def.py` | Default 5 | **DONE** — thin wrapper over `CacheCoverage` |

### Medium Priority (improves completeness and traceability)

| # | File | Source Stage | Effort |
| --- | --- | --- | --- |
| 4 | `unity_test/Cache/` sub-specs | GenSpec 3 | **DONE** |
| 5 | `unity_test/Cache_line_func_map.md` | GenSpec 6 | **DONE** |
| 6 | `unity_test/Cache_spec_summary.md` | GenSpec 4 | **DONE** |

### Low Priority (nice to have)

| # | File | Source Stage | Effort |
| --- | --- | --- | --- |
| 7 | `unity_test/tests/test_cache_api_*.py` | Default 7 | Small — rename/restructure existing tests |
| 8 | Test templates (placeholders) | Default 8 | N/A — all tests implemented |

## Recommended Execution Order

```
Phase A: GenSpec (规范生成)
  A1. Create genspec_cache.yaml config
  A2. Run GenSpec Stage 1-3: generate Cache_spec.md + sub-specs
  A3. Run GenSpec Stage 4: human_check (manual review)
  A4. Run GenSpec Stage 5: regenerate Cache_functions_and_checks.md if needed
  A5. Run GenSpec Stage 6: generate Cache_line_func_map.md

Phase B: Standard API (标准 API 补全)
  B1. Create unity_test/tests/Cache_api.py (create_dut, fixtures, api_cache_*)
  B2. Create unity_test/tests/Cache_function_coverage_def.py
  B3. Verify UnityChipCheckerDutCreation/DutFixture/DutApi pass

Phase C: Validation (验证)
  C1. Run all existing tests to confirm no regression
  C2. Run UCAgent with standard config to verify checker compliance
  C3. Update this document with final status
```

Current status: Phases A, B, and C are complete. Wrapper syntax validation passed, `scripts/run_regression.sh` passed with `28 passed in 5.76s`, and `scripts/reproduce.sh` finished with `[reproduce] PASS`.

## Notes

- The existing verification work (26 tests, 98.4% coverage) is solid and should not be disrupted by the restructuring.
- The GenSpec workflow is documentation-focused and does not generate test code.
- The standard API file (`Cache_api.py`) can wrap existing `CacheEnv` methods without changing test behavior.
- Sub-specs for CacheStage1/2/3/CacheData are optional for the competition but would demonstrate thorough UCAgent integration.
