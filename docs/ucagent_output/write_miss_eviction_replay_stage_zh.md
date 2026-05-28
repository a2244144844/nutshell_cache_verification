# UCAgent Write Miss / Eviction 重放阶段

日期：2026-05-28

对应英文文档：`docs/ucagent_output/write_miss_eviction_replay_stage.md`

## 阶段说明

这是 DIR-011 至 DIR-013 的补充 UCAgent replay。原始实现历史仍按 direct-agent 工作记录，本阶段用于补强“这些复杂路径已经通过 UCAgent 通道复核”的证据。

## 覆盖路径

- DIR-011：write miss。
- DIR-012：clean eviction。
- DIR-013：write miss + dirty eviction。

## 命令结果

| 命令 | 结果 |
| --- | --- |
| focused replay tests | `7 passed in 0.58s` |
| `scripts/run_regression.sh` | `26 passed in 1.13s` |
| `scripts/collect_coverage.sh 7 18` | `27 passed, 16 warnings in 3.52s` |

## Toffee 覆盖率

- 12 groups
- 31 points
- 37 bins
- 31/31 points covered
- 37/37 bins covered
