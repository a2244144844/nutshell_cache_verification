# Cache 规格说明文档

> 本文是 NutShell Cache 在当前 GenSpec 输入包下的主规格初稿。DUT 边界以 Picker 导出的 `Cache.v` 为准，不把上游完整 Chisel/NutShell 构建当作当前验证边界。若存在与文档不一致之处，优先以本页引用的输入文件为准，并将不确定项标注为“待人工确认”。  
> 主要证据来源见 <ref_file>Cache/README.md:1-26</ref_file>、<ref_file>Cache/docs/dut_selection.md:5-25</ref_file>、<ref_file>Cache/docs/Cache_basic_info.md:3-26</ref_file>。

## 简介
- **设计背景**：`Cache` 是 Picker 示例目录中的 NutShell Cache RTL，当前验证对象是导出的 Verilog 顶层 `Cache`，而不是上游完整 Chisel 构建；Picker 生成的 wrapper 位于 `build/picker_cache`，验证栈采用 Python + pytest + Toffee 统计覆盖的方式运行 <ref_file>Cache/docs/dut_selection.md:7-15</ref_file> <ref_file>Cache/docs/dut_selection.md:49-69</ref_file> <ref_file>Cache/docs/Cache_basic_info.md:17-26</ref_file>。
- **版本信息**：当前文档为生成初稿，未绑定 RTL 提交哈希；参考资料日期集中在 2026-05-25 至 2026-05-27 之间 <ref_file>Cache/docs/dut_selection.md:3-3</ref_file> <ref_file>Cache/docs/interface_map.md:3-3</ref_file> <ref_file>Cache/docs/test_points.md:3-3</ref_file>。
- **设计目标**：实现一个具备 CPU 请求/响应、内存 refill/writeback、MMIO bypass、coherence probe、flush/empty 控制的 simple-bus cache block，并能在 Picker/Python/pytest 流程下完成 smoke、directed、random 与 bug-evidence 验证 <ref_file>Cache/docs/Cache_functions_and_checks.md:3-9</ref_file> <ref_file>Cache/docs/Cache_verification_needs_and_plan.md:3-19</ref_file>。

## 术语与缩写
| 缩写 | 全称 | 说明 |
| ---- | ---- | ---- |
| DUT | Design Under Test | 当前验证对象为 `Cache.v` 顶层模块 `Cache` <ref_file>Cache/docs/dut_selection.md:25-47</ref_file> |
| Picker | Picker exporter | 将 `Cache.v` 导出为 Verilator/Python 可驱动 wrapper 的工具链 <ref_file>Cache/docs/dut_selection.md:49-69</ref_file> |
| Toffee | Functional coverage model | 当前覆盖报告使用的功能覆盖模型 <ref_file>Cache/docs/coverage_report.md:7-10</ref_file> |
| MMIO | Memory-Mapped I/O | 通过独立 `io_mmio_*` 通道旁路 cache 分配 <ref_file>Cache/docs/interface_map.md:97-107</ref_file> |
| SimpleBus | Cache 总线协议抽象 | `READ/WRITE/READ_BURST/WRITE_BURST/...` 命令编码见资料 <ref_file>Cache/docs/Cache_basic_info.md:39-51</ref_file> |
| probe | Coherence probe | 协议侧探测请求，输入输出经 `io_out_coh_*` 传递 <ref_file>Cache/docs/Cache_basic_info.md:27-37</ref_file> |

## RTL源文件
对本任务有直接关联的文件如下：

- <ref_file>Cache/Cache.v</ref_file> 主 RTL，顶层模块 `Cache`，接口定义和核心时序逻辑均在此文件中 <ref_file>Cache/Cache.v:2057-2107</ref_file>。
- <ref_file>Cache/Test.v</ref_file> 辅助 RTL/测试相关源码，当前内容是空壳 `Testmodule`（仅声明 `clk/rst/addr/data_in/data_out/cmd` 端口，无内部逻辑）；可视为占位文件而非 DUT 功能实现 <ref_file>Cache/Test.v:1-10</ref_file> <ref_file>Cache/README.md:6-11</ref_file> <ref_file>Cache/docs/dut_selection.md:9-15</ref_file>。
- <ref_file>Cache/Cache.yaml</ref_file> Picker 导出选择配置，当前仅保留少量内部寄存器可见性（如 `s3_io_in_bits_r_datas_1_data`、`forwardDataReg_data_data`）；其作用更接近导出/观测约束，而不是功能配置，具体意图待人工确认 <ref_file>Cache/Cache.yaml:1-5</ref_file>。

## 顶层接口概览
- **模块名称**：`Cache` <ref_file>Cache/Cache.v:2057-2107</ref_file>。
- **端口列表**：

  | 信号名 | 方向 | 位宽/类型 | 复位值 | 描述 |
  | ------ | ---- | -------- | ------ | ---- |
  | `clock` | input | 1 | 无 | 时钟输入 <ref_file>Cache/Cache.v:2057-2107</ref_file> |
  | `reset` | input | 1 | 无 | 复位输入 <ref_file>Cache/Cache.v:2057-2107</ref_file> |
  | `io_in_req_valid` / `io_in_req_ready` | input / output | 1 | 无 | CPU 请求握手 <ref_file>Cache/Cache.v:2060-2067</ref_file> <ref_file>Cache/Cache.v:2673-2677</ref_file> |
  | `io_in_req_bits_*` | input | addr[31:0], size[2:0], cmd[3:0], wmask[7:0], wdata[63:0], user[15:0] | 无 | CPU 请求内容 <ref_file>Cache/Cache.v:2062-2067</ref_file> |
  | `io_in_resp_valid` / `io_in_resp_ready` | output / input | 1 | 无 | CPU 响应握手 <ref_file>Cache/Cache.v:2068-2072</ref_file> <ref_file>Cache/Cache.v:2785-2786</ref_file> |
  | `io_in_resp_bits_*` | output | cmd[3:0], rdata[63:0], user[15:0] | 无 | CPU 响应内容 <ref_file>Cache/Cache.v:2069-2072</ref_file> |
  | `io_out_mem_req_valid` / `io_out_mem_req_ready` | output / input | 1 | 无 | 内存侧 refill/writeback 请求握手 <ref_file>Cache/Cache.v:2074-2080</ref_file> <ref_file>Cache/Cache.v:2678-2684</ref_file> |
  | `io_out_mem_resp_valid` / `io_out_mem_resp_ready` | input / output | 1 | 无 | 内存侧响应握手 <ref_file>Cache/Cache.v:2081-2084</ref_file> <ref_file>Cache/Cache.v:2792-2795</ref_file> |
  | `io_out_coh_req_valid` / `io_out_coh_req_ready` | input / output | 1 | 无 | coherence probe 请求握手 <ref_file>Cache/Cache.v:2085-2091</ref_file> <ref_file>Cache/Cache.v:2685-2688</ref_file> |
  | `io_out_coh_resp_valid` / `io_out_coh_resp_ready` | output / input | 1 | 无 | coherence probe 响应握手 <ref_file>Cache/Cache.v:2092-2095</ref_file> <ref_file>Cache/Cache.v:2799-2799</ref_file> |
  | `io_mmio_req_valid` / `io_mmio_req_ready` | output / input | 1 | 无 | MMIO 请求握手 <ref_file>Cache/Cache.v:2096-2102</ref_file> <ref_file>Cache/Cache.v:2689-2695</ref_file> |
  | `io_mmio_resp_valid` / `io_mmio_resp_ready` | input / output | 1 | 无 | MMIO 响应握手 <ref_file>Cache/Cache.v:2103-2106</ref_file> <ref_file>Cache/Cache.v:2796-2798</ref_file> |
  | `io_flush` | input | [1:0] | 无 | flush 控制，两个 bit 的行为不完全对称 <ref_file>Cache/Cache.v:2073-2073</ref_file> <ref_file>Cache/Cache.v:2836-2862</ref_file> |
  | `io_empty` | output | 1 | 无 | pipeline empty 状态 <ref_file>Cache/Cache.v:2107-2107</ref_file> <ref_file>Cache/Cache.v:2696-2696</ref_file> |

- **时钟与复位要求**：`clock` 为唯一时钟；`reset` 需在若干周期内保持高电平，再观察请求路径恢复。内部 metadata SRAM reset sweep 约 128 个周期，释放复位后不应立即假设缓存已完全可用 <ref_file>Cache/docs/interface_map.md:27-35</ref_file> <ref_file>Cache/docs/Cache_basic_info.md:53-58</ref_file>。
- **外部依赖**：验证依赖 Picker 导出、Verilator 仿真、Python/pytest 驱动以及 `cache_coverage.py` / `toffee_coverage.py` 覆盖统计 <ref_file>Cache/docs/Cache_basic_info.md:17-26</ref_file> <ref_file>Cache/docs/Cache_line_coverage_analysis.md:3-12</ref_file>。

## 功能描述

### DUT 边界与验证背景
- DUT 边界以 `rtl/dut/Cache.v` 为准，模块 `Cache` 是当前顶层；`Test.v` 与 `Cache.yaml` 仅作为导出时的附加输入，不应被当作 DUT 主体 <ref_file>Cache/docs/dut_selection.md:7-15</ref_file> <ref_file>Cache/docs/dut_selection.md:25-47</ref_file>。
- 当前验证方法是 Picker 生成 wrapper 后，由 Python/pytest 执行 smoke、directed、random、bug-injection 和 coverage 流程 <ref_file>Cache/docs/Cache_basic_info.md:17-26</ref_file> <ref_file>Cache/docs/Cache_verification_needs_and_plan.md:3-19</ref_file>。

### CPU 请求与响应
- **概述**：CPU 请求通过 `io_in_req_*` 输入，Cache 仲裁后进入内部 pipeline；CPU 响应通过 `io_in_resp_*` 返回。请求和响应均采用 ready/valid 语义 <ref_file>Cache/Cache.v:2060-2072</ref_file> <ref_file>Cache/Cache.v:2673-2677</ref_file> <ref_file>Cache/Cache.v:2785-2786</ref_file>。
- **执行流程**：
  1. `io_in_req_valid` 与 `io_in_req_ready` 同时为真并完成握手后，请求被送入内部仲裁与 pipeline <ref_file>Cache/docs/interface_map.md:116-125</ref_file> <ref_file>Cache/Cache.v:2825-2833</ref_file>。
  2. 命中时，`io_in_resp_valid` 直接返回 `READ_LAST` 或 `WRITE_RESP`，并携带 `rdata` / `user` 字段 <ref_file>Cache/docs/interface_map.md:67-77</ref_file> <ref_file>Cache/Cache.v:2674-2677</ref_file>。
  3. `io_in_resp_ready` 由下游消费端控制；在压力条件下，响应必须保持稳定，直到 `ready` 拉高 <ref_file>Cache/docs/Cache_functions_and_checks.md:137-145</ref_file>。
- **边界与异常**：
  - `PREFETCH` 请求在 CPU 侧不应产生普通响应，资料中明确说明该命令在 CPU 响应侧被抑制 <ref_file>Cache/docs/Cache_basic_info.md:39-51</ref_file> <ref_file>Cache/Cache.v:2674-2677</ref_file>。
  - 当 `io_in_resp_ready` 低时，响应必须保持有效与稳定；这是现有 corner test 的明确检查点 <ref_file>Cache/docs/Cache_functions_and_checks.md:137-145</ref_file> <ref_file>Cache/docs/test_points.md:54-55</ref_file>。

### 内存 Refill / Writeback
- **概述**：Cache 对内存侧使用 `io_out_mem_*` 通道发起 refill 或 dirty writeback。`READ_BURST` 表示 refill 请求，`WRITE_BURST` 表示脏块回写请求，最终 beat 分别使用 `READ_LAST` / `WRITE_LAST` <ref_file>Cache/docs/Cache_basic_info.md:39-51</ref_file> <ref_file>Cache/docs/interface_map.md:79-96</ref_file>。
- **执行流程**：
  1. 读 miss 触发 `READ_BURST`，memory 侧响应后，Cache 返回 CPU `READ_LAST` <ref_file>Cache/docs/interface_map.md:116-127</ref_file> <ref_file>Cache/docs/Cache_functions_and_checks.md:65-76</ref_file>。
  2. 写 miss 需要先完成 refill，并在必要时合并写掩码与 refill 数据；clean/dirty 相关流程分别由 DIR-011、DIR-013 证明 <ref_file>Cache/docs/test_points.md:56-58</ref_file> <ref_file>Cache/docs/Cache_functions_and_checks.md:65-76</ref_file>。
  3. 脏 victim eviction 时，`WRITE_BURST` / `WRITE_LAST` 必须先于后续 refill 出现 <ref_file>Cache/docs/Cache_bug_analysis.md:39-55</ref_file> <ref_file>Cache/docs/test_points.md:56-58</ref_file>。
- **边界与异常**：
  - 内存请求 size 在实现中固定输出为 `3'h3`，即 64-bit 访问粒度；上层若传入其他 size，需依赖协议约束而非动态适配 <ref_file>Cache/Cache.v:2678-2684</ref_file>。
  - refill beat 顺序从 `addr[5:3]` 指定的 word index 开始并回绕，缓存行共 8 个 word；这是现有资料明确给出的约束 <ref_file>Cache/docs/Cache_basic_info.md:55-58</ref_file> <ref_file>Cache/docs/interface_map.md:126-127</ref_file>。

### Meta / Data SRAM
- **概述**：Cache 的 tag/valid/dirty 元数据与 data 存储分别由 `SRAMTemplate` 和 `SRAMTemplateWithArbiter` 实现；两类存储均按 4-way 组织，每个 way 对应 128 个 set <ref_file>Cache/Cache.v:1043-1293</ref_file> <ref_file>Cache/Cache.v:1306-1575</ref_file>。
- **结构细节**：
  - metadata array 每个 entry 为 21 bit，字段拼接为 `{tag[18:0], valid[0], dirty[0]}`；这与顶层 meta 读口输出的 tag/valid/dirty 一致 <ref_file>Cache/Cache.v:1085-1180</ref_file>。
  - data array 每个 entry 为 64 bit，按 word 粒度存储；顶层通过 `addr[12:6]` 选 set，通过 `addr[5:3]` 选 line 内 word <ref_file>Cache/Cache.v:1085-1180</ref_file> <ref_file>Cache/Cache.v:51-53</ref_file>。
  - metadata 和 data 都支持读写分离的握手接口，读口带一拍管线寄存；`resetState` 触发时会对 128 个 set 执行清扫初始化 <ref_file>Cache/Cache.v:1125-1214</ref_file>。
- **执行流程**：
  1. `CacheStage1` 计算 meta set index 和 data set index，并把请求与 SRAM 读口同时拉起 <ref_file>Cache/Cache.v:41-53</ref_file>。
  2. `CacheStage2` 接收 meta/data 读口返回值，计算 `hitVec`、`invalidVec`、`victimWaymask`、`refillInvalidWaymask`，并依据 forward 写回覆盖读值 <ref_file>Cache/Cache.v:128-176</ref_file> <ref_file>Cache/Cache.v:202-220</ref_file>。
  3. `CacheStage3` 在写入阶段通过 `metaWriteArb` 与 `dataWriteArb` 将 refill、hit-write、writeback 等写请求合并后送入 SRAM <ref_file>Cache/Cache.v:479-504</ref_file> <ref_file>Cache/Cache.v:672-751</ref_file>。
- **边界与异常**：
  - 由于 `waymask` 必须是单热编码，RTL 中对 `PopCount(waymask) > 1` 设有断言；若上游构造非法多热 waymask，会直接触发断言 <ref_file>Cache/Cache.v:262-275</ref_file>。
  - `SRAMTemplate` 复位期间会先对所有 set 做初始化写入，此时读请求不应被视为稳定功能访问 <ref_file>Cache/Cache.v:1125-1214</ref_file>。

### MMIO
- **概述**：MMIO 使用独立 `io_mmio_*` 通道，接口形状与内存侧一致，但用于非缓存路径；测试资料要求 MMIO 读写不得产生 cache 命中或普通 memory 请求 <ref_file>Cache/docs/Cache_basic_info.md:27-37</ref_file> <ref_file>Cache/docs/interface_map.md:97-107</ref_file> <ref_file>Cache/docs/test_points.md:51-51</ref_file>。
- **执行流程**：
  1. 地址命中 MMIO 区间时，cache 通过 `io_mmio_req_valid` 对外发出请求 <ref_file>Cache/Cache.v:2689-2695</ref_file>。
  2. MMIO 响应通过 `io_mmio_resp_valid` 返回，不应污染 cache line 状态 <ref_file>Cache/docs/Cache_functions_and_checks.md:97-107</ref_file>。
- **边界与异常**：
  - MMIO 读/写在验证中必须保持“旁路不分配”语义；若后续读命中，说明旁路失效，需要作为功能缺陷处理 <ref_file>Cache/docs/Cache_functions_and_checks.md:97-107</ref_file> <ref_file>Cache/docs/test_points.md:51-51</ref_file>。

### Coherence Probe
- **概述**：`io_out_coh_*` 通道用于 probe/release 相关的 coherence 事务，当前资料把它当作可验证的 probe hit/miss 路径，而不是空接口 <ref_file>Cache/docs/Cache_basic_info.md:27-37</ref_file> <ref_file>Cache/docs/interface_map.md:103-107</ref_file>。
- **执行流程**：
  1. probe 请求从 `io_out_coh_req_valid` 发出，top-level `Cache` 将其交给内部仲裁后处理 <ref_file>Cache/Cache.v:2085-2095</ref_file> <ref_file>Cache/Cache.v:2819-2824</ref_file>。
  2. 现有 directed test 以 `cmd=0xc` 作为 hit、`cmd=0x8` 作为 miss 的检查字段 <ref_file>Cache/docs/test_points.md:53-53</ref_file>。
  3. 文档提醒：第一次 probe-hit 的 data 可能受 S3 `dataWay_*` 寄存器状态影响，因此稳定检查项应优先使用 hit/miss command <ref_file>Cache/docs/Cache_basic_info.md:55-58</ref_file>。
- **边界与异常**：
  - probe 命中后的返回 data 若在首次场景中有轻微不确定性，应标注为实现相关而非直接判定为错误；这一点需要在后续规格/测试中进一步确认 <ref_file>Cache/docs/Cache_basic_info.md:55-58</ref_file>。

### Flush / Empty
- **概述**：`io_flush[0]` 和 `io_flush[1]` 分别作用于不同 pipeline stage 的清空逻辑，`io_empty` 表示 pipeline 为空 <ref_file>Cache/Cache.v:2073-2073</ref_file> <ref_file>Cache/Cache.v:2696-2696</ref_file> <ref_file>Cache/Cache.v:2833-2865</ref_file>。
- **执行流程**：
  1. 在 `io_flush[0]` 作用下，S1/S2 侧 valid 清零 <ref_file>Cache/Cache.v:2833-2840</ref_file>。
  2. 在 `io_flush[1]` 作用下，S3 侧 valid 清零 <ref_file>Cache/Cache.v:2859-2865</ref_file>。
   3. `io_empty` 等于 `~s2_io_in_valid` 且 `~s3_io_in_valid`，表示当前 pipeline 没有在途事务 <ref_file>Cache/Cache.v:2696-2696</ref_file>。
- **边界与异常**：
  - 现有测试资料明确指出，面向该 D-cache 实例时 `io_flush[1]` 会受到断言约束，因此 directed flush 主要使用 `io_flush[0]`；`io_flush[1]` 的架构级可用性需要人工确认 <ref_file>Cache/docs/Cache_basic_info.md:55-58</ref_file> <ref_file>Cache/docs/test_points.md:52-53</ref_file>。
  - flush 期间 `io_empty` 应按阶段预期收敛，不应出现 flush 后仍长期保留在途事务的现象 <ref_file>Cache/docs/Cache_functions_and_checks.md:109-117</ref_file>。

### 状态机与时序
- **状态机列表**：当前顶层实现可从 `CacheStage1/2/3` 三段 pipeline 与内部 arbiter 结构理解，且 `CacheStage3` 里包含命中、miss、MMIO、coherence、flush 相关状态转换 <ref_file>Cache/docs/dut_selection.md:27-47</ref_file> <ref_file>Cache/Cache.v:385-420</ref_file>。
  - `state = 4'h0`：idle / 接收新请求；probe、hit-read-burst、miss 都从这里分流 <ref_file>Cache/Cache.v:611-617</ref_file> <ref_file>Cache/Cache.v:764-775</ref_file>。
  - `state = 4'h1`：clean refill / 读 miss 的内存读 burst 入口 <ref_file>Cache/Cache.v:584-586</ref_file> <ref_file>Cache/Cache.v:719-723</ref_file>。
  - `state = 4'h3`：dirty writeback 入口，使用 `WRITE_BURST` / `WRITE_LAST` 逐 beat 回写 <ref_file>Cache/Cache.v:615-617</ref_file> <ref_file>Cache/Cache.v:719-723</ref_file>。
  - `state = 4'h5` / `4'h6`：MMIO request / response 等待阶段 <ref_file>Cache/Cache.v:724-730</ref_file> <ref_file>Cache/Cache.v:776-781</ref_file>。
  - `state = 4'h7`：返回 CPU 响应的收尾阶段，控制 `alreadyOutFire` 与 output fire 结束 <ref_file>Cache/Cache.v:620-623</ref_file> <ref_file>Cache/Cache.v:776-783</ref_file>。
  - `state = 4'h8`：hit-read-burst 或 probe 相关的 burst 读取阶段；该状态与 `state2` 子状态协同推进 <ref_file>Cache/Cache.v:611-617</ref_file> <ref_file>Cache/Cache.v:708-709</ref_file>。
- **关键时序图**：
  - CPU 请求先被 arbiter 接收，再进入 S1/S2/S3 pipeline；`io_in_req_ready` 由内部 arbiter 返回 <ref_file>Cache/Cache.v:2673-2677</ref_file> <ref_file>Cache/Cache.v:2825-2833</ref_file>。
  - reset 释放后，不应立即把 cache 当作完全可服务；文档要求等待 request-ready，再结合约 128 周期 metadata reset sweep 判断可用性 <ref_file>Cache/docs/interface_map.md:31-35</ref_file> <ref_file>Cache/docs/Cache_basic_info.md:55-58</ref_file>。
  - directed test 中，读 miss 典型序列是“请求握手 -> `READ_BURST` -> memory `READ_LAST` -> CPU `READ_LAST` -> 同址读命中” <ref_file>Cache/docs/interface_map.md:116-127</ref_file>。

### 子组件描述
- `CacheStage1`：请求接入、并行向 meta/data 读口发起查询、计算 set index 和 data index <ref_file>Cache/Cache.v:1-54</ref_file>。
- `CacheStage2`：命中判定、替换选择、forward 覆盖、MMIO 位判定和写掩码/word mask 计算 <ref_file>Cache/Cache.v:55-341</ref_file>。
- `CacheStage3`：最终状态机、refill/writeback/MMIO/probe/flush 收尾与对外响应 <ref_file>Cache/Cache.v:385-899</ref_file>。
- `MetaDataArray`：4-way metadata SRAM，负责 tag/valid/dirty 读写和 reset sweep <ref_file>Cache/Cache.v:1043-1293</ref_file>。
- `DataArray`：4-way data SRAM，负责 line word 数据读写与双读口并发 <ref_file>Cache/Cache.v:1576-1835</ref_file>。
- `Replacement`：由 Stage2 中的 invalid-way 优先与 LFSR victim 选择共同实现，建议作为独立验证主题 <ref_file>Cache/Cache.v:161-176</ref_file>。

### 配置寄存器及存储
| 寄存器名/地址 | 访问属性 | 位段 | 缺省值 | 描述 | 读写副作用 |
| ------------- | -------- | ---- | ------ | ---- | ---------- |
| 无显式寄存器接口 | N/A | N/A | N/A | 顶层 `Cache` 没有可见的配置寄存器地址空间；控制主要通过 ready/valid、`io_flush` 和复位完成 <ref_file>Cache/Cache.v:2057-2107</ref_file>。 | N/A |

- **寄存器映射基地址**：无；当前 DUT 不是寄存器映射型外设 <ref_file>Cache/Cache.v:2057-2107</ref_file>。
- **配置流程**：先拉高 `reset`，再等待 `io_in_req_ready` 恢复；之后通过普通请求流配置运行态，无需额外寄存器初始化 <ref_file>Cache/docs/interface_map.md:27-35</ref_file>。

### 复位与错误处理
- **复位行为**：`reset` 为同步输入复位语义下的顶层控制信号；复位释放后，internal metadata reset sweep 约 128 周期，期间不要假设行状态已稳定 <ref_file>Cache/docs/interface_map.md:27-35</ref_file> <ref_file>Cache/docs/Cache_basic_info.md:55-58</ref_file>。
- **错误上报**：当前可见文档未定义独立 error pin 或错误状态寄存器；错误主要通过 checker、scoreboard、以及 directed test 失败体现，属于“无显式硬件错误上报”状态 <ref_file>Cache/docs/Cache_functions_and_checks.md:161-190</ref_file> <ref_file>Cache/docs/Cache_bug_analysis.md:80-87</ref_file>。
- **自恢复策略**：当测试插入 bug 被关闭后，正常回归应恢复为 clean；bug injection 文档说明 recovery path 会退出成功 <ref_file>Cache/docs/Cache_bug_analysis.md:31-37</ref_file> <ref_file>Cache/docs/bug_tracking.md:39-55</ref_file>。

### 功耗、时钟与电源管理（如适用）
- **功耗模式**：暂缺；当前资料未描述低功耗/待机模式 <ref_file>Cache/docs/Cache_verification_needs_and_plan.md:3-19</ref_file>。
- **时钟门控**：暂缺；资料只暴露单一 `clock` 输入，没有显式时钟门控端口 <ref_file>Cache/Cache.v:2057-2107</ref_file>。
- **电源域**：暂缺；现有输入包未提供电源域信息 <ref_file>Cache/docs/Cache_basic_info.md:3-16</ref_file>。

### 参数化与可配置特性
- **模块参数**：无显式 parameter 列表；`Cache` 顶层以固定端口形式出现，参数化能力若存在，应属于上游生成阶段而非当前可见 RTL 顶层 <ref_file>Cache/Cache.v:2057-2107</ref_file>。
- **编译宏/生成选项**：当前资料未列出 RTL 编译宏；已知的生成入口是 `scripts/export_cache_dut.sh`，输出到 `build/picker_cache` <ref_file>Cache/docs/dut_selection.md:49-69</ref_file>。
- **编译宏/生成选项**：当前资料未列出 RTL 编译宏；已知的生成入口是 `scripts/export_cache_dut.sh`，输出到 `build/picker_cache`。`Cache.yaml` 还会影响导出后保留的内部寄存器可见性，属于观测配置而非 DUT 功能配置 <ref_file>Cache/docs/dut_selection.md:49-69</ref_file> <ref_file>Cache/Cache.yaml:1-5</ref_file>。

## 验证需求与覆盖建议
- **功能覆盖点**：FG/FC/CK 结构已在《Cache Functions And Checks》中定义，覆盖范围包括 smoke、写掩码、refill/write miss、replacement/eviction、MMIO、flush、coherence probe、backpressure、random coverage 与 bug evidence <ref_file>Cache/docs/Cache_functions_and_checks.md:11-190</ref_file>。
- **约束与假设**：
  - Cache line 为 8 个 word，refill 顺序从 `addr[5:3]` 起始并回绕 <ref_file>Cache/docs/Cache_basic_info.md:55-58</ref_file>。
  - `io_flush[1]` 的功能可用性在当前 D-cache 场景下受限，directed flush 主要以 `io_flush[0]` 为准 <ref_file>Cache/docs/Cache_basic_info.md:55-58</ref_file> <ref_file>Cache/docs/test_points.md:52-53</ref_file>。
  - 首次 coherence probe-hit 的 data 可能受内部状态影响，建议以命令字段与稳定的后续行为为主做判定 <ref_file>Cache/docs/Cache_basic_info.md:55-58</ref_file>。
- **测试接口**：需要 CPU 请求/响应驱动、memory/MMIO/coherence responder、flush 触发器、scoreboard/reference model、coverage collector，以及可重放的 bug injection 脚本 <ref_file>Cache/docs/Cache_basic_info.md:17-26</ref_file> <ref_file>Cache/docs/Cache_verification_needs_and_plan.md:11-18</ref_file> <ref_file>Cache/docs/bug_tracking.md:13-55</ref_file>。

## 潜在 bug 分析

> 以下条目同时包含“已知问题”和“高优先级验证风险”。凡是设计意图不完全明确的地方，均标注为待人工确认。

- **脏 victim writeback 逻辑回退风险（置信度 90%）**
  - 触发条件：dirty line 在 set conflict 下被替换时，若状态机错误跳过 `WRITE_BURST` / `WRITE_LAST`，则 dirty victim 会在 refill 前被静默丢弃 <ref_file>Cache/docs/Cache_bug_analysis.md:39-55</ref_file> <ref_file>Cache/docs/bug_tracking.md:63-105</ref_file>。
  - 影响范围：会破坏脏数据持久性，造成后续读写数据错误，属于高严重度功能缺陷 <ref_file>Cache/docs/Cache_bug_analysis.md:50-55</ref_file>。
  - 定位线索：`Cache.v` 中 `meta_dirty ? 4'h3 : 4'h1` 的 dirty-miss 决策点已在 bug 记录中被明确指向 <ref_file>Cache/Cache.v:614-617</ref_file> <ref_file>Cache/docs/bug_tracking.md:63-89</ref_file>。
  - 验证建议：保留 dirty writeback directed test，并在回归中检查 `write_reqs` 非空及写回/回填顺序 <ref_file>Cache/docs/test_points.md:57-58</ref_file> <ref_file>Cache/docs/Cache_functions_and_checks.md:77-88</ref_file>。

- **coherence probe 首次命中 data 依赖内部状态（置信度 65%）**
  - 触发条件：probe-hit 的第一次返回数据受到 S3 `dataWay_*` 寄存器状态影响，若测试强行比较首拍 data 可能出现不稳定结果 <ref_file>Cache/docs/Cache_basic_info.md:55-58</ref_file> <ref_file>Cache/docs/test_points.md:53-53</ref_file>。
  - 影响范围：容易引入误报，掩盖真实的 probe 命令错误；也可能说明 probe 数据输出路径还需要补充更强的规格约束 <ref_file>Cache/docs/Cache_functions_and_checks.md:119-129</ref_file>。
  - 定位线索：当前公开资料只给出“hit/miss 命令为稳定检查字段”，未给出首拍 data 的严格定义，属于待人工确认项 <ref_file>Cache/docs/Cache_basic_info.md:55-58</ref_file>。
  - 验证建议：对 probe 场景优先验证命令、握手和 resident line 关系，若要比较 data，需补充一致的前置填充条件与采样时序 <ref_file>Cache/docs/Cache_functions_and_checks.md:119-129</ref_file>。

- **flush 位语义可能存在层级区分，`io_flush[1]` 需人工确认（置信度 80%）**
  - 触发条件：顶层存在 `io_flush[0]` / `io_flush[1]` 两个 bit，但资料明确指出 D-cache 实例中 `io_flush[1]` 受断言限制，当前 directed flush 主要使用 `io_flush[0]` <ref_file>Cache/Cache.v:2073-2073</ref_file> <ref_file>Cache/Cache.v:2833-2862</ref_file> <ref_file>Cache/docs/test_points.md:52-53</ref_file>。
  - 影响范围：若规格误把两个 bit 视为完全等价，可能导致测试覆盖与实际架构意图不一致 <ref_file>Cache/docs/Cache_functions_and_checks.md:109-117</ref_file>。
  - 定位线索：`Cache.v` 中 S1/S2 由 `io_flush[0]` 清空，而 S3 由 `io_flush[1]` 清空；这说明 flush 两位的职责存在阶段差异 <ref_file>Cache/Cache.v:2833-2865</ref_file>。
  - 验证建议：在后续阶段补充“`io_flush[1]` 是否为架构上保留位”人工确认，并将相关测试命名与预期分开记录 <ref_file>Cache/docs/Cache_basic_info.md:55-58</ref_file>。

- **覆盖口径存在文档差异，需要人工确认最终对外表述（置信度 70%）**
  - 触发条件：`coverage_report.md` 记载 RTL line coverage 为 1344/1366 (98.4%)，而 `Cache_line_coverage_analysis.md` 又说明当前 active flow 并未正式收集 RTL line coverage 报告；两份资料对“是否已闭合”存在口径差异 <ref_file>Cache/docs/coverage_report.md:1-10</ref_file> <ref_file>Cache/docs/Cache_line_coverage_analysis.md:44-52</ref_file>。
  - 影响范围：若对外叙述不加区分，容易把“覆盖证据”和“覆盖流程闭环”混为一谈 <ref_file>Cache/docs/Cache_verification_needs_and_plan.md:43-51</ref_file>。
  - 定位线索：当前已知未覆盖区主要集中在 CacheStage3 的内部 probe path、`needFlush` 退回路径及部分 D-cache ports <ref_file>Cache/docs/test_points.md:170-176</ref_file> <ref_file>Cache/docs/Cache_line_coverage_analysis.md:36-47</ref_file>。
  - 验证建议：后续若要输出最终版规格，应先由人工确认到底采用“98.4% line coverage”还是“line coverage 不作为正式闭环指标”的对外口径 <ref_file>Cache/docs/coverage_report.md:3-10</ref_file> <ref_file>Cache/docs/Cache_line_coverage_analysis.md:46-52</ref_file>。

## 当前结论
- 当前资料已经足以支撑主规格初稿：DUT 边界、接口、功能点、覆盖状况和已知 bug 都有明确来源 <ref_file>Cache/docs/dut_selection.md:7-15</ref_file> <ref_file>Cache/docs/Cache_functions_and_checks.md:11-190</ref_file> <ref_file>Cache/docs/Cache_bug_analysis.md:3-87</ref_file>。
- 仍需人工确认的点主要是 `io_flush[1]` 的架构语义、probe 首次命中 data 的判定口径，以及 RTL line coverage 的最终对外表述 <ref_file>Cache/docs/Cache_basic_info.md:55-58</ref_file> <ref_file>Cache/docs/Cache_line_coverage_analysis.md:44-52</ref_file>。
