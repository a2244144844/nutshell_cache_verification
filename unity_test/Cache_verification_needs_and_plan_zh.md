# Cache 验证需求与计划

日期：2026-05-28

对应英文文档：`unity_test/Cache_verification_needs_and_plan.md`

## 验证目标

覆盖 Cache 的核心读写、miss/refill、替换、写掩码、MMIO bypass、flush、coherence probe、backpressure、CRV、bug injection 和报告复现链路。

## 当前状态

- smoke、directed、corner、random 与 bug-injection 流程已建立。
- Toffee 功能覆盖率达到 100%。
- RTL 行覆盖率经闭环后达到 `1359/1364 (99.6%)`。
- UCAgent GenSpec、line mapping 和标准 API/coverage wrapper 已补齐。

## 退出标准

`scripts/run_regression.sh` 和 `scripts/reproduce.sh` 均需通过；所有关键报告需在 `top.md` / `top_zh.md` 中索引。
