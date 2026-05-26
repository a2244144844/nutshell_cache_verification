# CRV 覆盖率 Stage

Stage：`crv_coverage_bootstrap`
强制 stage index：`2`
日期：`2026-05-26`

## 变更的文件

- `src/generator/cache_random.py`
- `src/utils/cache_coverage.py`
- `tests/random/test_random_cache.py`
- `scripts/run_random.sh`
- `scripts/collect_coverage.sh`
- `docs/coverage_report.md`
- `docs/test_points.md`
- `docs/ai_collaboration_report.md`
- `docs/ucagent_output/crv_coverage_stage.md`

## 运行的命令

- `scripts/collect_coverage.sh 7 18`
- `scripts/run_regression.sh`

## 精确结果

- `scripts/collect_coverage.sh 7 18` -> PASS，`1 passed in 0.09s`
- `scripts/run_regression.sh` -> PASS，`6 passed in 0.11s`

## 覆盖率摘要

- `cmd_type`：read 11，write 7
- `hit_miss_proxy`：hit 15，miss 3
- `write_mask_class`：none 11，byte 1，adjacent 1，low_half 1，high_half 1，full 1，sparse 2
- `word_offset`：0:4，1:1，2:4，3:1，4:3，5:2，6:1，7:2
- `refill_path`：clean_miss_refill 3，read_hit 8，write_hit 7，dirty_miss_writeback_refill 0

## 缺口与后续行动

- 脏缺失写回/refill 仍未覆盖。
- 下一步关闭行动：添加一个定向 eviction 序列，填满某一 set 的 4 路，将其全部脏化，然后访问第 5 个冲突行以强制触发写回加 refill。
- 运行边界说明：本 stage 调用 `Complete` 后，UCAgent 进程推进到了下一个已配置的 stage，尽管有单 stage 指令。该越界运行已被停止，越界范围内的 bug-injection 草稿文件已移除；bug injection 仍为下一 stage。
