# CacheStage1 子规范

日期：2026-05-28

对应英文文档：`unity_test/Cache/CacheStage1_spec.md`

## 摘要

CacheStage1 负责接收前级请求，完成基础握手、请求字段保持和向 Stage2 的流水传递。

## 关注点

- CPU request ready/valid 接收。
- PROBE/MMIO/cacheable 请求分类的前置路径。
- flush 或 backpressure 下的请求保持。

## 状态

该子规范由 UCAgent GenSpec 生成，并已纳入主规范与行映射闭环。
