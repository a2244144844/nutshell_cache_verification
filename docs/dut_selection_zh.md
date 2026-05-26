# DUT 选择

日期：2026-05-25

## 选定 DUT

本验证任务的 DUT 为来自 Picker 示例目录的 Cache RTL，而非从上游 Chisel 树生成的完整 NutShell RTL。

本地跟踪副本：

```text
rtl/dut/Cache.v
rtl/dut/Test.v
rtl/dut/Cache.yaml
```

原始源副本：

```text
tools/picker/example/Cache/Cache.v
tools/picker/example/Cache/Test.v
tools/picker/example/Cache/Cache.yaml
```

`Cache.v` 包含 NutShell Cache 的生成 Verilog 实现，顶层模块为 `Cache`。

## 模块清单

选定的 `Cache.v` 包含以下模块：

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

顶层模块为 `Cache`。

## Picker 导出

可重复执行命令：

```sh
competition/track1_nutshell_cache/scripts/export_cache_dut.sh
```

该脚本：

1. 当仓库 `.venv` 存在时激活它，使生成的 Python wrapper 使用 Python 3.11。
2. 加载 `scripts/env.sh` 配置 Picker 和其他本地工具。
3. 对 `rtl/dut/Cache.v` 运行 `picker export`。
4. 将 `rtl/dut/Test.v` 作为额外源文件包含。
5. 构建生成的 Verilator 和 Python 产物。

输出目录：

```text
build/picker_cache
```

生成的 Python 类：

```python
from __init__ import DUTCache
```

重要的生成引脚包括：

- CPU 侧请求：`io_in_req_valid`、`io_in_req_ready`、`io_in_req_bits_addr`、`io_in_req_bits_cmd`、`io_in_req_bits_size`、`io_in_req_bits_wmask`、`io_in_req_bits_wdata`、`io_in_req_bits_user`
- CPU 侧响应：`io_in_resp_valid`、`io_in_resp_ready`、`io_in_resp_bits_cmd`、`io_in_resp_bits_rdata`、`io_in_resp_bits_user`
- 内存侧请求/响应：`io_out_mem_*`
- MMIO 侧请求/响应：`io_mmio_*`
- Coherence 侧请求/响应：`io_out_coh_*`
- 控制/状态：`clock`、`reset`、`io_flush`、`io_empty`

## 修正说明

上一步中从上游 OSCPU/NutShell Chisel 构建的内容仍作为源码上下文有用，但它不是本赛题工作流选定的 DUT 边界。验证工作应以 `rtl/dut/Cache.v` 和 Picker 生成的 `DUTCache` wrapper 为基础进行。
