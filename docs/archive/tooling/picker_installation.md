# Picker Installation

Picker was installed from source following the official flow, with one local compatibility adjustment so the Python binding uses this repository's `.venv` Python 3.11 runtime.

## Install Location

```text
local/picker
```

Useful paths:

```text
local/picker/bin/picker
local/picker/share/picker/python
tools/picker
```

## Environment Setup

From repository root:

```bash
source .venv/bin/activate
source scripts/env.sh
```

Then verify:

```bash
picker --version
picker --check
python -c "import xspcomm; print(xspcomm.__file__)"
```

Expected status:

- `picker --version` reports `0.9.0-master-301c403-2026-05-12-dirty`.
- `picker --check` reports C++ and Python support as OK.
- Golang, Java, Lua, and Scala support may be reported as missing; this is acceptable for the current Python/Toffee verification flow.
- `xspcomm` imports successfully from `local/picker/share/picker/python`.

## Local Build Patch

The upstream CMake files requested only `Python3 Development.Module`. On this machine, that caused CMake to bind the native Python module to Homebrew Python 3.14, while UCAgent uses `.venv` Python 3.11. The resulting `_pyxspcomm.so` could not be imported in `.venv`.

Local patch:

```text
tools/picker/dependence/xcomm/swig/python/CMakeLists.txt
tools/picker/template/python/CMakeLists.txt
```

Change:

```cmake
find_package(Python3 REQUIRED COMPONENTS Interpreter Development.Module)
```

Build command:

```bash
cd tools/picker
make init
rm -rf build
make -j$(sysctl -n hw.ncpu) ARGS="-DPython3_EXECUTABLE=/Users/zzy/Workspace/ucagent/.venv/bin/python"
make install ARGS="-DCMAKE_INSTALL_PREFIX=/Users/zzy/Workspace/ucagent/local/picker -DPython3_EXECUTABLE=/Users/zzy/Workspace/ucagent/.venv/bin/python"
```

## Smoke Test

The installation was validated with the repository's simple Adder RTL:

```bash
rm -rf /tmp/picker_adder_smoke
mkdir -p /tmp/picker_adder_smoke
source .venv/bin/activate
source scripts/env.sh

picker export examples/Adder/Adder.v \
  --rw 1 \
  --sname Adder \
  --tdir /tmp/picker_adder_smoke/ \
  -c \
  -w /tmp/picker_adder_smoke/Adder/Adder.fst
```

Python import and execution check:

```bash
PYTHONPATH="/tmp/picker_adder_smoke:$PYTHONPATH" python - <<'PY'
from Adder import DUTAdder

dut = DUTAdder()
dut.a.value = 1
dut.b.value = 2
dut.cin.value = 0
dut.Step(1)
print(int(dut.sum.value), int(dut.cout.value))
dut.Finish()
PY
```

Observed output:

```text
3 0
```

