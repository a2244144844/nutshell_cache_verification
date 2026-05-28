# CacheStage2 子规范

日期：2026-05-28

对应英文文档：`unity_test/Cache/CacheStage2_spec.md`

## 摘要

CacheStage2 负责 tag/meta 查询、hit/miss 判断、way 选择、写掩码与 word offset 相关逻辑。

## 关注点

- read hit / write hit。
- invalid way 优先与 replacement 选择。
- byte/half/word/full/sparse write mask。
- MMIO bypass 的早期识别。

## 状态

该子规范由 UCAgent GenSpec 生成，相关 RTL 行已映射到 CK。
