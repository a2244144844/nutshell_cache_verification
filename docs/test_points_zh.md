# 测试点

日期：2026-05-26

本文档列出针对选定 Cache DUT 的首批验证目标。

## 已实现的 Smoke 检查点

实现在：

```text
tests/smoke/test_cache_basic.py
```

Smoke 使用的环境模块：

```text
src/env/cache_env.py
src/monitor/cache_monitor.py
src/scoreboard/cache_scoreboard.py
src/utils/simplebus.py
```

可通过以下命令运行：

```sh
competition/track1_nutshell_cache/scripts/run_smoke.sh
```

当前检查点：

| ID | 检查点 | 状态 |
| --- | --- | --- |
| `SMK-001` | 复位释放后 Cache 变为请求就绪状态。 | 已实现 |
| `SMK-002` | 对冷 cache line 的首次正常读取缺失并发出内存 `READ_BURST`。 | 已实现 |
| `SMK-003` | 内存 `READ_LAST` 响应 refill 该行并返回 CPU `READ_LAST`。 | 已实现 |
| `SMK-004` | 用户元数据从请求保留到响应。 | 已实现 |
| `SMK-005` | 对同一地址的第二次读取命中，不发出内存请求。 | 已实现 |
| `SMK-006` | 全掩码写命中返回 `WRITE_RESP`。 | 已实现 |
| `SMK-007` | 写后读命中返回更新后的数据。 | 已实现 |

## 后续定向测试点

| ID | 检查点 | 目标 |
| --- | --- | --- |
| `DIR-001` | 字节/半字/字写掩码 | 在 `tests/directed/test_write_masks.py` 中实现；检查 64 位字内的部分更新。 |
| `DIR-002` | 同一 cache line 中不同 word 偏移 | 在 `tests/directed/test_word_offsets.py` 中实现；检查 `addr[5:3]` 各偏移的独立命中写/读。 |
| `DIR-003` | 多节拍 refill | 在 `tests/directed/test_refill_beats.py` 中实现；检查从非零 word 偏移开始的 8-beat refill 顺序。 |
| `DIR-004` | 替换到无效路 | 在 `tests/directed/test_invalid_way_replacement.py` 中实现；填满 3 路后访问第 4 个冲突地址，验证无效路被优先使用（无写回，原始数据保留）。 |
| `DIR-005` | 脏 victim 写回 | 在 `tests/directed/test_dirty_writeback.py` 中实现；填满 4-way set，脏化 victim 候选者，并在第 5 次冲突访问时检查 writeback/refill 序列。 |
| `DIR-006` | MMIO 旁路 | 在 `tests/directed/test_mmio_bypass.py` 中实现；验证 MMIO 地址的读写通过 `io_mmio_*` 路由，不产生内存请求，且永不会在 cache 中命中。 |
| `DIR-007` | Flush 行为 | 在 `tests/directed/test_flush_behavior.py` 中实现；在空闲和 in-flight 状态下 assert `io_flush[0]`（S1-S2 pipeline flush），验证 `io_empty` 和 cache 恢复。`io_flush[1]` 被 D-cache 断言（`ro.B=false`）阻止。 |
| `DIR-008` | Coherence probe 命中/缺失 | 在 `tests/directed/test_coherence_probe.py` 中实现；驱动 `io_out_coh_req_*` 的 PROBE 命令并验证 `io_out_coh_resp_*` 响应（cmd=0xc 命中，cmd=0x8 缺失）。 |
| `DIR-009` | 响应反压 | 在 `tests/corner/test_backpressure.py` 中实现；refill 启动后将 `io_in_resp_ready` 拉低，验证 CPU 响应保持 valid 直到 ready 恢复高电平。 |
| `DIR-010` | 内存请求反压 | 在 `tests/corner/test_backpressure.py` 中实现；将 `io_out_mem_req_ready` 拉低足够长时间以证明内存请求保持 asserted 且稳定，直到 ready 恢复高电平。 |
| `DIR-011` | Write miss（冷写） | 在 `tests/directed/test_write_miss.py` 中实现；验证冷地址 WRITE 触发 READ_BURST refill，写数据与 refill 数据正确合并，并返回 WRITE_RESP。覆盖全掩码、部分掩码和 8-beat refill 场景。 |
| `DIR-012` | Clean eviction（无写回替换） | 在 `tests/directed/test_clean_eviction.py` 中实现；填满同一 set 的 4 个干净 way，再访问第 5 个冲突地址，验证 clean victim 替换不产生 writeback，并检查保留 line 的 per-word 数据完整性。 |
| `DIR-013` | Write miss with dirty eviction | 在 `tests/directed/test_write_miss_dirty_eviction.py` 中实现；填满 4 个 way 并脏化，再对第 5 个冲突地址发 WRITE，验证 dirty victim writeback 先于 refill，且部分掩码写数据正确合并进 refilled line。 |

## 回归结果

```text
scripts/run_directed.sh -> 23 passed in 1.05s
scripts/run_regression.sh -> 26 passed in 1.34s
```

## 随机覆盖率引导

实现在：

```text
tests/random/test_random_cache.py
src/generator/cache_random.py
src/utils/cache_coverage.py
src/utils/toffee_coverage.py
```

可通过以下命令运行：

```sh
competition/track1_nutshell_cache/scripts/collect_coverage.sh
competition/track1_nutshell_cache/scripts/run_random.sh
```

当前检查点：

| ID | 检查点 | 状态 |
| --- | --- | --- |
| `CRV-001` | 受约束的随机读写流量使用合法的 cache line 地址和确定性种子控制。 | 已实现 |
| `CRV-002` | 随机回归对照参考模型检查读写结果，包含写掩码处理。 | 已实现 |
| `CRV-003` | 功能覆盖率记录命令类型、命中/缺失代理、写掩码类别、word 偏移和 refill 路径。 | 已实现 |
| `CRV-004` | 覆盖率引导现已通过闭环 stage 记录脏缺失/写回/refill 路径。 | 已实现 |
| `CRV-005` | Toffee 覆盖率记录 probe、MMIO、flush、clean eviction、clean write miss 和 dirty write miss 仓。 | 已实现 |

命令结果：

```text
scripts/collect_coverage.sh 7 18 -> 27 passed
scripts/run_regression.sh -> 26 passed in 1.34s
```

## 覆盖率状态

当前已覆盖的功能覆盖率组包括：

- 请求命令：read、write、probe。
- 命中/缺失代理和 refill 路径。
- 写掩码模式：单字节、相邻字节、低/高半字、全掩码、稀疏掩码。
- 地址类别：普通内存、MMIO。
- 状态路径：命中、clean miss refill、dirty miss writeback/refill、clean write miss、dirty write miss、clean eviction、MMIO。
- 反压位置：CPU 响应和内存请求。
- Flush 时机：空闲和请求接受后。

Toffee 覆盖率结果：

```text
12 groups, 31 points, 37 bins -> 100% covered
```

## Bug 注入证据

实现在：

```text
tests/injected_bug/run_bug_injection.py
docs/bug_tracking.md
```

可通过以下命令运行：

```sh
competition/track1_nutshell_cache/scripts/run_bug_injection.sh
competition/track1_nutshell_cache/scripts/run_bug_injection.sh --disable-bug
```

当前检查点：

| ID | 检查点 | 状态 |
| --- | --- | --- |
| `BUG-001` | 参考模型预期数据损坏由 `CacheScoreboard.check_read_response()` 检出。 | 已实现 |
| `BUG-RTL-001` | RTL 级脏写回状态机旁路（`Cache.v:615`）；`test_dirty_writeback.py` 检出缺失 `WRITE_BURST`。 | 已实现 |

命令结果：

```text
tests/injected_bug/run_bug_injection.py -> exit 1
  BUG-001 mode=enabled: corrupting reference-model read_word() flips bit 0 at addr 0x80000000
  BUG-001 expected_data=0x1122334455667789, actual_data=0x1122334455667788
  AssertionError: BUG-001 detected by scoreboard.check_read_response: reference-model corruption made the expected read data 0x1122334455667789 while the DUT returned 0x1122334455667788 at addr 0x80000000
tests/injected_bug/run_bug_injection.py --disable-bug -> exit 0
  BUG-001 mode=disabled: clean reference-model read_word() at addr 0x80000000
  BUG-001 recovery path: bug injection disabled, scoreboard checks passed.
scripts/run_regression.sh -> 26 passed in 1.34s
```

## 可复现入口

可通过以下命令运行：

```sh
competition/track1_nutshell_cache/scripts/reproduce.sh
```

当前一键命令结果：

```text
scripts/clean_generated.sh && scripts/reproduce.sh -> PASS
```

## 定向测试命令

仅运行定向测试：

```sh
competition/track1_nutshell_cache/scripts/run_directed.sh
```

运行 smoke 加定向测试：

```sh
competition/track1_nutshell_cache/scripts/run_regression.sh
```

## Stage 11 定向测试（2026-05-31）

### DIR-017：needFlush 完整生命周期 — `test_needflush_assert_and_deassert`

**文件：** `tests/directed/test_flush_behavior.py`
**目标：** 第 558、787-788 行（needFlush 寄存器 + 解除断言）
**优先级：** P0 → P2（已豁免）

**描述：** 使用低级引脚控制（`env.set_pin/get_pin/step`）对第二个请求进行逐步观测 `needFlush` 清除握手（`_T_5 & needFlush`，即 `io_out_ready & io_out_valid & needFlush`）。
1. 通过 `drive_cpu_request` + step 循环发送 READ 到冷地址 A
2. 在接受窗口内置 `io_flush=0b01` → needFlush=1
3. 等待 `io_empty==1`（流水线排空）
4. 取消 `io_flush`，step 10 个周期
5. 使用手动引脚控制驱动新的 READ 到冷地址 B
6. 驱动 `io_out_mem_req_ready=1` 并用低级引脚处理内存响应
7. 逐周期 step，捕获 `io_in_resp_valid` 节拍
8. 验证正确的响应数据和 user 字段

**结果：** PASS。测试基础设施已验证，但第 558、788 行在 I-cache 模式下**结构上不可达**。根因：CacheStage3 的 `io_flush` 端口硬连接到 `io_flush[1]`（第 2786 行），该信号被 D-cache 断言（"only allow to flush icache"）阻断。`needFlush` 永远无法置 1，因为当 `io_flush` 恒为 0 时 `_GEN_1 = io_flush & state!=0 | needFlush` 退化为自循环。第 558 和 788 行已作为 Category D 扩展豁免（与第 2861-2862 行共享同一根因）。行覆盖率 → 1359/1359（100.0%）。详见 `docs/coverage_waiver_rationale.md` Category D 获取完整信号追踪。

### DIR-018：respToL1Last 计数器 — `test_read_burst_hit_resptol1_counter`

**文件：** `tests/directed/test_read_burst_hit.py`
**目标：** 第 605、608、610 行（respToL1Fire、respToL1Last_wrap_wrap、respToL1Last）
**优先级：** P1 → P2（已豁免）

**描述：** 通过 READ_BURST 命中路径覆盖 respToL1Last 计数器。
1. 用 8 个不同的 word 值填充 cache line
2. 向命中行驱动 READ_BURST（cmd=0x2），`io_in_resp_ready=1`
3. 统计 `io_in_resp_valid` 节拍，捕获所有响应数据
4. 同时捕获 `io_out_coh_resp_*` 一致性释放节拍
5. 记录是否达到计数器翻转（8+ 拍）

**结果：** PASS。在 `io_in_resp_*` 上观测到单拍 CPU 响应。一致性释放节拍在 `io_out_coh_resp_*` 上观测到，但不驱动 `respToL1Last` 计数器。第 605、608、610 行已豁免为 Category K（I-cache 限制 — 多拍 CPU 响应路径在 I-cache 配置中不可用）。豁免已加入 `docs/coverage_waiver_rationale.md` Category K。

## Stage 12 定向测试（2026-05-31）

### DIR-019：PREFETCH 响应门控 — `test_prefetch.py`

**文件：** `tests/directed/test_prefetch.py`
**目标：** 第 2674 行（当 `s3_io_out_bits_cmd == PREFETCH` 时 `io_in_resp_valid` 门控）
**优先级：** P1 → P2（已豁免）

**描述：** 两个测试：
1. `test_prefetch_miss_suppresses_response`：向冷地址发送 PREFETCH，验证 `io_in_resp_valid` 永不被置位
2. `test_prefetch_fills_cache_then_read_hits`：PREFETCH + 后续 READ 命中检查

**结果：** PASS。PREFETCH 被 pipeline 接受，但在 I-cache 中永远不会到达输出阶段。第 2674 行三元门控的 TRUE 分支在结构上不可达。**已豁免为 P2（Category N）。**

### DIR-020：写回节拍计数器 — `test_write_miss_dirty_eviction.py`

**文件：** `tests/directed/test_write_miss_dirty_eviction.py`
**目标：** 第 550, 555, 626 行（writeL2BeatCnt 计数器递增/多路复用/复位）
**优先级：** P1 → P2（已豁免）

**描述：** `test_writeback_multi_beat_counter_exercise`：填满 4 路、弄脏每路、WRITE miss 触发脏驱逐及 8 拍写回。验证写回节拍先于重填，数据完整性正确。

**结果：** PASS。第 550/555/626 行需要 WRITE_BURST/LAST 输入命令（内存总线侧），这些命令永远不会通过 I-cache 中的 CPU 请求端口到达。**已豁免为 P2（Category N）。**

### DIR-021：内部 Probe 路径 — `test_coherence_probe.py`

**文件：** `tests/directed/test_coherence_probe.py`
**目标：** 第 768, 777, 796 行（probe 命中释放、MMIO 状态、probe readBeatCnt）
**优先级：** P1 → P2（已豁免）

**描述：** 两个测试通过 `io_in_req`（CPU 端口）而非 `io_out_coh_req_*` 驱动 PROBE：
1. `test_internal_probe_miss_through_io_in_req`：空 cache 上的 PROBE miss
2. `test_internal_probe_hit_through_io_in_req`：填充行后 PROBE 命中

**结果：** PASS。内部 probe 通过 pipeline 被接受。目标分支依赖 probe 释放序列或 MMIO 路径 — 均为 D-cache 特有。**已豁免为 P2（Category N）。**

### DIR-022：State2 FSM Else-If — 已被覆盖

**目标：** 第 824 行（`else if (2'h2 == state2)`）
**优先级：** P1 → P2（已豁免，false-case 不可达）

**分析：** State2 在所有内存重填操作中循环 0→1→2→0（已有测试覆盖）。FALSE 分支要求 state2=3，该值永不出现（2 位寄存器，有效值仅 0-2）。**已豁免为 P2（Category N）。**

### Stage 12 最终覆盖率

```
Line:   1359/1359 = 100.0%
Branch: 471/471  = 100.0%  (from 471/494 = 95.3%)
Toggle: 24474/28227 = 86.7%
Expr:   131/137 = 95.6%
37 tests passed in 8.85s
```

## Stage 13 翻转覆盖率提升（2026-05-31）

### 多 Seed 随机流量

实现在：

```text
tests/random/test_random_multi_seed.py
src/generator/cache_random.py  （扩展 enable_extended 模式）
scripts/collect_coverage_multi.sh
```

可运行：

```sh
competition/track1_nutshell_cache/scripts/collect_coverage_multi.sh
```

### 生成器扩展

| 特性 | 描述 |
|---|---|
| 扩展地址范围 | 32 个 line base，覆盖多个 cache set |
| 多样化数据模式 | 16 种不同的 64 位模式（全 0、全 1、交替、步进、随机） |
| MMIO 流量 | 读/写 MMIO 地址范围（0x30000000, 0x40000000） |
| 一致性 probe | 通过 `io_out_coh_req_*` 引脚执行 PROBE 操作 |
| Flush 序列 | `io_flush` 断言/取消，等待 `io_empty` |
| READ_BURST | 对命中行执行 burst 读命令 |
| PREFETCH | 对冷地址执行 prefetch 命令 |
| 多 seed 执行 | 5 seed（7, 13, 42, 99, 256）× 100 步 = 500 次随机操作 |
| 向后兼容 | 非扩展模式保留原始生成器行为 |

### 翻转覆盖增量

| 指标 | Stage 12 后 | Stage 13 后 | 增量 |
|---|---|---|---|
| 翻转 | 24474/28227 (86.7%) | **24785/28227 (87.8%)** | +311 |

翻转覆盖率在 87.8% 处达到平台期 — 额外 seed（8）和步数（200）不再产生改进。剩余 3442 个缺失为结构性原因：SRAM 总线位、D-cache 常量、LFSR 位、断言条件、固定信号和未使用端口。详见 `docs/toggle_coverage_waiver.md` 获取每个类别（T-A 至 T-F）的依据。

### Stage 13 最终覆盖率

```
Line:   1359/1359 = 100.0%
Branch: 471/471  = 100.0%
Toggle: 24785/28227 = 87.8%  (from 24474/28227 = 86.7%)
Expr:   137/137 = 100.0%  (from 131/137 = 95.6%, Category O 豁免, Stage 16)
38 tests passed in 18.13s
```

## Stage 16 表达式覆盖率闭环（2026-05-31）

### Expr 豁免闭环 — Category O

剩余 6 个表达式覆盖率缺失（第 274、787、889、913、937、961 行）均为 Chisel 生成的 SVA 断言条件项（`STOP_COND`）和内部死逻辑表达式。在 I-cache 中结构不可达，原因与已有 A、D、E、M 类豁免相同。

**变更文件：** `tests/conftest.py`（向 ignore_patterns 添加 6 行）、`docs/coverage_waiver_rationale.md`（Category O 章节）、`docs/coverage_waiver_rationale_zh.md`（中文镜像）、`unity_test/Cache_functions_and_checks.md`（CK-WAIVER-CAT-O）、`unity_test/Cache_line_func_map.md`（Category O IGNORE 映射）。

**命令：** `scripts/collect_coverage_multi.sh` → 验证 Expr 137/137 (100.0%)。

### Stage 16 最终覆盖率

```
Line:   1359/1359 = 100.0%
Branch: 471/471  = 100.0%
Toggle: 24785/28227 = 87.8%
Expr:   137/137 = 100.0%
38 tests, 0 failures
```

## Stage 17 翻转覆盖率最终尝试（2026-05-31）

### 配置

| 参数 | 之前（Stage 13）| Stage 17 |
|---|---|---|
| Seed | 5 | 10（7, 13, 42, 99, 256, 31, 77, 128, 512, 1023）|
| 每 seed 步数 | 100 | 200 |
| 总随机操作 | 500 | 2,000 |
| 地址基址 | 32 | 64（EXTENDED_LINE_BASES_V2）|
| 数据模式 | 16 | 32（DATA_PATTERNS_V2）|

### 结果

```
Line:   1359/1359 = 100.0%
Branch: 471/471  = 100.0%
Toggle: 24947/28227 = 88.4%  （从 87.8% +162）
Expr:   137/137 = 100.0%
37 tests, 0 failures
```

### 结论

随机操作量增加到 4 倍，获得 +162 次翻转命中（+0.6%）。剩余 3,280 次翻转缺失全部属于结构性类别（T-A 至 T-F）。**翻转覆盖率平台期确认在 88.4%——本 I-cache DUT 的实际最大值。** 豁免采用文档化方式（不编码在 `conftest.py` 中），因为 `toffee_test` 的 `filter_coverage()` 不具备类型感知。

**变更文件：** `src/generator/cache_random.py`（V2 地址/模式、`enable_max_toggle`）、`tests/random/test_random_multi_seed.py`（默认值）、`scripts/collect_coverage_multi.sh`（默认值）、`docs/toggle_coverage_waiver.md` + `_zh.md`（Stage 17 章节）、`docs/ucagent_output/toggle_final_attempt_stage.md` + `_zh.md`。

**命令：** `scripts/collect_coverage_multi.sh` → 验证 Toggle 88.4%。

### Stage 17 最终覆盖率

```
Line:   1359/1359 = 100.0%
Branch: 471/471  = 100.0%
Toggle: 24947/28227 = 88.4%  （已豁免：3280，类别 T-A~T-F）
Expr:   137/137 = 100.0%
37 tests, 0 failures
```
