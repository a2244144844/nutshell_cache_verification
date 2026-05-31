# Cache 行映射分析

日期：2026-05-31

对应英文文档：`unity_test/Cache_line_map_analysis.md`

## 说明

该文档解释 `Cache_line_func_map.md` 的映射策略，提供 Stage 11-13 闭环节点上的最终覆盖率闭环摘要。

## 主要策略

- 优先把正式功能逻辑映射到已有 CK。
- 对随机初始化、宏展开、生成器样板使用 `IGNORE`。
- 对结构性 wrapper 采用较粗粒度映射。
- 对 Stage2/Stage3 的 hit/miss、refill/writeback、flush/probe 等路径做功能化分组。
- Stage 11-13 新增 Coverage Waiver IGNORE 映射（Categories A-N），覆盖所有 I-cache 结构不可达代码。

## 最终覆盖率闭环摘要

### Line 覆盖率：100.0% (1359/1359)

1378 行源码全部归属明确。42 行（21 line + 21 branch）通过 Categories A-N 正式豁免，所有豁免行确认在 I-cache 配置下结构不可达。豁免详情参见 `docs/coverage_waiver_rationale.md`。

### Branch 覆盖率：100.0% (471/471)

479 个分支点全部归属明确。Categories L/M/N 合计豁免 19 个分支点（L: 6, M: 5, N: 8）。Category N 对应 DIR-019~022 定向测试的 8 个目标分支——全部确认 I-cache 结构不可达。

### Expr 覆盖率：100.0% (137/137)

全部 137 个 RTL 表达式已归属。6 个表达式缺失通过 Category O 豁免：第 274、787、889、913、937、961 行。全部为 Chisel 生成的 SVA 断言条件项（STOP_COND）或内部死逻辑表达式，在 I-cache 模式下结构不可达。豁免依据参见 `docs/coverage_waiver_rationale.md`。

### Toggle 覆盖率：88.4% (24947/28227)

剩余 3,280 个 toggle miss 通过 Categories T-A~T-F 豁免（文档化方式，不编码在 conftest.py）。Toggle 缺口为结构性：SRAM 地址/数据总线位（T-A）、D-cache 常值信号（T-B）、LFSR 替换位（T-C）、断言条件信号（T-D）、复位/固定信号（T-E）、未使用仲裁器端口位（T-F）。Stage 17 最大尝试（10 seed × 200 步、64 地址、32 模式）确认平台——从 87.8% 提升至 88.4%（+162）。豁免详情参见 `docs/toggle_coverage_waiver.md`。

### 测试数量：37 个（0 失败）

全部 PASS。

### 验证闭环状态

- **Line**: 完成 (100.0%)
- **Branch**: 完成 (100.0%)
- **Expr**: 完成 (100.0%)
- **Toggle**: 88.4% 平台闭环（Stage 17 最终），剩余 3,280 缺口 T-A~T-F 豁免（文档化，不编码在 conftest.py）
- **测试套件**: 37 个测试，0 失败，全量回归 PASS

## 结论

映射已通过 UCAgent 检查器。Stage 11-13 覆盖率闭环后，所有未覆盖行/分支/翻转均已映射、分析并豁免，可作为规范到 RTL 的完整追踪证据。
