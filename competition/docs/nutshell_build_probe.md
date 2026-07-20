# NutShell Build Probe

Date: 2026-05-25

This document records the local NutShell/Chisel build closure explored for the Track1 Cache verification task. This build is useful for source context, but it is not the selected DUT boundary. The selected DUT is documented in `docs/dut_selection.md`.

## Local Toolchain

| Tool | Location | Result |
| --- | --- | --- |
| Java runtime | `local/jre17` | Azul Zulu JRE `17.0.19`; `java -version` passes. |
| Mill | `local/mill/bin/mill` | NutShell-required Mill `0.11.7`; `mill --version` passes. |
| Picker | `local/picker/bin/picker` | Picker `0.9.0...`; C++ and Python support pass. |

Load the environment with:

```sh
source competition/scripts/env.sh
```

The environment script exports `JAVA_HOME`, `MILL_HOME`, `PICKER_HOME`, `NOOP_HOME`, `PATH`, and `PYTHONPATH`.

The repeatable RTL build script is:

```sh
competition/scripts/build_nutshell_rtl.sh
```

## Source Closure

NutShell was downloaded into:

```text
competition/upstream/NutShell
```

The downloaded archive did not include the `difftest` submodule, so `OpenXiangShan/difftest` was downloaded and placed at:

```text
competition/upstream/NutShell/difftest
```

Without this submodule, Chisel compilation fails on missing `difftest.common.DifftestMem`, `UARTIO`, and related symbols.

## RTL Generation

Command:

```sh
source /Users/zzy/Workspace/ucagent/competition/scripts/env.sh
cd /Users/zzy/Workspace/ucagent/competition/upstream/NutShell
mill -i generator.test.runMain top.TopMain --target-dir build/rtl BOARD=sim CORE=inorder --split-verilog
```

Result:

- Scala/Chisel elaboration completed.
- Warnings were emitted for several dynamic index widths; no fatal elaboration error remained.
- Generated RTL directory: `upstream/NutShell/build/rtl`
- Generated difftest C/C++ side files: `upstream/NutShell/build/generated-src`

## Cache RTL Files

Generated Cache-related modules:

```text
Cache.sv
Cache_1.sv
Cache_2.sv
CacheStage1.sv
CacheStage1_1.sv
CacheStage1_2.sv
CacheStage2.sv
CacheStage2_1.sv
CacheStage2_2.sv
CacheStage3.sv
CacheStage3_1.sv
CacheStage3_2.sv
```

The suffixes correspond to Chisel-specialized variants for the instantiated icache, dcache, and l2cache configurations.

## Outcome

This build path was exploratory. After checking Picker's `example/Cache` directory, the selected DUT boundary was corrected to `rtl/dut/Cache.v`, copied from `tools/picker/example/Cache/Cache.v`.
