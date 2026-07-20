# CRV Coverage Stage

Stage: `crv_coverage_bootstrap`
Forced stage index: `2`
Date: `2026-05-26`

## Changed Files

- `src/generator/cache_random.py`
- `src/utils/cache_coverage.py`
- `tests/random/test_random_cache.py`
- `scripts/run_random.sh`
- `scripts/collect_coverage.sh`
- `docs/coverage_report.md`
- `docs/test_points.md`
- `docs/ai_collaboration_report.md`
- `docs/ucagent_output/crv_coverage_stage.md`

## Commands Run

- `scripts/collect_coverage.sh 7 18`
- `scripts/run_regression.sh`

## Exact Results

- `scripts/collect_coverage.sh 7 18` -> PASS, `1 passed in 0.09s`
- `scripts/run_regression.sh` -> PASS, `6 passed in 0.11s`

## Coverage Summary

- `cmd_type`: read 11, write 7
- `hit_miss_proxy`: hit 15, miss 3
- `write_mask_class`: none 11, byte 1, adjacent 1, low_half 1, high_half 1, full 1, sparse 2
- `word_offset`: 0 4, 1 1, 2 4, 3 1, 4 3, 5 2, 6 1, 7 2
- `refill_path`: clean_miss_refill 3, read_hit 8, write_hit 7, dirty_miss_writeback_refill 0

## Gaps And Next Actions

- Dirty miss writeback/refill remains uncovered.
- Next closure action: add a directed eviction sequence that fills all 4 ways of one set, dirties them, and then accesses a 5th conflicting line to force writeback plus refill.
- Run-boundary note: after this stage called `Complete`, the UCAgent process advanced into the next configured stage despite the one-stage instruction. That overrun was stopped, and the out-of-scope bug-injection draft files were removed. Dirty writeback coverage closure is now the next stage, with bug injection after it.
