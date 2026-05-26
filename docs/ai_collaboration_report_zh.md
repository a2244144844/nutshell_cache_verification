# AI 协同报告

本报告记录 UCAgent/Codex 生成或辅助的内容、人工检查的内容以及由工程判断做出的修改。

## UCAgent 使用评估

当前评估：项目拥有较强的 Codex 辅助验证工作，且现已拥有针对 audit、backpressure、CRV/coverage bootstrap 和 dirty-writeback 闭环四个 stage 的直接 Cache 专属 UCAgent 证据。Bug-injection 证据是下一个预期的 UCAgent stage，不应被视为已完成。

已验证的 UCAgent 能力：

- `instruction.md` 记录了成功的本地 UCAgent → Codex 后端 → UCAgent MCP 流程。
- 该 smoke 流程完成了 `SetCurrentStageJournal`、`Complete` 和 `Exit`。

当前 Cache 任务状态：

- `configs/ucagent_track1_cache.yaml` 已存在。
- UCAgent 通过 Codex 后端运行了 `cache_regression_audit`、`backpressure_directed_tests`、`crv_coverage_bootstrap` 和 `dirty_writeback_coverage_closure` 四个 stage。
- 这些 stage 检查了规划/测试文件，运行了指定命令，写入了 `docs/ucagent_output/stage_audit.md`、`docs/ucagent_output/backpressure_stage.md`、`docs/ucagent_output/crv_coverage_stage.md` 和 `docs/ucagent_output/dirty_writeback_stage.md`，并调用了 `SetCurrentStageJournal` 和 `Complete`。
- Audit 回归结果为 `4 passed in 0.11s`。
- Dirty-writeback 闭环 stage 结果为 `scripts/collect_coverage.sh 7 18 -> 1 passed in 0.12s` 和 `scripts/run_regression.sh -> 7 passed in 0.13s`。
- 清理越界 bug-injection 草稿后最新本地复查：`tests/directed/test_dirty_writeback.py -> 1 passed in 0.17s`，`scripts/collect_coverage.sh 7 18 -> 1 passed in 0.04s`，`scripts/run_regression.sh -> 7 passed in 0.13s`。
- Dirty-writeback 运行期间，UCAgent/Codex 在 `Complete` 后短暂推进到了下一个 bug-injection stage；这些越界草稿产物已被移除，Stage 4 将在下一步有意运行。
- 部分早期实现 stage 仍由 Codex 直接完成，因此报告不得暗示它们最初是 UCAgent 编排的。

修复计划：

- 使用 `scripts/run_ucagent_stage.sh <stage_index>` 执行后续实现 stage。
- 下一步用 `scripts/run_ucagent_stage.sh 4` 运行 `bug_injection_evidence`，并仅在该有意运行完成后记录受控故障/恢复证据。
- 每个后续 stage 在本报告中记录 UCAgent stage 名称、journal 摘要、输出文件、命令、通过/失败结果和人工审查决定。
- 以 `docs/ucagent_operation_plan.md` 为操作地图。

## 日志

| 步骤 | 日期 | AI 辅助内容 | 人工审查/决定 | 结果 |
| --- | --- | --- | --- | --- |
| Step 0 | 2026-05-25 | 根据赛题要求和本地 UCAgent/Codex 操作指南生成 `step.md`。 | 审查了计划并决定增量推进。 | 分阶段执行计划已创建。 |
| Step 1 | 2026-05-25 | 检查本地仓库，验证 UCAgent/Codex 版本，搜索 Cache/NutShell 材料，克隆 GitLink 任务环境，下载可访问的 NutShell Cache 源参考。 | 判定当前仓库尚未包含实际的 NutShell DUT 构建树；克隆的 GitLink 仓库是任务模板而非 DUT 实现。 | 创建了赛题工作区和源文件清单。 |
| Step 2 | 2026-05-25 | 从源码安装 Picker，识别 Python ABI 不匹配，修补本地 CMake 文件将 Picker Python 支持绑定到 `.venv` Python 3.11，用 `examples/Adder/Adder.v` 验证导出。 | 选择本地用户前缀安装以避免 `sudo`；仅接受 C++/Python 语言支持，因为 Toffee 验证需要 Python。 | Picker 安装于 `local/picker`；`xspcomm` 导入和 Adder 导出/运行 smoke 测试通过。 |
| Step 3 | 2026-05-25 | 安装本地 Azul Zulu JRE 17 和 Mill 0.11.7，下载 NutShell 源码树及缺失的 `difftest` 子模块，诊断 `NOOP_HOME`，为 `BOARD=sim CORE=inorder` 生成分割 SystemVerilog RTL。 | 使用工作区本地工具而非系统安装；将生成的 RTL 视为中间产物，上游/下载目录不纳入版本控制。 | NutShell RTL 生成成功；Cache 相关 RTL 变体在 `upstream/NutShell/build/rtl` 下可用。 |
| Step 3 修正 | 2026-05-25 | 用户反馈后重新检查 Picker 的 `example/Cache` 目录，确定 `example/Cache/Cache.v` 为选定 DUT，复制到 `rtl/dut/`，用 `.venv` Python 3.11 验证 Picker 导出。 | 将 DUT 边界从完整 NutShell 生成 RTL 修正；保留 NutShell 构建输出仅作源码上下文参考。 | 选定 DUT 现为 `rtl/dut/Cache.v`；`scripts/export_cache_dut.sh` 成功构建 `DUTCache`。 |
| Step 4 | 2026-05-26 | 映射选定 DUT 接口，从 RTL 和实验中推导 SimpleBus 命令常量，编写驱动 `DUTCache` 的 pytest smoke。 | 保持首个测试范围窄：一次冷读缺失/refill、一次读命中、一次写命中、一次写后读命中。 | `scripts/run_smoke.sh` 以 `1 passed` 通过；创建了接口和测试点文档。 |
| Step 5 | 2026-05-26 | 将 smoke 测试重构为可复用的 Python 验证骨架，包含 env、monitor、scoreboard 和 SimpleBus 工具模块。 | 保持首个 env 刻意小型化，与已观测到的 DUT 行为绑定，之后扩展到随机或覆盖率流程。 | `scripts/run_smoke.sh` 仍以 `1 passed` 通过；创建了 `top.md` 作为 Markdown 文档索引。 |
| Step 6 | 2026-05-26 | 新增针对部分写掩码和同 line word 偏移的定向测试，以及定向/回归运行脚本。 | 在实现完整的 8-beat refill 模型前先选择命中路径定向测试。 | `scripts/run_directed.sh` 以 `2 passed` 通过；`scripts/run_regression.sh` 以 `3 passed` 通过。 |
| Step 7 | 2026-05-26 | 扩展 Cache 环境以驱动多节拍内存 refill，新增从非零 word 偏移开始的 8-beat refill 定向测试。 | 保留 smoke 测试的现有单节拍快捷方式，同时为真实 refill 测试添加显式 `refill_beats` 支持。 | `scripts/run_directed.sh` 以 `3 passed` 通过；`scripts/run_regression.sh` 以 `4 passed` 通过。 |
| Step 8 | 2026-05-26 | 重新评估当前项目是否可视化展示了 UCAgent 操作，重写文档以暴露差距和集成路线。 | 决定不夸大：当前 Cache 验证为 Codex 辅助，UCAgent 编排是必需的下一步集成工作。 | 创建了 `docs/ucagent_operation_plan.md`；更新了 README、verification plan、collaboration report 和顶层 Markdown 索引。 |
| Step 9 | 2026-05-26 | 创建 `configs/ucagent_track1_cache.yaml` 并通过 UCAgent 以 Codex 后端运行 `cache_regression_audit` stage。 | 保持该 stage 低风险：检查 docs/scripts，运行已有回归，写入 stage audit 产物，调用 journal/Complete/Exit。 | `docs/ucagent_output/stage_audit.md` 已创建；UCAgent stage 记录 `scripts/run_regression.sh` PASS，`4 passed in 0.11s`。UCAgent 日志显示 `Complete: true`、`Exit: true`，Codex 后端返回码 0，但外部 CLI 进程在 Exit 流程后以码 1 结束。 |
| Step 10 | 2026-05-26 | 扩展 `configs/ucagent_track1_cache.yaml`，添加 backpressure、CRV/coverage、dirty writeback 闭环和 bug injection 四个后续实现 stage，新增按 stage 运行 UCAgent 的辅助脚本。 | 选择 `--force-stage-index` 使后续工作可从目标实现 stage 开始，避免每次都重新运行 audit stage。 | 新增 `scripts/run_ucagent_stage.sh`；`ucagent --emulate-config --force-stage-index 1` 成功选中 `backpressure_directed_tests` 为当前 stage。后续 stage 配置为通过 UCAgent/Codex 运行而非直接 Codex 执行。 |
| Step 11 | 2026-05-26 | 新增专注于内存请求和 CPU 响应反压的定向测试，在 `src/env/cache_env.py` 中添加原始驱动/采样辅助方法，更新 `scripts/run_regression.sh` 包含 corner 测试。 | 保持环境扩展最小化，使测试显式控制 `io_out_mem_req_ready` 和 `io_in_resp_ready` 时序，而非依赖不透明的辅助行为。 | `tests/corner/test_backpressure.py` 以 `2 passed in 0.11s` 通过；`scripts/run_regression.sh` 以 `6 passed in 0.16s` 通过。UCAgent 运行在被停止前短暂推进到 CRV/coverage；CRV 后续在 Step 12 中有意完成。 |
| Step 12 | 2026-05-26 | 通过 UCAgent 实现 CRV bootstrap stage：规范化受约束随机生成器种子和合法的 line-base 处理，运行覆盖率 bootstrap 脚本，运行完整回归脚本，撰写首份功能覆盖率报告和 stage 产物。 | 使用已有 cache DUT 导出流程并记录覆盖率缺口而非掩盖，因为首个 bootstrap 报告预期留出 dirty writeback/refill 闭环供下一 stage 处理。`Complete` 后 UCAgent 短暂推进到 bug-injection stage；该越界被停止，越界草稿文件已移除。 | `scripts/collect_coverage.sh 7 18` 以 `1 passed in 0.09s` 通过；`scripts/run_regression.sh` 以 `6 passed in 0.11s` 通过。覆盖率摘要：read 11 / write 7，hit 15 / miss 3，写掩码类别全部覆盖（含 sparse），word 偏移 0-7 全覆盖，refill 路径 `clean_miss_refill` 3、`read_hit` 8、`write_hit` 7、`dirty_miss_writeback_refill` 0。 |
| Step 13 | 2026-05-26 | 通过 UCAgent 实现 dirty-victim writeback/refill 闭环：新增 4-way set 冲突定向测试，使环境支持在 refill 前应答 writeback 节拍，扩展随机/覆盖率流程以触发脏路径，更新全部文档集。 | 在确认 victim 为四个冲突路之一且覆盖率报告显示 `dirty_miss_writeback_refill` 已覆盖后接受 writeback/refill 证据。 | `tests/directed/test_dirty_writeback.py` 以 `1 passed in 0.04s` 通过；`scripts/collect_coverage.sh 7 18` 以 `1 passed in 0.12s` 通过；`scripts/run_regression.sh` 以 `7 passed in 0.13s` 通过。覆盖率增量：`dirty_miss_writeback_refill` 从 `0` 变为 `1`。 |
| Step 14 | 2026-05-26 | 新增受控 bug-injection harness 于 `tests/injected_bug/`，在参考模型预期数据中注入一位翻转损坏，编写 `docs/bug_tracking.md` 和 stage 输出产物。 | 将失败视为有意的证据：损坏后的预期值触发 `CacheScoreboard.check_read_response()`，而关闭注入路径证明同一流程可干净恢复。 | `tests/injected_bug/run_bug_injection.py` 以码 `1` 退出并检出预期 scoreboard 失败；`tests/injected_bug/run_bug_injection.py --disable-bug` 以码 `0` 退出；最新 `scripts/run_regression.sh` 以 `7 passed in 0.14s` 通过。 |

## 当前人工决策

- 将赛题工作保持在 `competition/track1_nutshell_cache/` 下，使 UCAgent 框架仓库与验证产物分离。
- 将 `examples/GenSpec/DCache` 仅作为参考，不作为赛题 DUT。
- 将 `rtl/dut/Cache.v` 作为选定 DUT。
- 将当前 smoke 视为首个可执行验证基线；在声称有意义覆盖率之前先以定向测试拓宽。
- 每当任务 Markdown 文件新增或用途变更时维护 `top.md`。
- 目前声明 `cache_regression_audit`、`backpressure_directed_tests`、`crv_coverage_bootstrap`、`dirty_writeback_coverage_closure` 和 `bug_injection_evidence` 为 UCAgent 驱动的 stage。

## 需关注的已知 AI/自动化风险

- 将 XiangShan DCache 示例误读为 NutShell Cache 目标。
- 将完整生成的 NutShell RTL 误读为赛题 DUT，而 Picker 的 Cache 示例已提供预期的 RTL。
- 在实际 DUT 接口确定之前就生成测试。
- 选择完整芯片 RTL 导出，而聚焦的 Cache wrapper 更可控。
- 在没有可复现命令和产物支撑的情况下报告覆盖率。
- 将直接由 Codex 运行的 Cache 工作夸大为 UCAgent stage 驱动。
