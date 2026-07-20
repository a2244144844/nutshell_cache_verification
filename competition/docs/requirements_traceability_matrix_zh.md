# 需求-测试-覆盖追溯矩阵 (RTM)

> **创建日期**: 2026-06-01
> **目的**: 将每个验证需求映射到对应的测试、覆盖组和验证状态。
> **格式**: 需求 → 测试 → 覆盖组 → 状态

---

## 需求 → 覆盖矩阵

### R1: 基本读写功能

| 属性 | 详情 |
|-----------|--------|
| **需求** | Cache 必须正确处理冷缓存上的基本读写操作。 |
| **RTL 源码** | `Cache.v`: Stage1 (请求解码), Stage2 (SRAM 访问), Stage3 (响应/refill) |
| **定向测试** | `test_cache_basic.py` |
| **Corner 测试** | — |
| **随机测试** | `test_random_cache.py`, `test_random_multi_seed.py` |
| **覆盖组** | `cache_cmd_type`, `cache_hit_miss`, `cache_req_accepted` |
| **状态** | ✅ 100% |

---

### R2: 写掩码粒度

| 属性 | 详情 |
|-----------|--------|
| **需求** | 64 位写入必须支持字节级掩码（8 位 wmask）。所有掩码模式必须验证。 |
| **RTL 源码** | `Cache.v`: Stage2 中 `data_write_bus` 生成及 `wmask` |
| **定向测试** | `test_write_masks.py` |
| **Corner 测试** | — |
| **随机测试** | `test_random_cache.py` |
| **覆盖组** | `cache_write_mask_class` (7 bins: none/byte/adjacent/low_half/high_half/full/sparse) |
| **状态** | ✅ 100% |

---

### R3: Word Offset 处理

| 属性 | 详情 |
|-----------|--------|
| **需求** | 读写必须正确处理 64B 缓存行中全部 8 个 word offset。 |
| **RTL 源码** | `Cache.v`: `addr_wordIndex = io_in_req_bits_addr[5:3]` |
| **定向测试** | `test_word_offsets.py` |
| **Corner 测试** | — |
| **随机测试** | `test_random_cache.py` |
| **覆盖组** | `cache_word_offset` (8 bins: 0-7) |
| **状态** | ✅ 100% |

---

### R4: Refill 节拍排序（Critical-Word-First）

| 属性 | 详情 |
|-----------|--------|
| **需求** | Cache 缺失必须按 critical-word-first 顺序 refill 8 拍：第一拍 = 请求的 word，后续循环绕回。 |
| **RTL 源码** | `Cache.v`: Stage2 中 `refillBeatCnt` 状态机 |
| **定向测试** | `test_refill_beats.py`, `test_read_burst_hit.py` |
| **Corner 测试** | — |
| **随机测试** | `test_random_cache.py` |
| **覆盖组** | `cache_refill_path` (4 bins: read_burst/read_last/writeback/refill) |
| **状态** | ✅ 100% |

---

### R5: Cache 替换（LFSR）

| 属性 | 详情 |
|-----------|--------|
| **需求** | 当某 set 的 4 个 way 全部占用时，新的 cache miss 必须选择一个 victim way 将其驱逐。 |
| **RTL 源码** | `Cache.v`: `replace_way` 中基于 LFSR 的替换 |
| **定向测试** | `test_invalid_way_replacement.py`, `test_clean_eviction.py` |
| **Corner 测试** | — |
| **随机测试** | — |
| **覆盖组** | `cache_clean_eviction` (1 bin: clean_eviction_detected) |
| **状态** | ✅ 100% |

---

### R6: Dirty Writeback 驱逐

| 属性 | 详情 |
|-----------|--------|
| **需求** | 当 dirty 缓存行被驱逐时，在 refill 新行之前必须先将脏数据写回内存。写回地址必须匹配 victim 地址。 |
| **RTL 源码** | `Cache.v`: dirty writeback 状态机 (`WRITE_BURST` → `WRITE_LAST`) |
| **定向测试** | `test_dirty_writeback.py`, `test_write_miss_dirty_eviction.py` |
| **Corner 测试** | — |
| **随机测试** | — |
| **覆盖组** | `cache_write_miss` (3 bins: none/clean/dirty), `cache_miss_x_addr_type` |
| **Scoreboard** | `check_dirty_writeback_refill()` — 多事务 writeback-before-refill 验证 |
| **状态** | ✅ 100% |

---

### R7: MMIO 地址绕过

| 属性 | 详情 |
|-----------|--------|
| **需求** | MMIO 地址（addr ≥ `0x4000_0000`）必须完全绕过 Cache — 不填充 cache line，不标记 dirty。 |
| **RTL 源码** | `Cache.v`: 地址解码时的 MMIO 检测 |
| **定向测试** | `test_mmio_bypass.py` |
| **Corner 测试** | — |
| **随机测试** | — |
| **覆盖组** | `cache_addr_class` (2 bins: normal/mmio) |
| **状态** | ✅ 100% |

---

### R8: Write Miss 处理

| 属性 | 详情 |
|-----------|--------|
| **需求** | 写入一个不在缓存中的 cache line 时，必须先 refill（读 burst），然后将写数据合并到填充后的行。 |
| **RTL 源码** | `Cache.v`: write miss 路径 — refill 先，write hit 后 |
| **定向测试** | `test_write_miss.py` |
| **Corner 测试** | — |
| **随机测试** | — |
| **覆盖组** | `cache_write_miss`, `cache_write_hit_x_wmask` (48 bins) |
| **状态** | ✅ 100% |

---

### R9: 一致性探针

| 属性 | 详情 |
|-----------|--------|
| **需求** | 外部一致性探针必须返回 hit/miss 状态。Probe hit 时数据必须正确。探针不能破坏缓存状态。 |
| **RTL 源码** | `Cache.v`: `io_out_coh_req` / `io_out_coh_resp` 端口 |
| **定向测试** | `test_coherence_probe.py` |
| **Corner 测试** | — |
| **随机测试** | — |
| **覆盖组** | `cache_coherence_probe` (2 bins: probe_hit/probe_miss), `cache_probe_x_cache_state` (5 bins: hit/miss × empty/valid/dirty) |
| **Scoreboard** | 探针响应命令检查 (`0xc` = hit, `0x8` = miss) |
| **状态** | ✅ 100% |

---

### R10: 流水线反压

| 属性 | 详情 |
|-----------|--------|
| **需求** | Cache 必须正确处理 CPU 端（请求未接受）和内存端（响应未就绪）的反压。 |
| **RTL 源码** | `Cache.v`: `io_in_req_ready` / `io_out_mem_req_ready` 握手信号 |
| **定向测试** | — |
| **Corner 测试** | `test_backpressure.py` |
| **随机测试** | — |
| **覆盖组** | `cache_backpressure` (2 bins: cpu_resp/mem_req) |
| **状态** | ✅ 100% |

---

### R11: Cache Flush

| 属性 | 详情 |
|-----------|--------|
| **需求** | Flush 信号必须使所有 cache line 无效化。Post-flush 读取必须产生 cache miss（冷启动状态）。 |
| **RTL 源码** | `Cache.v`: flush 流水线清除 |
| **定向测试** | `test_flush_behavior.py` |
| **Corner 测试** | — |
| **随机测试** | — |
| **覆盖组** | `cache_flush` (2 bins: idle/after_accept) |
| **状态** | ✅ 100% |

---

### R12: PREFETCH 指令（I-Cache 专有）

| 属性 | 详情 |
|-----------|--------|
| **需求** | PREFETCH 指令不应引起写回或 dirty line 损坏。 |
| **RTL 源码** | `Cache.v`: PREFETCH 解码 case — 抑制 store/fill 行为 |
| **定向测试** | `test_prefetch.py` |
| **Corner 测试** | — |
| **随机测试** | — |
| **覆盖组** | `cache_cmd_type` (3 bins: read/write/prefetch) |
| **状态** | ✅ 100% |

---

### R13: Bug 注入检测

| 属性 | 详情 |
|-----------|--------|
| **需求** | 验证环境必须检测注入的故障 — 证明 scoreboard 能捕获真实设计错误。 |
| **RTL 源码** | N/A (故障注入框架) |
| **定向测试** | — |
| **Bug 注入测试** | `bug_003_address_corruption.py`, `bug_004_dirty_bit_loss.py`, `bug_005_refill_scramble.py`, `bug_006_race_condition.py` |
| **Bug 恢复** | `run_bug_injection.py` (--disable-bug 模式确认无误报) |
| **覆盖组** | N/A (正确性验证，非覆盖率) |
| **状态** | ✅ 全部 6 种 bug 已检测；全部可通过 --disable-bug 恢复 |

---

## 交叉引用索引

### 测试 → 覆盖 映射

| 测试文件 | 涉及的覆盖组 |
|-----------|------------------------|
| `test_cache_basic.py` | cmd_type, hit_miss, req_accepted, word_offset |
| `test_write_masks.py` | write_mask_class |
| `test_word_offsets.py` | word_offset |
| `test_refill_beats.py` | refill_path, word_offset |
| `test_read_burst_hit.py` | refill_path, hit_miss |
| `test_invalid_way_replacement.py` | clean_eviction |
| `test_clean_eviction.py` | clean_eviction |
| `test_dirty_writeback.py` | write_miss, miss_x_addr_type |
| `test_write_miss.py` | write_miss, write_hit_x_wmask |
| `test_write_miss_dirty_eviction.py` | write_miss, miss_x_addr_type |
| `test_write_hit_wmask.py` | write_hit_x_wmask (48/48) |
| `test_mmio_bypass.py` | addr_class |
| `test_coherence_probe.py` | coherence_probe, probe_x_cache_state |
| `test_flush_behavior.py` | flush |
| `test_prefetch.py` | cmd_type |
| `test_backpressure.py` | backpressure |
| `test_random_cache.py` | cmd_type, hit_miss, write_mask_class, word_offset, refill_path (探索性) |

### 覆盖 → 测试 映射

| 覆盖组 | Bins | 主要测试 |
|----------------|------|-----------------|
| `cache_cmd_type` | 3 | `test_cache_basic.py`, `test_prefetch.py`, random |
| `cache_hit_miss` | 2 | `test_cache_basic.py`, `test_read_burst_hit.py`, random |
| `cache_write_mask_class` | 7 | `test_write_masks.py`, random |
| `cache_addr_class` | 2 | `test_mmio_bypass.py` |
| `cache_refill_path` | 4 | `test_refill_beats.py`, random |
| `cache_backpressure` | 2 | `test_backpressure.py` |
| `cache_req_accepted` | 1 | `test_cache_basic.py` |
| `cache_coherence_probe` | 2 | `test_coherence_probe.py` |
| `cache_write_miss` | 3 | `test_write_miss.py`, `test_dirty_writeback.py` |
| `cache_clean_eviction` | 1 | `test_invalid_way_replacement.py`, `test_clean_eviction.py` |
| `cache_flush` | 2 | `test_flush_behavior.py` |
| `cache_word_offset` | 8 | `test_word_offsets.py`, random |
| `cache_write_hit_x_wmask` | 48 | `test_write_hit_wmask.py` |
| `cache_miss_x_addr_type` | 3 | `test_dirty_writeback.py`, `test_write_miss_dirty_eviction.py` |
| `cache_probe_x_cache_state` | 5 | `test_coherence_probe.py` |
| `cache_req_tracker` | 2 | (状态采集 — 所有测试) |
| `cache_write_tracker` | 2 | (状态采集 — 所有写测试) |
| `cache_probe_tracker` | 1 | (状态采集 — probe 测试) |

---

## 验证完备性摘要

| 指标 | 数值 |
|--------|-------|
| 功能需求 | 13 (R1-R13) |
| 定向测试 | 15 文件, 81 个测试函数 |
| Corner 测试 | 1 文件, 2 个测试函数 |
| 随机测试 | 2 文件 (单 seed + 多 seed) |
| Bug 注入场景 | 4 种 (+ 2 遗留: ref-model 损坏 + RTL 绕过) |
| 功能覆盖组 | 18 (15 真实 + 3 tracker) |
| 功能覆盖点 | 91 |
| 功能覆盖仓 | 98 |
| 功能覆盖率 | **100%** |
| 行覆盖率 (RTL) | **100%** |
| 分支覆盖率 (RTL) | **100%** |
| 表达式覆盖率 (RTL) | **100%** |
| 翻转覆盖率 | 88.4% (3,280 豁免) |
| 无覆盖缺口的需求 | 13/13 |
