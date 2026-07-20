# DataArray 子规范

日期：2026-05-28

对应英文文档：`unity_test/Cache/DataArray_spec.md`

## 摘要

DataArray 保存 Cache line 数据，支持 refill 写入、hit 读取、部分写掩码合并和 victim writeback 数据读取。

## 关注点

- refill beat 写入。
- hit path 数据读取。
- partial write mask merge。
- dirty eviction writeback 数据来源。

## 状态

该子规范由 GenSpec 生成，并与 write mask、word offset、refill/writeback 相关 CK 形成追踪关系。
