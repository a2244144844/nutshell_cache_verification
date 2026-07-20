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

本表面向提交评分中的"协同过程记录"要求，记录 agent 辅助路径中被人工审查、Prompt 调整或直接工程修改纠正的具体问题。

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
| 行覆盖率豁免粒度 | 初始方案整体豁免 `Cache_top.sv`（Picker 生成的 DPI wrapper），但用户质疑整体文件豁免是否合适。 | 分析 `Cache_top.sv` 组成（~126 个 DPI getter/setter 函数，全部由 Picker 生成）；建议整体文件豁免作为生成测试台基础设施的行业标准做法；对 `Cache.v` 做逐行分析并施加 12 行精确豁免（Categories A-G），同时保留 H/I/J 类别作为潜在测试目标。 | Step 25；`docs/coverage_waiver_rationale.md`；`tests/conftest.py` |
| Verilator 覆盖率禁用缺口 | 不存在 Verilator `--coverage-exclude` 编译标志；只能在后处理层面进行过滤。 | 使用 `toffee_test` 的 `ignore_patterns` 机制，通过 `fnmatch` 过滤文件级模式，通过 `parse_ignore_miss_lines()` 过滤行范围模式（`file.v:line1,range1-range2`）。| Step 25；`docs/coverage_waiver_rationale.md` |
| Toffee 分支覆盖率报告遗漏 | LCOV HTML 显示 85% 分支覆盖率（C++ 级，28,949 个分支），而 `code_coverage.json` 为 95.3%（RTL 级，494 个分支）。`convert_line_coverage()` 计算出正确的 RTL 数值，但仅对 C++ 级 `merged.info` 生成 HTML。 | 追溯 toffee-test 源码（`__init__.py` 第 34 行，`processor.py` 第 40 行）记录精确的流水线缺口；从 `code_coverage.json` 生成 `rtl_coverage.html` 作为提交用可视化；在 `docs/toffee_branch_coverage_gap.md` 中记录缺口分析及源码证据，并对 toffee-test 提供修复建议。 | Step 30；`docs/toffee_branch_coverage_gap.md`；`build/reports/rtl_coverage.html` |

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

- 将赛题工作保持在 `competition/` 下，使 UCAgent 框架仓库与验证产物分离。
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
- 将 I-cache 配置约束下的结构不可达行误判为测试覆盖缺口——需要通过 RTL 信号链追踪区分"测试不足"和"硬件配置不可达"。详见 Category D（needFlush）和 Category K（respToL1Last）的豁免分析。

## Stage 11：行覆盖率 100% — DIR-017 与 DIR-018（2026-05-31）

### UCAgent + Claude Code 协同执行

**后端：** Claude Code CLI（`claude --dangerously-skip-permissions -p`）连接至 UCAgent MCP 服务器（127.0.0.1:5002）。
**阶段：** `12-line_coverage_100`（索引 11）

### 自动生成代码（UCAgent + Claude Code）

UCAgent 启动 Claude Code 作为后端 agent。Claude Code 独立完成：

1. **DIR-017**（`test_needflush_assert_and_deassert`，位于 `test_flush_behavior.py`）：
   - 生成了使用低级引脚控制的完整测试
   - 正确构建了测试流程：drive_cpu_request → assert flush → 等待 io_empty → 取消 flush → 手动引脚驱动第二个请求
   - 使用 `io_out_mem_resp_valid/bits_*` 引脚处理内存响应驱动
   - 捕获并验证 CPU 响应数据和 user 字段

2. **DIR-018**（`test_read_burst_hit_resptol1_counter`，位于 `test_read_burst_hit.py`）：
   - 生成了填充 cache line、驱动 READ_BURST 并统计响应拍数的测试
   - 同时捕获 CPU 响应（`io_in_resp_*`）和一致性响应（`io_out_coh_resp_*`）拍数

### 人工干预与优化

1. **豁免识别 — 第 605、608、610 行**：确认 respToL1Last 计数器在 I-cache 模式下不可达。这些行需要 8 拍 CPU 响应路径，仅 D-cache 中存在。I-cache 的多拍释放通过一致性端口使用 `releaseLast` 计数器。已加入 `conftest.py` 的 `ignore_patterns` 并记录在 `coverage_waiver_rationale.md` Category K。

2. **覆盖分析 — 第 558、788 行已解决（2026-05-31）**：经过 DIR-017 测试和更深入的 RTL 分析，确认这两行在 I-cache 模式下**结构上不可达**。根因：
   - `Cache.v:2786`：`assign s3_io_flush = io_flush[1];` — CacheStage3 的 `io_flush` 硬连接到 `io_flush[1]`
   - I-cache 中，断言 `!(!ro.B && io_flush)` 阻止 `io_flush[1]` 被置 1
   - 因此 CacheStage3 的 `io_flush` 始终为 0，`_GEN_1` 退化为自循环，`needFlush` 永不离复位值 0
   - 与第 2861-2862 行（Category D，已豁免）共享同一根因
   - **解决方案**：作为 Category D 扩展豁免。已加入 `conftest.py` 的 `ignore_patterns`。行覆盖率 → **1359/1359（100.0%）**。

3. **文档完整性**：所有要求的输出文件已更新：test_points.md、coverage_waiver_rationale.md（扩展 Category D）、coverage_waiver_rationale_zh.md（完整重写）、coverage_closure_final.md、coverage_closure_final_zh.md、ai_collaboration_report.md、ai_collaboration_report_zh.md。

### 执行的命令

```bash
# 单个测试验证
python -m pytest tests/directed/test_flush_behavior.py::test_needflush_assert_and_deassert -v → PASSED
python -m pytest tests/directed/test_read_burst_hit.py::test_read_burst_hit_resptol1_counter -v → PASSED

# 完整回归
scripts/run_regression.sh → 32 passed in 8.34s

# 覆盖率采集
scripts/collect_coverage.sh 7 18 → 32 passed, Line: 1359/1359 (100.0%)
```

### 覆盖增量

| 阶段 | 覆盖率 | 未覆盖行 | 已豁免行 |
|---|---|---|---|
| Stage 11 前 | 1359/1364 (99.6%) | 5 (558,605,608,610,788) | 16 |
| Stage 11 初始 | 1359/1361 (99.9%) | 2 (558,788) | 19 |
| **D 类扩展豁免后** | **1359/1359 (100.0%)** | **0** | **21** |

## Stage 12 — 分支覆盖率闭环（2026-05-31）

UCAgent Stage：`branch_coverage_closure` | 后端：Claude Code CLI | 配置：`configs/ucagent_track1_cache.yaml` | Stage 索引：12

### UCAgent 流程

- 通过 UCAgent MCP 服务器启动（RoleInfo → SetCurrentStageJournal → Complete → Exit 工作流）。
- 检查 `Cache.v`（CacheStage3 第 530-630、760-830 行）、现有定向测试、`tests/conftest.py`、`docs/coverage_waiver_rationale.md` 和 `docs/coverage_closure_final.md`。
- 实现 DIR-019（新建 `test_prefetch.py`，2 个测试）、DIR-020（扩展 `test_write_miss_dirty_eviction.py`，1 个测试）、DIR-021（扩展 `test_coherence_probe.py`，2 个测试）。
- DIR-022（state2 FSM else-if 第 824 行）确认为已被覆盖 — false-case 在结构上不可达。
- 8 条新 P2 分支豁免作为 Category N 应用于 `tests/conftest.py`。
- 在 `docs/coverage_waiver_rationale.md` 中新增 Category N 分支豁免文档，包含每条线的分析。

### 变更文件

| 文件 | 变更 |
|---|---|
| `tests/directed/test_prefetch.py` | 新建 — DIR-019 PREFETCH 响应门控测试 |
| `tests/directed/test_write_miss_dirty_eviction.py` | 扩展 — DIR-020 写回节拍计数器测试 |
| `tests/directed/test_coherence_probe.py` | 扩展 — DIR-021 内部 probe 路径测试 |
| `tests/conftest.py` | 新增 8 条分支豁免（Category N） |
| `docs/coverage_waiver_rationale.md` | 新增 Category N 分支豁免 |
| `docs/test_points.md` | 新增 DIR-019 至 DIR-022 |
| `docs/ucagent_output/branch_coverage_closure_stage.md` | 已创建 Stage 12 产物 |
| `docs/ai_collaboration_report.md` | 已更新 Stage 12 条目 |

### 人工干预

1. **PREFETCH 测试重写**：初版使用 `send_cpu_request()`，因 PREFETCH 抑制 `io_in_resp_valid`（第 2674 行门控）导致超时。重写为使用低级引脚驱动（`env.drive_cpu_request` + 手动步进循环）。

2. **Verilator 覆盖率文件冲突**：发现 `VCache_coverage.dat` 以只读权限写入 CWD。顺序运行单个测试失败。解决方法：每次测试前 `rm -f VCache_coverage.dat`，或使用在单个 pytest 进程中运行所有测试的 `collect_coverage.sh`。

3. **分支豁免分析**：全部 8 个剩余未覆盖分支确认在 I-cache 模式下不可达：
   - 第 550, 555, 626 行：writeL2BeatCnt 计数器 — 需要 WRITE_BURST/LAST 输入命令（内存总线侧，永不来自 CPU）
   - 第 768, 777, 796 行：probe/MMIO 路径 — D-cache 特有状态转换
   - 第 824 行：state2 else-if false 分支 — state2 永不等于 3
   - 第 2674 行：PREFETCH 响应门控 TRUE 分支 — PREFETCH 在 I-cache 中永不达输出阶段

4. **豁免文档**：在 `coverage_waiver_rationale.md` 中新增 Category N，含逐一行的详细分析。用 8 条额外分支豁免更新 `conftest.py`。

### 执行的命令

```bash
# 单个 DIR 测试验证
python -m pytest tests/directed/test_prefetch.py -v → 2 passed in 0.52s
python -m pytest tests/directed/test_write_miss_dirty_eviction.py::test_writeback_multi_beat_counter_exercise -v → 1 passed in 0.30s
python -m pytest tests/directed/test_coherence_probe.py::test_internal_probe_miss_through_io_in_req tests/directed/test_coherence_probe.py::test_internal_probe_hit_through_io_in_req -v → 2 passed in 0.39s

# 完整覆盖率采集
scripts/collect_coverage.sh 7 18 → 37 passed in 8.85s
```

### 覆盖增量

| 指标 | Stage 11 后 | Stage 12 后 | 增量 |
|---|---|---|---|
| 分支覆盖 | 471/494 (95.3%) | **471/471 (100.0%)** | +23 豁免 |
| 未覆盖分支 | 23 | 0 | -23 |
| 定向测试 | 28 | 33 | +5 |
| 回归通过 | 32 | 37 | +5 |
| 分支豁免 | 9（L、M 类） | 17（+N 类：8 条） | +8 |

## Stage 13 — 翻转覆盖率提升（2026-05-31）

UCAgent Stage：`toggle_coverage_improvement` | 后端：Claude Code CLI | 配置：`configs/ucagent_track1_cache.yaml` | Stage 索引：13

### UCAgent 流程

- 通过 UCAgent MCP 服务器启动（RoleInfo → SetCurrentStageJournal → Complete → Exit 工作流）。
- 检查 `src/generator/cache_random.py`、`tests/random/test_random_cache.py`、`scripts/collect_coverage.sh` 和 RTL 覆盖率数据。
- 用双模式设计扩展随机生成器（`enable_extended=False` 保留原始行为，`enable_extended=True` 添加 MMIO、probe、flush、READ_BURST、PREFETCH 和冷 miss 流量）。
- 创建 `tests/random/test_random_multi_seed.py` — 面向翻转覆盖率的专项测试，在单个 pytest 进程中运行多个 seed 以实现累积 Verilator 覆盖率。
- 创建 `scripts/collect_coverage_multi.sh` — 结合 smoke + directed + corner + 多 seed 随机运行。
- 在 `docs/toggle_coverage_waiver.md` 中记录翻转豁免类别 T-A 至 T-F，含各模块预期最大值。
- 生成 `docs/ucagent_output/toggle_coverage_improvement_stage.md`，包含完整逐模块增量、平台期分析和实现说明。

### 变更文件

| 文件 | 变更 |
|---|---|
| `src/generator/cache_random.py` | 扩展：`enable_extended` 标志、`_build_extended_random_ops`、`_build_basic_random_ops`、`_build_mmio_ops`、`_build_probe_ops`、`_build_flush_ops`、16 种多样化数据模式、32 个扩展 line base |
| `tests/random/test_random_multi_seed.py` | 新建：多 seed 随机测试（seed 间 DUT 复位，无 scoreboard 检查 — 仅翻转） |
| `scripts/collect_coverage_multi.sh` | 新建：多 seed 覆盖率采集（默认 5 seed × 100 步） |
| `docs/toggle_coverage_waiver.md` | 新建：6 个翻转豁免类别（T-A 至 T-F） |
| `docs/ucagent_output/toggle_coverage_improvement_stage.md` | 新建：完整 Stage 13 产物 |
| `docs/test_points.md` | 更新：Stage 13 翻转覆盖率状态 |
| `docs/ai_collaboration_report.md` | 更新：Stage 13 条目 |

### 人工干预

1. **翻转覆盖率平台期**：5 seed × 100 步后翻转达 24785/28227（87.8%）。测试 8 seed × 200 步产生零额外命中，确认剩余 3442 个缺失为结构性原因。决定不追求递减收益。

2. **无 Scoreboard 的测试设计**：多 seed 测试跳过所有 scoreboard 检查，因为 cache 数据在 DUT 复位后仍然保留。对翻转覆盖率而言，正确性无关紧要 — 目标是信号翻转。功能正确性已由回归套件验证。

3. **生成器向后兼容**：原始 `CacheRandomGenerator.build_workload()` 行为通过 `enable_extended=False` 默认值保留。现有 `test_random_cache.py` 带着 scoreboard 检查不变运行。

### 执行的命令

```bash
# 标准多 seed 覆盖率（5 seed × 100 步）
scripts/collect_coverage_multi.sh → 37 passed in 18.13s

# 扩展多 seed 测试（8 seed × 200 步）
CACHE_RANDOM_SEEDS="7,13,42,99,256,512,1024,2048" CACHE_RANDOM_STEPS="200" pytest ... → 37 passed in 38.75s

# 完整回归
scripts/run_regression.sh → 37 passed in 6.56s
```

### 覆盖增量

| 指标 | Stage 12 后 | Stage 13 后 | 增量 |
|---|---|---|---|
| 翻转 | 24474/28227 (86.7%) | **24785/28227 (87.8%)** | +311 |
| 行 | 1359/1359 (100.0%) | 1359/1359 (100.0%) | — |
| 分支 | 471/471 (100.0%) | 471/471 (100.0%) | — |
| 表达式 | 131/137 (95.6%) | 131/137 (95.6%) | — |

### 主要改善模块

| 模块 | Stage 12 | Stage 13 | Δ |
|---|---|---|---|
| Cache | 9847/11440 (86.1%) | 9965/11440 (87.1%) | +118 |
| SRAMTemplate | 581/820 (70.9%) | 618/820 (75.4%) | +37 |
| Arbiter_4 | 591/744 (79.4%) | 625/744 (84.0%) | +34 |
| CacheStage3 | 4129/4682 (88.2%) | 4160/4682 (88.9%) | +31 |
| CacheStage1 | 1094/1238 (88.4%) | 1121/1238 (90.5%) | +27 |

## Stage 16 — 表达式覆盖率闭环（Category O 豁免）（2026-05-31）

UCAgent Stage：`expr_coverage_closure` | 后端：Claude Code CLI | 配置：`configs/ucagent_track1_cache.yaml` | Stage 索引：16

### UCAgent 流程

- 通过 UCAgent MCP 服务器启动（RoleInfo → SetCurrentStageJournal → Complete → Exit 工作流）。
- 检查 `tests/conftest.py`、`docs/coverage_waiver_rationale.md`、`unity_test/Cache_functions_and_checks.md`、`unity_test/Cache_line_func_map.md`、`unity_test/Cache_line_map_analysis.md` 及所有 `_zh.md` 镜像。
- 向 `tests/conftest.py` 的 `ignore_patterns` 添加 6 个表达式缺失行（274, 787, 889, 913, 937, 961），在 Cache.v 模式内按排序插入。
- 更新注释块添加 Category O 说明。
- 在 `docs/coverage_waiver_rationale.md` 中新增 Category O 章节，包含逐行分析表和最终豁免汇总更新。
- 更新所有中文镜像文件。

### 变更文件

| 文件 | 变更 |
|---|---|
| `tests/conftest.py` | 向 ignore_patterns 添加 6 个表达式行 |
| `docs/coverage_waiver_rationale.md` | 新增 Category O 章节，更新汇总和覆盖率数据 |
| `docs/coverage_waiver_rationale_zh.md` | 新增 Category O 中文章节 |
| `unity_test/Cache_functions_and_checks.md` | 新增 CK-WAIVER-CAT-O |
| `unity_test/Cache_functions_and_checks_zh.md` | 更新覆盖率数据 |
| `unity_test/Cache_line_func_map.md` | 新增 Category O IGNORE 映射 |
| `unity_test/Cache_line_func_map_zh.md` | 新增 Category O 至豁免表 |
| `unity_test/Cache_line_map_analysis.md` | 新增 Expr 章节 |
| `unity_test/Cache_line_map_analysis_zh.md` | 新增 Expr 章节 |
| `docs/test_points.md` 和 `_zh.md` | 新增 Stage 16 条目 |
| `docs/ai_collaboration_report.md` 和 `_zh.md` | 新增 Stage 16 条目 |
| `docs/ucagent_output/expr_coverage_closure_stage.md` | 创建 Stage 16 UCAgent 产物 |
| `top.md` 和 `top_zh.md` | 新增 Stage 16 条目 |

### 覆盖增量

| 指标 | Stage 13 后 | Stage 16 后 | 增量 |
|---|---|---|---|
| Expr | 131/137 (95.6%) | **137/137 (100.0%)** | +6 豁免 (Category O) |
| 行 | 1359/1359 (100.0%) | 1359/1359 (100.0%) | — |
| 分支 | 471/471 (100.0%) | 471/471 (100.0%) | — |
| 翻转 | 24785/28227 (87.8%) | 24785/28227 (87.8%) | — |
| 总豁免数 | 42 (A-N) | 48 (+Category O: 6) | +6 |

### Stage 17 — 翻转覆盖率最终尝试（2026-05-31）

- **UCAgent 阶段：** `toggle_improvement_final`，定义在 `configs/ucagent_track1_cache.yaml`。
- **内容：** 执行最激进的翻转覆盖率提升尝试——10 seed、200 步/seed、64 地址基址、32 数据模式。
- **命令结果：**
  ```
  Line:   1359/1359 = 100.0%
  Branch: 471/471  = 100.0%
  Toggle: 24947/28227 = 88.4%  （从 87.8% +162）
  Expr:   137/137 = 100.0%
  37 tests, 0 failures
  ```
- **覆盖率增量：**
  | 指标 | 之前（Stage 16）| 之后（Stage 17）| 增量 |
  |---|---|---|---|
  | 翻转 | 24785/28227 (87.8%) | 24947/28227 (88.4%) | +162 |
  | 行 | 1359/1359 (100.0%) | 1359/1359 (100.0%) | — |
  | 分支 | 471/471 (100.0%) | 471/471 (100.0%) | — |
  | 表达式 | 137/137 (100.0%) | 137/137 (100.0%) | — |
- **结论：** 翻转覆盖率平台期确认在 88.4%。剩余 3,280 次缺失属于结构性原因（T-A~T-F）。豁免采用文档化方式，因为 `toffee_test` 的 `filter_coverage()` 不具备类型感知。

## Stage 21：功能覆盖率闭环 — 71/92 (77.2%) → 91/91 (100%)（2026-06-01）

UCAgent Stage: `funcov_closure` | Backend: Claude Code CLI | 通过 UCAgent MCP Server

### 人工分析阶段

修复 tracker 组（A1，+4 点）和添加 probe 交叉状态测试（A2，+4 点）后，功能覆盖率处于 71/92（77.2%），剩余 21 个仓缺口，分布如下：

| 缺口组 | 缺失仓数 | 问题性质 |
|--------|---------|---------|
| `cache_write_hit_x_wmask` | 18/48 | 随机测试偏向低地址，offset 3-7 覆盖不足 |
| `cache_miss_x_addr_type` | 1（`miss_mmio`） | 物理不可达——MMIO 永不产生 cache miss |
| `cache_probe_x_cache_state` | 2（`probe_hit_empty`、`probe_miss_dirty`） | 一个不可达，一个模型语义错误 |

人工将缺口按优先级分类：
- **P0**：删除 2 个物理不可达仓（`probe_hit_empty`、`miss_mmio`）
- **P1**：修复 `_eval_probe_cross` 对 probe_miss 的语义——将"被探测行状态"改为"全局 cache 状态"
- **P2**：新增 18 个定向测试覆盖缺失的 write_hit_x_wmask 组合

### AI 执行阶段（通过 UCAgent MCP Server + Claude Code）

**P0 — 删除不可达仓**：
- 从 `src/utils/toffee_coverage.py` 的 `cache_miss_x_addr_type` 移除 `miss_mmio`
- 从 `cache_probe_x_cache_state` 移除 `probe_hit_empty`（probe 不可能命中空行，该行从未被填充）
- 同步更新 `src/utils/cache_coverage.py` 的 EXPECTED_BINS

**P1 — 修复 probe_miss 模型语义**：
- 重写 `_eval_probe_cross` 函数：probe_miss 仓现检查全局 cache 状态（`any(self._line_dirty.values())` / `self._line_valid`），而非被探测行的状态（对 miss 而言始终为空）
- probe_hit 仓保持检查命中行的特定状态
- 使 `probe_miss_valid` 和 `probe_miss_dirty` 语义正确可达

**P2 — 新增 write_hit_x_wmask 定向测试**：
- 在 `tests/directed/test_write_hit_wmask.py` 中新增 18 个测试，使用 0x8000_2000+ 范围的独立 cache line 基地址
- byte(3,4)、adjacent(0,4,5)、low_half(0,5,6)、high_half(0,6,7)、full(2,3,4,6,7)、sparse(0,1)
- 文件总计 44 个测试，覆盖全部 48 种 wmask × offset 组合

### 人工审阅阶段

1. 运行 `scripts/collect_coverage.sh 7 18` → 86 passed，确认 91/91 点（100%）、98/98 仓（100%）
2. 指示 AI 更新 6 个 markdown 文档（英文原版 + 中文镜像），添加完成状态及逐组分解
3. 创建 `manual_finding_funcov_gap_zh.md` 和 `funcov_closure_action_plan_zh.md`
4. 同步 `top.md` / `top_zh.md` 索引中的全部新增条目

### 涉及命令

```bash
.venv/bin/python -m pytest competition/tests/directed/test_write_hit_wmask.py -v → 44 passed in 11.85s
.venv/bin/python -m pytest competition/tests/directed/test_coherence_probe.py -v → 10 passed in 2.48s
.venv/bin/python -m pytest competition/tests/directed/ -v → 81 passed in 19.93s
bash scripts/collect_coverage.sh 7 18 → 86 passed, 91/91 points (100%), 98/98 bins (100%)
```

### 修改文件

| 文件 | 变更 |
|------|------|
| `src/utils/toffee_coverage.py` | 修复 tracker 返回值, 移除 2 个不可达仓, 修复 probe_miss 的 `_eval_probe_cross` |
| `src/utils/cache_coverage.py` | 同步 `EXPECTED_BINS` 与模型变更 |
| `tests/directed/test_write_hit_wmask.py` | 新增 18 个缺失的 wmask × offset 组合（共 44 个测试，覆盖 48/48 仓） |
| `docs/manual_finding_funcov_gap.md` | 重写——添加解决状态及最终覆盖率数据 |
| `docs/manual_finding_funcov_gap_zh.md` | 新建——中文镜像 |
| `docs/funcov_closure_action_plan.md` | 重写——添加已完成状态及逐组分解 |
| `docs/funcov_closure_action_plan_zh.md` | 新建——中文镜像 |
| `docs/ai_collaboration_report.md` | 新增 Step 31 日志条目 |
| `top.md` | 更新日期，更新两条文档描述 |
| `top_zh.md` | 更新日期，新增英文条目 + 中文镜像条目 |

### 覆盖率增量

| 指标 | 之前 | 之后 | 增量 |
|---|---|---|---|
| Toffee 点数 | 71/92 (77.2%) | **91/91 (100%)** | +20 |
| Toffee 仓数 | 79/100 (79.0%) | **98/98 (100%)** | +19 |
| 行覆盖率 | 1359/1359 (100.0%) | 1359/1359 (100.0%) | — |
| 分支覆盖率 | 471/471 (100.0%) | 471/471 (100.0%) | — |

### 人机协同模式

- **人工主导**：覆盖率缺口分类（P0/P1/P2）、优先级排序、RTL 可达性分析
- **AI 执行**：代码修改（模型修复 + 测试编写）、一轮覆盖率验证、文档撰写
- **人工审阅**：覆盖率结果验证、文档完整性检查、中英文配套要求
