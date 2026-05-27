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
