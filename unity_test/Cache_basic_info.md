# Cache Basic Info

## DUT Identity

| Item | Value |
| --- | --- |
| DUT name | `Cache` |
| Selected RTL | `rtl/dut/Cache.v` |
| Extra RTL | `rtl/dut/Test.v`, `rtl/dut/Cache.yaml` |
| Original source | Picker example Cache RTL |
| Generated wrapper | `build/picker_cache` |
| Python class | `DUTCache` |
| Export command | `scripts/export_cache_dut.sh` |

The selected DUT is the Picker example Cache RTL copied into this workspace. The earlier full NutShell/Chisel build remains source context only; it is not the active verification boundary.

## Verification Stack

| Layer | Tooling |
| --- | --- |
| RTL export | Picker + Verilator |
| Test language | Python |
| Test runner | pytest |
| Functional coverage | `src/utils/cache_coverage.py`, `src/utils/toffee_coverage.py` |
| Toggle coverage | `scripts/collect_coverage_multi.sh`, `scripts/generate_rtl_coverage_html.py` |
| UCAgent orchestration | `configs/ucagent_track1_cache.yaml`, `scripts/run_ucagent_stage.sh` |

## Top-Level Interfaces

| Interface | Signals | Purpose |
| --- | --- | --- |
| Clock/reset | `clock`, `reset` | Clock and reset sequencing. |
| CPU request | `io_in_req_*` | CPU-side SimpleBus request channel. |
| CPU response | `io_in_resp_*` | CPU-side response channel. |
| Memory | `io_out_mem_*` | Refill and dirty writeback memory traffic. |
| MMIO | `io_mmio_*` | MMIO bypass traffic. |
| Coherence | `io_out_coh_*` | Probe request and response path. |
| Control/status | `io_flush`, `io_empty` | Flush control and pipeline-empty status. |

## SimpleBus Commands

| Name | Code | Usage |
| --- | --- | --- |
| `READ` | `0` | CPU-side read request. |
| `WRITE` | `1` | CPU-side write request. |
| `READ_BURST` | `2` | Memory refill request. |
| `WRITE_BURST` | `3` | Dirty victim writeback request. |
| `PREFETCH` | `4` | Prefetch command; CPU response suppressed. |
| `WRITE_RESP` | `5` | CPU-side write response. |
| `READ_LAST` | `6` | Final read/refill response. |
| `WRITE_LAST` | `7` | Final writeback beat. |
| `PROBE` | `8` | Coherence probe request. |

## Key Constraints

- Metadata reset sweep takes about 128 cycles after reset release.
- Cache line is 8 words; refill order starts at `addr[5:3]` and wraps.
- For the selected D-cache instance, `io_flush[1]` is blocked by a D-cache assertion; directed flush tests use `io_flush[0]`.
- First coherence probe-hit data can depend on S3 `dataWay_*` register state; hit/miss command is the stable checked field.
