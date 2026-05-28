# Cache GenSpec 流程计划

日期：2026-05-28

对应英文文档：`docs/genspec_flow_plan.md`

## 目的

记录对官方 UCAgent GenSpec 工作流的修正理解，并说明如何把它接入当前 Track1 NutShell Cache 验证项目。

核心结论：GenSpec 不是手写一份规格文档，而是一个独立的 UCAgent 自定义工作流，用于在验证实现之前生成 DUT 功能规范、子规范、检查点和源码行映射。

## 官方六阶段

| 阶段 | 名称 | 产物 |
| --- | --- | --- |
| 1 | `collect_existing_assets` | `unity_test/Cache_spec.md` 初稿 |
| 2 | `augment_with_code` | 结合 RTL 增强后的主规范 |
| 3 | `complete_subspecs` | `unity_test/Cache/*_spec.md` 子规范 |
| 4 | `human_check` | 人工审查与 `Cache_spec_summary.md` |
| 5 | `functional_specification_analysis` | `Cache_functions_and_checks.md` |
| 6 | `ref_function_line_map_generation` | `Cache_line_func_map.md` |

## 当前执行状态

该计划已经执行完成：

- GenSpec overlay 位于 `genspec_workspace/`
- 根目录配置副本为 `genspec_cache.yaml`
- 主规范、子规范、FG/FC/CK 和行映射已同步到 `unity_test/`
- `FileLineMapChecker` 已通过

## 关键约束

- GenSpec 不修改 RTL。
- GenSpec 不改动现有可运行测试。
- `human_check` 必须人工确认后再进入后续阶段。
- 生成物需回填到 `top.md` 和 `top_zh.md`。
