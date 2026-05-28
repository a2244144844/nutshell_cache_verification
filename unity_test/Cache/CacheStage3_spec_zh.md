# CacheStage3 子规范

日期：2026-05-28

对应英文文档：`unity_test/Cache/CacheStage3_spec.md`

## 摘要

CacheStage3 是 Cache 的主要状态机阶段，负责 miss/refill、dirty writeback、MMIO 响应、flush、coherence probe 和最终 response 控制。

## 关注点

- read miss 与 refill。
- write miss clean/dirty 路径。
- dirty victim writeback。
- probe hit/miss 和 release。
- flush drain/recovery。
- backpressure 下 response 保持。

## 状态

该子规范已通过 GenSpec 流程生成，并通过 directed tests、Toffee coverage 和 line coverage closure 获得验证支撑。
