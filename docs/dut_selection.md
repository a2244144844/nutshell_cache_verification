# DUT Selection

Date: 2026-05-25

## Selected DUT

The DUT for this verification task is the Cache RTL from Picker's example directory, not the full NutShell RTL generated from the upstream Chisel tree.

Local tracked copy:

```text
rtl/dut/Cache.v
rtl/dut/Test.v
rtl/dut/Cache.yaml
```

Original source copy:

```text
tools/picker/example/Cache/Cache.v
tools/picker/example/Cache/Test.v
tools/picker/example/Cache/Cache.yaml
```

`Cache.v` contains the generated Verilog implementation of the NutShell Cache, with top module `Cache`.

## Module Inventory

The selected `Cache.v` contains these modules:

```text
CacheStage1
CacheStage2
Arbiter
Arbiter_1
CacheStage3
SRAMTemplate
Arbiter_2
SRAMTemplateWithArbiter
SRAMTemplate_1
Arbiter_3
SRAMTemplateWithArbiter_1
Arbiter_4
Cache
```

The top module is `Cache`.

## Picker Export

Repeatable command:

```sh
scripts/export_cache_dut.sh
```

The script:

1. Activates the repository `.venv` when available, so the generated Python wrapper uses Python 3.11.
2. Loads `scripts/env.sh` for Picker and other local tools.
3. Runs `picker export` on `rtl/dut/Cache.v`.
4. Includes `rtl/dut/Test.v` as an extra source file.
5. Builds the generated Verilator and Python artifacts.

Output directory:

```text
build/picker_cache
```

Generated Python class:

```python
from __init__ import DUTCache
```

Important generated pins include:

- CPU-side request: `io_in_req_valid`, `io_in_req_ready`, `io_in_req_bits_addr`, `io_in_req_bits_cmd`, `io_in_req_bits_size`, `io_in_req_bits_wmask`, `io_in_req_bits_wdata`, `io_in_req_bits_user`
- CPU-side response: `io_in_resp_valid`, `io_in_resp_ready`, `io_in_resp_bits_cmd`, `io_in_resp_bits_rdata`, `io_in_resp_bits_user`
- Memory-side request/response: `io_out_mem_*`
- MMIO-side request/response: `io_mmio_*`
- Coherence-side request/response: `io_out_coh_*`
- Control/status: `clock`, `reset`, `io_flush`, `io_empty`

## Correction

The upstream OSCPU/NutShell Chisel build from the previous step remains useful as source context, but it is not the selected DUT boundary for this competition workflow. Verification work should proceed from `rtl/dut/Cache.v` and the Picker-generated `DUTCache` wrapper.
