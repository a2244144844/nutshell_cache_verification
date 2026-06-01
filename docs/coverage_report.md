# Coverage Report

- HTML report: `build/reports/cache_coverage.html`
- **Line coverage (RTL)**: 1359/1359 lines (100.0%)
- Random seed: `7`
- Random steps: `18`
- **Toffee funcov**: 18 groups, 91 points, 98 bins
- **Marked Points**: 91/91 (100%)
- **Covered Bins**: 98/98 (100%)

## Cmd Type

| Bin | Count | Status |
| --- | ---: | --- |
| `read` | 8 | covered |
| `write` | 10 | covered |
| `probe` | 0 | gap |

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

## Write Hit X Wmask

| Bin | Count | Status |
| --- | ---: | --- |
| `byte_0` | 0 | gap |
| `byte_1` | 0 | gap |
| `byte_2` | 0 | gap |
| `byte_3` | 1 | covered |
| `byte_4` | 1 | covered |
| `byte_5` | 0 | gap |
| `byte_6` | 0 | gap |
| `byte_7` | 0 | gap |
| `adjacent_0` | 0 | gap |
| `adjacent_1` | 0 | gap |
| `adjacent_2` | 0 | gap |
| `adjacent_3` | 0 | gap |
| `adjacent_4` | 1 | covered |
| `adjacent_5` | 1 | covered |
| `adjacent_6` | 0 | gap |
| `adjacent_7` | 0 | gap |
| `low_half_0` | 0 | gap |
| `low_half_1` | 0 | gap |
| `low_half_2` | 0 | gap |
| `low_half_3` | 0 | gap |
| `low_half_4` | 0 | gap |
| `low_half_5` | 1 | covered |
| `low_half_6` | 1 | covered |
| `low_half_7` | 0 | gap |
| `high_half_0` | 0 | gap |
| `high_half_1` | 0 | gap |
| `high_half_2` | 0 | gap |
| `high_half_3` | 0 | gap |
| `high_half_4` | 0 | gap |
| `high_half_5` | 0 | gap |
| `high_half_6` | 1 | covered |
| `high_half_7` | 1 | covered |
| `full_0` | 1 | covered |
| `full_1` | 0 | gap |
| `full_2` | 0 | gap |
| `full_3` | 0 | gap |
| `full_4` | 0 | gap |
| `full_5` | 0 | gap |
| `full_6` | 0 | gap |
| `full_7` | 0 | gap |
| `sparse_0` | 0 | gap |
| `sparse_1` | 1 | covered |
| `sparse_2` | 0 | gap |
| `sparse_3` | 0 | gap |
| `sparse_4` | 0 | gap |
| `sparse_5` | 0 | gap |
| `sparse_6` | 0 | gap |
| `sparse_7` | 0 | gap |

## Miss X Addr Type

| Bin | Count | Status |
| --- | ---: | --- |
| `hit_normal` | 13 | covered |
| `hit_mmio` | 0 | gap |
| `miss_normal` | 5 | covered |

## Probe X Cache State

| Bin | Count | Status |
| --- | ---: | --- |
| `probe_hit_valid` | 0 | gap |
| `probe_hit_dirty` | 0 | gap |
| `probe_miss_empty` | 0 | gap |
| `probe_miss_valid` | 0 | gap |
| `probe_miss_dirty` | 0 | gap |

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
| `cache_miss_x_addr_type` | 2/2 | 3/3 | covered |
| `cache_probe_tracker` | 1/1 | 1/1 | covered |
| `cache_probe_x_cache_state` | 5/5 | 5/5 | covered |
| `cache_refill_path` | 3/3 | 4/4 | covered |
| `cache_req_accepted` | 1/1 | 1/1 | covered |
| `cache_req_tracker` | 2/2 | 2/2 | covered |
| `cache_word_offset` | 8/8 | 8/8 | covered |
| `cache_write_hit_x_wmask` | 48/48 | 48/48 | covered |
| `cache_write_mask_class` | 7/7 | 7/7 | covered |
| `cache_write_miss` | 2/2 | 3/3 | covered |
| `cache_write_tracker` | 2/2 | 2/2 | covered |

## Gaps And Next Actions

- No functional-coverage gaps remain in the Toffee model.
- Legacy random-collector write-miss bins may show gaps because the constrained-random bootstrap focuses on write hits; directed tests close these paths in the Toffee model.

