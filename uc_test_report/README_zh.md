# UC 测试报告索引

日期：2026-05-28

对应英文文档：`uc_test_report/README.md`

## 作用

本目录用于归档提交面向的测试报告入口，指向生成的覆盖率 HTML、LCOV 和 Markdown 报告。

## 当前主要报告

- 功能/行覆盖率 HTML：`build/reports/cache_coverage.html`
- LCOV HTML：`build/reports/line_dat/index.html`
- Markdown 覆盖率摘要：`docs/coverage_report.md`

## 最新验证

最近一次 `scripts/reproduce.sh` 已完成正常回归、覆盖率采集、预期失败 bug injection 和恢复路径，最终输出 `[reproduce] PASS`。
