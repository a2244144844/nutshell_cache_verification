# Cache 功能与检查点矩阵

日期：2026-05-28

对应英文文档：`unity_test/Cache_functions_and_checks.md`

## 说明

该文档记录 GenSpec 对齐后的 FG/FC/CK 结构。英文文件包含完整标签和检查点表，本中文文件说明当前矩阵状态。

## 最新状态

- FG 数量：5
- CK 数量：45
- 覆盖范围：API/reset、核心 cache hit/miss/refill/writeback、MMIO/flush/coherence、backpressure/CRV、bug/report evidence。
- `UnityChipCheckerLabelStructure` 已通过。

## 使用方式

后续新增测试或报告时，应先确认对应 CK 标签，再更新测试点、覆盖率报告和行映射。
