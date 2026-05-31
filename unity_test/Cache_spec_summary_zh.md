# Cache 规范人工审查摘要（中文版）

日期：2026-05-31

对应英文文档：`unity_test/Cache_spec_summary.md`

## 说明

该文件对应 GenSpec `human_check` 阶段生成的审查摘要。经过 Stage 11/12/13 的三轮覆盖闭环，待确认项已全部解决或确认为豁免项。

## 审查结论

- 主规范和子规范覆盖了 Cache 主要结构。
- `io_flush[1]` 已确认为 Category D 豁免项（I-cache 配置下结构不可达，对应 RTL lines 2861-2862）。
- 最终覆盖率：Line 1359/1359 (100.0%)、Branch 471/471 (100.0%)、Toggle 24947/28227 (88.4%，豁免 3,280：T-A~T-F)、Expr 137/137 (100.0%)。
- 原有"98.4% line coverage"表述已淘汰，统一为最终闭环数据。
- `probe` 首次命中 data 稳定性以命中/未命中命令字段为稳定判定依据。
- 豁免依据见 `docs/coverage_waiver_rationale.md` 与 `docs/toggle_coverage_waiver.md`。

## 待确认项解决情况

| 原待确认项 | 状态 | 裁决 |
| --- | --- | --- |
| `io_flush[1]` 架构语义 | 已解决 | Category D 豁免 — I-cache 配置下结构不可达 |
| Probe 首次命中 data 判定 | 已记录 | 命中/未命中命令字段为稳定判定依据 |
| Coverage 对外口径 | 已统一 | Line 100% / Branch 100% / Toggle 88.4%（豁免 3,280）/ Expr 100% |
| `Cache.yaml` 配置写入主规格 | 可选项 | 保持现有配置文档索引 |

## 风险缓解

- **Stage3 needFlush/MMIO 交叠风险**：经 DIR-017/018 实现行覆盖闭环，`io_flush[1]` 豁免确认。
- **Reset sweep 风险**：测试前置条件已记录于 smoke 检查。
- **Dirty victim 回写风险**：由 `BUG-RTL-001` 与 writeback directed 测试覆盖。
- **WordIdx 绑定风险**：由 read-after-write 与 write-mask 测试覆盖。
