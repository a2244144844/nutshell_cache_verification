# Markdown 索引

日期：2026-05-28

本文件是 Track1 NutShell Cache 验证任务所维护 Markdown 文档的顶层索引，记录每份文档的角色和路径，方便后续工作步骤从正确的源文件开始。

## 指导性源文件

| 路径 | 角色 |
| --- | --- |
| `/Users/zzy/Workspace/ucagent/docs/track1_UCAgent_competition_requirements.md` | 赛题要求来源。作为 Track1 目标、交付物和预期验证方向的权威参考。 |
| `/Users/zzy/Workspace/ucagent/instruction.md` | 本地 UCAgent/Codex 操作指南来源。用于将实现流程与所需的 agent 工作流对齐。 |
| `/Users/zzy/Workspace/ucagent/step.md` | 从赛题要求和本地操作指南派生的分步执行计划。作为高层路线图使用。 |

## 任务工作区文档

| 路径 | 角色 |
| --- | --- |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/README.md` | 工作区概览、当前状态、目录布局和当前工程里程碑。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/top.md` | 本文档索引。每当创建新的任务 Markdown 文件或其用途变更时需更新。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/source_inventory.md` | 本地源文件、上游引用、克隆仓库和已知源文件缺口的清单。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/verification_plan.md` | 分阶段验证计划和当前阶段状态。用于决定下一步实现步骤。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ai_collaboration_report.md` | AI 辅助操作、人工决策和自动化风险的持续记录。最终报告必需。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ucagent_operation_plan.md` | UCAgent 集成差距分析、建议的 stage contract、命令模板和报告规则，用于使 Cache 任务的 UCAgent 驱动过程可视化。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/picker_installation.md` | Picker 安装、本地补丁、验证命令和安装路径。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/nutshell_build_probe.md` | 探索性 NutShell/Chisel RTL 构建记录。仅作上下文参考，非选定的 DUT 路径。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/dut_selection.md` | 选定 DUT 的决策记录。实际 DUT 为复制到 `rtl/dut/Cache.v` 的 Picker 示例 Cache RTL。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/interface_map.md` | Cache DUT 引脚/协议映射、SimpleBus 命令常量及首次观测到的传输行为。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/test_points.md` | 已实现的 smoke、directed、corner 和 CRV 检查点，以及剩余定向测试和覆盖率候选点。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/bug_tracking.md` | Bug-injection 证据记录。说明 `BUG-001` 的触发条件、scoreboard 检出路径、失败证据和关闭注入后的恢复路径。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/configs/ucagent_track1_cache.yaml` | Cache 专属 UCAgent 配置文件。包含 audit、backpressure、CRV/coverage、dirty-writeback 闭环、bug-injection、final-report、flush 和 coherence-probe stage。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ucagent_output/stage_audit.md` | 首个 Cache 专属 UCAgent stage 输出。记录了检查的文件、回归命令、警告和 `4 passed` audit 结果。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ucagent_output/backpressure_stage.md` | UCAgent backpressure stage 输出。记录了变更的文件、回归命令、`6 passed` 结果和残留风险。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/coverage_report.md` | CRV stage 2 生成的功能覆盖率引导报告，包含已观测仓和剩余闭环缺口。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ucagent_output/crv_coverage_stage.md` | UCAgent CRV/coverage stage 输出。记录了变更文件、命令、精确通过/失败结果、覆盖率摘要和剩余缺口。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ucagent_output/dirty_writeback_stage.md` | UCAgent dirty-writeback 闭环 stage 输出。记录了变更文件、命令、精确通过/失败结果、覆盖率增量和残留风险。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ucagent_output/bug_injection_stage.md` | UCAgent bug-injection stage 输出。记录变更文件、预期失败命令、恢复命令、干净回归结果和残留风险。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ucagent_output/final_report_stage.md` | UCAgent 最终报告打包 stage 输出。记录审查的文件、运行的命令、精确结果、提交检查清单状态和残留风险。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ucagent_output/flush_stage.md` | UCAgent flush 行为 stage 输出（DIR-007）。记录文件变更、命令、pass/fail 结果、D-cache io_flush 约束及剩余风险。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ucagent_output/coherence_probe_stage.md` | UCAgent coherence-probe stage 输出（DIR-008）。记录文件变更、命令、pass/fail 结果、probe pipeline 说明和剩余风险。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ucagent_output/write_miss_eviction_replay_stage.md` | DIR-011 至 DIR-013 的补充 UCAgent replay 产物。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/coverage_waiver_rationale.md` | 行覆盖率豁免依据，按类别解释不可达或不应覆盖的 RTL 行。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/line_coverage_closure_plan.md` | 行覆盖率闭环计划，记录 DIR-014/015/016 和 Category J 豁免策略及最终结果。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ucagent_output/line_coverage_closure_stage.md` | UCAgent 行覆盖率闭环阶段产物，记录覆盖率从 98.4% 提升到 99.6% 的证据。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/genspec_flow_plan.md` | 官方六阶段 GenSpec 流程应用到 Cache 项目的修正计划。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ucagent_output/genspec_flow_plan_stage.md` | GenSpec 计划审查阶段 UCAgent 产物。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/dir_014_015_016_guide.md` | DIR-014/015/016 行覆盖率闭环实现指南。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/genspec_cache.yaml` | GenSpec 根目录配置副本，用于运行官方六阶段 Cache 规范生成流程。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/genspec_workspace/genspec_cache.yaml` | UCAgent 实际消费的 overlay GenSpec 配置。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/genspec_workspace/Cache/README.md` | Overlay 工作区说明，记录提供给 UCAgent GenSpec 的 RTL 和参考文档包。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ucagent_output/genspec_full_stage.md` | UCAgent GenSpec 完整阶段产物，记录命令流程、human_check 处理、检查器结果和生成的规范文件。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/scripts/run_ucagent_stage.sh` | 通过 `--force-stage-index` 运行指定 UCAgent stage 的辅助脚本；stage index 以 `configs/ucagent_track1_cache.yaml` 为准。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/scripts/reproduce.sh` | 一键复现入口。运行正常回归、覆盖率收集、预期失败 bug 注入和 bug 恢复路径。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/scripts/run_bug_injection.sh` | 受控 bug-injection harness 的包装脚本，支持 `--disable-bug` 恢复模式。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/scripts/clean_generated.sh` | 清理生成的 build、Python cache、本地波形和 pytest cache 等产物。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/README.md` | 模板对齐的 Cache unity-test 整合交付物索引。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/Cache_basic_info.md` | 整合后的 DUT 身份、源码边界、接口概要和工具流程报告。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/Cache_verification_needs_and_plan.md` | 整合后的验证目标、计划、stage 证据和退出标准。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/Cache_spec.md` | GenSpec 根据 `Cache.v` 和既有项目文档生成的 Cache 主规范。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/Cache/` | GenSpec 子规范目录，包含 CacheStage1、CacheStage2、CacheStage3、MetaDataArray、DataArray 和 Replacement。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/Cache/CacheStage1_spec.md` | CacheStage1 请求接收和早期流水行为子规范。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/Cache/CacheStage2_spec.md` | CacheStage2 hit/miss、way select、MMIO 分类和写掩码逻辑子规范。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/Cache/CacheStage3_spec.md` | CacheStage3 refill、writeback、flush、probe、MMIO 和 response FSM 子规范。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/Cache/MetaDataArray_spec.md` | Metadata SRAM 和 reset sweep 子规范。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/Cache/DataArray_spec.md` | Data SRAM、refill、hit read、write mask 和 writeback 数据子规范。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/Cache/Replacement_spec.md` | invalid-way 优先、replacement choice 和 clean/dirty eviction 子规范。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/Cache_spec_summary.md` | GenSpec human_check 阶段生成的人工审查摘要。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/Cache_functions_and_checks.md` | 整合后的 smoke、directed、corner、random、scoreboard 和 coverage 检查矩阵。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/Cache_line_func_map.md` | GenSpec CK 到 `Cache.v` 行号的映射，已通过 `FileLineMapChecker`。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/Cache_line_map_analysis.md` | 行映射分组和生成器样板忽略策略的审查说明。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/Cache_line_coverage_analysis.md` | 整合后的覆盖率结果、Toffee 功能覆盖率和 RTL line coverage 限制说明。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/Cache_bug_analysis.md` | 整合后的 bug-injection 与 RTL bug 证据摘要。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/Cache_test_summary.md` | 整合后的最终测试结果、可复现性、UCAgent 证据和提交说明。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/tests/Cache_api.py` | 标准 UCAgent API 薄包装，暴露 `create_dut`、pytest fixtures 和 `api_cache_*` 函数，内部调用 `src/env/cache_env.py`。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/tests/Cache_function_coverage_def.py` | 标准 UCAgent 覆盖率薄包装，暴露 `get_coverage_groups(dut)`，内部调用 `src/utils/toffee_coverage.py`。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/uc_test_report/README.md` | 模板风格测试报告索引，指向生成的 coverage HTML 和 Markdown 报告。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/uc_test_report/README_zh.md` | UC 测试报告索引的中文镜像。 |

## 中文镜像文档

| 路径 | 角色 |
| --- | --- |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/README_zh.md` | 工作区概览和当前状态的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/top_zh.md` | 本 Markdown 索引的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/source_inventory_zh.md` | 源文件清单和缺口记录的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/verification_plan_zh.md` | 分阶段验证计划的中文镜像；英文 `verification_plan.md` 是当前活跃的 stage 状态来源。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ai_collaboration_report_zh.md` | AI 协同日志的中文镜像；英文 `ai_collaboration_report.md` 是当前活跃的状态来源。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ucagent_operation_plan_zh.md` | UCAgent 操作计划的中文镜像；英文 `ucagent_operation_plan.md` 是当前活跃的 stage 控制来源。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/picker_installation_zh.md` | Picker 安装记录的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/nutshell_build_probe_zh.md` | 探索性 NutShell 构建记录的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/dut_selection_zh.md` | DUT 选择决策的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/interface_map_zh.md` | Cache 接口/协议映射的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/test_points_zh.md` | 测试点表格的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/coverage_report_zh.md` | 功能覆盖率报告的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/coverage_waiver_rationale_zh.md` | 行覆盖率豁免依据的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/dir_014_015_016_guide_zh.md` | DIR-014/015/016 实现指南的中文镜像入口。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/genspec_flow_plan_zh.md` | GenSpec 流程计划的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/line_coverage_closure_plan_zh.md` | 行覆盖率闭环计划的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ucagent_output/stage_audit_zh.md` | Audit stage UCAgent 输出的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ucagent_output/backpressure_stage_zh.md` | Backpressure stage UCAgent 输出的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ucagent_output/crv_coverage_stage_zh.md` | CRV/coverage stage UCAgent 输出的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ucagent_output/dirty_writeback_stage_zh.md` | Dirty-writeback stage UCAgent 输出的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ucagent_output/bug_injection_stage_zh.md` | Bug-injection stage UCAgent 输出的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/bug_tracking_zh.md` | Bug 追踪证据记录的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ucagent_output/final_report_stage_zh.md` | 最终报告打包 stage UCAgent 输出的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ucagent_output/flush_stage_zh.md` | Flush stage UCAgent 输出的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ucagent_output/coherence_probe_stage_zh.md` | Coherence-probe stage UCAgent 输出的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ucagent_output/write_miss_eviction_replay_stage_zh.md` | Write-miss / eviction replay stage UCAgent 输出的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ucagent_output/line_coverage_closure_stage_zh.md` | Line coverage closure stage UCAgent 输出的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ucagent_output/genspec_flow_plan_stage_zh.md` | GenSpec 计划阶段 UCAgent 输出的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ucagent_output/genspec_full_stage_zh.md` | GenSpec 完整阶段 UCAgent 输出的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/workflow_gap_analysis_zh.md` | UCAgent 工作流 gap 分析的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/README_zh.md` | Cache unity-test 交付物索引的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/Cache_basic_info_zh.md` | Cache 基本信息的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/Cache_verification_needs_and_plan_zh.md` | Cache 验证需求和计划的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/Cache_spec_zh.md` | GenSpec Cache 主规范的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/Cache_spec_summary_zh.md` | GenSpec human_check 摘要的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/Cache_functions_and_checks_zh.md` | FG/FC/CK 功能和检查矩阵的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/Cache_line_func_map_zh.md` | CK 到 RTL 行映射的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/Cache_line_map_analysis_zh.md` | 行映射分析的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/Cache_line_coverage_analysis_zh.md` | 行覆盖率分析的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/Cache_bug_analysis_zh.md` | Cache bug 分析的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/Cache_test_summary_zh.md` | Cache 测试总结的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/Cache/CacheStage1_spec_zh.md` | CacheStage1 子规范的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/Cache/CacheStage2_spec_zh.md` | CacheStage2 子规范的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/Cache/CacheStage3_spec_zh.md` | CacheStage3 子规范的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/Cache/MetaDataArray_spec_zh.md` | MetaDataArray 子规范的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/Cache/DataArray_spec_zh.md` | DataArray 子规范的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/unity_test/Cache/Replacement_spec_zh.md` | Replacement 子规范的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/uc_test_report/README_zh.md` | UC 测试报告索引的中文镜像。 |

## 更新规则

在本任务下新增 Markdown 交付物时，同步更新本文件：

- 绝对路径。
- 一句话说明用途。
- 标明属于指导源文件、状态记录、设计分析、测试计划还是最终报告产物。
