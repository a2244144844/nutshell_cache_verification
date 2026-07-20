# Replacement 规格说明文档

> 本文描述 Cache 的替换选择策略：invalid way 优先，其次使用 LFSR victim；同时覆盖 clean eviction 与 dirty eviction 的行为。结构说明参考主规格 [Cache 规格说明文档](/Users/zzy/Workspace/ucagent/competition/genspec_workspace/unity_test/Cache_spec.md)。

## 简介
- **设计背景**：Cache 的替换不是单独模块，而是由 Stage2 选择和 Stage3 状态机共同完成 <ref_file>Cache/Cache.v:161-176</ref_file> <ref_file>Cache/Cache.v:611-617</ref_file>。
- **设计目标**：优先利用 invalid way；当所有 way 都 valid 时，根据 LFSR 产生 victim way，并按 dirty 位决定是否需要 writeback <ref_file>Cache/Cache.v:165-176</ref_file> <ref_file>Cache/Cache.v:615-617</ref_file>。

## 术语与缩写
| 缩写 | 全称 | 说明 |
| ---- | ---- | ---- |
| Replacement | Replacement policy | Cache 替换策略 <ref_file>Cache/Cache.v:161-176</ref_file> |
| invalid way | Invalid way | 未填充的 way，优先被选中 <ref_file>Cache/Cache.v:166-176</ref_file> |
| victim | Victim way | 需要被替换的 way <ref_file>Cache/Cache.v:161-176</ref_file> |

## RTL源文件
- <ref_file>Cache/Cache.v</ref_file> 替换逻辑散布在 `CacheStage2` 和 `CacheStage3` <ref_file>Cache/Cache.v:161-176</ref_file> <ref_file>Cache/Cache.v:611-617</ref_file>。

## 顶层接口概览
| 信号名 | 方向 | 位宽/类型 | 描述 |
| ------ | ---- | -------- | ---- |
| `waymask` / `victimWaymask` / `refillInvalidWaymask` | internal | 4 | 替换选择结果 <ref_file>Cache/Cache.v:165-176</ref_file> |
| `meta_dirty` | internal | 1 | 目标 way 是否脏 <ref_file>Cache/Cache.v:514-515</ref_file> |

## 功能描述
### Invalid-way 优先
- 只要 `invalidVec` 非零，`refillInvalidWaymask` 就覆盖 LFSR victim <ref_file>Cache/Cache.v:166-176</ref_file>。
- 这一策略减少不必要的 writeback，是 clean refill 的基础前提 <ref_file>Cache/Cache.v:174-176</ref_file>。

### Dirty / Clean 选择
- `meta_dirty` 为真时，`_state_T_3` 进入 dirty writeback 路径，否则进入 clean refill 路径 <ref_file>Cache/Cache.v:514-515</ref_file> <ref_file>Cache/Cache.v:614-617</ref_file>。
- `dirty` victim 的回写必须先于后续 refill；`clean` victim 则直接替换即可 <ref_file>Cache/Cache.v:719-723</ref_file> <ref_file>Cache/docs/test_points.md:57-58</ref_file>。

### 选择器实现
- victim 由 `victimWaymask_lfsr[1:0]` 生成，LFSR 复位初值固定为 `64'h1234567887654321` <ref_file>Cache/Cache.v:161-165</ref_file> <ref_file>Cache/Cache.v:238-243</ref_file>。
- `waymask` 在命中时直接采用 hitVec，否则采用替换选择结果 <ref_file>Cache/Cache.v:175-176</ref_file> <ref_file>Cache/Cache.v:214-215</ref_file>。

## 状态机与时序
- 替换决策在 Stage2 完成，Stage3 只消费选择结果并发起相应 burst / writeback <ref_file>Cache/Cache.v:614-617</ref_file> <ref_file>Cache/Cache.v:719-723</ref_file>。
- 对 dirty victim 的回写序列由 `writeBeatCnt_value` 控制，8 beat 内输出 `WRITE_BURST` 到 `WRITE_LAST` <ref_file>Cache/Cache.v:633-641</ref_file>。

## 验证需求与覆盖建议
- 需要验证 single invalid way、多个 invalid way、clean eviction、dirty eviction 和 dirty writeback/refill 顺序 <ref_file>Cache/docs/test_points.md:49-58</ref_file>。
- 需要检查替换结果是否和 waymask 单热约束一致 <ref_file>Cache/Cache.v:262-275</ref_file>。

## 潜在 bug 分析
- **victim 选择与复位相关（待确认）**：LFSR 初值与随机初始化会影响 victim way 的可重复性；若验证环境对替换顺序有强假设，可能出现不稳定 <ref_file>Cache/Cache.v:238-243</ref_file>。
