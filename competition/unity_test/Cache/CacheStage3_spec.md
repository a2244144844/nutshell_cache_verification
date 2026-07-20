# CacheStage3 规格说明文档

> 本文描述 `CacheStage3` 的职责：执行最终状态机、发起 memory/MMIO/coherence 请求、产生 CPU 返回，并处理 flush 收尾。结构说明参考主规格 [Cache 规格说明文档](/Users/zzy/Workspace/ucagent/competition/genspec_workspace/unity_test/Cache_spec.md)。

## 简介
- **设计背景**：`CacheStage3` 是 Cache 的事务执行层，包含 refill、writeback、MMIO、probe 和 flush 的最终控制逻辑 <ref_file>Cache/Cache.v:385-899</ref_file>。
- **设计目标**：把 Stage2 的判定结果转为可见协议事务，并在状态收敛时返回 CPU 响应 <ref_file>Cache/Cache.v:703-734</ref_file>。

## 术语与缩写
| 缩写 | 全称 | 说明 |
| ---- | ---- | ---- |
| Stage3 | CacheStage3 | Cache 事务执行层 <ref_file>Cache/Cache.v:385-899</ref_file> |
| refill | Refilling cache line | 从 memory 拉回 cache line <ref_file>Cache/Cache.v:719-723</ref_file> |
| writeback | Dirty eviction writeback | dirty victim 回写 <ref_file>Cache/Cache.v:615-617</ref_file> |

## RTL源文件
- <ref_file>Cache/Cache.v</ref_file> `CacheStage3` 定义 <ref_file>Cache/Cache.v:385-899</ref_file>。

## 顶层接口概览
| 信号名 | 方向 | 位宽/类型 | 描述 |
| ------ | ---- | -------- | ---- |
| `io_in_valid` / `io_in_ready` | input / output | 1 | Stage2 到 Stage3 的握手 <ref_file>Cache/Cache.v:385-460</ref_file> |
| `io_flush` | input | 1 | Stage3 flush 控制 <ref_file>Cache/Cache.v:420-420</ref_file> |
| `io_mem_req_*` / `io_mem_resp_*` | output / input | 1 / 4 / 64 | memory refill/writeback 通道 <ref_file>Cache/Cache.v:437-445</ref_file> |
| `io_mmio_req_*` / `io_mmio_resp_*` | output / input | 1 / 3 / 4 / 8 / 64 | MMIO 通道 <ref_file>Cache/Cache.v:446-455</ref_file> |
| `io_cohResp_*` | output / input | 1 / 4 / 64 | coherence 响应 <ref_file>Cache/Cache.v:456-459</ref_file> |
| `io_out_valid` / `io_out_bits_*` | output | 1 / cmd/rdata/user | CPU 响应 <ref_file>Cache/Cache.v:414-419</ref_file> |

## 功能描述
### 事务类型
- `probe`：以 `cmd == 4'h8` 识别，用于 coherence probe <ref_file>Cache/Cache.v:510-512</ref_file>。
- `hitReadBurst`：命中后的 burst 读取路径，主要影响 `io_dataReadBus` 与 L1 返回 <ref_file>Cache/Cache.v:512-513</ref_file> <ref_file>Cache/Cache.v:734-734</ref_file>。
- `miss` / `mmio`：分别进入 refill/writeback 或 MMIO 分支 <ref_file>Cache/Cache.v:507-516</ref_file>。

### 外部通道
- memory 侧 `io_mem_req_bits_cmd` 在 clean refill 时使用 `READ_BURST`，dirty victim 时使用 `WRITE_BURST` / `WRITE_LAST` <ref_file>Cache/Cache.v:584-586</ref_file> <ref_file>Cache/Cache.v:719-723</ref_file>。
- MMIO 路径直接转发 addr/size/cmd/wmask/wdata，并在响应到来后收尾 <ref_file>Cache/Cache.v:724-730</ref_file> <ref_file>Cache/Cache.v:776-781</ref_file>。
- coherence 响应命令以 `hit ? 4'hc : 4'h8` 为主；release 场景还有 `READ_LAST` 收尾 <ref_file>Cache/Cache.v:603-604</ref_file> <ref_file>Cache/Cache.v:731-733</ref_file>。

### CPU 响应
- `io_out_bits_rdata` 命中时直接取 `dataRead`，否则取 `inRdataRegDemand` <ref_file>Cache/Cache.v:705-706</ref_file>。
- `io_out_bits_cmd` 由请求命令映射得到，写返回 `WRITE_RESP`，读返回 `READ_LAST` <ref_file>Cache/Cache.v:664-666</ref_file> <ref_file>Cache/Cache.v:704-706</ref_file>。

## 状态机与时序
- `state = 4'h0`：idle；probe/hit/miss 在此分流 <ref_file>Cache/Cache.v:611-617</ref_file> <ref_file>Cache/Cache.v:764-775</ref_file>。
- `state = 4'h1`：clean refill 的 memory burst 入口 <ref_file>Cache/Cache.v:584-586</ref_file> <ref_file>Cache/Cache.v:719-723</ref_file>。
- `state = 4'h3`：dirty writeback 入口，按 `writeBeatCnt_value` 输出 `WRITE_BURST` / `WRITE_LAST` <ref_file>Cache/Cache.v:615-617</ref_file> <ref_file>Cache/Cache.v:633-641</ref_file>。
- `state = 4'h5` / `4'h6`：MMIO 请求和响应等待 <ref_file>Cache/Cache.v:724-730</ref_file> <ref_file>Cache/Cache.v:776-781</ref_file>。
- `state = 4'h7`：返回 CPU 的收尾阶段，处理 output fire 与 `alreadyOutFire` <ref_file>Cache/Cache.v:620-623</ref_file> <ref_file>Cache/Cache.v:838-853</ref_file>。
- `state = 4'h8`：hit-read-burst / probe 相关 burst 路径 <ref_file>Cache/Cache.v:623-625</ref_file> <ref_file>Cache/Cache.v:708-709</ref_file>。

## 验证需求与覆盖建议
- 覆盖 clean refill、dirty writeback、MMIO bypass、probe hit/miss、flush 收敛和 response fire 顺序 <ref_file>Cache/Cache.v:702-734</ref_file> <ref_file>Cache/Cache.v:785-865</ref_file>。
- 需要验证 `io_flush` 清空后 `io_empty` 能及时归零/恢复 <ref_file>Cache/Cache.v:696-696</ref_file> <ref_file>Cache/Cache.v:783-865</ref_file>。

## 潜在 bug 分析
- **dirty writeback 漏发（已知高风险）**：若 `meta_dirty ? 4'h3 : 4'h1` 决策被破坏，dirty victim 可能直接进入 refill 并丢数据 <ref_file>Cache/Cache.v:614-617</ref_file> <ref_file>Cache/docs/bug_tracking.md:63-105</ref_file>。
- **flush / MMIO 交叠时序（待确认）**：`needFlush` 与 `state` 交互较复杂，若 flush 在 MMIO 或 burst 中插入，可能出现状态提前清零或 stuck 风险 <ref_file>Cache/Cache.v:558-559</ref_file> <ref_file>Cache/Cache.v:785-791</ref_file>。
