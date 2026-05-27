# UCAgent GenSpec 完整阶段记录

日期：2026-05-27

## 目的

记录 Track1 NutShell Cache DUT 的官方 UCAgent GenSpec 流程执行结果。本阶段补齐“先规范、后验证”的产物链：RTL 主规范、子规范、FG/FC/CK 矩阵以及 CK 到 RTL 行号映射。

## 结果

| GenSpec 阶段 | 结果 | 证据 |
| --- | --- | --- |
| collect_existing_assets | PASS | 生成 `unity_test/Cache_spec.md`。 |
| augment_with_code | PASS | 结合 `Cache.v` 和既有项目文档增强主规范。 |
| complete_subspecs | PASS | 在 `unity_test/Cache/` 下生成六份子规范。 |
| human_check | REVIEWED | 生成 `unity_test/Cache_spec_summary.md`；人工审查后从 stage 4 恢复继续。 |
| functional_specification_analysis | PASS | `UnityChipCheckerLabelStructure` 通过，最终矩阵包含 5 个 FG、45 个 CK。 |
| ref_function_line_map_generation | PASS | `FileLineMapChecker` 通过，`Cache/Cache.v` 全部行均已映射或忽略。 |

## 关键产物

| 路径 | 用途 |
| --- | --- |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/genspec_cache.yaml` | GenSpec 根目录配置副本。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/Cache_spec.md` | RTL 分析生成的 Cache 主规范。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/Cache/` | CacheStage1/2/3、MetaDataArray、DataArray、Replacement 子规范目录。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/Cache_spec_summary.md` | human_check 阶段生成的人工审查摘要。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/Cache_functions_and_checks.md` | GenSpec 对齐的 FG/FC/CK 矩阵。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/Cache_line_func_map.md` | CK 到 `Cache.v` 行号的映射。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/Cache_line_map_analysis.md` | 行映射审查说明。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/tests/Cache_api.py` | 对现有 `CacheEnv` 的标准 API 薄包装。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/tests/Cache_function_coverage_def.py` | 对现有 `CacheCoverage` 的标准覆盖率薄包装。 |

## 人工审查说明

- `human_check` 已生成摘要；由于 `--exit-on-completion` 下无法稳定注入交互式通过命令，本次采用人工确认后从后续 stage 显式恢复的方式继续。
- 行映射中 `IGNORE` 仅用于随机初始化、生成器样板和非功能性脚手架。
- Phase B 的 API/coverage 文件是新增包装层，没有修改既有验证逻辑。

## Phase C 验证

| 命令 | 结果 |
| --- | --- |
| `source scripts/env.sh && python3 -m py_compile unity_test/tests/Cache_api.py unity_test/tests/Cache_function_coverage_def.py` | PASS |
| `source scripts/env.sh && scripts/run_regression.sh` | PASS — `28 passed in 5.76s` |
| `source scripts/env.sh && scripts/reproduce.sh` | PASS — 覆盖率步骤 `29 passed, 18 warnings in 8.08s`；bug-injection 预期失败被捕获；恢复路径通过；最终输出 `[reproduce] PASS` |
