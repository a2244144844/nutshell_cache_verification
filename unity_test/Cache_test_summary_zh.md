# Cache 测试总结（中文版）

日期：2026-05-31

对应英文文档：`unity_test/Cache_test_summary.md`

## 最终验证结果

| 命令 | 结果 |
| --- | --- |
| `scripts/run_directed.sh` | `37 passed` |
| `scripts/run_regression.sh` | `37 passed` |
| `scripts/collect_coverage.sh` | `37 passed, RTL 行覆盖率 1359/1359 (100.0%), 分支覆盖率 471/471 (100.0%)` |
| `scripts/collect_coverage_multi.sh` | 翻转覆盖率 24947/28227 (88.4%, Stage 17 最终) |
| `scripts/clean_generated.sh && scripts/reproduce.sh` | `PASS` |

## 测试清单

| 类别 | 数量 / 范围 |
| --- | --- |
| Smoke | Reset、read miss/refill、read hit、write hit、read-after-write |
| Directed | DIR-001 至 DIR-022 全部实现并记录 |
| Corner | CPU 响应与内存请求背压 |
| Random | 确定性约束随机读写引导 + 多种子随机流量（Stage 13/17） |
| Bug 证据 | 参考模型污染与 RTL dirty-writeback 绕过 |
| 功能覆盖率 | Toffee 模型：12 组、31 点、37 bins，100% 覆盖 |
| RTL 行覆盖率 | Verilator：1359/1359 (100.0%)，42 行豁免（Categories A-N） |
| RTL 分支覆盖率 | Verilator：471/471 (100.0%) |
| RTL 翻转覆盖率 | Verilator：24947/28227 (88.4%)，3,280 翻转位豁免（Categories T-A–T-F，文档化方式） |
| RTL 表达式覆盖率 | Verilator：137/137 (100.0%)，6 表达式豁免（Category O） |

## UCAgent 阶段证据

| 产物 | 用途 |
| --- | --- |
| `docs/ucagent_output/stage_audit.md` | 初始 UCAgent 回归审计 |
| `docs/ucagent_output/backpressure_stage.md` | 背压实现证据 |
| `docs/ucagent_output/crv_coverage_stage.md` | 随机与首次覆盖率引导 |
| `docs/ucagent_output/dirty_writeback_stage.md` | Dirty writeback 闭环 |
| `docs/ucagent_output/bug_injection_stage.md` | 受控 Bug 注入证据 |
| `docs/ucagent_output/final_report_stage.md` | 提交检查清单与文档刷新 |
| `docs/ucagent_output/coherence_probe_stage.md` | Coherence probe 定向阶段 |
| `docs/ucagent_output/flush_stage.md` | Flush 定向阶段 |
| `docs/ucagent_output/line_coverage_closure_stage.md` | 行覆盖闭环（DIR-014/015/016） |
| `docs/ucagent_output/line_coverage_100_stage.md` | 行覆盖 100% 闭环（DIR-017/018, Stage 11） |
| `docs/ucagent_output/branch_coverage_closure_stage.md` | 分支覆盖 100% 闭环（DIR-019–022, Stage 12） |
| `docs/ucagent_output/toggle_coverage_improvement_stage.md` | 翻转覆盖率提升（多种子随机, Stage 13） |

## 可复现性

```sh
cd /Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache
scripts/reproduce.sh
```

## 提交说明

- 主回归排除故意失败的 bug 注入运行。
- RTL 行覆盖率 100.0%，分支覆盖率 100.0%，表达式覆盖率 100.0%，翻转覆盖率 88.4%（3,280 豁免位，文档化方式）。
- DIR-017 (needFlush) 与 DIR-018 (respToL1Last) 通过 Stage 11 实现行覆盖 100%。
- DIR-019 (PREFETCH)、DIR-020 (writeback counters)、DIR-021 (internal probe)、DIR-022 (state2) 通过 Stage 12 实现分支覆盖 100%。
- 多种子随机流量 (Stage 13) 将翻转覆盖率从 86.7% 提升至 87.8%。
- Stage 17 最大设置尝试（10 seed × 200 步、64 地址、32 模式）将翻转覆盖率推至 88.4% 最终平台。
- Stage 18 将翻转豁免正式化至 GenSpec 文档。
- 豁免依据见 `docs/coverage_waiver_rationale.md` 与 `docs/toggle_coverage_waiver.md`。
