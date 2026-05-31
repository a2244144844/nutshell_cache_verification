# Stage 16：表达式覆盖率闭环 — Category O 豁免

日期：2026-05-31
UCAgent Stage：`17-expr_coverage_closure`（索引 16）
后端：Claude Code CLI

## 概要

通过 Category O 豁免闭合了剩余 6 个表达式覆盖率缺失，将 Expr 从 131/137（95.6%）提升至 **131/131（100.0%）**（6 个表达式行通过 ignore_patterns 从覆盖率计数中过滤）。全部 6 个表达式均为 Chisel 生成的 SVA 断言条件项（`STOP_COND`）和内部死逻辑条件，在 I-cache 模式下结构上不可达。

## Category O 详情

| 行号 | 模块 | 表达式 | 已有类别 | 原因 |
|---|---|---|---|---|
| 274 | CacheStage2 | `~(~(io_in_valid & _T_13)) & _T_16` | E | Waymask PopCount SVA 条件 |
| 787 | CacheStage3 | `_T_5 & needFlush` | D | needFlush 在 I-cache 中恒为 0 |
| 889 | CacheStage3 | `~(~(mmio & hit)) & ~reset` | A | MMIO+hit STOP_COND |
| 913 | CacheStage3 | `~(~(metaHitWriteBus_x5 & metaRefillWriteBus_req_valid)) & _T_3` | M | Meta 冲突 STOP_COND |
| 937 | CacheStage3 | `~(~(hitWrite & dataRefillWriteBus_x9)) & _T_3` | M | Data 冲突 STOP_COND |
| 961 | CacheStage3 | `~_T_38 & _T_3` | A/D | D-cache flush 断言 STOP_COND |

全部 6 个表达式在 I-cache 中结构上不可达。保护对象（MMIO+hit 冲突、meta 端口冲突、data 端口冲突、D-cache flush、needFlush 解除）在 I-cache 操作中永不发生。与已有 A、D、E、M 类豁免根因相同。

## 变更文件

| 文件 | 变更 |
|---|---|
| `tests/conftest.py` | 向 ignore_patterns 添加 6 行；新增 Category O 注释 |
| `docs/coverage_waiver_rationale.md` | 新增 Category O 章节 |
| `docs/coverage_waiver_rationale_zh.md` | 新增 Category O 中文章节 |
| `unity_test/Cache_functions_and_checks.md` | 新增 CK-WAIVER-CAT-O |
| `unity_test/Cache_functions_and_checks_zh.md` | 更新覆盖率数据 |
| `unity_test/Cache_line_func_map.md` | 新增 Category O IGNORE 映射 |
| `unity_test/Cache_line_func_map_zh.md` | 新增 Category O 至豁免表 |
| `unity_test/Cache_line_map_analysis.md` | 新增 Expr 章节 |
| `unity_test/Cache_line_map_analysis_zh.md` | 新增 Expr 章节（中文）|
| `docs/test_points.md` 及 `_zh.md` | 新增 Stage 16 条目 |
| `docs/ai_collaboration_report.md` 及 `_zh.md` | 新增 Stage 16 条目 |
| `top.md` 及 `top_zh.md` | 新增 Stage 16 输出文件条目 |

## ignore_patterns 字符串（最终版）

```
Cache.v:138,148,150,152,202-207,240-241,262,263,274,411,420,460,524,532,550,555,558,605,608,610,626,768,777,787,788,796,824,876,877,889,900,901,913,924,925,937,948,949,961,2267,2276,2316,2418,2674,2861-2862
```

## 执行的命令

```bash
scripts/collect_coverage_multi.sh → 38 passed
```

## 覆盖增量

| 指标 | Stage 13 后 | Stage 16 后 | 增量 |
|---|---|---|---|
| Expr | 131/137 (95.6%) | **131/131 (100.0%)** | +6 豁免 (Category O) |
| 行 | 1359/1359 (100.0%) | 1359/1359 (100.0%) | — |
| 分支 | 471/471 (100.0%) | 471/471 (100.0%) | — |
| 翻转 | 24785/28227 (87.8%) | 24785/28227 (87.8%) | — |

说明：toffee_test 的 ignore_patterns 从分子和分母中同时移除已豁免行。6 个表达式豁免后 → 131/131。

## 最终覆盖率

```
Line:   1359/1359 = 100.0%
Branch: 471/471  = 100.0%
Expr:   131/131 = 100.0%  (6 个表达式已豁免，共 137 个)
Toggle: 24785/28227 = 87.8%
38 tests, 0 failures
```

四项覆盖率指标均已达到最终值。行、分支、表达式均达到 100.0%。翻转处于平台期（87.8%），剩余 3442 个缺失通过 Categories T-A 至 T-F 结构性豁免。
