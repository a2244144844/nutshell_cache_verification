# 行覆盖率闭环计划

日期：2026-05-28

对应英文文档：`docs/line_coverage_closure_plan.md`

## 状态

已完成。UCAgent stage 9 `line_coverage_closure` 已通过 Claude Code 后端执行，阶段产物为：

- `docs/ucagent_output/line_coverage_closure_stage.md`
- `docs/ucagent_output/line_coverage_closure_stage_zh.md`

## 目标

闭合 `Cache.v` 剩余未覆盖行中的 H/I/J 类缺口，把 RTL 行覆盖率从 `98.4%` 推到约 `99.6%`。

## 最终结果

| 指标 | 闭环前 | 闭环后 |
| --- | --- | --- |
| RTL 行覆盖率 | `1344/1366 (98.4%)` | `1359/1364 (99.6%)` |
| 未覆盖行 | 22 | 5 |
| 定向测试 | 23 | 26 |

## 覆盖动作

- DIR-014：Probe hit full release sequence。
- DIR-015：Read-burst hit。
- DIR-016：needFlush de-assertion。
- Category J：D-cache 专用端口精确豁免。

## 复现命令

```bash
scripts/run_directed.sh
scripts/run_regression.sh
scripts/collect_coverage.sh 7 18
```
