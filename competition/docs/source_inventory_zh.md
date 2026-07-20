# 源文件清单

本文记录 Track1 NutShell Cache 验证任务的源材料及各项本地可用状态。

## 本地参考资料

| 项目 | 路径 | 状态 | 备注 |
| --- | --- | --- | --- |
| 赛题要求摘要 | `docs/track1_UCAgent_competition_requirements.md` | 可用 | 定义了 UCAgent/Picker/Toffee 期望、评分、交付物和检查清单。 |
| UCAgent + Codex 操作指南 | `instruction.md` | 可用 | 定义了已验证的本地 UCAgent/Codex MCP 执行路径。 |
| 分步计划 | `step.md` | 可用 | 基于上述两份文件生成本地分阶段计划。 |
| UCAgent 示例 | `examples/` | 可用 | 对于输出风格、文档和面向 Toffee 的测试/报告模式有参考价值。 |
| DCache 示例文档 | `examples/GenSpec/DCache/` | 可用 | XiangShan DCache 材料，非 NutShell Cache DUT，但可作为复杂 cache 分析参考。 |
| 选定 Cache DUT RTL | `rtl/dut/Cache.v` | 可用 | 从 Picker `example/Cache/Cache.v` 复制，为此验证任务选定的 DUT。 |
| 选定 Cache 辅助源文件 | `rtl/dut/Test.v` | 可用 | Picker 的 Cache 示例导出流程使用的额外源文件。 |
| 选定 Cache 信号配置 | `rtl/dut/Cache.yaml` | 可用 | 来自 Picker 的 Cache 示例的内部信号配置。 |

## 上游参考资料

| 项目 | URL / 本地路径 | 状态 | 备注 |
| --- | --- | --- | --- |
| GitLink 赛题环境 | `https://gitlink.org.cn/XS-MLVP/env-xs-ov-00-nutshell-cache.git` / `upstream/env-xs-ov-00-nutshell-cache` | 已克隆 | 包含任务说明和提交模板目录，但不包含 Cache DUT 实现。 |
| NutShell Cache 文档 | `https://oscpu.github.io/NutShell-doc/功能部件/cache.html` | 可访问 | 官方 Cache 文档页面。 |
| NutShell 源码树 | `https://github.com/OSCPU/NutShell` / `upstream/NutShell` | 已下载 | 从 GitHub 归档下载的 Chisel 源码树。 |
| NutShell `difftest` 子模块 | `https://github.com/OpenXiangShan/difftest` / `upstream/NutShell/difftest` | 已下载 | `BOARD=sim` 综合所需；由于 NutShell zip 不含子模块内容，采用归档下载方式。 |
| NutShell Cache 源码 | `upstream/NutShell/src/main/scala/nutcore/mem/Cache.scala` | 本地可用 | `Cache.scala` 的 Chisel 源码；许可证头为 Mulan PSL v2。 |
| Picker Cache 示例 | `tools/picker/example/Cache` | 本地可用 | 选定 DUT 的原始来源；作为上游工具源文件忽略，在 `rtl/dut/` 中保留跟踪副本。 |

## 初步 DUT 观察

从可访问的 `Cache.scala` 源码来看，Cache 设计包含以下主要结构：

- `CacheConfig`：如只读模式、cache 层级、总大小、路数、用户位和 ID 位等参数。
- `CacheIO`：顶层请求/响应、内存、MMIO、flush、finish 和可选的 coherence 响应接口。
- `CacheStage1`：请求接收及 meta/data 数组读取。
- `CacheStage2`：meta/data 响应处理、命中检测、无效路/替换路选择及转发。
- `CacheStage3`：命中响应、缺失处理、内存读取 refill、脏数据写回、MMIO 路径、probe/release 路径及响应生成。

值得验证的重要行为候选：

- 读命中和写命中。
- 读缺失和写缺失。
- 缺失后 refill。
- 脏 victim 在 refill 前写回。
- 替换前优先选择无效路。
- 突发读写路径。
- Flush 处理。
- MMIO 旁路路径。
- 可选的 coherence/probe/release 路径。
- meta/data 写入后的转发。

## 选定 DUT 边界

选定 DUT 为 `rtl/dut/Cache.v`，从 Picker 的 `example/Cache/Cache.v` 复制。

备注：

- 顶层模块：`Cache`。
- Picker 生成的 Python 类：`DUTCache`。
- 可重复执行的导出脚本：`scripts/export_cache_dut.sh`。
- 输出目录：`build/picker_cache`。

OSCPU/NutShell Chisel 构建路径仍作为源码上下文有用，但生成的完整 NutShell RTL 不是选定的 DUT 边界。

## 本地工具探测

于 2026-05-25 检查：

| 工具 / 包 | 状态 | 备注 |
| --- | --- | --- |
| UCAgent | 可用 | `ucagent --version` 报告 `0.9.2.dev1+geda2d0d7d`。 |
| Codex CLI | 可用 | `codex --version` 报告 `0.131.0-alpha.9`。 |
| pytoffee | 可用 | Python 包 `pytoffee` 已安装。 |
| toffee-test | 可用 | Python 包 `toffee-test` 已安装。 |
| pytest | 可用 | Python 包可导入。 |
| Verilator | 可用 | `/opt/homebrew/bin/verilator`，版本 `5.046`。 |
| Picker CLI | 本地可用 | 从源码安装于 `competition/local/picker`；参见 `docs/picker_installation.md`。 |
| Java 运行时 | 本地可用 | Azul Zulu JRE `17.0.19` 安装于 `competition/local/jre17`。 |
| Mill | 本地可用 | Mill `0.11.7` 安装于 `competition/local/mill/bin/mill`，匹配 NutShell `.mill-version`。 |

Picker 验证：

- `picker --version` 报告 `0.9.0-master-301c403-2026-05-12-dirty`。
- `picker --check` 报告 C++ 和 Python 支持正常。
- `.venv` 可从本地 Picker 安装导入 `xspcomm`。
- `picker export` 在 `examples/Adder/Adder.v` 上通过 smoke 测试；生成的 Python DUT 输出 `1 + 2 = 3`。

NutShell 构建验证：

- `mill -i generator.test.runMain top.TopMain --target-dir build/rtl BOARD=sim CORE=inorder --split-verilog` 完成。
- 生成的 RTL 位于 `upstream/NutShell/build/rtl`。
- Cache 相关生成模块包括 `Cache.sv`、`Cache_1.sv`、`Cache_2.sv` 及对应的 `CacheStage1/2/3` 变体。

选定 DUT 导出验证：

- `scripts/export_cache_dut.sh` 完成。
- 虚拟环境存在时生成的 wrapper 使用 `.venv` Python 3.11。
- `DUTCache` 可从 Python 实例化、步进和结束。
