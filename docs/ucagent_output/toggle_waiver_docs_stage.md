# Stage 18: Toggle Waiver Documentation Closure

Date: 2026-05-31 | UCAgent Stage: `toggle_waiver_docs`

## Context

After Stage 17 confirmed the toggle coverage plateau at 88.4% (24947/28227), this stage formalizes the toggle waivers across all GenSpec and project documentation.

## Final Coverage

```
Line:   1359/1359 = 100.0%
Branch: 471/471  = 100.0%
Toggle: 24947/28227 = 88.4%  (waived: 3,280, Categories T-A~T-F)
Expr:   137/137 = 100.0%
37 tests, 0 failures
```

## Waiver Mechanism

Toggle waivers are **documentation-based** — they are NOT encoded in `conftest.py` `ignore_patterns`. This is because:

1. `toffee_test`'s `filter_coverage()` has no type-awareness — it filters ALL coverage types (line/branch/toggle/expr) by line number indiscriminately
2. Adding 195+ line ranges for toggle-only misses would mask future line/branch/expr regressions on those same lines
3. GenSpec does not require 100% toggle coverage — the focus is on line, branch, and functional coverage
4. The waiver categories (T-A through T-F) are well-documented with clear structural rationale

## Waiver Categories

| Category | Description | Affected Modules |
|---|---|---|
| T-A | SRAM address/data bus bits | SRAMTemplate, SRAMTemplateWithArbiter, SRAMTemplate_1, Arbiter_4 |
| T-B | D-cache constant signals (hardwired to 0) | CacheStage3, CacheStage2, Cache |
| T-C | LFSR replacement bits (2^64 cycles) | Cache, Arbiter_4 |
| T-D | Assertion-only condition signals | CacheStage2, CacheStage3, Cache |
| T-E | Reset-only / tie-off signals | All |
| T-F | Unused/NC port bits | Arbiter, Arbiter_1, Arbiter_2, Arbiter_3 |

## Files Updated

- `unity_test/Cache_functions_and_checks.md` + `_zh.md` — Added Stage 17 FC group, updated toggle CKs, final coverage numbers
- `unity_test/Cache_spec_summary.md` + `_zh.md` — Updated toggle coverage to 88.4%
- `unity_test/Cache_line_map_analysis.md` + `_zh.md` — Updated toggle section with plateau confirmation
- `unity_test/Cache_verification_needs_and_plan.md` + `_zh.md` — Updated stage plan table, exit criteria
- `unity_test/Cache_test_summary.md` + `_zh.md` — Updated test counts, coverage table, notes
- `docs/coverage_waiver_rationale.md` + `_zh.md` — Updated toggle waiver references
- `docs/toggle_coverage_waiver.md` + `_zh.md` — Already updated in Stage 17
- `docs/test_points.md` + `_zh.md` — Already updated in Stage 17
- `docs/ai_collaboration_report.md` + `_zh.md` — Already updated in Stage 17
- `docs/ucagent_output/toggle_waiver_docs_stage.md` + `_zh.md` — This artifact

## Verdict

Toggle coverage at 88.4% is the practical maximum for this I-cache DUT. All remaining 3,280 misses are structural and formally waived under Categories T-A through T-F with documentation-based waivers.
