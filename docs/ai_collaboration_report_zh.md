# AI 协同报告

本报告记录 UCAgent/Codex 生成或辅助的内容、人工检查的内容以及由工程判断做出的修改。

## UCAgent 使用评估

当前评估：项目拥有较强的 Codex/Claude 辅助验证工作，且现已拥有针对 audit、backpressure、CRV/coverage bootstrap、dirty-writeback 闭环、bug-injection、final-report、flush、coherence-probe、补充 write-miss/eviction replay，以及官方 GenSpec 六阶段流程的直接 Cache 专属 UCAgent 证据。Post-coherence 的 write miss 和 eviction closure 由其他 agent 完成，并在本日志中单独记录。

已验证的 UCAgent 能力：

- `instruction.md` 记录了成功的本地 UCAgent → Codex 后端 → UCAgent MCP 流程。
- 该 smoke 流程完成了 `SetCurrentStageJournal`、`Complete` 和 `Exit`。

当前 Cache 任务状态：

- `configs/ucagent_track1_cache.yaml` 已存在。
- UCAgent 通过 Codex 或 Claude Code 后端运行了 `cache_regression_audit`、`backpressure_directed_tests`、`crv_coverage_bootstrap`、`dirty_writeback_coverage_closure`、`bug_injection_evidence`、`final_report_package`、`flush_directed_test` 和 `coherence_probe_directed_test`。
- 这些 stage 检查了规划/测试文件，运行了指定命令，写入了 `docs/ucagent_output/stage_audit.md`、`docs/ucagent_output/backpressure_stage.md`、`docs/ucagent_output/crv_coverage_stage.md`、`docs/ucagent_output/dirty_writeback_stage.md`、`docs/ucagent_output/bug_injection_stage.md`、`docs/ucagent_output/final_report_stage.md`、`docs/ucagent_output/flush_stage.md` 和 `docs/ucagent_output/coherence_probe_stage.md`，并调用了 `SetCurrentStageJournal` 和 `Complete`。
- Audit 回归结果为 `4 passed in 0.11s`。
- 历史 dirty-writeback 闭环 stage 结果为 `scripts/collect_coverage.sh 7 18 -> 1 passed in 0.12s` 和 `scripts/run_regression.sh -> 7 passed in 0.13s`。
- 历史 bug-injection evidence stage 结果为 `tests/injected_bug/run_bug_injection.py -> exit 1` 并检出预期 scoreboard 失败，`tests/injected_bug/run_bug_injection.py --disable-bug -> exit 0`。
- 最新提交面向验证：`scripts/run_directed.sh -> 23 passed in 1.05s`；`scripts/run_regression.sh -> 26 passed in 1.34s`。
- 2026-05-27，UCAgent 在 `genspec_workspace/` 中运行官方 GenSpec 流程，生成 `unity_test/Cache_spec.md`、六份子规范、`unity_test/Cache_functions_and_checks.md`、`unity_test/Cache_line_func_map.md`，并通过 `FileLineMapChecker`。
- 部分早期实现 stage 以及 post-coherence 的 write miss / eviction closure 由 Codex/Claude 风格 agent 直接完成，因此报告不得暗示它们最初是 UCAgent 编排的。

修复计划：

- 使用 `scripts/run_ucagent_stage.sh <stage_index>` 执行后续实现 stage。
- 如需重新声明 post-coherence directed closure 为 UCAgent-run，应通过新的 UCAgent stage 重放；否则继续按直接 agent 工作记录。
- 每个后续 stage 在本报告中记录 UCAgent stage 名称、journal 摘要、输出文件、命令、通过/失败结果和人工审查决定。
- 以 `docs/ucagent_operation_plan.md` 为操作地图。

## AI 缺陷与人工修正对比表

本表面向提交评分中的“协同过程记录”要求，记录 agent 辅助路径中被人工审查、Prompt 调整或直接工程修改纠正的具体问题。

| 问题 / 盲区 | AI 或自动化行为 | 人工修正 / 决策 | 证据 |
| --- | --- | --- | --- |
| DUT 边界选择 | 早期探索偏向完整 NutShell 生成 RTL 和 XiangShan 风格参考。 | 用户反馈后重新检查 Picker `example/Cache`，最终选择 `rtl/dut/Cache.v` 作为聚焦 DUT，完整 NutShell 输出仅保留为上下文。 | Step 3 修正；`docs/dut_selection.md`；`rtl/dut/Cache.v` |
| UCAgent 参与度夸大风险 | 早期 Cache 工作主要是直接 Codex 工作，不是 UCAgent stage 编排。 | 新增 `configs/ucagent_track1_cache.yaml`、`scripts/run_ucagent_stage.sh` 和 stage 产物，并在报告中区分 UCAgent-run 与 direct-agent work。 | Steps 8-10；`docs/ucagent_output/*.md` |
| `Complete` 后 stage 越界 | UCAgent 有时在完成当前 stage 后推进到下一个 stage。 | 在 prompt 中要求 `Complete` 后调用 `Exit`；记录越界并移除越界草稿产物。 | Steps 12-13；`docs/ucagent_output/crv_coverage_stage.md` |
| 随机覆盖过浅 | 初版 CRV bootstrap 覆盖了合法流量，但未覆盖 dirty writeback/refill。 | 增加 4-way set conflict 脏 victim 定向测试并扩展覆盖率采集，直到 `dirty_miss_writeback_refill` 被观测到。 | Step 13；`tests/directed/test_dirty_writeback.py`；`docs/coverage_report.md` |
| 复杂 write-miss 路径缺失 | 早期测试主要覆盖 write hit 和 read miss。 | 增加 clean write miss、clean eviction、dirty write miss with eviction 定向测试，并扩展 Toffee coverage。 | Steps 19-21；`tests/directed/test_write_miss*.py`；`tests/directed/test_clean_eviction.py` |
| Probe pipeline 时序 | 生成式 probe 驱动过早清除 valid，导致请求未进入 S1/S2/S3。 | 调整 valid/step 顺序以匹配 DUT pipeline，并记录 probe data 的微结构限制。 | Step 18；`tests/directed/test_coherence_probe.py`；`docs/ucagent_output/coherence_probe_stage.md` |
| Flush 覆盖过度 | 朴素测试会同时 assert 两个 flush bit，但 D-cache 实例对 `io_flush[1]` 有断言约束。 | 定向测试限定使用 `io_flush[0]`，并将限制写入 stage 产物和风险项。 | Step 17；`tests/directed/test_flush_behavior.py`；`docs/ucagent_output/flush_stage.md` |
| 报告再生成漂移 | 手工整理的 coverage report 强于 `collect_coverage.sh` 的可再生报告模板。 | 更新覆盖率脚本，使其重新生成 Toffee summary，并保留 legacy random bins 与 Toffee 闭环的区别。 | Step 23；`scripts/collect_coverage.sh`；`docs/coverage_report.md` |

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
| Step 14 | 2026-05-26 | 新增受控 bug-injection harness 于 `tests/injected_bug/`，在参考模型预期数据中注入一位翻转损坏，编写 `docs/bug_tracking.md` 和 stage 输出产物。 | 将失败视为有意的证据：损坏后的预期值触发 `CacheScoreboard.check_read_response()`，而关闭注入路径证明同一流程可干净恢复。 | `tests/injected_bug/run_bug_injection.py` 以码 `1` 退出并检出预期 scoreboard 失败；`tests/injected_bug/run_bug_injection.py --disable-bug` 以码 `0` 退出；stage 当时 `scripts/run_regression.sh` 以 `7 passed in 0.14s` 通过。 |
| Step 15 | 2026-05-26 | 新增一键复现入口 `scripts/reproduce.sh`、bug-injection wrapper `scripts/run_bug_injection.sh` 和清理辅助脚本 `scripts/clean_generated.sh`；移除 `scripts/collect_coverage.sh` 中的硬编码工作区路径。 | 选择从清理生成物后的状态验证，使入口能够在单一路径中证明重建、回归、覆盖率、有意 bug 失败及恢复。 | `bash -n` 通过所有 shell 脚本；`scripts/run_bug_injection.sh --disable-bug` 通过；`scripts/clean_generated.sh && scripts/reproduce.sh` 以 `[reproduce] PASS` 完成。 |
| Step 16 | 2026-05-26 | 检查所有交付文档（README.md、ai_collaboration_report.md 等），运行 `scripts/run_regression.sh` 和 `scripts/reproduce.sh`，审查提交就绪性，新增 Prompt Strategy Review 章节，创建 `docs/ucagent_output/final_report_stage.md`，更新 `top.md`。 | 审查所有文档完整性；验证一键复现仍通过；确认当时已有的 UCAgent stage 有输出产物；确认 prompt 策略和人工-vs-AI 决策已记录。 | Stage 当时结果：`scripts/run_regression.sh -> 7 passed in 0.15s`；`scripts/reproduce.sh -> [reproduce] PASS`；final report stage 产物已创建；提交检查清单已完成。 |
| Step 17 | 2026-05-26 | 通过 UCAgent stage 6（Claude Code 后端）实现 DIR-007 flush 行为定向测试：检查 Cache.v 中的 io_flush/io_empty/needFlush 逻辑，发现 D-cache 断言阻止 io_flush[1]，实现三个仅使用 io_flush[0] 的测试函数，运行定向和完整回归套件，创建 stage 输出产物。 | 适配测试在 D-cache 约束下工作（`ro.B=false` 断言阻止 io_flush[1]）；仅使用 io_flush=0b01 进行 S1→S2 pipeline flush；验证 pipeline squash 时序（在 pipeline 捕获前 assert flush）。 | `tests/directed/test_flush_behavior.py -> 3 passed in 0.05s`；`tests/directed/ -> 13 passed in 0.12s`；`scripts/run_regression.sh -> 16 passed in 0.13s`。 |
| Step 18 | 2026-05-26 | 通过 Claude Code 实现 DIR-008 coherence probe 定向测试：分析 `io_out_coh_req_*` / `io_out_coh_resp_*` 和 S1/S2/S3 pipeline，修正 probe valid 清除时序，新增空 cache probe miss、probe hit、不同地址 probe miss 三个测试。 | 接受首个 probe hit 的 rdata 受 S3 dataWay 寄存器状态约束这一 DUT 微结构行为，并在 stage 产物中说明风险。 | `tests/directed/test_coherence_probe.py -> 3 passed in 0.01s`；`tests/directed/ -> 16 passed in 0.59s`；`scripts/run_regression.sh -> 20 passed in 0.72s`。 |
| Step 19 | 2026-05-26 | 通过 Claude Code 实现 DIR-011 write miss 定向测试：分析 CacheStage3 clean write-miss 流程，新增全掩码、部分掩码合并和 8-beat wrap-around refill 三个测试，并扩展 Toffee coverage。 | 确认原有 WRITE 操作均为 write hit，write miss 是此前未覆盖的独立微架构路径。 | `tests/directed/test_write_miss.py -> 3 passed in 0.23s`；`scripts/run_regression.sh -> 22 passed in 0.89s`；Toffee funcov 100% covered。 |
| Step 20 | 2026-05-26 | 通过 Claude Code 实现 DIR-012 clean eviction 定向测试：新增 set conflict clean replacement 与 surviving-line data integrity 两个测试，并扩展 clean eviction coverage。 | 将 clean eviction 与 DIR-004 invalid-way fill、DIR-005 dirty writeback 区分开；使用 refill-data-protected re-read 验证替换行为。 | `tests/directed/test_clean_eviction.py -> 2 passed in 0.24s`；`scripts/run_regression.sh -> 24 passed in 1.13s`；Toffee funcov 100% covered。 |
| Step 21 | 2026-05-26 | 通过 Claude Code 实现 DIR-013 write miss + dirty eviction 定向测试：新增 dirty victim writeback+refill sequencing 和 partial-mask write merge after dirty eviction 两个测试，并为 `cache_write_miss` coverage 添加 clean/dirty bins。 | 验证 dirty eviction 中 writeback 先于 refill，且 refilled line 中的写数据合并正确。 | `tests/directed/test_write_miss_dirty_eviction.py -> 2 passed in 0.34s`；`scripts/run_regression.sh -> 26 passed in 1.16s`；Toffee funcov：12 groups、31 points、37 bins，全部 100% covered。 |
| Step 22 | 2026-05-26 | 刷新所有提交面向文档：README、中文 README、verification plan、test points、operation plan、coverage 中文镜像、final report stage、top 索引和协同报告。 | 保留早期 UCAgent stage 产物作为历史证据，但将当前总览文档统一到最新验证结果。 | `scripts/run_directed.sh -> 23 passed in 1.05s`；`scripts/run_regression.sh -> 26 passed in 1.34s`；最终文档区分 UCAgent-run stage 与 post-coherence 直接 agent 工作。 |
| Step 23 | 2026-05-27 | 按最终评分细则重新审视项目，新增显式“AI 缺陷与人工修正对比表”，并修复 `scripts/collect_coverage.sh`，使重新生成的 coverage report 也包含 Toffee summary 数据。 | 将报告可复现性视为工程质量的一部分：脚本再生成的文档不能弱于手工整理的提交文档。 | `scripts/collect_coverage.sh` 现在会生成 legacy bin 表和 Toffee group/point/bin summary，并保留 random bootstrap gap 与 Toffee 闭环之间的区别。 |
| Step 24 | 2026-05-27 | 通过 UCAgent 运行官方 GenSpec 流程：生成 `Cache_spec.md`、六份子规范、更新后的 FG/FC/CK 矩阵和 CK 到 `Cache.v` 的行映射。新增 `unity_test/tests/Cache_api.py` 与 `unity_test/tests/Cache_function_coverage_def.py`，作为现有 `CacheEnv` 和 Toffee coverage 的标准薄包装。 | `human_check` 生成了 `Cache_spec_summary.md`；由于 `--exit-on-completion` 下无法稳定注入交互式通过命令，本次采用人工确认后从 stage 4 恢复继续。包装层保持最小化，避免影响现有回归。 | `FileLineMapChecker -> PASS`，`Cache/Cache.v` 全部行已映射或忽略；`python3 -m py_compile ... -> PASS`；`scripts/run_regression.sh -> 28 passed in 5.76s`；`scripts/reproduce.sh -> [reproduce] PASS`。 |

## 当前人工决策

- 将赛题工作保持在 `competition/track1_nutshell_cache/` 下，使 UCAgent 框架仓库与验证产物分离。
- 将 `examples/GenSpec/DCache` 仅作为参考，不作为赛题 DUT。
- 将 `rtl/dut/Cache.v` 作为选定 DUT。
- 将当前 smoke 视为首个可执行验证基线；在声称有意义覆盖率之前先以定向测试拓宽。
- 每当任务 Markdown 文件新增或用途变更时维护 `top.md`。
- 目前声明 `cache_regression_audit`、`backpressure_directed_tests`、`crv_coverage_bootstrap`、`dirty_writeback_coverage_closure`、`bug_injection_evidence`、`final_report_package`、`flush_directed_test`、`coherence_probe_directed_test`、补充 `write_miss_eviction_replay` 和官方 GenSpec 流程为 UCAgent 驱动证据。
- Write miss 和 eviction closure 步骤按 post-coherence 直接 agent 工作记录，除非后续通过 UCAgent stage 重放。

## 需关注的已知 AI/自动化风险

- 将 XiangShan DCache 示例误读为 NutShell Cache 目标。
- 将完整生成的 NutShell RTL 误读为赛题 DUT，而 Picker 的 Cache 示例已提供预期的 RTL。
- 在实际 DUT 接口确定之前就生成测试。
- 选择完整芯片 RTL 导出，而聚焦的 Cache wrapper 更可控。
- 在没有可复现命令和产物支撑的情况下报告覆盖率。
- 将直接由 Codex 运行的 Cache 工作夸大为 UCAgent stage 驱动。
