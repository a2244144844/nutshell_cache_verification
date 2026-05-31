# Cache 基本信息（中文版）

日期：2026-05-31

对应英文文档：`unity_test/Cache_basic_info.md`

## 摘要

本文件是 Cache DUT 的中文对应说明。当前 DUT 为 Picker example Cache RTL，工作区选定源码为 `rtl/dut/Cache.v`，通过 Picker 导出为 Python 可驱动的 `DUTCache`。

## 验证工具链

| 层次 | 工具 |
| --- | --- |
| RTL 导出 | Picker + Verilator |
| 测试语言 | Python |
| 测试运行器 | pytest |
| 功能覆盖率 | `src/utils/cache_coverage.py`、`src/utils/toffee_coverage.py` |
| 翻转覆盖率 | `scripts/collect_coverage_multi.sh`、`scripts/generate_rtl_coverage_html.py` |
| UCAgent 编排 | `configs/ucagent_track1_cache.yaml`、`scripts/run_ucagent_stage.sh` |

## 重点内容

- DUT 边界：聚焦 Cache 模块，不使用完整 NutShell SoC 作为验证对象。
- 接口：CPU request/response、memory request/response、MMIO、coherence probe、flush/empty。
- 工具链：Picker + Verilator + Python/Toffee。
- 约束：当前验证目标为 I-cache 配置下的 Cache 行为。
- 测试规模：37 个测试，行/分支/表达式覆盖 100%，翻转覆盖 88.4%（豁免 3,280：T-A~T-F）。
