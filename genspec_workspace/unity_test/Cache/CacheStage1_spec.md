# CacheStage1 规格说明文档

> 本文描述 `CacheStage1` 的职责：接收上游请求、同时启动 meta/data 读查询，并把 set index / word index 传播给下一级。结构说明参考主规格 [Cache 规格说明文档](/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/genspec_workspace/unity_test/Cache_spec.md)。

## 简介
- **设计背景**：`CacheStage1` 是 Cache pipeline 的入口级组合逻辑，负责把请求与 SRAM 读口对接 <ref_file>Cache/Cache.v:1-54</ref_file>。
- **设计目标**：在不改变请求语义的前提下，尽早完成 set decode，并在 meta/data 读口都就绪时向下游转发 <ref_file>Cache/Cache.v:41-53</ref_file>。

## 术语与缩写
| 缩写 | 全称 | 说明 |
| ---- | ---- | ---- |
| Stage1 | CacheStage1 | Cache 入口接入层 <ref_file>Cache/Cache.v:1-54</ref_file> |
| meta/data read bus | Meta/Data read bus | Stage1 向 SRAM 发起的并行查询通道 <ref_file>Cache/Cache.v:18-39</ref_file> |

## RTL源文件
- <ref_file>Cache/Cache.v</ref_file> `CacheStage1` 定义 <ref_file>Cache/Cache.v:1-54</ref_file>。

## 顶层接口概览
| 信号名 | 方向 | 位宽/类型 | 描述 |
| ------ | ---- | -------- | ---- |
| `io_in_valid` / `io_in_ready` | input / output | 1 | 请求握手 <ref_file>Cache/Cache.v:1-54</ref_file> |
| `io_in_bits_*` | input | addr/size/cmd/wmask/wdata/user | CPU 请求字段 <ref_file>Cache/Cache.v:1-54</ref_file> |
| `io_out_valid` / `io_out_ready` | output / input | 1 | 向下一级转发握手 <ref_file>Cache/Cache.v:1-54</ref_file> |
| `io_metaReadBus_*` | output / input | setIdx + meta 返回 | meta 读通道 <ref_file>Cache/Cache.v:18-32</ref_file> |
| `io_dataReadBus_*` | output / input | setIdx + data 返回 | data 读通道 <ref_file>Cache/Cache.v:33-39</ref_file> |

## 功能描述
### 请求接入
- `io_out_valid` 仅在 `io_in_valid` 且 meta/data 读口都 ready 时拉高 <ref_file>Cache/Cache.v:41-53</ref_file>。
- `io_in_ready` 只有在本拍请求未阻塞、且两类读口可用时才返回真 <ref_file>Cache/Cache.v:41-43</ref_file>。

### 地址拆分
- meta set index 使用 `addr[12:6]` <ref_file>Cache/Cache.v:50-52</ref_file>。
- data set index 使用 `{addr[12:6], addr[5:3]}`，因此 Stage1 只做索引拼接，不解释命中/替换语义 <ref_file>Cache/Cache.v:52-53</ref_file>。

## 状态机与时序
- `CacheStage1` 本身没有显式状态机；它是纯组合接入层 <ref_file>Cache/Cache.v:41-54</ref_file>。
- 若下游回压，Stage1 通过 `io_out_ready` 维持 backpressure，避免提前消耗请求 <ref_file>Cache/Cache.v:41-43</ref_file>。

## 验证需求与覆盖建议
- 验证重点应放在 set index 计算和 ready/valid 稳定性，不应把它当成功能决策层 <ref_file>Cache/Cache.v:41-54</ref_file>。
- 建议检查同一请求在下游回压时不会改变 addr/size/cmd/wmask/wdata/user 字段 <ref_file>Cache/Cache.v:44-49</ref_file>。

## 潜在 bug 分析
- **组合接入口回压异常（待确认）**：若 `io_metaReadBus_req_ready` 或 `io_dataReadBus_req_ready` 在同拍抖动，Stage1 可能导致请求吞吐下降；需要结合上游协议确认是否允许这一类 stall <ref_file>Cache/Cache.v:41-43</ref_file>。
