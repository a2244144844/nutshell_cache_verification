# Track1 NutShell Cache 验证工作区

本工作区用于 CCF Track1 UCAgent 赛题：以 UCAgent 辅助、人工审查的方式完成对 NutShell Cache 的验证。

## 当前状态

- 本机已安装 UCAgent 和 Codex CLI。
- UCAgent/Codex 联动已验证通过，且已产生针对 Cache 的 audit、backpressure、CRV/coverage、dirty-writeback 和 bug-injection 五个 stage 的 UCAgent 运行记录。
- GitLink 赛题环境仓库已克隆到 `upstream/env-xs-ov-00-nutshell-cache`。
- 选定 DUT 为 Picker 的 Cache 示例 RTL，已复制到 `rtl/dut/Cache.v`。
- Picker 将选定 DUT 导出为 Python 类 `DUTCache`。
- `scripts/run_smoke.sh` 已通过首个 reset/read/write smoke test。
- 首个可复用的 Python 验证骨架已建立，位于 `src/env`、`src/monitor`、`src/scoreboard` 和 `src/utils`。
- 定向测试目前覆盖了部分写掩码、同 cache line 内不同 word 偏移、完整 8-beat refill 顺序以及 dirty-victim writeback/refill 闭环。
- `scripts/run_regression.sh` 目前通过 smoke、directed、corner 测试，共 `7 passed in 0.14s`。
- `scripts/collect_coverage.sh 7 18` 通过 CRV/coverage bootstrap，`1 passed in 0.04s`，dirty writeback 缺口现已关闭。
- 首个 Cache 专属 UCAgent audit stage 已完成，生成了 `docs/ucagent_output/stage_audit.md`。
- UCAgent backpressure、CRV/coverage、dirty-writeback 闭环和 bug-injection stage 已完成，生成了 `docs/ucagent_output/backpressure_stage.md`、`docs/ucagent_output/crv_coverage_stage.md`、`docs/ucagent_output/dirty_writeback_stage.md` 和 `docs/ucagent_output/bug_injection_stage.md`。
- `scripts/reproduce.sh` 是一键复现入口，已从清理生成物后的状态验证通过。

## UCAgent 集成状态

当前验证进展真实且可复现。项目现已拥有五个 Cache 专属 UCAgent stage 产物，最终提交前仍需完成最终报告 stage。

- 已有工作：Codex 在本工作区中实现并运行了 Cache 验证文件。
- 工作区外已验证：`instruction.md` 证明了本地 UCAgent → Codex → MCP `Complete` 路径可运行。
- 工作区内已验证：`configs/ucagent_track1_cache.yaml` 通过 UCAgent/Codex 运行了 `cache_regression_audit`、`backpressure_directed_tests`、`crv_coverage_bootstrap`、`dirty_writeback_coverage_closure` 和 `bug_injection_evidence`，记录了 stage journal 并调用了 `Complete`。
- 下一 stage 就绪：最终报告包和提交前复核。
- Config 校验通过：`ucagent --emulate-config --force-stage-index 1` 识别了全部 5 个 stage 并选中 backpressure stage。
- 仍缺：最终报告包装需要专门一轮整理。
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
│   │   ├── crv_coverage_stage.md
│   │   ├── dirty_writeback_stage.md
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
│   ├── random/
│   ├── corner/
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

## 下一步

继续以 UCAgent 为 stage 控制器扩展测试：

1. 完成最终报告包。
2. 提交前复跑 `scripts/reproduce.sh`。

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
