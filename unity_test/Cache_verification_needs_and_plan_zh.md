# Cache 验证需求与计划（中文版）

日期：2026-05-31

对应英文文档：`unity_test/Cache_verification_needs_and_plan.md`

## 验证目标

覆盖 Cache 的核心读写、miss/refill、替换、写掩码、MMIO bypass、flush、coherence probe、backpressure、CRV、bug injection、行/分支/翻转覆盖率闭环与报告复现链路。

## UCAgent 阶段计划

| 阶段 | 状态 | 产物 |
| --- | --- | --- |
| `cache_regression_audit` | Complete | `docs/ucagent_output/stage_audit.md` |
| `backpressure_directed_tests` | Complete | `docs/ucagent_output/backpressure_stage.md` |
| `crv_coverage_bootstrap` | Complete | `docs/ucagent_output/crv_coverage_stage.md` |
| `dirty_writeback_coverage_closure` | Complete | `docs/ucagent_output/dirty_writeback_stage.md` |
| `bug_injection_evidence` | Complete | `docs/ucagent_output/bug_injection_stage.md` |
| `final_report_package` | Complete | `docs/ucagent_output/final_report_stage.md` |
| `coherence_probe_directed_test` | Complete | `docs/ucagent_output/coherence_probe_stage.md` |
| `flush_directed_test` | Complete | `docs/ucagent_output/flush_stage.md` |
| `line_coverage_100` | Complete | `docs/ucagent_output/line_coverage_100_stage.md` |
| `branch_coverage_closure` | Complete | `docs/ucagent_output/branch_coverage_closure_stage.md` |
| `toggle_coverage_improvement` | Complete | `docs/ucagent_output/toggle_coverage_improvement_stage.md` |

DIR-017 (needFlush) 与 DIR-018 (respToL1Last) 通过 Stage 11 实现行覆盖 100%。DIR-019 (PREFETCH)、DIR-020 (writeback counters)、DIR-021 (internal probe)、DIR-022 (state2) 通过 Stage 12 实现分支覆盖 100%。多种子随机流量通过 Stage 13 提升翻转覆盖率。

行/分支豁免依据见 `docs/coverage_waiver_rationale.md`。翻转豁免依据见 `docs/toggle_coverage_waiver.md`。

## 退出标准

| 标准 | 当前状态 |
| --- | --- |
| Directed 套件通过 | `scripts/run_directed.sh -> 37 passed` |
| 全量回归通过 | `scripts/run_regression.sh -> 37 passed` |
| 可复现入口通过 | `scripts/clean_generated.sh && scripts/reproduce.sh -> PASS` |
| Toffee 功能覆盖闭环 | 12 组、31 点、37 bins，全部 100% |
| RTL 行覆盖率 | 1359/1359 (100.0%)，42 行豁免（Categories A-N） |
| RTL 分支覆盖率 | 471/471 (100.0%) |
| RTL 翻转覆盖率 | 24947/28227 (88.4%)，3,280 翻转位豁免（Categories T-A–T-F，文档化方式） |
| RTL 表达式覆盖率 | 137/137 (100.0%)，6 表达式豁免（Category O） |
| Bug 证据 | `BUG-001` 与 `BUG-RTL-001` 已记录 |
| 豁免依据 | `docs/coverage_waiver_rationale.md`、`docs/toggle_coverage_waiver.md` |
