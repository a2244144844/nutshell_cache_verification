# Cache 行号到检查点映射

日期：2026-05-31

对应英文文档：`unity_test/Cache_line_func_map.md`

## 说明

该文件是 UCAgent GenSpec `ref_function_line_map_generation` 阶段的中文对应说明。英文文件包含完整 CK 到 `Cache.v` 行号区间映射，以及 Stage 11-13 闭环后的覆盖率豁免 IGNORE 行映射。

## 检查结果

`FileLineMapChecker` 已通过：`Cache/Cache.v` 全部 3046 行均已映射到 CK 或通过 IGNORE 明确标注。IGNORE 分为两类：

1. **生成器/初始化代码**（`FC-GEN-INIT/CK-RANDOM-INIT`）：随机寄存器初始化、FIRRTL 样板代码。
2. **覆盖率豁免行**（`FG-COVERAGE-WAIVER/FC-LINE-WAIVER`）：Categories A-N，涵盖 I-cache 结构不可达的断言消息、D-cache 转发信号、流水线终止位、LFSR 死状态及 DIR-019~022 目标分支。全部 42 行已获豁免。

## 豁免行清单 (Categories A-N)

| Category | 行号 | 数量 | 原因 |
|---|---|---|---|
| A | 263, 877, 901, 925, 949 | 5 | 断言 $fwrite 消息 |
| B | 411, 524, 2267, 2418 | 4 | D-cache 转发信号 |
| D | 558, 788, 2861-2862 | 4 | io_flush[1] + needFlush |
| E | 262 | 1 | CacheStage2 断言 |
| F | 240-241 | 2 | LFSR 死状态 |
| G | 138 | 1 | 转发元数据寄存器 |
| J | 420, 460, 2276, 2316 | 4 | CacheStage3 D-cache 端口 |
| K | 605, 608, 610 | 3 | respToL1Last 计数器 |
| L | 148, 150, 152, 202-207 | 6 | 转发元多路复用器（分支） |
| M | 532, 876, 900, 924, 948 | 5 | D-cache 断言（分支） |
| N | 550, 555, 626, 768, 777, 796, 824, 2674 | 8 | DIR-019~022 目标分支 |
| O | 274, 787, 889, 913, 937, 961 | 6 | Expr SVA 断言/死逻辑条件 |

## 作用

该映射用于证明功能检查点与 RTL 代码之间存在可追溯关系，也是覆盖率闭环和报告审查的依据。豁免行均通过 `docs/coverage_waiver_rationale.md` 和 `tests/conftest.py` 记录并执行。
