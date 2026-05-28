# Cache 行映射分析

日期：2026-05-28

对应英文文档：`unity_test/Cache_line_map_analysis.md`

## 说明

该文档解释 `Cache_line_func_map.md` 的映射策略。

## 主要策略

- 优先把正式功能逻辑映射到已有 CK。
- 对随机初始化、宏展开、生成器样板使用 `IGNORE`。
- 对结构性 wrapper 采用较粗粒度映射。
- 对 Stage2/Stage3 的 hit/miss、refill/writeback、flush/probe 等路径做功能化分组。

## 结论

映射已通过 UCAgent 检查器，可作为规范到 RTL 的追踪证据。
