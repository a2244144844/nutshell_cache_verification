# Reviewer Quick Start

This document is the short evaluation route for the Track1 NutShell Cache verification package.

## 1. Reproduce

Run from the workspace root:

```sh
make reproduce
```

Expected final line:

```text
[reproduce] PASS
```

Latest local validation:

```text
2026-06-03 15:12 CST
make reproduce -> PASS
normal regression: 84 passed
coverage suite: 86 passed, Toffee funcov 91/91 points and 98/98 bins
RTL coverage from default reproduce: line 100.0%, branch 100.0%, expr 100.0%, toggle 87.8%
bug injection: expected scoreboard failure observed; disabled-bug recovery passed
```

The reproduce target runs:

- normal regression: smoke + directed + corner tests
- full coverage collection over `tests/`
- expected-failure bug injection
- disabled-bug recovery run

For a fast sanity check:

```sh
make test-smoke
```

Expected result:

```text
1 passed
```

## 2. Read Reports

Recommended review order:

| Artifact | Why it matters |
| --- | --- |
| `final_report/nutshell_cache_report.pdf` | Polished final competition report |
| `docs/verification_plan.md` | Verification scope, phases, and exit criteria |
| `docs/coverage_report.md` | Functional coverage summary generated from the latest coverage run |
| `docs/bug_tracking.md` | Bug-injection evidence and scoreboard detection path |
| `docs/ai_collaboration_report.md` | AI-human collaboration, manual corrections, and prompt strategy |
| `docs/coverage_waiver_rationale.md` | Line/branch/expression waiver rationale |
| `docs/toggle_coverage_waiver.md` | Toggle waiver rationale |
| `unity_test/Cache_test_summary.md` | UCAgent template-aligned final test summary |

## 3. Coverage Targets

Latest recorded closure:

| Coverage type | Result |
| --- | --- |
| Toffee functional coverage | 18 groups, 91 points, 98 bins, all bins covered |
| RTL line coverage | 1359/1359, 100.0% |
| RTL branch coverage | 471/471, 100.0% |
| RTL expression coverage | 137/137, 100.0% in final report set |
| RTL toggle coverage | 24775/28227, 87.8% in default reproduce; 24947/28227, 88.4% in multi-seed final report set; documented waiver |

Note: `86 passed` is the pytest test-case count; `91/91 points` is the Toffee functional-coverage point count. They are intentionally different metrics and do not need to match.

## 4. Source Map

| Directory | Content |
| --- | --- |
| `src/env` | Cache environment and DUT lifecycle |
| `src/generator` | Constrained-random transaction generation |
| `src/monitor` | Bus-level observation helpers |
| `src/scoreboard` | Reference checking and data consistency |
| `src/utils` | SimpleBus definitions and coverage utilities |
| `tests/smoke` | Minimal read/write path proof |
| `tests/directed` | Replacement, dirty writeback, refill, probe, flush, MMIO, write-mask tests |
| `tests/corner` | Backpressure scenarios |
| `tests/random` | CRV and multi-seed random traffic |
| `tests/injected_bug` | Expected-failure bug-injection harness |

## 5. Submission Boundary

The intended submission root is the workspace root.

Source-controlled deliverables:

- `README.md`, `LICENSE`, `Makefile`
- `src/`, `tests/`, `scripts/`, `rtl/`, `configs/`
- `docs/`, `unity_test/`, `uc_test_report/`, `final_report/`

Generated or local-heavy artifacts:

- `build/`, `local/`, `tools/`
- `cache.vcd`, `*_coverage.dat`
- Python caches and wave files

These generated directories are useful on this workstation for fast reruns, but they are not required for source review because the reproducible commands and evidence documents are included.
