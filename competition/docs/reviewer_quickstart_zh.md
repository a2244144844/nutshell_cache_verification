# 评审快速上手

本文档是 Track1 NutShell Cache 验证包的中文短评审路线。

## 1. 一键复现

在 `competition/` 目录下运行：

```sh
make reproduce
```

预期最终输出：

```text
[reproduce] PASS
```

最新本地验证记录：

```text
2026-06-03 15:12 CST
make reproduce -> PASS
normal regression: 84 passed
coverage suite: 86 passed, Toffee funcov 91/91 points and 98/98 bins
RTL coverage from default reproduce: line 100.0%, branch 100.0%, expr 100.0%, toggle 87.8%
bug injection: expected scoreboard failure observed; disabled-bug recovery passed
```

`make reproduce` 会依次执行：

- 正常回归：smoke + directed + corner 测试
- 完整覆盖率收集：运行 `tests/` 全套
- 预期失败的 bug injection
- 关闭 bug injection 后的恢复路径验证

快速 sanity check：

```sh
make test-smoke
```

预期结果：

```text
1 passed
```

## 2. 推荐阅读顺序

| 文档 | 评审价值 |
| --- | --- |
| `final_report/nutshell_cache_report.pdf` | 最终参赛报告 |
| `docs/verification_plan.md` | 验证范围、阶段计划和退出标准 |
| `docs/coverage_report.md` / `docs/coverage_report_zh.md` | 最新覆盖率摘要 |
| `docs/bug_tracking.md` | Bug injection 证据和 scoreboard 检出链路 |
| `docs/ai_collaboration_report.md` / `docs/ai_collaboration_report_zh.md` | AI/人工协作、人工修正、Prompt 策略 |
| `docs/coverage_waiver_rationale.md` / `docs/coverage_waiver_rationale_zh.md` | 行/分支/表达式豁免依据 |
| `docs/toggle_coverage_waiver.md` / `docs/toggle_coverage_waiver_zh.md` | Toggle 豁免依据 |
| `unity_test/Cache_test_summary.md` / `unity_test/Cache_test_summary_zh.md` | UCAgent 模板对齐测试总结 |

## 3. 覆盖率目标

最新闭环结果：

| 覆盖率类型 | 结果 |
| --- | --- |
| Toffee 功能覆盖 | 18 组、91 个覆盖点、98 个 bin，全部覆盖 |
| RTL 行覆盖 | 1359/1359，100.0% |
| RTL 分支覆盖 | 471/471，100.0% |
| RTL 表达式覆盖 | final report set 中为 137/137，100.0% |
| RTL 翻转覆盖 | default reproduce 为 24775/28227，87.8%；multi-seed final report set 为 24947/28227，88.4%；剩余项已文档化豁免 |

注意：`86 passed` 是 pytest 测试用例数量；`91/91 points` 是 Toffee 功能覆盖点数量。二者不是同一个指标，不需要强行改成一致。

## 4. 源码地图

| 目录 | 内容 |
| --- | --- |
| `src/env` | Cache 验证环境和 DUT 生命周期 |
| `src/generator` | 受约束随机事务生成 |
| `src/monitor` | 总线级观测辅助 |
| `src/scoreboard` | 参考检查和数据一致性检查 |
| `src/utils` | SimpleBus 定义和覆盖率工具 |
| `tests/smoke` | 最小读写路径证明 |
| `tests/directed` | 替换、dirty writeback、refill、probe、flush、MMIO、写掩码等定向测试 |
| `tests/corner` | Backpressure 场景 |
| `tests/random` | CRV 和 multi-seed random traffic |
| `tests/injected_bug` | 预期失败的 bug injection harness |

## 5. 交付边界

预期提交根目录是 `competition/`。

源码和报告交付物：

- `README.md`、`README_zh.md`、`LICENSE`、`Makefile`
- `src/`、`tests/`、`scripts/`、`rtl/`、`configs/`
- `docs/`、`unity_test/`、`uc_test_report/`、`final_report/`

生成物或本地重型工具链：

- `build/`、`local/`、`tools/`
- `cache.vcd`、`*_coverage.dat`
- Python cache 和波形文件

这些生成目录在当前工作站上有利于快速复跑，但源码审阅不依赖它们；可复现命令和证据文档已经包含在提交包中。
