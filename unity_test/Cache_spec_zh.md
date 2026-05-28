# Cache 主规范

日期：2026-05-28

对应英文文档：`unity_test/Cache_spec.md`

## 说明

该文档是 UCAgent GenSpec 根据 `Cache.v` 和既有项目文档生成的主规范。英文文件保留完整 RTL 分析细节；本中文对应文件记录最新状态和阅读入口。

## 覆盖内容

- DUT 背景与 Cache 在 NutShell/RISC-V SoC 中的角色。
- SimpleBus、cache line、way、set、refill、writeback 等术语。
- 顶层端口和 ready/valid 协议。
- CacheStage1/2/3 的流水职责。
- Stage3 FSM、MMIO bypass、flush、coherence probe。
- MetaDataArray/DataArray 和 replacement 行为。
- 验证需求与潜在 bug 风险。

## 状态

GenSpec 主规范已生成，并已进入后续 FG/FC/CK 分析和 line map 阶段。
