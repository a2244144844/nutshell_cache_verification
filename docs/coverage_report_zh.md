# 覆盖率报告

- HTML 报告：`build/reports/cache_coverage.html`
- 随机种子：`7`
- 随机步数：`18`
- **Toffee 功能覆盖率**：12 个 group、31 个 point、37 个 bin
- **Marked Points**：31/31 (100%)
- **Covered Bins**：37/37 (100%)

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
| `write_miss_clean_refill` | 0 | gap |
| `write_miss_dirty_refill` | 0 | gap |

## Write Miss

| 仓 | 计数 | 状态 |
| --- | ---: | --- |
| `clean` | 0 | gap |
| `dirty` | 0 | gap |
| `none` | 18 | 已覆盖 |

## Toffee Group Summary

| Group | Points | Bins | 状态 |
| --- | ---: | ---: | --- |
| `cache_addr_class` | 1/1 | 2/2 | 已覆盖 |
| `cache_backpressure` | 2/2 | 2/2 | 已覆盖 |
| `cache_clean_eviction` | 1/1 | 1/1 | 已覆盖 |
| `cache_cmd_type` | 2/2 | 3/3 | 已覆盖 |
| `cache_coherence_probe` | 1/1 | 2/2 | 已覆盖 |
| `cache_flush` | 1/1 | 2/2 | 已覆盖 |
| `cache_hit_miss` | 2/2 | 2/2 | 已覆盖 |
| `cache_refill_path` | 3/3 | 4/4 | 已覆盖 |
| `cache_req_accepted` | 1/1 | 1/1 | 已覆盖 |
| `cache_word_offset` | 8/8 | 8/8 | 已覆盖 |
| `cache_write_mask_class` | 7/7 | 7/7 | 已覆盖 |
| `cache_write_miss` | 2/2 | 3/3 | 已覆盖 |

## 缺口与说明

- 当前 Toffee 功能覆盖率模型无剩余缺口。
- Legacy random collector 中的 write-miss bins 仍显示 gap，因为随机 bootstrap 重点覆盖 write hit；这些路径已由 directed tests 在 Toffee 模型中闭合。
