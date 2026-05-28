# Replacement 子规范

日期：2026-05-28

对应英文文档：`unity_test/Cache/Replacement_spec.md`

## 摘要

Replacement 逻辑用于在没有 invalid way 可用时选择 victim way。RTL 中包含 LFSR 相关保护逻辑。

## 关注点

- invalid way 优先。
- clean eviction。
- dirty victim writeback。
- replacement stability。
- LFSR 全零状态保护的不可达豁免。

## 状态

该子规范由 GenSpec 生成，并通过 clean/dirty eviction directed tests 与覆盖率闭环获得支撑。
