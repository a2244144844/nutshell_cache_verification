# Cache 接口映射

日期：2026-05-26

## DUT

选定 RTL：

```text
rtl/dut/Cache.v
```

顶层模块：

```text
Cache
```

Picker 生成的 Python wrapper：

```python
from __init__ import DUTCache
```

wrapper 由 `scripts/export_cache_dut.sh` 生成至 `build/picker_cache`。

## 时钟与复位

| 信号 | 方向 | 位宽 | 备注 |
| --- | --- | --- | --- |
| `clock` | input | 1 | 在调用 `dut.Step(...)` 之前必须调用 `dut.InitClock("clock")`。 |
| `reset` | input | 1 | 保持高电平若干周期，然后等待 `io_in_req_ready` 变为 1。 |

内部元数据 SRAM 复位扫描在释放 reset 后大约需要 128 个周期。

## SimpleBus 命令编码

从 RTL 和 smoke 行为观测：

| 名称 | 编码 | 备注 |
| --- | --- | --- |
| `READ` | `0` | 普通 CPU 侧读请求。 |
| `WRITE` | `1` | 普通 CPU 侧写请求。 |
| `READ_BURST` | `2` | 读缺失时发出的内存侧 refill 请求。 |
| `WRITE_BURST` | `3` | 脏 victim 写回突发命令。 |
| `PREFETCH` | `4` | 此命令的响应在 CPU 侧被抑制。 |
| `WRITE_RESP` | `5` | CPU 侧写响应。 |
| `READ_LAST` | `6` | CPU 侧读响应及 smoke 测试使用的内存 refill 响应。 |
| `WRITE_LAST` | `7` | 最终写回节拍。 |
| `PROBE` | `8` | Coherence probe 请求。 |

## CPU 侧请求

前缀：`io_in_req_*`

| 信号 | 方向 | 位宽 | 备注 |
| --- | --- | --- | --- |
| `io_in_req_valid` | input | 1 | 请求有效。 |
| `io_in_req_ready` | output | 1 | 请求就绪。 |
| `io_in_req_bits_addr` | input | 32 | 字节地址。 |
| `io_in_req_bits_size` | input | 3 | Smoke 使用 `3` 表示 64 位访问。 |
| `io_in_req_bits_cmd` | input | 4 | SimpleBus 命令。 |
| `io_in_req_bits_wmask` | input | 8 | 字节写掩码。 |
| `io_in_req_bits_wdata` | input | 64 | 写数据。 |
| `io_in_req_bits_user` | input | 16 | 用户元数据，随 CPU 响应返回。 |

## CPU 侧响应

前缀：`io_in_resp_*`

| 信号 | 方向 | 位宽 | 备注 |
| --- | --- | --- | --- |
| `io_in_resp_ready` | input | 1 | 响应就绪。Smoke 保持高电平。 |
| `io_in_resp_valid` | output | 1 | 响应有效。 |
| `io_in_resp_bits_cmd` | output | 4 | 读为 `READ_LAST`，写为 `WRITE_RESP`。 |
| `io_in_resp_bits_rdata` | output | 64 | 读数据。 |
| `io_in_resp_bits_user` | output | 16 | 回显请求用户元数据。 |

## 内存侧接口

前缀：`io_out_mem_*`

| 信号 | 方向 | 位宽 | 备注 |
| --- | --- | --- | --- |
| `io_out_mem_req_valid` | output | 1 | 内存请求有效。 |
| `io_out_mem_req_ready` | input | 1 | 内存请求就绪。Smoke 保持高电平。 |
| `io_out_mem_req_bits_addr` | output | 32 | Refill/写回地址。 |
| `io_out_mem_req_bits_size` | output | 3 | 生成为 64 位大小。 |
| `io_out_mem_req_bits_cmd` | output | 4 | Smoke 在首次读缺失时观测到 `READ_BURST`。 |
| `io_out_mem_req_bits_wmask` | output | 8 | 写回掩码。 |
| `io_out_mem_req_bits_wdata` | output | 64 | 写回数据。 |
| `io_out_mem_resp_valid` | input | 1 | 内存响应有效。 |
| `io_out_mem_resp_ready` | output | 1 | 内存响应就绪。 |
| `io_out_mem_resp_bits_cmd` | input | 4 | Smoke 返回 `READ_LAST`。 |
| `io_out_mem_resp_bits_rdata` | input | 64 | Refill 数据。 |

## MMIO 接口

前缀：`io_mmio_*`

MMIO 与内存接口具有相同的请求/响应结构。Smoke 保持 `io_mmio_req_ready` 高电平且 `io_mmio_resp_valid` 低电平，因为测试地址非 MMIO。

## Coherence 接口

前缀：`io_out_coh_*`

选定的 Cache 具有 probe/release 支持。Smoke 保持 `io_out_coh_req_valid` 低电平且 `io_out_coh_resp_ready` 高电平。Coherence 场景是后续定向测试的目标。

## 控制与状态

| 信号 | 方向 | 位宽 | 备注 |
| --- | --- | --- | --- |
| `io_flush` | input | 2 | 流水线 flush 控制。 |
| `io_empty` | output | 1 | 流水线空状态。 |

## Smoke 时序说明

在 `tests/smoke/test_cache_basic.py` 中观测到的首次读缺失流程：

1. 当 `io_in_req_valid && io_in_req_ready` 时 CPU 请求被接受。
2. Cache 随后发出一个内存请求，`cmd == READ_BURST`。
3. 测试用内存以 `cmd == READ_LAST` 和 refill 数据响应。
4. Cache 返回 CPU 响应，`cmd == READ_LAST`，包含 refill 数据和回显的用户元数据。
5. 对相同地址的再次读取命中，不再发出内存请求。
6. 全掩码写命中返回 `WRITE_RESP`；后续读取返回写入的值。

对于 `tests/directed/test_refill_beats.py` 中更完整的 refill 模型，内存响应以 8 个节拍驱动。前 7 个节拍使用 `READ`；最后一个节拍使用 `READ_LAST`。Refill 从请求的 `addr[5:3]` word 索引开始，然后环绕 8-word 的 cache line。
