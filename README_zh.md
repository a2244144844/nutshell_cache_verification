# Track1 NutShell Cache 验证工作区

本工作区用于 CCF Track1 UCAgent 赛题：以 UCAgent 辅助、人工审查的方式完成对 NutShell Cache 的验证。

## 当前状态

- 本机已安装 UCAgent 和 Codex CLI。
- UCAgent/Codex 和 UCAgent/Claude Code 联动已验证通过，且已产生针对 Cache 的 audit、backpressure、CRV/coverage、dirty-writeback、bug-injection、final report、flush 和 coherence probe 八个 stage 的证据记录。
- GitLink 赛题环境仓库已克隆到 `upstream/env-xs-ov-00-nutshell-cache`。
- 选定 DUT 为 Picker 的 Cache 示例 RTL，已复制到 `rtl/dut/Cache.v`。
- Picker 将选定 DUT 导出为 Python 类 `DUTCache`。
- `scripts/run_smoke.sh` 已通过首个 reset/read/write smoke test。
- 首个可复用的 Python 验证骨架已建立，位于 `src/env`、`src/monitor`、`src/scoreboard` 和 `src/utils`。
- 定向测试目前覆盖了部分写掩码、同 cache line 内不同 word 偏移、完整 8-beat refill 顺序、无效路替换优先级、MMIO 旁路、flush 行为、coherence probe 命中/缺失、write miss、clean eviction、dirty-victim writeback/refill，以及 write miss dirty eviction 闭环。
- `scripts/run_directed.sh` 目前通过全部 directed 测试，共 `23 passed in 1.05s`。
- `scripts/run_regression.sh` 目前通过 smoke、directed、corner 测试，共 `26 passed in 1.34s`。
- `scripts/collect_coverage.sh 7 18` 通过完整覆盖率采集运行，结果为 `27 passed`；Toffee 功能覆盖率模型为 12 个 group、31 个 point、37 个 bin，全部 100% covered。
- 首个 Cache 专属 UCAgent audit stage 已完成，生成了 `docs/ucagent_output/stage_audit.md`。
- UCAgent backpressure、CRV/coverage、dirty-writeback 闭环、bug-injection、final report、flush 和 coherence probe stage 已完成，生成了 `docs/ucagent_output/backpressure_stage.md`、`docs/ucagent_output/crv_coverage_stage.md`、`docs/ucagent_output/dirty_writeback_stage.md`、`docs/ucagent_output/bug_injection_stage.md`、`docs/ucagent_output/final_report_stage.md`、`docs/ucagent_output/flush_stage.md` 和 `docs/ucagent_output/coherence_probe_stage.md`。
- `scripts/reproduce.sh` 是一键复现入口，已从清理生成物后的状态验证通过。

## UCAgent 集成状态

当前验证进展真实且可复现。项目现已拥有八个 Cache 专属 UCAgent stage 产物，覆盖 audit、backpressure、CRV/coverage、dirty-writeback 闭环、bug-injection 证据、最终报告打包、flush 行为和 coherence probe。后续由其他 agent 完成的 write miss / eviction 定向补强已记录在 AI 协同报告中。

- 已有工作：Codex 在本工作区中实现并运行了 Cache 验证文件。
- 工作区外已验证：`instruction.md` 证明了本地 UCAgent → Codex → MCP `Complete` 路径可运行。
- 工作区内已验证：`configs/ucagent_track1_cache.yaml` 通过 UCAgent/Codex 或 UCAgent/Claude Code 运行了已配置的 Cache stage，记录了 stage journal 并调用了 `Complete`。
- 提交就绪：已配置的 UCAgent stage 已完成，post-coherence 定向测试干净通过，回归干净，可复现入口已验证通过。
- Config 校验通过：`ucagent --emulate-config --force-stage-index 1` 识别了全部 stage 并选中 backpressure stage。
- 最终报告打包已完成。参见 `docs/ucagent_output/final_report_stage.md`。
- 集成计划：参见 `docs/ucagent_operation_plan.md`。

## 工作目录

```text
competition/track1_nutshell_cache/
├── LICENSE
├── README.md
├── top.md
├── configs/
│   └── ucagent_track1_cache.yaml
├── docs/
│   ├── ai_collaboration_report.md
│   ├── bug_tracking.md
│   ├── dut_selection.md
│   ├── interface_map.md
│   ├── nutshell_build_probe.md
│   ├── picker_installation.md
│   ├── source_inventory.md
│   ├── test_points.md
│   ├── ucagent_operation_plan.md
│   ├── ucagent_output/
│   │   ├── backpressure_stage.md
│   │   ├── bug_injection_stage.md
│   │   ├── coherence_probe_stage.md
│   │   ├── crv_coverage_stage.md
│   │   ├── dirty_writeback_stage.md
│   │   ├── final_report_stage.md
│   │   └── stage_audit.md
│   └── verification_plan.md
├── rtl/
│   └── dut/
├── src/
│   ├── env/
│   ├── generator/
│   ├── monitor/
│   ├── scoreboard/
│   └── utils/
├── tests/
│   ├── smoke/
│   ├── corner/
│   ├── directed/
│   ├── random/
│   └── injected_bug/
├── scripts/
│   ├── clean_generated.sh
│   ├── collect_coverage.sh
│   ├── reproduce.sh
│   ├── run_bug_injection.sh
│   ├── run_ucagent_stage.sh
│   ├── run_regression.sh
│   ├── run_directed.sh
│   └── run_smoke.sh
└── upstream/
    └── env-xs-ov-00-nutshell-cache/
```

## 验证完成

当前提交包内计划的验证工作均已完成：

1. 最终报告打包和可复现性清理已完成。
2. Bug-injection harness 保持在正常回归路径之外，`scripts/run_regression.sh` 仍干净通过 `26 passed in 1.34s`。
3. 完整可复现入口 `scripts/reproduce.sh` 已验证通过。

## 模板对齐报告集

UCAgent 模板风格的整合 Markdown 交付物位于：

```text
unity_test/
```

`unity_test/Cache_basic_info.md`、`unity_test/Cache_verification_needs_and_plan.md`、`unity_test/Cache_functions_and_checks.md`、`unity_test/Cache_line_coverage_analysis.md`、`unity_test/Cache_bug_analysis.md` 和 `unity_test/Cache_test_summary.md` 已将 `docs/` 下的过程记录整合成提交面向报告。

## 可复现入口

在本工作区运行：

```sh
scripts/reproduce.sh
```

它会依次运行正常回归、默认 seed `7` / `18` 条事务的覆盖率收集、预期失败的 bug 注入，以及关闭 bug 注入后的恢复路径。清理生成物可运行：

```sh
scripts/clean_generated.sh
```

最新验证：

```text
scripts/clean_generated.sh && scripts/reproduce.sh -> PASS
```
