# NutShell 构建探索

日期：2026-05-25

本文档记录为 Track1 Cache 验证任务探索的本地 NutShell/Chisel 构建闭环。此构建作源码上下文参考有用，但不是选定的 DUT 边界。选定的 DUT 记录在 `docs/dut_selection.md`。

## 本地工具链

| 工具 | 位置 | 结果 |
| --- | --- | --- |
| Java 运行时 | `local/jre17` | Azul Zulu JRE `17.0.19`；`java -version` 通过。 |
| Mill | `local/mill/bin/mill` | NutShell 所需的 Mill `0.11.7`；`mill --version` 通过。 |
| Picker | `local/picker/bin/picker` | Picker `0.9.0...`；C++ 和 Python 支持通过。 |

使用以下命令加载环境：

```sh
source competition/track1_nutshell_cache/scripts/env.sh
```

环境脚本导出 `JAVA_HOME`、`MILL_HOME`、`PICKER_HOME`、`NOOP_HOME`、`PATH` 和 `PYTHONPATH`。

可重复的 RTL 构建脚本：

```sh
competition/track1_nutshell_cache/scripts/build_nutshell_rtl.sh
```

## 源码闭环

NutShell 下载至：

```text
competition/track1_nutshell_cache/upstream/NutShell
```

下载的归档不含 `difftest` 子模块，因此下载了 `OpenXiangShan/difftest` 并放置于：

```text
competition/track1_nutshell_cache/upstream/NutShell/difftest
```

没有这个子模块，Chisel 编译会在 `difftest.common.DifftestMem`、`UARTIO` 及相关符号上报缺。

## RTL 生成

命令：

```sh
source /Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/scripts/env.sh
cd /Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/upstream/NutShell
mill -i generator.test.runMain top.TopMain --target-dir build/rtl BOARD=sim CORE=inorder --split-verilog
```

结果：

- Scala/Chisel 综合完成。
- 若干动态索引宽度产生警告；无致命综合错误残留。
- 生成 RTL 目录：`upstream/NutShell/build/rtl`
- 生成 difftest C/C++ 侧文件：`upstream/NutShell/build/generated-src`

## Cache RTL 文件

生成的 Cache 相关模块：

```text
Cache.sv
Cache_1.sv
Cache_2.sv
CacheStage1.sv
CacheStage1_1.sv
CacheStage1_2.sv
CacheStage2.sv
CacheStage2_1.sv
CacheStage2_2.sv
CacheStage3.sv
CacheStage3_1.sv
CacheStage3_2.sv
```

后缀对应为实例化的 icache、dcache 和 l2cache 配置生成的 Chisel 特化变体。

## 结论

此构建路径为探索性质。在检查 Picker 的 `example/Cache` 目录后，选定的 DUT 边界被修正为 `rtl/dut/Cache.v`，从 `tools/picker/example/Cache/Cache.v` 复制。
