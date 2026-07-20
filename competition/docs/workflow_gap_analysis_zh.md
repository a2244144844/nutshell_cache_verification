# UCAgent 工作流 Gap 分析

日期: 2026-05-27

## 目的

本文档将当前 Track1 NutShell Cache 验证工作区与 UCAgent 标准工作流（11 阶段验证 + 6 阶段 GenSpec）进行对比，识别缺失的交付物和结构性差距。目标是使项目完全符合 UCAgent 推荐实践：**先 GenSpec 生成规范，再进行验证**。

## 参考来源

| 来源 | URL |
| --- | --- |
| UCAgent 规范生成工作流 | https://ucagent.open-verify.cc/content/04_case/00_genspec/ |
| UCAgent 默认 11 阶段工作流 | https://ucagent.open-verify.cc/content/03_develop/03_workflow/ |
| GenSpec 示例配置 | `examples/GenSpec/genspec.yaml` |
| GenSpec 规范模板 | `examples/GenSpec/SpecDoc/dut_spec_template.md` |

## 当前项目状态

- DUT: NutShell Cache（`rtl/dut/Cache.v`），通过 Picker 导出为 `DUTCache`
- 测试: 26 passed（smoke + directed + corner + random + bug injection）
- 覆盖率: Toffee 12 groups / 31 points / 37 bins（100%）；RTL 行覆盖率 1344/1366（98.4%）
- UCAgent 已完成阶段: Cache 实现阶段、补充 write-miss/eviction replay，以及官方 GenSpec 六阶段流程
- 可复现性: `scripts/reproduce.sh` 从干净状态通过

## UCAgent 默认 11 阶段工作流映射

### 阶段 1: 需求分析与验证规划

| 项目 | 状态 |
| --- | --- |
| 预期输出 | `unity_test/Cache_verification_needs_and_plan.md` |
| 当前文件 | `unity_test/Cache_verification_needs_and_plan.md` |
| 检查器 | `UnityChipCheckerMarkdownFileFormat` |
| 状态 | **PASS** — 文件存在且结构规范 |

### 阶段 2: DUT 功能理解

| 项目 | 状态 |
| --- | --- |
| 预期输出 | `unity_test/Cache_basic_info.md` |
| 当前文件 | `unity_test/Cache_basic_info.md` |
| 检查器 | `UnityChipCheckerMarkdownFileFormat` |
| 状态 | **PASS** — 覆盖身份标识、接口、SimpleBus 命令、约束 |

### 阶段 3: 功能规格分析与测试点定义（FG/FC/CK）

| 项目 | 状态 |
| --- | --- |
| 预期输出 | `unity_test/Cache_functions_and_checks.md` |
| 当前文件 | `unity_test/Cache_functions_and_checks.md` |
| 检查器 | `UnityChipCheckerLabelStructure`（FG, FC, CK） |
| 状态 | **PASS** — GenSpec 功能规格分析后包含 5 个 FG 组、45 个 CK 标签 |

当前 FG/FC/CK 结构:

| FG 组 | FC 数量 | CK 数量 |
| --- | --- | --- |
| `FG-API` | 2（HARNESS, SMOKE） | 9 |
| `FG-CORE-CACHE` | 3（WRITE-MASK-OFFSET, REFILL-WRITE-MISS, REPLACEMENT-EVICTION） | 11 |
| `FG-MMIO-FLUSH-COH` | 3（MMIO-BYPASS, FLUSH-BEHAVIOR, COHERENCE-PROBE） | 10 |
| `FG-BACKPRESSURE-CRV` | 2（BACKPRESSURE, CRV-COVERAGE） | 8 |
| `FG-EVIDENCE` | 2（BUG-INJECTION, REPORTING） | 7 |
| **合计** | **12** | **45** |

### 阶段 4: 测试平台基础架构设计（DUT API + Fixtures）

| 项目 | 状态 |
| --- | --- |
| 预期输出 | `unity_test/tests/Cache_api.py` |
| 当前文件 | `unity_test/tests/Cache_api.py` |
| 检查器 | `UnityChipCheckerDutCreation`, `UnityChipCheckerDutFixture`, `UnityChipCheckerEnvFixture` |
| 状态 | **PASS** — 已新增对 `src/env/cache_env.py` 的薄包装 |

已有内容:
- `src/env/cache_env.py` — `CacheEnv` 类，含 reset、CPU 请求、内存响应、MMIO、flush、probe 辅助方法
- `tests/conftest.py` — pytest fixtures（`cache_env`, `mem_model`, `scoreboard`）
- `src/scoreboard/cache_scoreboard.py` — 读写响应检查器
- `src/monitor/cache_monitor.py` — 事务记录器
- `src/utils/simplebus.py` — SimpleBus 常量和数据类

现已补充:
- `create_dut(request=None, coverage=False, reset=True)`
- `cache_env` 和 `dut` pytest fixtures
- `api_cache_*` 前缀函数，包装 reset、step、pin 访问、CPU/MMIO 请求、内存响应和采样接口

### 阶段 5: 功能覆盖率模型实现

| 项目 | 状态 |
| --- | --- |
| 预期输出 | `unity_test/tests/Cache_function_coverage_def.py` |
| 当前文件 | `unity_test/tests/Cache_function_coverage_def.py` |
| 检查器 | `UnityChipCheckerCoverageGroup`, `UnityChipCheckerCoverageGroupBatchImplementation` |
| 状态 | **PASS** — 已新增对 `src/utils/toffee_coverage.py` 的薄包装 |

已有内容:
- `src/utils/cache_coverage.py` — 记录命令类型、命中/未命中代理、写掩码类、字偏移、refill 路径 bins
- `src/utils/toffee_coverage.py` — Toffee 功能覆盖率模型（12 groups, 31 points, 37 bins）

现已补充:
- `get_coverage_groups(dut)` 返回 `CacheCoverage` 里的 Toffee `CovGroup`
- `create_coverage(dut)` 供需要完整覆盖率对象的调用方使用

### 阶段 6: 基础 API 实现

| 项目 | 状态 |
| --- | --- |
| 预期输出 | `unity_test/tests/Cache_api.py`（API 函数） |
| 当前文件 | `unity_test/tests/Cache_api.py` |
| 检查器 | `UnityChipCheckerDutApi` |
| 状态 | **PASS** — `api_cache_*` 前缀函数已包装现有 `CacheEnv` 方法 |

### 阶段 7: 基础 API 功能测试

| 项目 | 状态 |
| --- | --- |
| 预期输出 | `unity_test/tests/test_cache_api_*.py` |
| 当前状态 | 测试存在于 `tests/smoke/`, `tests/directed/` 等但不符合 `test_cache_api_*` 格式 |
| 检查器 | `UnityChipCheckerDutApiTest` |
| 状态 | **PARTIAL** — 测试可用但未遵循标准 `dut.fc_cover` 标记约定 |

### 阶段 8: 测试框架脚手架

| 项目 | 状态 |
| --- | --- |
| 预期输出 | 未覆盖 CK 点的占位测试模板 |
| 当前状态 | 所有 CK 点已有实际实现（不需要占位） |
| 检查器 | `UnityChipCheckerTestTemplate` |
| 状态 | **N/A** — 所有测试已实现，不需要脚手架 |

### 阶段 9: 全面验证执行与缺陷分析

| 项目 | 状态 |
| --- | --- |
| 预期输出 | `unity_test/Cache_bug_analysis.md` |
| 当前文件 | `unity_test/Cache_bug_analysis.md` |
| 检查器 | `UnityChipCheckerTestCase` |
| 状态 | **PASS** — 覆盖 BUG-001（参考模型损坏）和 BUG-RTL-001（脏写回绕过） |

### 阶段 10: 代码行覆盖率分析与提升

| 项目 | 状态 |
| --- | --- |
| 预期输出 | `unity_test/Cache_line_coverage_analysis.md` |
| 当前文件 | `unity_test/Cache_line_coverage_analysis.md` |
| 检查器 | `UnityChipCheckerTestCaseWithLineCoverage` |
| 状态 | **PASS** — 98.4% 行覆盖率，含 waiver 理由 |

### 阶段 11: 验证审查与总结

| 项目 | 状态 |
| --- | --- |
| 预期输出 | `unity_test/Cache_test_summary.md` |
| 当前文件 | `unity_test/Cache_test_summary.md` |
| 检查器 | `UnityChipCheckerTestCase` |
| 状态 | **PASS** |

## GenSpec 6 阶段工作流映射

### GenSpec 阶段 1: 收集现有资料

| 项目 | 状态 |
| --- | --- |
| 预期输出 | `unity_test/Cache_spec.md`（主规范文档） |
| 当前文件 | `unity_test/Cache_spec.md` |
| 检查器 | `MarkDownHeadChecker` |
| 状态 | **PASS** — 已由 UCAgent GenSpec collect/augment 阶段生成 |

`Cache_spec.md` 应包含:
- 设计背景（NutShell Cache 在 RISC-V SoC 中的角色）
- 术语表（SimpleBus、cache line、way、set 等）
- RTL 源文件清单（含 `<ref_file>` 标签）
- 顶层接口表（所有端口的方向、位宽、复位值）
- 功能描述（可缓存访问、MMIO bypass、flush、一致性探测）
- 状态机描述（CacheStage3 状态）
- 配置参数
- 验证需求摘要
- 潜在 bug 分析

### GenSpec 阶段 2: 源码增强补全细节

| 项目 | 状态 |
| --- | --- |
| 预期输出 | 经 RTL 源码分析增强的 `Cache_spec.md` |
| 当前文件 | `unity_test/Cache_spec.md` |
| 检查器 | `WalkFilesOneByOne` |
| 状态 | **PASS** — 已通过源码增强阶段补全 |

### GenSpec 阶段 3: 批量完善子规范

| 项目 | 状态 |
| --- | --- |
| 预期输出 | `unity_test/Cache_spec_*.md`（子模块规范） |
| 当前文件 | `unity_test/Cache/` |
| 检查器 | `BatchMarkDownHeadChecker` |
| 状态 | **PASS** — 已生成六份子规范 |

已生成的子规范:
- `unity_test/Cache/CacheStage1_spec.md`
- `unity_test/Cache/CacheStage2_spec.md`
- `unity_test/Cache/CacheStage3_spec.md`
- `unity_test/Cache/MetaDataArray_spec.md`
- `unity_test/Cache/DataArray_spec.md`
- `unity_test/Cache/Replacement_spec.md`

### GenSpec 阶段 4: 人工综合检查

| 项目 | 状态 |
| --- | --- |
| 预期输出 | `unity_test/Cache_spec_summary.md` |
| 当前文件 | `unity_test/Cache_spec_summary.md` |
| 检查器 | `HumanChecker` |
| 状态 | **REVIEWED** — 已生成 human_check 摘要，人工确认后从 stage 4 恢复继续 |

### GenSpec 阶段 5: 功能规格分析

| 项目 | 状态 |
| --- | --- |
| 预期输出 | `unity_test/Cache_functions_and_checks.md` |
| 当前文件 | `unity_test/Cache_functions_and_checks.md` |
| 检查器 | `UnityChipCheckerLabelStructure`（FG, FC, CK） |
| 状态 | **PASS** — 已由 GenSpec 重新验证，包含 5 个 FG 组、45 个 CK 标签 |

### GenSpec 阶段 6: 功能行映射生成

| 项目 | 状态 |
| --- | --- |
| 预期输出 | `unity_test/Cache_line_func_map.md` |
| 当前文件 | `unity_test/Cache_line_func_map.md` |
| 检查器 | `FileLineMapChecker` |
| 状态 | **PASS** — `FileLineMapChecker` 通过，`Cache/Cache.v` 全部行已映射或忽略 |

`Cache_line_func_map.md` 应包含:
- 每个 CK 标签到 `Cache.v` 具体行号的映射
- 功能覆盖率点到 RTL 代码的可追溯性
- 文档化功能与实际 RTL 路径之间的差距分析

## 总结：缺失交付物

### 高优先级（阻塞标准工作流合规）

| # | 文件 | 来源阶段 | 工作量 |
| --- | --- | --- | --- |
| 1 | `unity_test/Cache_spec.md` | GenSpec 1-2 | **DONE** — UCAgent GenSpec 已生成 |
| 2 | `unity_test/tests/Cache_api.py` | 默认 4, 6 | **DONE** — 已薄包装 `CacheEnv` |
| 3 | `unity_test/tests/Cache_function_coverage_def.py` | 默认 5 | **DONE** — 已薄包装 `CacheCoverage` |

### 中优先级（提升完整性和可追溯性）

| # | 文件 | 来源阶段 | 工作量 |
| --- | --- | --- | --- |
| 4 | `unity_test/Cache/` 子规范 | GenSpec 3 | **DONE** |
| 5 | `unity_test/Cache_line_func_map.md` | GenSpec 6 | **DONE** |
| 6 | `unity_test/Cache_spec_summary.md` | GenSpec 4 | **DONE** |

### 低优先级（锦上添花）

| # | 文件 | 来源阶段 | 工作量 |
| --- | --- | --- | --- |
| 7 | `unity_test/tests/test_cache_api_*.py` | 默认 7 | 小 — 重命名/重构现有测试 |
| 8 | 测试模板（占位） | 默认 8 | N/A — 所有测试已实现 |

## 建议执行顺序

```
Phase A: GenSpec（规范生成）
  A1. 创建 genspec_cache.yaml 配置
  A2. 运行 GenSpec 阶段 1-3: 生成 Cache_spec.md + 子规范
  A3. 运行 GenSpec 阶段 4: human_check（人工审核）
  A4. 运行 GenSpec 阶段 5: 按需重新生成 Cache_functions_and_checks.md
  A5. 运行 GenSpec 阶段 6: 生成 Cache_line_func_map.md

Phase B: 标准 API 补全
  B1. 创建 unity_test/tests/Cache_api.py（create_dut, fixtures, api_cache_*）
  B2. 创建 unity_test/tests/Cache_function_coverage_def.py
  B3. 验证 UnityChipCheckerDutCreation/DutFixture/DutApi 通过

Phase C: 验证
  C1. 运行所有现有测试确认无回归
  C2. 使用标准配置运行 UCAgent 验证 checker 合规性
  C3. 更新本文档记录最终状态
```

当前状态：Phase A、Phase B、Phase C 均已完成。新包装文件语法检查通过，`scripts/run_regression.sh` 以 `28 passed in 5.76s` 通过，`scripts/reproduce.sh` 最终输出 `[reproduce] PASS`。

## 备注

- 现有验证工作（26 tests, 98.4% 覆盖率）质量扎实，不应被重构破坏。
- GenSpec 工作流以文档为中心，不生成测试代码。
- 标准 API 文件（`Cache_api.py`）可以包装现有 `CacheEnv` 方法而不改变测试行为。
- CacheStage1/2/3/CacheData 的子规范对竞赛来说是可选的，但能展示 thorough UCAgent 集成。
