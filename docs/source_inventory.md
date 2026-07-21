# Source Inventory

This document records the source material for the Track1 NutShell Cache verification task and the current local availability of each item.

## Local References

| Item | Path | Status | Notes |
| --- | --- | --- | --- |
| Competition requirement summary | `docs/track1_UCAgent_competition_requirements.md` | Available | Defines UCAgent/Picker/Toffee expectations, scoring, deliverables, and checklist. |
| UCAgent + Codex instruction | `instruction.md` | Available | Defines the verified local UCAgent/Codex MCP execution path. |
| Step plan | `step.md` | Available | Local phased plan generated from the two files above. |
| UCAgent examples | `examples/` | Available | Useful for output style, docs, and Toffee-oriented test/report patterns. |
| DCache example docs | `examples/GenSpec/DCache/` | Available | XiangShan DCache material, not the NutShell Cache DUT, but useful as a complex cache-analysis reference. |
| Selected Cache DUT RTL | `rtl/dut/Cache.v` | Available | Copied from Picker `example/Cache/Cache.v`; this is the selected DUT for verification. |
| Selected Cache helper source | `rtl/dut/Test.v` | Available | Extra source used by Picker's Cache example export flow. |
| Selected Cache signal config | `rtl/dut/Cache.yaml` | Available | Internal signal config from Picker's Cache example. |

## Upstream References

| Item | URL / Local Path | Status | Notes |
| --- | --- | --- | --- |
| GitLink competition env | `https://gitlink.org.cn/XS-MLVP/env-xs-ov-00-nutshell-cache.git` / `upstream/env-xs-ov-00-nutshell-cache` | Cloned | Contains task instructions and a submit-template directory, but does not contain the Cache DUT implementation. |
| NutShell Cache documentation | `https://oscpu.github.io/NutShell-doc/%E5%8A%9F%E8%83%BD%E9%83%A8%E4%BB%B6/cache.html` | Reachable | Official Cache documentation page. |
| NutShell source tree | `https://github.com/OSCPU/NutShell` / `upstream/NutShell` | Downloaded | Chisel source tree downloaded from GitHub archive. |
| NutShell `difftest` submodule | `https://github.com/OpenXiangShan/difftest` / `upstream/NutShell/difftest` | Downloaded | Required for `BOARD=sim` elaboration; archive download was used because the NutShell zip did not include submodule contents. |
| NutShell Cache source | `upstream/NutShell/src/main/scala/nutcore/mem/Cache.scala` | Available locally | Chisel source for `Cache.scala`; license header is Mulan PSL v2. |
| Picker Cache example | `tools/picker/example/Cache` | Available locally | Original source for the selected DUT; ignored as upstream tool source, with a tracked copy in `rtl/dut/`. |

## Initial DUT Observations

From the reachable `Cache.scala` source, the Cache design includes these major structures:

- `CacheConfig`: parameters such as read-only mode, cache level, total size, ways, user bits, and id bits.
- `CacheIO`: top-level request/response, memory, MMIO, flush, finish, and optional coherence response interfaces.
- `CacheStage1`: request intake and meta/data array read.
- `CacheStage2`: meta/data response handling, hit detection, invalid-way/refill-way selection, and forwarding.
- `CacheStage3`: hit response, miss handling, memory read refill, dirty writeback, MMIO path, probe/release path, and response generation.

Important behavior candidates for verification:

- Read hit and write hit.
- Read miss and write miss.
- Refill after miss.
- Dirty victim writeback before refill.
- Invalid-way selection before replacement.
- Burst read/write paths.
- Flush handling.
- MMIO bypass path.
- Optional coherence/probe/release path.
- Forwarding after meta/data writes.

## Selected DUT Boundary

The selected DUT is `rtl/dut/Cache.v`, copied from Picker's `example/Cache/Cache.v`.

Notes:

- Top module: `Cache`.
- Picker-generated Python class: `DUTCache`.
- Repeatable export script: `scripts/export_cache_dut.sh`.
- Output directory: `build/picker_cache`.

The OSCPU/NutShell Chisel build path remains useful as source context, but the generated full NutShell RTL is not the selected DUT boundary.

## Local Tool Probe

Checked on 2026-05-25:

| Tool / Package | Status | Notes |
| --- | --- | --- |
| UCAgent | Available | `ucagent --version` reports `0.9.2.dev1+geda2d0d7d`. |
| Codex CLI | Available | `codex --version` reports `0.131.0-alpha.9`. |
| pytoffee | Available | Python package `pytoffee` is installed. |
| toffee-test | Available | Python package `toffee-test` is installed. |
| pytest | Available | Python package import succeeds. |
| Verilator | Available | `/opt/homebrew/bin/verilator`, version `5.046`. |
| Picker CLI | Available locally | Installed from source at `local/picker`; see `docs/picker_installation.md`. |
| Java runtime | Available locally | Azul Zulu JRE `17.0.19` installed at `local/jre17`. |
| Mill | Available locally | Mill `0.11.7` installed at `local/mill/bin/mill`, matching NutShell `.mill-version`. |

Picker validation:

- `picker --version` reports `0.9.0-master-301c403-2026-05-12-dirty`.
- `picker --check` reports C++ and Python support as OK.
- `.venv` can import `xspcomm` from the local Picker installation.
- `picker export` was smoke-tested on `examples/Adder/Adder.v`; the generated Python DUT produced `1 + 2 = 3`.

NutShell build validation:

- `mill -i generator.test.runMain top.TopMain --target-dir build/rtl BOARD=sim CORE=inorder --split-verilog` completes.
- Generated RTL is under `upstream/NutShell/build/rtl`.
- Cache-related generated modules include `Cache.sv`, `Cache_1.sv`, `Cache_2.sv`, and matching `CacheStage1/2/3` variants.

Selected DUT export validation:

- `scripts/export_cache_dut.sh` completes.
- Generated wrapper uses `.venv` Python 3.11 when the virtual environment is present.
- `DUTCache` can be instantiated, stepped, and finished from Python.
