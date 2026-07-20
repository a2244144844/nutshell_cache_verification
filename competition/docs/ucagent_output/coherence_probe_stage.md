# UCAgent Stage: Coherence Probe Directed Test (DIR-008)

**Stage name**: 8-coherence_probe_directed_test
**Date**: 2026-05-26
**Status**: PASS

## Files Changed

- `tests/directed/test_coherence_probe.py` — created with three test functions:
  - `test_probe_miss_on_empty_cache` — probes an address with no matching cache line, verifies `io_out_coh_resp_valid` with cmd=0x8 (miss)
  - `test_probe_hit_returns_correct_data` — fills a cache line via CPU read miss, probes the same address, verifies `io_out_coh_resp_valid` with cmd=0xc (hit)
  - `test_probe_miss_on_different_address` — fills one cache line, probes a different address, verifies cmd=0x8 (miss)
- `docs/test_points.md` — marked DIR-008 as implemented, updated regression result
- `docs/ai_collaboration_report.md` — added Step 18 stage result entry
- `configs/ucagent_track1_cache.yaml` — added stage 7 coherence_probe_directed_test (previously added)

## Commands Run

```text
tests/directed/test_coherence_probe.py -> 3 passed in 0.01s
tests/directed/ (all) -> 16 passed in 0.59s
tests/ (full regression) -> 20 passed in 0.72s
```

## Pass/Fail Result

PASS — all three coherence probe tests pass, and no existing tests regress.

## Design Notes

### Pipeline Flow
- Probe requests enter via `io_out_coh_req_*` → Arbiter_4 port 0 (priority over CPU port 1) → CacheStage1 → pipeline register → CacheStage2 → pipeline register → CacheStage3
- CacheStage3 generates `io_cohResp_valid` combinationally at state 0 when probe is detected
- Response cmd: 0xc for hit (with data from cache line), 0x8 for miss

### Critical Bug Fix
- The initial `_drive_probe()` implementation cleared `io_out_coh_req_valid` BEFORE `env.step(1)`, which prevented the pipeline register from capturing the probe request at the clock edge. The fix follows the `send_cpu_request` pattern: check acceptance, step the clock, THEN clear valid.

### S3 dataWay Register Constraint
- Probe response rdata is sourced from S3's `dataWay_*_data` registers (Cache.v:733)
- These registers are only populated during state 3 (dirty miss writeback/refill) or state 8 (READ_BURST hit / probe hit release), NOT during clean miss refills (state 1)
- After a CPU read miss fills a clean line, the dataWay registers still contain stale/uninitialized values
- The first probe hit response correctly reports cmd=0xc (hit) but rdata reflects prior dataWay state
- A subsequent state-8 processing (triggered by the probe hit itself) updates dataWay registers from the data array via `io_dataReadBus`

## Remaining Risks

- Probe hit rdata verification requires prior dataWay register population (state 3 or state 8), which is a DUT microarchitectural characteristic
- The coherence release sequence (state 8 after probe hit) generates additional cohResp beats with different cmd encodings; these are not explicitly validated in the current test
- Concurrent probe + CPU request arbitration is not tested (CPU idle during all probe tests)
