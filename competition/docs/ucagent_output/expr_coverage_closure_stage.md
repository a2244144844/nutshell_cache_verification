# Stage 16: Expr Coverage Closure — Category O Waiver

Date: 2026-05-31
UCAgent Stage: `17-expr_coverage_closure` (index 16)
Backend: Claude Code CLI

## Summary

Closed the remaining 6 expression coverage misses, bringing Expr from 131/137 (95.6%) to **131/131 (100.0%)** through Category O waivers (6 expression lines filtered from coverage count by ignore_patterns). All 6 expressions are Chisel-generated SVA assertion condition terms (`STOP_COND`) and internal dead-logic conditions, structurally unreachable in I-cache mode.

## Category O Detail

| Line | Module | Expression | Existing Category | Reason |
|---|---|---|---|---|
| 274 | CacheStage2 | `~(~(io_in_valid & _T_13)) & _T_16` | E | Waymask PopCount SVA condition |
| 787 | CacheStage3 | `_T_5 & needFlush` | D | needFlush always 0 in I-cache |
| 889 | CacheStage3 | `~(~(mmio & hit)) & ~reset` | A | MMIO+hit STOP_COND |
| 913 | CacheStage3 | `~(~(metaHitWriteBus_x5 & metaRefillWriteBus_req_valid)) & _T_3` | M | Meta conflict STOP_COND |
| 937 | CacheStage3 | `~(~(hitWrite & dataRefillWriteBus_x9)) & _T_3` | M | Data conflict STOP_COND |
| 961 | CacheStage3 | `~_T_38 & _T_3` | A/D | D-cache flush assertion STOP_COND |

All 6 expressions are structurally unreachable in I-cache. The underlying signals they protect against (MMIO+hit conflict, meta port conflict, data port conflict, D-cache flush, needFlush deassert) never occur in I-cache operation. Same root causes as existing Category A, D, E, M line/branch waivers.

## Files Changed

| File | Change |
|---|---|
| `tests/conftest.py` | Added 6 expr miss lines (274, 787, 889, 913, 937, 961) to ignore_patterns in sorted order; added Category O comment block |
| `docs/coverage_waiver_rationale.md` | Added Category O section; updated Summary, Post-Waiver Coverage, Final Waiver Summary, Post-Stage-12 Coverage, Waiver Implementation |
| `docs/coverage_waiver_rationale_zh.md` | Added Category O section (Chinese); updated ignore_patterns, coverage numbers |
| `unity_test/Cache_functions_and_checks.md` | Added CK-WAIVER-CAT-O; updated final coverage numbers |
| `unity_test/Cache_functions_and_checks_zh.md` | Updated coverage numbers to include Expr 100% |
| `unity_test/Cache_line_func_map.md` | Added Category O IGNORE mapping (lines 274,787,889,913,937,961) |
| `unity_test/Cache_line_func_map_zh.md` | Added Category O to waiver table |
| `unity_test/Cache_line_map_analysis.md` | Added Expr coverage section; updated Verification Closure Status |
| `unity_test/Cache_line_map_analysis_zh.md` | Added Expr coverage section (Chinese); updated Verification Closure Status |
| `docs/test_points.md` | Added Stage 16 entry |
| `docs/test_points_zh.md` | Added Stage 16 entry (Chinese) |
| `docs/ai_collaboration_report.md` | Added Stage 16 entry |
| `docs/ai_collaboration_report_zh.md` | Added Stage 16 entry (Chinese) |
| `top.md` | Added Stage 16 output file entries |
| `top_zh.md` | Added Stage 16 output file entries (Chinese) |

## ignore_patterns String (Final)

```
Cache.v:138,148,150,152,202-207,240-241,262,263,274,411,420,460,524,532,550,555,558,605,608,610,626,768,777,787,788,796,824,876,877,889,900,901,913,924,925,937,948,949,961,2267,2276,2316,2418,2674,2861-2862
```

## Commands Run

```bash
scripts/collect_coverage_multi.sh → 38 passed
```

## Coverage Delta

| Metric | Before (Stage 13) | After (Stage 16) | Delta |
|---|---|---|---|
| Expr | 131/137 (95.6%) | **131/131 (100.0%)** | +6 waived (Category O) |
| Line | 1359/1359 (100.0%) | 1359/1359 (100.0%) | — |
| Branch | 471/471 (100.0%) | 471/471 (100.0%) | — |
| Toggle | 24785/28227 (87.8%) | 24785/28227 (87.8%) | — |

Note: toffee_test ignore_patterns removes waived lines from both numerator and denominator. 6 expr waived → 131/131.

## Final Coverage

```
Line:   1359/1359 = 100.0%
Branch: 471/471  = 100.0%
Expr:   131/131 = 100.0%  (6 expr waived, 137 total)
Toggle: 24785/28227 = 87.8%
38 tests, 0 failures
```

All four coverage metrics are now at their final values. Line, Branch, and Expr are all at 100.0%. Toggle is at plateau (87.8%) with remaining 3442 misses structurally waived under Categories T-A through T-F.
