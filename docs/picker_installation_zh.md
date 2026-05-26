# Picker 安装

Picker 按官方流程从源码安装，并进行了一项本地兼容性调整，使 Python 绑定使用本仓库 `.venv` 的 Python 3.11 运行时。

## 安装位置

```text
competition/track1_nutshell_cache/local/picker
```

常用路径：

```text
competition/track1_nutshell_cache/local/picker/bin/picker
competition/track1_nutshell_cache/local/picker/share/picker/python
competition/track1_nutshell_cache/tools/picker
```

## 环境设置

在仓库根目录下：

```bash
source .venv/bin/activate
source competition/track1_nutshell_cache/scripts/env.sh
```

然后验证：

```bash
picker --version
picker --check
python -c "import xspcomm; print(xspcomm.__file__)"
```

预期状态：

- `picker --version` 报告 `0.9.0-master-301c403-2026-05-12-dirty`。
- `picker --check` 报告 C++ 和 Python 支持正常。
- Golang、Java、Lua 和 Scala 支持可能显示缺失；对于当前 Python/Toffee 验证流程这是可接受的。
- `xspcomm` 可从 `local/picker/share/picker/python` 成功导入。

## 本地构建补丁

上游 CMake 文件仅请求 `Python3 Development.Module`。在本机上这导致 CMake 将原生 Python 模块绑定到 Homebrew Python 3.14，而 UCAgent 使用 `.venv` Python 3.11。结果是生成的 `_pyxspcomm.so` 无法在 `.venv` 中导入。

本地补丁：

```text
tools/picker/dependence/xcomm/swig/python/CMakeLists.txt
tools/picker/template/python/CMakeLists.txt
```

修改：

```cmake
find_package(Python3 REQUIRED COMPONENTS Interpreter Development.Module)
```

构建命令：

```bash
cd competition/track1_nutshell_cache/tools/picker
make init
rm -rf build
make -j$(sysctl -n hw.ncpu) ARGS="-DPython3_EXECUTABLE=/Users/zzy/Workspace/ucagent/.venv/bin/python"
make install ARGS="-DCMAKE_INSTALL_PREFIX=/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/local/picker -DPython3_EXECUTABLE=/Users/zzy/Workspace/ucagent/.venv/bin/python"
```

## Smoke 测试

使用仓库中的简单 Adder RTL 验证安装：

```bash
rm -rf /tmp/picker_adder_smoke
mkdir -p /tmp/picker_adder_smoke
source .venv/bin/activate
source competition/track1_nutshell_cache/scripts/env.sh

picker export examples/Adder/Adder.v \
  --rw 1 \
  --sname Adder \
  --tdir /tmp/picker_adder_smoke/ \
  -c \
  -w /tmp/picker_adder_smoke/Adder/Adder.fst
```

Python 导入和执行检查：

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

观测输出：

```text
3 0
```
