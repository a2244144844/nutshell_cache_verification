# Requirements Traceability Matrix (RTM)

> **Created**: 2026-06-01  
> **Purpose**: Map every verification requirement to its corresponding tests, coverage groups, and verification status.  
> **Format**: Requirement → Test(s) → Coverage Group(s) → Status

---

## Requirement → Coverage Matrix

### R1: Basic Read/Write Functionality

| Attribute | Detail |
|-----------|--------|
| **Requirement** | Cache must correctly handle basic read and write operations on a cold cache. |
| **RTL Source** | `Cache.v`: Stage1 (request decode), Stage2 (SRAM access), Stage3 (response/refill) |
| **Directed Test** | `test_cache_basic.py` |
| **Corner Test** | — |
| **Random Test** | `test_random_cache.py`, `test_random_multi_seed.py` |
| **Coverage Groups** | `cache_cmd_type`, `cache_hit_miss`, `cache_req_accepted` |
| **Status** | ✅ 100% |

---

### R2: Write Mask Granularity

| Attribute | Detail |
|-----------|--------|
| **Requirement** | 64-bit write must support byte-level masking (8 bits of wmask). All mask patterns must be verified. |
| **RTL Source** | `Cache.v`: `data_write_bus` generation with `wmask` in Stage2 |
| **Directed Test** | `test_write_masks.py` |
| **Corner Test** | — |
| **Random Test** | `test_random_cache.py` |
| **Coverage Groups** | `cache_write_mask_class` (7 bins: none/byte/adjacent/low_half/high_half/full/sparse) |
| **Status** | ✅ 100% |

---

### R3: Word Offset Handling

| Attribute | Detail |
|-----------|--------|
| **Requirement** | Reads and writes must correctly handle all 8 word offsets within a 64B cache line. |
| **RTL Source** | `Cache.v`: `addr_wordIndex = io_in_req_bits_addr[5:3]` |
| **Directed Test** | `test_word_offsets.py` |
| **Corner Test** | — |
| **Random Test** | `test_random_cache.py` |
| **Coverage Groups** | `cache_word_offset` (8 bins: 0-7) |
| **Status** | ✅ 100% |

---

### R4: Refill Beat Ordering (Critical-Word-First)

| Attribute | Detail |
|-----------|--------|
| **Requirement** | Cache misses must refill 8 beats in critical-word-first order: first beat = requested word, remaining beats wrap around. |
| **RTL Source** | `Cache.v`: `refillBeatCnt` state machine in Stage2 |
| **Directed Test** | `test_refill_beats.py`, `test_read_burst_hit.py` |
| **Corner Test** | — |
| **Random Test** | `test_random_cache.py` |
| **Coverage Groups** | `cache_refill_path` (4 bins: read_burst/read_last/writeback/refill) |
| **Status** | ✅ 100% |

---

### R5: Cache Replacement (LRU/PLRU/LFSR)

| Attribute | Detail |
|-----------|--------|
| **Requirement** | When all 4 ways of a set are occupied, a new cache miss must select a victim way and evict it. |
| **RTL Source** | `Cache.v`: LFSR-based replacement in `replace_way` |
| **Directed Test** | `test_invalid_way_replacement.py`, `test_clean_eviction.py` |
| **Corner Test** | — |
| **Random Test** | — |
| **Coverage Groups** | `cache_clean_eviction` (1 bin: clean_eviction_detected) |
| **Status** | ✅ 100% |

---

### R6: Dirty Writeback on Eviction

| Attribute | Detail |
|-----------|--------|
| **Requirement** | When a dirty cache line is evicted, it must be written back to memory before the new line is refilled. Writeback address must match victim address. |
| **RTL Source** | `Cache.v`: dirty writeback state machine (`WRITE_BURST` → `WRITE_LAST`) |
| **Directed Test** | `test_dirty_writeback.py`, `test_write_miss_dirty_eviction.py` |
| **Corner Test** | — |
| **Random Test** | — |
| **Coverage Groups** | `cache_write_miss` (3 bins: none/clean/dirty), `cache_miss_x_addr_type` |
| **Scoreboard** | `check_dirty_writeback_refill()` — multi-transaction writeback-before-refill verification |
| **Status** | ✅ 100% |

---

### R7: MMIO Address Bypass

| Attribute | Detail |
|-----------|--------|
| **Requirement** | MMIO addresses (addr ≥ `0x4000_0000`) must bypass the cache entirely — no cache line fill, no dirty marking. |
| **RTL Source** | `Cache.v`: MMIO detection at address decode |
| **Directed Test** | `test_mmio_bypass.py` |
| **Corner Test** | — |
| **Random Test** | — |
| **Coverage Groups** | `cache_addr_class` (2 bins: normal/mmio) |
| **Status** | ✅ 100% |

---

### R8: Write Miss Handling

| Attribute | Detail |
|-----------|--------|
| **Requirement** | A write to a cache line not in cache triggers a refill (read burst), then merges write data into the filled line. |
| **RTL Source** | `Cache.v`: write miss path — refill first, then write hit |
| **Directed Test** | `test_write_miss.py` |
| **Corner Test** | — |
| **Random Test** | — |
| **Coverage Groups** | `cache_write_miss`, `cache_write_hit_x_wmask` (48 bins) |
| **Status** | ✅ 100% |

---

### R9: Coherence Probe

| Attribute | Detail |
|-----------|--------|
| **Requirement** | External coherence probes must return hit/miss status. Data must be correct for probe hits. Probe must not corrupt cache state. |
| **RTL Source** | `Cache.v`: `io_out_coh_req` / `io_out_coh_resp` ports |
| **Directed Test** | `test_coherence_probe.py` |
| **Corner Test** | — |
| **Random Test** | — |
| **Coverage Groups** | `cache_coherence_probe` (2 bins: probe_hit/probe_miss), `cache_probe_x_cache_state` (5 bins: hit/miss × empty/valid/dirty) |
| **Scoreboard** | Probe response command check (`0xc` = hit, `0x8` = miss) |
| **Status** | ✅ 100% |

---

### R10: Pipeline Backpressure

| Attribute | Detail |
|-----------|--------|
| **Requirement** | Cache must correctly handle backpressure on both CPU-side (request not accepted) and memory-side (response not ready). |
| **RTL Source** | `Cache.v`: `io_in_req_ready` / `io_out_mem_req_ready` handshakes |
| **Directed Test** | — |
| **Corner Test** | `test_backpressure.py` |
| **Random Test** | — |
| **Coverage Groups** | `cache_backpressure` (2 bins: cpu_resp/mem_req) |
| **Status** | ✅ 100% |

---

### R11: Cache Flush

| Attribute | Detail |
|-----------|--------|
| **Requirement** | Flush signal must invalidate all cache lines. Post-flush reads must result in cache misses (cold-start state). |
| **RTL Source** | `Cache.v`: flush pipeline kill |
| **Directed Test** | `test_flush_behavior.py` |
| **Corner Test** | — |
| **Random Test** | — |
| **Coverage Groups** | `cache_flush` (2 bins: idle/after_accept) |
| **Status** | ✅ 100% |

---

### R12: PREFETCH Instruction (I-Cache Specific)

| Attribute | Detail |
|-----------|--------|
| **Requirement** | PREFETCH instructions should not cause writebacks or dirty-line corruption. |
| **RTL Source** | `Cache.v`: PREFETCH decode case — suppresses store/fill behavior |
| **Directed Test** | `test_prefetch.py` |
| **Corner Test** | — |
| **Random Test** | — |
| **Coverage Groups** | `cache_cmd_type` (3 bins: read/write/prefetch) |
| **Status** | ✅ 100% |

---

### R13: Bug Injection Detection

| Attribute | Detail |
|-----------|--------|
| **Requirement** | Verification environment must detect injected faults — proving that the scoreboard catches real design errors. |
| **RTL Source** | N/A (fault injection framework) |
| **Directed Test** | — |
| **Bug Injection Test** | `bug_003_address_corruption.py`, `bug_004_dirty_bit_loss.py`, `bug_005_refill_scramble.py`, `bug_006_race_condition.py` |
| **Bug Recovery** | `run_bug_injection.py` (--disable-bug mode confirms false-positives don't occur) |
| **Coverage Groups** | N/A (correctness verification, not coverage) |
| **Status** | ✅ All 6 bug types detected; all recoverable via --disable-bug |

---

## Cross-Reference Index

### Test → Coverage Mapping

| Test File | Coverage Groups Touched |
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
| `test_random_cache.py` | cmd_type, hit_miss, write_mask_class, word_offset, refill_path (exploratory) |

### Coverage → Test Mapping

| Coverage Group | Bins | Primary Test(s) |
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
| `cache_req_tracker` | 2 | (state capture only — all tests) |
| `cache_write_tracker` | 2 | (state capture only — all write tests) |
| `cache_probe_tracker` | 1 | (state capture only — probe tests) |

---

## Verification Completeness Summary

| Metric | Value |
|--------|-------|
| Functional Requirements | 13 (R1-R13) |
| Directed Tests | 15 files, 81 test functions |
| Corner Tests | 1 file, 2 test functions |
| Random Tests | 2 files (single-seed + multi-seed) |
| Bug Injection Scenarios | 4 types (+ 2 legacy: ref-model corruption + RTL bypass) |
| Functional Coverage Groups | 18 (15 real + 3 tracker) |
| Functional Coverage Points | 91 |
| Functional Coverage Bins | 98 |
| Functional Coverage | **100%** |
| Line Coverage (RTL) | **100%** |
| Branch Coverage (RTL) | **100%** |
| Expr Coverage (RTL) | **100%** |
| Toggle Coverage | 88.4% (3,280 waived) |
| Requirements with No Coverage Gaps | 13/13 |
