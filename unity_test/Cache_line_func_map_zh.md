# Cache 行号到检查点映射

日期：2026-05-28

对应英文文档：`unity_test/Cache_line_func_map.md`

## 说明

该文件是 UCAgent GenSpec `ref_function_line_map_generation` 阶段的中文对应说明。英文文件包含完整 CK 到 `Cache.v` 行号区间映射。

## 检查结果

`FileLineMapChecker` 已通过：`Cache/Cache.v` 全部行均已映射到 CK，或通过 `IGNORE` 明确标注为随机初始化、生成器样板、非功能性脚手架。

## 作用

该映射用于证明功能检查点与 RTL 代码之间存在可追溯关系，也是后续覆盖率闭环和报告审查的依据。
