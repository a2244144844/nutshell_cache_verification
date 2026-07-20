# Track1 NutShell Cache 验证工作区

本工作区用于 CCF Track1 UCAgent 赛题：以 UCAgent 辅助、人工审查的方式完成对 NutShell Cache 的验证。

## 一等奖评审路径

建议评审按以下顺序快速阅读：

1. `docs/reviewer_quickstart_zh.md` — 命令、预期结果、交付边界。
2. `final_report/nutshell_cache_report.pdf` — 最终参赛报告。
3. `docs/ai_collaboration_report.md` — AI/人工分工、Prompt 策略、人工修正和阶段证据。
4. `docs/coverage_report_zh.md` + `docs/coverage_waiver_rationale_zh.md` + `docs/toggle_coverage_waiver_zh.md` — 覆盖率闭环和豁免依据。

## 评审快速上手（3 条命令）

1. **一键复现**：`make reproduce`
   - 预期输出：`[reproduce] PASS`（回归 + 覆盖率 + bug 注入 + 恢复）

2. **覆盖率报告**：
   - RTL：`open build/reports/rtl_coverage.html` — Line 100.0% | Branch 100.0% | Toggle 88.4% | Expr 100.0%
   - 功能覆盖：`open build/reports/cache_coverage.html` — 18 组、91 点、98 bins，全部 100%

3. **关键文档**（推荐阅读顺序）：

   | 文档 | 用途 |
   |------|------|
   | `docs/reviewer_quickstart_zh.md` | 三分钟评审路线、命令清单和交付边界 |
   | `docs/ai_collaboration_report.md` | AI-人工协同日志、缺陷对照表、Prompt 策略、17 个阶段 |
   | `docs/verification_plan.md` | 分阶段验证计划与当前状态 |
   | `docs/coverage_waiver_rationale.md` | 逐行豁免分析（15 个类别，48 行/表达式豁免） |
   | `docs/gap_analysis_first_prize.md` | 一等奖差距分析与改进行动计划 |

## 当前状态

- 本机已安装 UCAgent 和 Claude Code CLI。
- 18 个 UCAgent 阶段（0-17）通过 `configs/ucagent_track1_cache.yaml` 以 Claude Code 后端完成。
- 选定 DUT 为 Picker 的 Cache 示例 RTL，已复制到 `rtl/dut/Cache.v`。
- Picker 将选定 DUT 导出为 Python 类 `DUTCache`。
- `make test-smoke` 已通过首个 reset/read/write smoke test。
- 结构化验证环境位于 `src/env`、`src/monitor`、`src/scoreboard`、`src/utils`、`src/generator`。
- 当前 `tests/` 可收集 86 个测试，覆盖 smoke、directed、corner、random 及 multi-seed random。
- 这里的 86 是 pytest 测试用例数量；Toffee 功能覆盖中的 91 是 coverage point 数量，二者不是同一个指标。
- 定向测试覆盖：部分写掩码、同行 word 偏移、refill beats、替换、MMIO 旁路、flush、coherence probe、write miss、clean eviction、dirty writeback、read-burst hit、write-miss dirty eviction、PREFETCH。
- `make test-directed` 运行 directed suite。
- `make test` 运行 smoke + directed + corner 回归。
- `scripts/collect_coverage.sh` 运行完整 `tests/` 套件并生成 Toffee/RTL 覆盖率报告。
- `make coverage-multi` 通过，Toffee 功能覆盖率：18 组、91 点、98 bins，全部 100%。
- RTL 覆盖率：**Line 1359/1359 (100.0%) | Branch 471/471 (100.0%) | Toggle 24947/28227 (88.4%) | Expr 137/137 (100.0%)**。
- 48 行/表达式豁免，覆盖 Categories A-O（参见 `docs/coverage_waiver_rationale.md`）。
- Toggle 豁免：3,280 个 toggle 缺失，Categories T-A~T-F（参见 `docs/toggle_coverage_waiver.md`）。
- `make reproduce` 是一键复现入口，已从清理生成物后的状态验证通过。
- Bug 注入证据记录在 `docs/bug_tracking.md`，保持在正常回归路径之外。

## UCAgent 集成状态

全部 18 个 UCAgent 阶段（0-17）已完成，产物位于 `docs/ucagent_output/`。竞赛工作流定义在 `configs/ucagent_track1_cache.yaml`。集成计划：参见 `docs/ucagent_operation_plan.md`。

## 工作目录

```text
competition/
├── LICENSE
├── Makefile
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

当前计划的验证工作均已全部完成：

1. Line 覆盖率：1359/1359 (100.0%)，21 行豁免（Categories A-K, D）。
2. Branch 覆盖率：471/471 (100.0%)，23 个分支豁免（Categories L-N）。
3. Expr 覆盖率：137/137 (100.0%)，6 个表达式豁免（Category O）。
4. Toggle 覆盖率：24947/28227 (88.4%)，3,280 个 toggle 豁免（Categories T-A~T-F，基于文档）。
5. 功能覆盖率：18 组、91 点、98 bins，全部 100%。
6. Bug-injection harness 保持在正常回归路径之外；`make test` 干净通过 `84 passed`。
7. 完整可复现入口 `make reproduce` 已验证通过。

## 交付边界

评审提交根目录为 `competition/`。核心源码和报告包括：

- `src/`、`tests/`、`scripts/`、`rtl/`、`configs/`
- `docs/`、`unity_test/`、`final_report/`、`uc_test_report/`
- `README.md`、`LICENSE`、`Makefile`、`top.md`、`instruction.md`、`step.md`

以下目录和文件属于生成物或本地工具链，可按需保留用于快速复跑，也可根据提交平台体积限制排除：

- `build/`
- `local/`
- `tools/`
- `cache.vcd`、`*_coverage.dat`、Python 缓存、波形文件

正式证据已沉淀在 `docs/`、`unity_test/`、`uc_test_report/` 和 `final_report/`。

## 模板对齐报告集

UCAgent 模板风格的整合 Markdown 交付物位于：

```text
unity_test/
```

`unity_test/Cache_basic_info.md`、`unity_test/Cache_verification_needs_and_plan.md`、`unity_test/Cache_functions_and_checks.md`、`unity_test/Cache_line_coverage_analysis.md`、`unity_test/Cache_bug_analysis.md` 和 `unity_test/Cache_test_summary.md` 已将 `docs/` 下的过程记录整合成提交面向报告。

## 可复现入口

在本工作区运行：

```sh
make reproduce
```

它会依次运行正常回归、默认 seed `7` / `18` 条事务的覆盖率收集、预期失败的 bug 注入，以及关闭 bug 注入后的恢复路径。清理生成物可运行：

```sh
make clean
```

最新验证：

```text
2026-06-03 15:12 CST
make reproduce -> PASS
normal regression: 84 passed
coverage suite: 86 passed, Toffee funcov 91/91 points and 98/98 bins
RTL coverage from default reproduce: line 100.0%, branch 100.0%, expr 100.0%, toggle 87.8%
bug injection: expected scoreboard failure observed; disabled-bug recovery passed
```
