# UCAgent Stage: Flush Behavior Directed Test (DIR-007)

**Stage name**: 7-flush_directed_test
**Date**: 2026-05-26
**Status**: PASS

## Files Changed

- `tests/directed/test_flush_behavior.py` — created with three test functions:
  - `test_flush_while_idle` — asserts io_flush while idle, verifies io_empty, deasserts, verifies cache ready
  - `test_flush_during_miss` — asserts io_flush before pipeline capture of an accepted read miss, verifies io_empty stays high, verifies recovery
  - `test_flush_recovery` — after flush deasserted, verifies read miss, write hit, and read-after-write work correctly
- `docs/test_points.md` — marked DIR-007 as implemented
- `docs/ai_collaboration_report.md` — added stage result entry

## Commands Run

```text
tests/directed/test_flush_behavior.py -> 3 passed in 0.05s
tests/directed/ (all) -> 13 passed in 0.12s
tests/smoke/ + tests/directed/ + tests/corner/ (full regression) -> 16 passed in 0.13s
```

## Pass/Fail Result

PASS — all three flush behavior tests pass, and no existing tests regress.

## Design Notes

- **io_flush constraint**: The DUT has a Chisel assertion `assert(!(!ro.B && io.flush))` in CacheStage3 (Cache.v:950). For this D-cache instance (`ro.B=false`), `io_flush[1]` (which connects to CacheStage3) triggers `$fatal`. Only `io_flush[0]` (S1→S2 pipeline flush) is safe to use.
- **Pipeline flush timing**: `io_flush[0]` is sampled on the same posedge as the pipeline valid register. To squash an in-flight request, io_flush must be asserted BEFORE the clock step where the pipeline would capture the request. Asserting io_flush after the pipeline has already captured the request does not retroactively clear it.
- **io_empty**: Defined as `~s2_io_in_valid & ~s3_io_in_valid` (Cache.v:2696). With `io_flush=0b01`, only the S1→S2 valid register is cleared; the S2→S3 valid register is unaffected.
- **Cache recovery**: After flush deassertion, `io_in_req_ready` returns high and the cache accepts new requests normally.

## Remaining Risks

- `io_flush[1]` (Stage3/CacheStage3 flush) cannot be tested on this D-cache instance without either reconfiguring the cache as I-cache or removing the assertion.
- The CacheStage3 state machine's `needFlush` mechanism (which drains in-flight operations during flush) is untested because it requires `io_flush[1]`.
- Edge case: asserting flush while CacheStage3 is in the middle of a refill (state 2) or writeback (state 3) is not covered by these tests.
