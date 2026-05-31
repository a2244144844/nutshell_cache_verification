# Cache 功能与检查点矩阵

日期：2026-05-31

对应英文文档：`unity_test/Cache_functions_and_checks.md`

## 说明

该文档记录 GenSpec 对齐后的 FG/FC/CK 结构，包含 Stage 11-13 覆盖率闭环后新增的功能组。英文文件包含完整标签和检查点表，本中文文件说明当前矩阵状态。

## 最新状态

- FG 数量：7（原5 + FG-COVERAGE-WAIVER + FG-STAGE11-13-TESTS）
- CK 数量：70+（含新增line/branch waiver CKs、toggle waiver CKs、Stage 11-13 CKs）
- 覆盖范围：API/reset、核心 cache hit/miss/refill/writeback、MMIO/flush/coherence、backpressure/CRV、coverage waivers（line/branch A-N + toggle T-A~T-F）、Stage 11-13 闭环测试、bug/report evidence。
- `UnityChipCheckerLabelStructure` 已通过。

### 新增功能组

#### FG-COVERAGE-WAIVER

记录正式审查并接受的 line、branch、expr、toggle 覆盖率豁免。Line/branch 豁免（Categories A-N）标记了 I-cache 配置下结构不可达代码。Expr 豁免（Category O）标记了 SVA 断言/死逻辑表达式条件。Toggle 豁免（Categories T-A~T-F）覆盖结构性翻转缺失，采用文档化方式（不编码在 conftest.py）。参考文档：`docs/coverage_waiver_rationale.md`、`docs/toggle_coverage_waiver.md`。

#### FG-STAGE11-13-TESTS

记录 Stage 11（DIR-017 needFlush、DIR-018 respToL1Last → line 100%）、Stage 12（DIR-019~022 → branch 100%）、Stage 13（多种子随机流量 → toggle 87.8%）和 Stage 17（最大设置最终尝试 → toggle 88.4%）的覆盖率闭环测试工作。

## 最终覆盖率

- Line: 1359/1359 (100.0%)，42 行豁免 (Categories A-N)
- Branch: 471/471 (100.0%)，豁免 Categories L/M/N
- Expr: 137/137 (100.0%)，6 表达式豁免 (Category O)
- Toggle: 24947/28227 (88.4%)，3,280 miss 豁免 (Categories T-A~T-F，文档化方式)
- 测试数：37 个，0 失败

## 使用方式

后续新增测试或报告时，应先确认对应 CK 标签，再更新测试点、覆盖率报告和行映射。
