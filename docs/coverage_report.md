# Coverage Report

- HTML report: `build/reports/cache_coverage.html`
- **Line coverage (RTL)**: 1359/1364 lines (99.6%)
- Random seed: `7`
- Random steps: `18`
- **Toffee funcov**: 12 groups, 31 points, 37 bins
- **Marked Points**: 31/31 (100%)
- **Covered Bins**: 37/37 (100%)

## Cmd Type

| Bin | Count | Status |
| --- | ---: | --- |
| `read` | 8 | covered |
| `write` | 10 | covered |

## Hit Miss Proxy

| Bin | Count | Status |
| --- | ---: | --- |
| `hit` | 13 | covered |
| `miss` | 5 | covered |

## Write Mask Class

| Bin | Count | Status |
| --- | ---: | --- |
| `none` | 8 | covered |
| `byte` | 2 | covered |
| `adjacent` | 2 | covered |
| `low_half` | 2 | covered |
| `high_half` | 2 | covered |
| `full` | 1 | covered |
| `sparse` | 1 | covered |

## Word Offset

| Bin | Count | Status |
| --- | ---: | --- |
| `0` | 4 | covered |
| `1` | 3 | covered |
| `2` | 2 | covered |
| `3` | 2 | covered |
| `4` | 2 | covered |
| `5` | 2 | covered |
| `6` | 2 | covered |
| `7` | 1 | covered |

## Refill Path

| Bin | Count | Status |
| --- | ---: | --- |
| `clean_miss_refill` | 4 | covered |
| `read_hit` | 3 | covered |
| `write_hit` | 10 | covered |
| `dirty_miss_writeback_refill` | 1 | covered |
| `write_miss_clean_refill` | 0 | gap |
| `write_miss_dirty_refill` | 0 | gap |

## Write Miss

| Bin | Count | Status |
| --- | ---: | --- |
| `clean` | 0 | gap |
| `dirty` | 0 | gap |
| `none` | 18 | covered |

## Toffee Group Summary

| Group | Points | Bins | Status |
| --- | ---: | ---: | --- |
| `cache_addr_class` | 1/1 | 2/2 | covered |
| `cache_backpressure` | 2/2 | 2/2 | covered |
| `cache_clean_eviction` | 1/1 | 1/1 | covered |
| `cache_cmd_type` | 2/2 | 3/3 | covered |
| `cache_coherence_probe` | 1/1 | 2/2 | covered |
| `cache_flush` | 1/1 | 2/2 | covered |
| `cache_hit_miss` | 2/2 | 2/2 | covered |
| `cache_refill_path` | 3/3 | 4/4 | covered |
| `cache_req_accepted` | 1/1 | 1/1 | covered |
| `cache_word_offset` | 8/8 | 8/8 | covered |
| `cache_write_mask_class` | 7/7 | 7/7 | covered |
| `cache_write_miss` | 2/2 | 3/3 | covered |

## Gaps And Next Actions

- No functional-coverage gaps remain in the Toffee model.
- Legacy random-collector write-miss bins may show gaps because the constrained-random bootstrap focuses on write hits; directed tests close these paths in the Toffee model.

