# Cache 覆盖率分析（中文版）

日期：2026-05-31

对应英文文档：`unity_test/Cache_line_coverage_analysis.md`

## 最终覆盖率状态

- Toffee 功能覆盖率：12 groups / 31 points / 37 bins, 100%。
- **RTL 行覆盖率：1359/1359 (100.0%)** — Stage 11 闭环。
- **RTL 分支覆盖率：471/471 (100.0%)** — Stage 12 闭环。
- **RTL 翻转覆盖率：24947/28227 (88.4%)** — Stage 17 最终平台（Stage 13 提升至 87.8%，Stage 17 提升至 88.4%）。

## 豁免总结

| 维度 | 豁免数量 | 依据文档 |
| --- | --- | --- |
| 行/分支 | 42 行（Categories A-N） | `docs/coverage_waiver_rationale.md` |
| 翻转 | 3280 翻转位（Categories T-A–T-F，文档化方式） | `docs/toggle_coverage_waiver.md` |

主要豁免类别：
- Categories A, E：`$fwrite` 断言失败消息 — 设计上不可达
- Categories B, G, J：D-cache 专用信号 — I-cache 配置下结构不可达
- Category D：`io_flush[1]` pipeline kill — D-cache 断言阻断
- Category F：LFSR 全零死锁态 — 无破坏不可达
- Categories H, I, K, L, M, N：额外豁免 — 结构不可达或假路径

## 覆盖闭环时间线

- Stage 9 (`line_coverage_closure`)：DIR-014/015/016 → 行覆盖 99.6%
- Stage 11 (`line_coverage_100`)：DIR-017 (needFlush)、DIR-018 (respToL1Last) → 行覆盖 100.0%
- Stage 12 (`branch_coverage_closure`)：DIR-019 (PREFETCH)、DIR-020 (writeback counters)、DIR-021 (internal probe)、DIR-022 (state2) → 分支覆盖 100.0%
- Stage 13 (`toggle_coverage_improvement`)：多种子随机流量 → 翻转覆盖 87.8%

所有行与分支在豁免应用后均已覆盖。翻转覆盖率已达到当前验证目标上限，剩余未翻转位均记录在豁免文档中。
