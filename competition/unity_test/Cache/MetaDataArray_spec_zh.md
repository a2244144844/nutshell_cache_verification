# MetaDataArray 子规范

日期：2026-05-28

对应英文文档：`unity_test/Cache/MetaDataArray_spec.md`

## 摘要

MetaDataArray 保存 Cache line 的 tag、valid/dirty 等元数据，并包含 reset sweep 相关行为。

## 关注点

- reset 后 metadata 初始化。
- read/write 端口仲裁。
- hit/miss 判断所需的 meta 输出。
- dirty/valid 状态更新。

## 状态

该子规范由 UCAgent GenSpec 生成，reset sweep 与 metadata access 已在检查点和行映射中体现。
