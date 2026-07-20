# MetaDataArray 规格说明文档

> 本文描述 Cache 的 metadata 存储阵列：4-way、128-set、21-bit 结构，包含 tag/valid/dirty 字段与 reset sweep 行为。结构说明参考主规格 [Cache 规格说明文档](/Users/zzy/Workspace/ucagent/competition/genspec_workspace/unity_test/Cache_spec.md)。

## 简介
- **设计背景**：metadata 存储用于保存每个 set 的 4 路 tag/valid/dirty 状态，顶层由 `CacheStage1/2/3` 访问 <ref_file>Cache/Cache.v:1043-1293</ref_file>。
- **设计目标**：在复位时完成全表清扫，在运行时提供一拍延迟读出和按 waymask 写入 <ref_file>Cache/Cache.v:1125-1214</ref_file>。

## 术语与缩写
| 缩写 | 全称 | 说明 |
| ---- | ---- | ---- |
| MetaDataArray | Metadata array | Cache 元数据存储阵列 <ref_file>Cache/Cache.v:1043-1293</ref_file> |
| waymask | Way mask | 选择哪个 way 写入/读取 <ref_file>Cache/Cache.v:1131-1167</ref_file> |

## RTL源文件
- <ref_file>Cache/Cache.v</ref_file> `SRAMTemplate` 定义 <ref_file>Cache/Cache.v:1043-1293</ref_file>。

## 顶层接口概览
| 信号名 | 方向 | 位宽/类型 | 描述 |
| ------ | ---- | -------- | ---- |
| `io_r_req_valid/ready` | input / output | 1 | metadata 读握手 <ref_file>Cache/Cache.v:1046-1065</ref_file> |
| `io_r_req_bits_setIdx` | input | 7 | set 索引 <ref_file>Cache/Cache.v:1048-1048</ref_file> |
| `io_r_resp_data_*` | output | 21 split 成 tag/valid/dirty | 4 路 metadata 返回 <ref_file>Cache/Cache.v:1049-1060</ref_file> |
| `io_w_req_*` | input | setIdx/tag/dirty/waymask | metadata 写通道 <ref_file>Cache/Cache.v:1061-1065</ref_file> |

## 功能描述
### 存储结构
- 四个 way 分别对应 `array_0` 到 `array_3`，每个 array 有 128 个 entry <ref_file>Cache/Cache.v:1085-1124</ref_file>。
- 每个 entry 21 bit，拆成 tag[18:0]、valid、dirty <ref_file>Cache/Cache.v:1133-1179</ref_file>。

### 读写与初始化
- 读口为一拍管线，`io_r_req_valid` 与 `_realRen_T` 同时为真后下一拍出数 <ref_file>Cache/Cache.v:1180-1208</ref_file>。
- 写口按 waymask 局部更新，复位时写入全 0 并遍历所有 set <ref_file>Cache/Cache.v:1131-1214</ref_file>。

### 与顶层的关系
- 顶层 `CacheStage1`/`CacheStage2` 通过 `metaArray` 获取 tag/valid/dirty，用于命中和替换决策 <ref_file>Cache/Cache.v:2620-2624</ref_file> <ref_file>Cache/Cache.v:2705-2717</ref_file>。

## 状态机与时序
- `resetState` 置位后进入 128-set sweep，直到 `resetSet == 7'h7f` 才结束 <ref_file>Cache/Cache.v:1125-1130</ref_file>。
- 在 reset sweep 期间，`io_r_req_ready` 为假，避免把初始化当成正常访问 <ref_file>Cache/Cache.v:1131-1167</ref_file>。

## 验证需求与覆盖建议
- 验证应覆盖 reset sweep、4-way 同时读回、按 waymask 局部写入、dirty 位保持与 tag 更新 <ref_file>Cache/Cache.v:1131-1214</ref_file>。
- 建议检查 MetaDataArray 与 Stage2 的 hit/invalid/victim 选择一致性 <ref_file>Cache/Cache.v:148-176</ref_file>。

## 潜在 bug 分析
- **初始化窗口误用（待确认）**：复位 sweep 期间若上层把读返回当成功能结果，可能引入错误判定；需要保证测试在 reset 完成后再启动 <ref_file>Cache/Cache.v:1129-1214</ref_file>。
