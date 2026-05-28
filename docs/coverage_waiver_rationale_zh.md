# 行覆盖率豁免依据

日期：2026-05-28

对应英文文档：`docs/coverage_waiver_rationale.md`

## 最新状态

- 原始 Verilator 行覆盖率：`1344/1378 (97.5%)`
- 应用 A-G 类豁免后：`1344/1366 (98.4%)`
- 后续 line coverage closure 阶段继续提升到：`1359/1364 (99.6%)`

## 豁免原则

仅豁免不可达或不应以功能测试覆盖的 RTL 行：

- 断言失败 `$fwrite` 分支：只有 DUT 断言失败时才会执行。
- I-cache 配置下不可达的 D-cache forwarding 信号。
- `io_flush[1]` 相关 D-cache flush 路径，受 RTL 断言约束。
- LFSR 全零保护状态，正常最大长度 LFSR 不会自然进入。
- D-cache 专用端口或元数据寄存器。

## 人工保留分析项

文档明确区分了可豁免项与仍可测试项。Category H/I/J 最初未直接豁免，而是进入后续 `line_coverage_closure` 阶段，通过 DIR-014、DIR-015、DIR-016 和 Category J 精确豁免完成闭环。

## 作用

本文件是英文文档的中文对应说明，用于提交时解释为什么行覆盖率豁免不是“掩盖缺口”，而是对不可达结构和测试目标边界的工程化标注。
