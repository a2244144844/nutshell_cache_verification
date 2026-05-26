# Markdown 索引

日期：2026-05-26

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
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/configs/ucagent_track1_cache.yaml` | Cache 专属 UCAgent 配置文件。包含 audit、backpressure、CRV/coverage、dirty-writeback 闭环和 bug-injection 五个 stage，后续工作均应通过 UCAgent 运行。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ucagent_output/stage_audit.md` | 首个 Cache 专属 UCAgent stage 输出。记录了检查的文件、回归命令、警告和 `4 passed` audit 结果。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ucagent_output/backpressure_stage.md` | UCAgent backpressure stage 输出。记录了变更的文件、回归命令、`6 passed` 结果和残留风险。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/coverage_report.md` | CRV stage 2 生成的功能覆盖率引导报告，包含已观测仓和剩余闭环缺口。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ucagent_output/crv_coverage_stage.md` | UCAgent CRV/coverage stage 输出。记录了变更文件、命令、精确通过/失败结果、覆盖率摘要和剩余缺口。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ucagent_output/dirty_writeback_stage.md` | UCAgent dirty-writeback 闭环 stage 输出。记录了变更文件、命令、精确通过/失败结果、覆盖率增量和残留风险。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ucagent_output/bug_injection_stage.md` | UCAgent bug-injection stage 输出。记录变更文件、预期失败命令、恢复命令、干净回归结果和残留风险。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ucagent_output/final_report_stage.md` | UCAgent 最终报告打包 stage 输出。记录审查的文件、运行的命令、精确结果、提交检查清单状态和残留风险。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/scripts/run_ucagent_stage.sh` | 通过 `--force-stage-index` 运行指定 UCAgent stage 的辅助脚本；1 对应 backpressure，2 对应 CRV/coverage，3 对应 dirty-writeback 闭环，4 对应 bug injection。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/scripts/reproduce.sh` | 一键复现入口。运行正常回归、覆盖率收集、预期失败 bug 注入和 bug 恢复路径。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/scripts/run_bug_injection.sh` | 受控 bug-injection harness 的包装脚本，支持 `--disable-bug` 恢复模式。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/scripts/clean_generated.sh` | 清理生成的 build、Python cache、本地波形和 pytest cache 等产物。 |

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
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ucagent_output/stage_audit_zh.md` | Audit stage UCAgent 输出的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ucagent_output/backpressure_stage_zh.md` | Backpressure stage UCAgent 输出的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ucagent_output/crv_coverage_stage_zh.md` | CRV/coverage stage UCAgent 输出的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ucagent_output/dirty_writeback_stage_zh.md` | Dirty-writeback stage UCAgent 输出的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ucagent_output/bug_injection_stage_zh.md` | Bug-injection stage UCAgent 输出的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/bug_tracking_zh.md` | Bug 追踪证据记录的中文镜像。 |
| `/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/docs/ucagent_output/final_report_stage_zh.md` | 最终报告打包 stage UCAgent 输出的中文镜像。 |

## 更新规则

在本任务下新增 Markdown 交付物时，同步更新本文件：

- 绝对路径。
- 一句话说明用途。
- 标明属于指导源文件、状态记录、设计分析、测试计划还是最终报告产物。
