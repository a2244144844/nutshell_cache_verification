# UCAgent 操作计划

日期：2026-05-26

## 当前评估

当前 Cache 验证工作区具有真实的可执行进展：Picker 导出工作正常，Python 测试驱动 DUT，directed/corner/random 测试通过，VCD 波形已生成。工作流现已拥有 UCAgent 驱动的 audit、backpressure、CRV/coverage 和 dirty-writeback 闭环 stage，但完整验证实现尚未端到端地通过 stage 编排。

目前真实状况：

- `instruction.md` 中已单独验证 UCAgent/Codex 集成。
- Cache 专属的 `cache_regression_audit`、`backpressure_directed_tests`、`crv_coverage_bootstrap` 和 `dirty_writeback_coverage_closure` 四个 stage 已使用 `configs/ucagent_track1_cache.yaml` 通过 UCAgent 运行。
- 这些 stage 生成了 `docs/ucagent_output/stage_audit.md`、`docs/ucagent_output/backpressure_stage.md`、`docs/ucagent_output/crv_coverage_stage.md` 和 `docs/ucagent_output/dirty_writeback_stage.md`，并记录了回归或覆盖率通过。
- 本 Cache 工作区由 Codex 在共享仓库中实现，人工审查和决策记录在 `docs/ai_collaboration_report.md`。
- 当前 Cache 测试可通过 shell 脚本复现。

强烈 Track1 提交仍欠缺的：

- 早期技术实现 stage 最初并非通过 UCAgent 启动。
- Bug-injection 仍需直接的 UCAgent stage 证据。
- 下一个实现 stage 已列入 UCAgent config，应通过同一 `ucagent <workspace> Cache --backend codex` 路径执行。
- 报告必须区分 UCAgent 编排的工作和直接 Codex 辅助的工作。

因此，下一步文档和工作流目标是使 UCAgent 成为验证流程的可视化编排者，同时保持 Codex 作为后端实现 agent。

## UCAgent 在本项目中的角色

UCAgent 应作为 stage 控制器：

- 定义验证 stage 和预期交付物。
- 将每个 stage 的任务喂给 Codex 后端。
- 要求记录设计假设、生成文件、人工决策和测试结果的 journal。
- 仅在脚本/测试通过后将每个 stage 标记为完成。
- 保留最终输出文件供审查。

Codex 应作为实现后端：

- 检查 RTL 和生成的 Picker wrapper。
- 编辑源码、测试、脚本和 Markdown 文件。
- 运行 smoke、directed、regression、waveform、coverage 和 bug-injection 命令。
- 将发现报告回 UCAgent 的 stage journal 和最终 Markdown 交付物。

人工审查仍是必需的：

- 纠正 DUT 边界决策。
- 批准协议假设。
- 决定哪些生成的测试是有意义的。
- 识别并记录 AI 的误解。
- 决定覆盖率或 bug 证据何时达到提交强度。

## 建议的 Stage Contract

Cache 赛题任务应表示为以下 UCAgent stage。

| Stage | UCAgent Stage 名称 | 主要任务 | 必需的输出文件 |
| --- | --- | --- | --- |
| 0 | `inventory_and_dut_boundary` | 阅读要求，清点源文件，决定并论证选定 DUT。 | `docs/source_inventory.md`、`docs/dut_selection.md`、`docs/nutshell_build_probe.md` |
| 1 | `picker_export_and_interface_map` | 安装/验证 Picker，导出选定 Cache DUT，映射接口和协议常量。 | `docs/picker_installation.md`、`docs/interface_map.md`、`scripts/export_cache_dut.sh` |
| 2 | `smoke_closure` | 构建首个 reset/read/write smoke 测试和单命令运行器。 | `tests/smoke/test_cache_basic.py`、`scripts/run_smoke.sh`、`docs/test_points.md` |
| 3 | `structured_env_refactor` | 将原型重构为 env、monitor、scoreboard 和 utils。 | `src/env/cache_env.py`、`src/monitor/cache_monitor.py`、`src/scoreboard/cache_scoreboard.py`、`src/utils/simplebus.py` |
| 4 | `directed_cache_tests` | 添加写掩码、word 偏移和完整 refill 顺序的定向测试。 | `tests/directed/`、`scripts/run_directed.sh`、`scripts/run_regression.sh` |
| 5 | `backpressure_directed_tests` | 添加内存/CPU 响应反压测试。 | `tests/corner/test_backpressure.py`、`docs/ucagent_output/backpressure_stage.md` |
| 6 | `crv_coverage_bootstrap` | 添加受约束随机激励生成器和首次功能覆盖率收集。 | `tests/random/`、`docs/coverage_report.md`、`docs/ucagent_output/crv_coverage_stage.md` |
| 7 | `dirty_writeback_coverage_closure` | 添加 dirty-victim writeback/refill 覆盖率闭环。 | `tests/directed/test_dirty_writeback.py`、`docs/coverage_report.md`、`docs/ucagent_output/dirty_writeback_stage.md` |
| 8 | `bug_injection_evidence` | 添加故障注入测试和 bug 追踪证据。 | `tests/injected_bug/`、`docs/bug_tracking.md`、`docs/ucagent_output/bug_injection_stage.md` |
| 9 | `final_report_package` | 汇总最终报告和可复现性说明。 | `README.md`、`docs/ai_collaboration_report.md`、`top.md` |

## UCAgent 运行模板

预期命令应遵循 `instruction.md` 中已验证的本地 UCAgent/Codex 联动方式。

```sh
cd /Users/zzy/Workspace/ucagent
source .venv/bin/activate

UCAGENT_CMDLINE_START_MCP=1 \
UC_ENV_CMD_BACKEND_EX_ARGS="-m gpt-5.4-mini --ephemeral" \
ucagent /Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache Cache \
  --config /Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/configs/ucagent_track1_cache.yaml \
  --backend codex \
  --exit-on-completion \
  --mcp-server-no-file-tools \
  --mcp-server-host 127.0.0.1 \
  --mcp-server-port 5002 \
  --no-embed-tools \
  -s
```

初始的 `configs/ucagent_track1_cache.yaml` 文件是一个 audit stage 配置。它通过 UCAgent 验证了已有回归，现已扩展为完整的五阶段比赛流程。

初始 audit 结果：

- Stage：`cache_regression_audit`
- 输出文件：`docs/ucagent_output/stage_audit.md`
- 回归结果：`4 passed in 0.11s`
- UCAgent 工具证据：调用了 `SetCurrentStageJournal`、`Complete` 和 `Exit`。
- 日志解读说明：UCAgent 日志显示 `Complete: true`、`Exit: true`，Codex 后端返回码 0。外部 CLI 命令在 Exit 流程后以码 1 结束，因此应使用 stage audit 产物和工具日志作为完成证据。

## 运行指定后续 Stage

使用 `--force-stage-index` 通过辅助脚本，使新工作从目标 stage 开始，而非重新运行 audit stage。

```sh
cd /Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache

# Stage 1：backpressure 实现
scripts/run_ucagent_stage.sh 1

# Stage 2：CRV 和覆盖率引导
scripts/run_ucagent_stage.sh 2

# Stage 3：dirty writeback 覆盖率闭环
scripts/run_ucagent_stage.sh 3

# Stage 4：bug-injection 证据
scripts/run_ucagent_stage.sh 4
```

辅助脚本使用 `configs/ucagent_track1_cache.yaml`，启动 UCAgent MCP server，使用 Codex 作为后端，并保持 UCAgent 对每次单 stage 运行调用 `SetCurrentStageJournal`、`Complete` 然后 `Exit` 的要求。

配置检查：

- 命令：`ucagent ... --emulate-config --force-stage-index 1`
- 结果：UCAgent 识别了已配置的 stage 并选中 `backpressure_directed_tests` 为当前 stage。
- 注意：emulate 模式使用临时工作区，因此对后续 stage 将创建文件的缺失输出警告是预期现象。

## 当前 Config 结构

`configs/ucagent_track1_cache.yaml` 当前包含这些可运行 stage：

- Stage 0：`cache_regression_audit`
- Stage 1：`backpressure_directed_tests`
- Stage 2：`crv_coverage_bootstrap`
- Stage 3：`dirty_writeback_coverage_closure`
- Stage 4：`bug_injection_evidence`

这足以使后续实现工作保持在 UCAgent 通道上而非直接 Codex 执行。Stage 0 至 4 已通过此通道执行。

当前已执行 stage：

- Stage 0 `cache_regression_audit`：完成。
- Stage 1 `backpressure_directed_tests`：完成。
- Stage 2 `crv_coverage_bootstrap`：完成。
- Stage 3 `dirty_writeback_coverage_closure`：完成。
- Stage 4 `bug_injection_evidence`：完成。

下一项预期工作是 final report package 和可复现性清理。

## 报告规则

每个 UCAgent 驱动的 stage 应留下包含以下内容的报告条目：

- UCAgent stage 名称。
- Codex 后端操作。
- 生成或编辑的文件。
- 运行的命令和精确结果。
- 人工决定或修正。
- 该 stage 是否调用了 `Complete`。

这是当前可工作的验证代码与赛题要求的 UCAgent 辅助工程证明之间缺失的桥梁。
