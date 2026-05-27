# 验证计划

## 目标

以 UCAgent 辅助和人工审查的验证流程验证 NutShell Cache 设计。目标是产出一个可复现的验证环境，包含结构化的 Toffee 组件、受约束随机测试、功能覆盖率、scoreboard 检查和 bug 检测证据。

重要状态说明：

- 可执行的 Cache 验证环境已在通过 Picker/Python/Codex 工作推进中。
- Cache 任务现已拥有 UCAgent 编排的 audit、backpressure、CRV/coverage、dirty-writeback 闭环、bug-injection、final report、flush 和 coherence probe stage；post-coherence 的 write miss / eviction 定向闭环记录在 AI 协同报告中。
- `docs/ucagent_operation_plan.md` 定义了如何将当前工作转化为 UCAgent 可视化的工作流，包含 stage contract、输出文件和 journal 证据。
- `docs/ucagent_output/stage_audit.md`、`docs/ucagent_output/backpressure_stage.md`、`docs/ucagent_output/crv_coverage_stage.md`、`docs/ucagent_output/dirty_writeback_stage.md`、`docs/ucagent_output/bug_injection_stage.md`、`docs/ucagent_output/final_report_stage.md`、`docs/ucagent_output/flush_stage.md` 和 `docs/ucagent_output/coherence_probe_stage.md` 是当前 Cache 专属的 UCAgent 输出产物。

## UCAgent Stage 覆盖层

为更好地匹配 Track1 要求，以下每个技术阶段应映射到一个 UCAgent stage。

| 验证阶段 | 所需的 UCAgent Stage 证据 |
| --- | --- |
| 源文件准备 | Stage journal 记录源文件清单、DUT 边界决策，以及从完整 NutShell RTL 到 Picker Cache DUT 的人工修正。 |
| Picker 导出 | Stage 输出包含 Picker 命令、生成 wrapper 位置和导出通过/失败结果。 |
| Smoke 闭环 | Stage 输出包含 smoke 测试文件、运行器、命令结果和人工验收说明。 |
| 结构化环境 | Stage 输出包含 env/monitor/scoreboard/utils 文件，以及说明组件归属的审查说明。 |
| 定向测试 | Stage 输出包含定向测试、回归结果、波形路径和更新的测试点表格。 |
| CRV/coverage | Stage 输出包含随机激励生成器、覆盖率模型、覆盖率报告和覆盖率缺口关闭说明。 |
| Bug 证据 | Stage 输出包含故障注入测试、scoreboard 失败证据和 bug 追踪报告。 |

首次 audit 通过已运行：

```sh
ucagent /Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache Cache \
  --config /Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/configs/ucagent_track1_cache.yaml \
  --backend codex \
  --exit-on-completion
```

Audit 结果：

- Stage：`cache_regression_audit`
- 输出：`docs/ucagent_output/stage_audit.md`
- Audit 时间结果：`scripts/run_regression.sh` 以 `4 passed in 0.11s` 通过
- UCAgent 证据：Codex 后端调用了 `SetCurrentStageJournal`、`Complete` 和 `Exit`。

Backpressure 结果：

- Stage：`backpressure_directed_tests`
- 输出：`docs/ucagent_output/backpressure_stage.md`
- 当前结果：`scripts/run_regression.sh` 以 `6 passed in 0.11s` 通过

CRV/coverage 结果：

- Stage：`crv_coverage_bootstrap`
- 输出：`docs/ucagent_output/crv_coverage_stage.md` 和 `docs/coverage_report.md`
- 当前结果：`scripts/collect_coverage.sh 7 18` 以 `27 passed` 通过；`scripts/run_regression.sh` 以 `26 passed in 1.34s` 通过
- 已知缺口：当前功能覆盖率 bootstrap 集合中无缺口。

Dirty writeback 闭环结果：

- Stage：`dirty_writeback_coverage_closure`
- 输出：`docs/ucagent_output/dirty_writeback_stage.md` 和 `docs/coverage_report.md`
- 当前结果：`scripts/collect_coverage.sh 7 18` 以 `27 passed` 通过；`scripts/run_regression.sh` 以 `26 passed in 1.34s` 通过
- 覆盖率增量：`dirty_miss_writeback_refill` 从 `0` 变为 `1`。

## Phase 0：工作区和源文件准备

状态：源文件/工作区清单已完成；Picker 安装已完成；选定 DUT 已复制，Picker 导出已验证，首个 smoke 测试已实现，首个结构化 Python 验证环境骨架已建立。

任务：

- 确认本地 UCAgent/Codex 可用。
- 收集赛题说明和源参考。
- 克隆 GitLink 任务环境仓库。
- 获取 NutShell Cache 源参考。
- 安装本地 Java 运行时和匹配 NutShell `.mill-version` 的 Mill。
- 从 Chisel 源码生成 NutShell RTL。
- 决定 Picker 导出的 DUT wrapper 边界。
- 将 Picker `example/Cache` RTL 复制到赛题工作区。
- 为选定 DUT 验证 Picker 导出和生成的 Python wrapper。

退出标准：

- `docs/source_inventory.md` 识别所有必需源文件和当前缺口。
- 存在具体选定的 DUT 且可由 Picker 导出。

结果：

- 工作区骨架已创建。
- GitLink 任务模板已克隆。
- NutShell Cache 源和文档链接已验证可访问。
- 本地工具探测已完成。
- Picker 已安装并以小型 Adder 导出/导入/运行 smoke 测试验证。
- Java 运行时和 Mill 已通过 `scripts/env.sh` 本地安装。
- NutShell `BOARD=sim CORE=inorder` RTL 生成已完成，作源码上下文探索。
- 选定 DUT 边界确定于 `rtl/dut/Cache.v`，从 Picker `example/Cache/Cache.v` 复制。
- `scripts/export_cache_dut.sh` 验证 Picker 导出和 Python wrapper 生成。
- 首批结构化环境模块现已封装用于 reset、请求驱动、监控和 scoreboard 检查的 `DUTCache` 访问。
- 当前行动：完成最终文档和提交包同步。

## Phase 1：DUT 理解与最小闭环

任务：

- 阅读 Cache 文档和 `Cache.scala`。
- 提取顶层接口、传输类型、状态机和主要内部路径。
- 产出接口映射和功能/测试点列表。
- 使用 Picker 生成的 `DUTCache` wrapper。
- 运行 reset 加一个基本读/写 smoke 测试。

交付物：

- `docs/interface_map.md`
- `docs/test_points.md`
- `scripts/run_smoke.sh`
- `tests/smoke/`

注：`docs/cache_architecture.md` 未作为独立文档创建；架构描述已纳入 `docs/interface_map.md` 和 `docs/source_inventory.md`。

当前结果：

- `docs/interface_map.md` 已创建。
- `docs/test_points.md` 已创建。
- `scripts/run_smoke.sh` 已创建并通过。
- `tests/smoke/test_cache_basic.py` 覆盖 reset、读缺失/refill、读命中、写命中和写后读。
- Smoke 现使用 `src/env/cache_env.py`、`src/monitor/cache_monitor.py`、`src/scoreboard/cache_scoreboard.py` 和 `src/utils/simplebus.py`。

## Phase 2：结构化验证环境

任务：

- 构建 Toffee 风格的环境结构。
- 实现 Generator、Driver、Monitor、Scoreboard 和内存/参考模型。
- 将测试拆分为 smoke、定向 corner case、随机测试和故障注入测试。

交付物：

- `src/env/`
- `src/generator/`
- `src/monitor/`
- `src/scoreboard/`
- `src/utils/`
- `scripts/run_regression.sh`

当前结果：

- `src/env/cache_env.py` 提供首个可复用 DUT wrapper、reset 序列、周期步进、CPU 请求驱动、简单内存响应处理和 monitor 钩子。
- `src/monitor/cache_monitor.py` 记录 CPU 请求、CPU 响应和内存请求。
- `src/scoreboard/cache_scoreboard.py` 检查当前 smoke 级别的读/写响应和内存请求期望。
- `src/utils/simplebus.py` 集中管理 SimpleBus 命令常量和请求/响应数据类。
- `tests/directed/test_write_masks.py` 覆盖 cache 命中时的部分字节掩码写。
- `tests/directed/test_word_offsets.py` 覆盖同一 cache line 中 8 个 word 偏移的独立命中写/读。
- `tests/directed/test_refill_beats.py` 覆盖从非零 word 偏移开始的完整 8-beat refill 顺序。
- `tests/directed/test_invalid_way_replacement.py` 覆盖无效路替换优先级（优先于随机 victim 选择）。
- `tests/directed/test_mmio_bypass.py` 覆盖 MMIO 读写通过 `io_mmio_*` 路由及非命中行为。
- `tests/directed/test_flush_behavior.py` 覆盖空闲和 in-flight 状态下的 flush 行为、`io_empty` 验证及 cache 恢复（仅 io_flush[0]；io_flush[1] 被 D-cache 断言阻止）。
- `tests/directed/test_dirty_writeback.py` 覆盖脏 victim 写回/refill 闭环。
- `tests/directed/test_coherence_probe.py` 覆盖 coherence probe 命中/缺失响应。
- `tests/directed/test_write_miss.py` 覆盖 clean write miss refill 和写数据合并行为。
- `tests/directed/test_clean_eviction.py` 覆盖无写回的 clean victim 替换。
- `tests/directed/test_write_miss_dirty_eviction.py` 覆盖 write miss dirty eviction、writeback-before-refill 顺序以及 refill 后的部分掩码写合并。
- `scripts/run_directed.sh` 和 `scripts/run_regression.sh` 提供仅定向测试和 smoke+定向测试命令。
- 当前定向测试结果：`scripts/run_directed.sh` 以 `23 passed in 1.05s` 通过。
- 当前回归结果：`scripts/run_regression.sh` 以 `26 passed in 1.34s` 通过。
- 当前 UCAgent audit 结果：`configs/ucagent_track1_cache.yaml` stage `cache_regression_audit` 通过并记录 `docs/ucagent_output/stage_audit.md`。

## Phase 3：CRV 与覆盖率闭环

任务：

- 实现受约束随机流量。
- 添加针对缺失/命中、替换、脏写回、MMIO、flush 和突发路径的定向测试。
- 构建功能覆盖率点和覆盖率仓。
- 对覆盖率缺口进行迭代。

目标覆盖率：

- 功能覆盖率：尽量接近 100%，以 90%+ 为第一个里程碑。
- 行覆盖率：若 RTL 仿真流程可用则收集，GitLink 任务参考提到 96%+ 有效行覆盖率。

交付物：

- `tests/random/`
- `tests/corner/`
- `docs/coverage_report.md`
- `scripts/collect_coverage.sh`

当前结果：

- `src/generator/cache_random.py` 提供确定性的受约束随机读写流量。
- `src/utils/cache_coverage.py` 记录命令类型、命中/缺失代理、写掩码类别、word 偏移和 refill 路径仓。
- `src/utils/toffee_coverage.py` 记录更完整的 Toffee 功能覆盖率模型，包括 probe、MMIO、flush、clean eviction、clean write miss 和 dirty write miss 仓。
- `tests/random/test_random_cache.py` 通过 `scripts/collect_coverage.sh 7 18` 通过。
- `tests/directed/test_dirty_writeback.py` 以 4-way set 冲突测试关闭 dirty-victim writeback/refill 缺口，并验证 writeback/refill 序列。
- `docs/coverage_report.md` 记录完整覆盖率 bootstrap。已覆盖仓包括 read/write/probe 命令、命中/缺失代理、写掩码类别、所有 word 偏移、coherence probe、clean eviction 及 `dirty_miss_writeback_refill`。
- Toffee 功能覆盖率结果：12 个 group、31 个 point、37 个 bin，全部 100% covered。
- UCAgent stage `crv_coverage_bootstrap` 和 `dirty_writeback_coverage_closure` 将这些结果记录在 `docs/ucagent_output/crv_coverage_stage.md` 和 `docs/ucagent_output/dirty_writeback_stage.md`。
- 当前行动：保持覆盖率和最终报告文档与最新 directed closure 同步。

## Phase 4：Bug 注入与检测证据

任务：

- 创建可控 bug 场景。
- 通过 scoreboard、monitor 检查或断言展示检测能力。
- 记录触发方式、症状、根因、修复和重新运行结果。

候选注入 bug：

- 错误的命中/缺失判定。
- 错误的替换路。
- Dirty 位更新错误。
- 写回地址/数据不匹配。
- Refill 数据损坏。
- 反压下响应丢失。

交付物：

- `tests/injected_bug/`
- `docs/bug_tracking.md`

当前结果：

- `tests/injected_bug/run_bug_injection.py` 注入参考模型预期数据一位翻转。
- 默认运行触发 `CacheScoreboard.check_read_response()`，期望值为 `0x1122334455667789`，DUT 实际返回 `0x1122334455667788`。
- `--disable-bug` 使用干净参考模型运行同一流程并成功退出。
- 正常 `scripts/run_regression.sh` 套件保持干净，通过 `26 passed in 1.34s`。

## Phase 5：最终报告与可复现性

任务：

- 完成验证报告。
- 完成 AI 协同报告。
- 确保单命令 smoke/regression/coverage 流程。
- 清理中间文件。

交付物：

- `README.md`
- `docs/coverage_report.md`
- `docs/bug_tracking.md`
- `docs/ai_collaboration_report.md`
- 最终测试报告包。

当前结果：

- `scripts/reproduce.sh` 提供一键复现入口：依次运行正常回归、覆盖率收集、预期失败 bug 注入和 bug 恢复路径，已通过 `scripts/clean_generated.sh && scripts/reproduce.sh -> PASS` 验证。
- `scripts/clean_generated.sh` 清理生成的 build、Python cache、本地波形和 pytest cache 等产物。
- `scripts/run_bug_injection.sh` 包装受控 bug-injection harness，支持 `--disable-bug` 恢复模式。
- `README.md`、`docs/ai_collaboration_report.md` 和 `docs/coverage_report.md` 已经过 UCAgent stage 与 post-coherence directed closure 迭代。
- 最终报告打包已在 post-final directed tests 后刷新。`docs/ucagent_output/final_report_stage.md` 记录审查文件、命令结果、提交检查清单和剩余风险。
- 最新验证：`scripts/run_directed.sh -> 23 passed in 1.05s`；`scripts/run_regression.sh -> 26 passed in 1.34s`；`scripts/reproduce.sh -> [reproduce] PASS`。
