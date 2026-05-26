覆盖率数据文件：`/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/build/cache_random_coverage.json`

## Stage 说明

- UCAgent stage `dirty_writeback_coverage_closure` 已关闭 dirty miss writeback/refill 缺口。
- 清理越界 bug-injection 草稿后最新本地复查：`scripts/collect_coverage.sh 7 18` 以 `1 passed in 0.04s` 通过。
- Stage 4（`bug_injection_evidence`）已完成，记录于 `docs/ucagent_output/bug_injection_stage.md`。

# 覆盖率报告

种子：`7`
传输次数：`18`

## 命令
- `scripts/collect_coverage.sh 7 18`

## 命令类型

| 仓 | 计数 | 状态 |
| --- | ---: | --- |
| `read` | 8 | 已覆盖 |
| `write` | 10 | 已覆盖 |

## 命中/缺失代理

| 仓 | 计数 | 状态 |
| --- | ---: | --- |
| `hit` | 13 | 已覆盖 |
| `miss` | 5 | 已覆盖 |

## 写掩码类别

| 仓 | 计数 | 状态 |
| --- | ---: | --- |
| `none` | 8 | 已覆盖 |
| `byte` | 2 | 已覆盖 |
| `adjacent` | 2 | 已覆盖 |
| `low_half` | 2 | 已覆盖 |
| `high_half` | 2 | 已覆盖 |
| `full` | 1 | 已覆盖 |
| `sparse` | 1 | 已覆盖 |

## Word 偏移

| 仓 | 计数 | 状态 |
| --- | ---: | --- |
| `0` | 4 | 已覆盖 |
| `1` | 3 | 已覆盖 |
| `2` | 2 | 已覆盖 |
| `3` | 2 | 已覆盖 |
| `4` | 2 | 已覆盖 |
| `5` | 2 | 已覆盖 |
| `6` | 2 | 已覆盖 |
| `7` | 1 | 已覆盖 |

## Refill 路径

| 仓 | 计数 | 状态 |
| --- | ---: | --- |
| `clean_miss_refill` | 4 | 已覆盖 |
| `read_hit` | 3 | 已覆盖 |
| `write_hit` | 10 | 已覆盖 |
| `dirty_miss_writeback_refill` | 1 | 已覆盖 |

## 缺口与下一步行动

- 当前 bootstrap 集合中无直接的功能覆盖率缺口。
