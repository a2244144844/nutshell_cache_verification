# DataArray 规格说明文档

> 本文描述 Cache 的 data 存储阵列：4-way、1024-entry/way、64-bit word 组织，支持两读一写的使用模式。结构说明参考主规格 [Cache 规格说明文档](/Users/zzy/Workspace/ucagent/competition/genspec_workspace/unity_test/Cache_spec.md)。

## 简介
- **设计背景**：data array 保存 cache line 的 word 数据，Stage1/Stage3 会以不同读口访问同一类存储 <ref_file>Cache/Cache.v:1576-1835</ref_file> <ref_file>Cache/Cache.v:2626-2646</ref_file>。
- **设计目标**：支持 line refill、hit write、forward 覆盖和 burst read，同时保持按 waymask 的独立更新 <ref_file>Cache/Cache.v:1576-1835</ref_file>。

## 术语与缩写
| 缩写 | 全称 | 说明 |
| ---- | ---- | ---- |
| DataArray | Data array | Cache 数据存储阵列 <ref_file>Cache/Cache.v:1576-1835</ref_file> |
| wordIdx | Word index | line 内 word 索引 <ref_file>Cache/Cache.v:51-53</ref_file> <ref_file>Cache/Cache.v:582-583</ref_file> |

## RTL源文件
- <ref_file>Cache/Cache.v</ref_file> `SRAMTemplate_1` 与 `SRAMTemplateWithArbiter_1` 定义 <ref_file>Cache/Cache.v:1576-1835</ref_file> <ref_file>Cache/Cache.v:1801-1835</ref_file>。

## 顶层接口概览
| 信号名 | 方向 | 位宽/类型 | 描述 |
| ------ | ---- | -------- | ---- |
| `io_r_0_req_*` / `io_r_1_req_*` | input / output | 10-bit setIdx | 双读口 <ref_file>Cache/Cache.v:1801-1821</ref_file> |
| `io_r_0_resp_data_*` / `io_r_1_resp_data_*` | output | 64-bit data x4 | 四路 data 返回 <ref_file>Cache/Cache.v:1801-1821</ref_file> |
| `io_w_req_*` | input | setIdx/data/waymask | 写通道 <ref_file>Cache/Cache.v:1801-1821</ref_file> |

## 功能描述
### 存储结构
- 每个 way 有 1024 个 64-bit entry，对应 `{setIdx[6:0], wordIdx[2:0]}` 的合成索引空间 <ref_file>Cache/Cache.v:1606-1645</ref_file> <ref_file>Cache/Cache.v:745-750</ref_file>。
- 读口使用一拍延迟输出，写口按 waymask 局部更新 <ref_file>Cache/Cache.v:1646-1708</ref_file>。

### 访问模式
- Stage1 用 `dataArray_io_r_0` 支持当前请求的 hit 检查，Stage3 用 `dataArray_io_r_1` 支持 refill / burst 读取 <ref_file>Cache/Cache.v:2718-2722</ref_file> <ref_file>Cache/Cache.v:2787-2791</ref_file>。
- 写入时，hit write 和 refill write 都走 `io_dataWriteBus_req_*`，由 arbiter 合并 <ref_file>Cache/Cache.v:710-718</ref_file> <ref_file>Cache/Cache.v:744-751</ref_file>。

## 状态机与时序
- 读口是独立的管线寄存器队列，`io_r_req_valid` 与 `_realRen_T` 同时为真后下一拍返回数据 <ref_file>Cache/Cache.v:1680-1708</ref_file>。
- 在复位或 write 期间，读口 ready 可能被拉低，以保证一致性 <ref_file>Cache/Cache.v:1646-1675</ref_file>。

## 验证需求与覆盖建议
- 验证应覆盖 8-word line 的 word 选择、同 way 的写后读回、refill 数据写入和 forward 覆盖 <ref_file>Cache/Cache.v:744-751</ref_file> <ref_file>Cache/Cache.v:855-860</ref_file>。
- 建议检查 `addr[5:3]` 与 `readBeatCnt_value` 的对应关系，避免 refill 线内顺序错误 <ref_file>Cache/Cache.v:612-613</ref_file> <ref_file>Cache/Cache.v:748-750</ref_file>。

## 潜在 bug 分析
- **wordIdx 绑定错误（待确认）**：如果 word 选择索引拼接错位，可能导致同一 cache line 内不同 word 互相覆盖；需要通过定向 word-offset 测试验证 <ref_file>Cache/Cache.v:745-750</ref_file> <ref_file>Cache/docs/test_points.md:47-48</ref_file>。
