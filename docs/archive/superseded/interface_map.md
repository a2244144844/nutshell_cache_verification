# Cache Interface Map

Date: 2026-05-26

## DUT

Selected RTL:

```text
rtl/dut/Cache.v
```

Top module:

```text
Cache
```

Picker-generated Python wrapper:

```python
from __init__ import DUTCache
```

The wrapper is generated under `build/picker_cache` by `scripts/export_cache_dut.sh`.

## Clock And Reset

| Signal | Direction | Width | Notes |
| --- | --- | --- | --- |
| `clock` | input | 1 | Must call `dut.InitClock("clock")` before `dut.Step(...)`. |
| `reset` | input | 1 | Hold high for several cycles, then wait until `io_in_req_ready` becomes 1. |

The internal metadata SRAM reset sweep takes about 128 cycles after reset is released.

## SimpleBus Command Codes

Observed from RTL and smoke behavior:

| Name | Code | Notes |
| --- | --- | --- |
| `READ` | `0` | Normal CPU-side read request. |
| `WRITE` | `1` | Normal CPU-side write request. |
| `READ_BURST` | `2` | Memory-side refill request emitted on read miss. |
| `WRITE_BURST` | `3` | Dirty victim writeback burst command. |
| `PREFETCH` | `4` | Response with this command is suppressed on CPU side. |
| `WRITE_RESP` | `5` | CPU-side write response. |
| `READ_LAST` | `6` | CPU-side read response and memory refill response used by the smoke test. |
| `WRITE_LAST` | `7` | Final writeback beat. |
| `PROBE` | `8` | Coherence probe request. |

## CPU-Side Request

Prefix: `io_in_req_*`

| Signal | Direction | Width | Notes |
| --- | --- | --- | --- |
| `io_in_req_valid` | input | 1 | Request valid. |
| `io_in_req_ready` | output | 1 | Request ready. |
| `io_in_req_bits_addr` | input | 32 | Byte address. |
| `io_in_req_bits_size` | input | 3 | Smoke uses `3` for 64-bit access. |
| `io_in_req_bits_cmd` | input | 4 | SimpleBus command. |
| `io_in_req_bits_wmask` | input | 8 | Byte write mask. |
| `io_in_req_bits_wdata` | input | 64 | Write data. |
| `io_in_req_bits_user` | input | 16 | User metadata, returned on CPU response. |

## CPU-Side Response

Prefix: `io_in_resp_*`

| Signal | Direction | Width | Notes |
| --- | --- | --- | --- |
| `io_in_resp_ready` | input | 1 | Response ready. Smoke holds it high. |
| `io_in_resp_valid` | output | 1 | Response valid. |
| `io_in_resp_bits_cmd` | output | 4 | `READ_LAST` for reads, `WRITE_RESP` for writes. |
| `io_in_resp_bits_rdata` | output | 64 | Read data. |
| `io_in_resp_bits_user` | output | 16 | Echoes request user metadata. |

## Memory-Side Interface

Prefix: `io_out_mem_*`

| Signal | Direction | Width | Notes |
| --- | --- | --- | --- |
| `io_out_mem_req_valid` | output | 1 | Memory request valid. |
| `io_out_mem_req_ready` | input | 1 | Memory request ready. Smoke holds it high. |
| `io_out_mem_req_bits_addr` | output | 32 | Refill/writeback address. |
| `io_out_mem_req_bits_size` | output | 3 | Generated as 64-bit size. |
| `io_out_mem_req_bits_cmd` | output | 4 | Smoke observes `READ_BURST` on first read miss. |
| `io_out_mem_req_bits_wmask` | output | 8 | Writeback mask. |
| `io_out_mem_req_bits_wdata` | output | 64 | Writeback data. |
| `io_out_mem_resp_valid` | input | 1 | Memory response valid. |
| `io_out_mem_resp_ready` | output | 1 | Memory response ready. |
| `io_out_mem_resp_bits_cmd` | input | 4 | Smoke returns `READ_LAST`. |
| `io_out_mem_resp_bits_rdata` | input | 64 | Refill data. |

## MMIO Interface

Prefix: `io_mmio_*`

MMIO has the same request/response shape as the memory interface. Smoke keeps `io_mmio_req_ready` high and `io_mmio_resp_valid` low because the tested address is non-MMIO.

## Coherence Interface

Prefix: `io_out_coh_*`

The selected Cache has probe/release support. Smoke keeps `io_out_coh_req_valid` low and `io_out_coh_resp_ready` high. Coherence scenarios are a later directed-test target.

## Control And Status

| Signal | Direction | Width | Notes |
| --- | --- | --- | --- |
| `io_flush` | input | 2 | Pipeline flush control. |
| `io_empty` | output | 1 | Pipeline-empty status. |

## Smoke Timing Notes

The first read miss flow observed in `tests/smoke/test_cache_basic.py`:

1. CPU request is accepted when `io_in_req_valid && io_in_req_ready`.
2. Cache later emits one memory request with `cmd == READ_BURST`.
3. Test memory responds with `cmd == READ_LAST` and refill data.
4. Cache returns CPU response with `cmd == READ_LAST`, refill data, and echoed user metadata.
5. A repeated read to the same address hits and emits no memory request.
6. A full-mask write hit returns `WRITE_RESP`; a later read returns the written value.

For the fuller refill model in `tests/directed/test_refill_beats.py`, memory responses are driven as 8 beats. The first 7 beats use `READ`; the final beat uses `READ_LAST`. Refill starts at the requested `addr[5:3]` word index and then wraps around the 8-word line.
