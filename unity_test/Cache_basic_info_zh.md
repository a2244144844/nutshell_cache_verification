# Cache 基本信息

日期：2026-05-28

对应英文文档：`unity_test/Cache_basic_info.md`

## 摘要

本文件是 Cache DUT 的中文对应说明。当前 DUT 为 Picker example Cache RTL，工作区选定源码为 `rtl/dut/Cache.v`，通过 Picker 导出为 Python 可驱动的 `DUTCache`。

## 重点内容

- DUT 边界：聚焦 Cache 模块，不使用完整 NutShell SoC 作为验证对象。
- 接口：CPU request/response、memory request/response、MMIO、coherence probe、flush/empty。
- 工具链：Picker + Verilator + Python/Toffee。
- 约束：当前验证目标为 I-cache 配置下的 Cache 行为。
