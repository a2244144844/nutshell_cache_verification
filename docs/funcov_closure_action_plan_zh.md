# 功能覆盖率闭环行动计划

## 目标

将功能覆盖率从 57/91（62%）提升至 87/91（96%），关闭所有可达点。

**状态：已完成（2026-06-01）** — 最终结果：**91/91 点（100%），98/98 仓（100%）**。

## 基线（2026-06-01）

- 点数：57/91（62%），仓数：64/99（64%）
- 排除 4 个 tracker 点（模型设计问题）后：57/87（65.5%）
- 行覆盖率：100%，分支覆盖率：100%，表达式覆盖率：100%，Toggle 覆盖率：86.9%

## 已完成操作

### A1：修复 tracker 组 `_mark` 返回值 ✅

**文件**：`src/utils/toffee_coverage.py`
**目标**：4 点 → 已覆盖，+4 点
**结果**：全部 4 个 tracker 函数（`_capture_req`、`_capture_write`、`_track_write`、`_capture_probe_req`）已修改，成功捕获时返回 True。全部 3 个 tracker 组达到 100%。

### A2：添加 probe × cache_state 交叉覆盖率测试 ✅

**文件**：`tests/directed/test_coherence_probe.py`
**目标**：4 → 5 点已覆盖
**结果**：10 个 probe 测试通过。在移除 `probe_hit_empty`（物理不可达）并修复 `_eval_probe_cross` 的 probe_miss 语义后，5/5 的 probe_x_cache_state 仓已覆盖。

已添加测试：
- `test_probe_hit_valid_state` — 填充行，probe 同一地址 → probe_hit（valid 状态）
- `test_probe_hit_dirty_state` — 填充 + 写脏行，probe 同一地址 → probe_hit（dirty 状态）
- `test_probe_miss_valid_state` — 填充行 A，probe 行 B → probe_miss（存在 valid 行）
- `test_probe_miss_dirty_state` — 填充 + 写脏行 A，probe 行 B → probe_miss（存在 dirty 行）

### A3：扩展 write_hit_x_wmask 覆盖率 ✅

**文件**：`tests/directed/test_write_hit_wmask.py`
**目标**：22 → 48 点已覆盖
**结果**：44 个测试覆盖全部 48 种 wmask × offset 组合。所有测试通过。

两轮测试添加：
- **第一轮**（原计划）：26 个测试覆盖 byte(1,2,5,6,7)、adjacent(1,2,3,6,7)、low_half(1,2,3,4,7)、high_half(1,2,3,4,5)、sparse(2,3,4,5,6,7)
- **第二轮**（缺口关闭）：18 个测试覆盖 byte(3,4)、adjacent(0,4,5)、low_half(0,5,6)、high_half(0,6,7)、full(2,3,4,6,7)、sparse(0,1)

### A4：移除物理不可达仓 ✅

**文件**：`src/utils/toffee_coverage.py`
- 从 `cache_miss_x_addr_type` 中移除 `miss_mmio` — MMIO 永远不会导致 cache miss（MMIO 绕过 cache）
- 从 `cache_probe_x_cache_state` 中移除 `probe_hit_empty` — probe 不可能命中从未填充的行

同步更新了 `src/utils/cache_coverage.py` 的 EXPECTED_BINS。

### A5：修复 probe_miss 的 `_eval_probe_cross` 语义 ✅

**文件**：`src/utils/toffee_coverage.py`
**变更**：对于 probe_miss 仓，检查整体 cache 状态（是否存在 dirty/valid 行？），而非被探测行的状态（对 miss 而言始终为空）。对于 probe_hit 仓，继续检查命中的特定行的状态。

## 执行顺序（历史记录）

| # | 项目 | 文件 | 点数 | 状态 |
|---|---|---|---|---|
| 1 | 修复 tracker `_mark` 返回值 | `src/utils/toffee_coverage.py` | +4 | 已完成 |
| 2 | 添加 probe × cache_state 测试 | `tests/directed/test_coherence_probe.py` | +4 | 已完成 |
| 3 | 定向 write_hit_x_wmask 组合（第一轮） | `tests/directed/test_write_hit_wmask.py` | +15 | 已完成 |
| 4 | 定向 write_hit_x_wmask 组合（第二轮） | `tests/directed/test_write_hit_wmask.py` | +18 | 已完成 |
| 5 | 移除不可达仓 + 修复 probe_miss 模型 | `src/utils/toffee_coverage.py` | -2 仓 | 已完成 |
| 6 | 通过 collect_coverage.sh 验证 | `scripts/collect_coverage.sh 7 18` | — | 已完成 |

## 最终结果（2026-06-01）

| 指标 | 修复前 | 修复后 | 备注 |
|---|---|---|---|
| 点数 | 57/91（62%） | **91/91（100%）** | 所有点已覆盖 |
| 仓数 | 64/99（64%） | **98/98（100%）** | 所有仓已覆盖（移除 2 个不可达） |
| 行覆盖率 | 1359/1359（100%） | 1359/1359（100%） | 无变化 |
| 分支覆盖率 | 471/471（100%） | 471/471（100%） | 无变化 |

### 逐组分解

| 组 | 点数 | 仓数 | 状态 |
|---|---|---|---|
| `cache_addr_class` | 1/1 | 2/2 | 已覆盖 |
| `cache_backpressure` | 2/2 | 2/2 | 已覆盖 |
| `cache_clean_eviction` | 1/1 | 1/1 | 已覆盖 |
| `cache_cmd_type` | 2/2 | 3/3 | 已覆盖 |
| `cache_coherence_probe` | 1/1 | 2/2 | 已覆盖 |
| `cache_flush` | 1/1 | 2/2 | 已覆盖 |
| `cache_hit_miss` | 2/2 | 2/2 | 已覆盖 |
| `cache_miss_x_addr_type` | 2/2 | 3/3 | 已覆盖 |
| `cache_probe_tracker` | 1/1 | 1/1 | 已覆盖 |
| `cache_probe_x_cache_state` | 5/5 | 5/5 | 已覆盖 |
| `cache_refill_path` | 3/3 | 4/4 | 已覆盖 |
| `cache_req_accepted` | 1/1 | 1/1 | 已覆盖 |
| `cache_req_tracker` | 2/2 | 2/2 | 已覆盖 |
| `cache_word_offset` | 8/8 | 8/8 | 已覆盖 |
| `cache_write_hit_x_wmask` | 48/48 | 48/48 | 已覆盖 |
| `cache_write_mask_class` | 7/7 | 7/7 | 已覆盖 |
| `cache_write_miss` | 2/2 | 3/3 | 已覆盖 |
| `cache_write_tracker` | 2/2 | 2/2 | 已覆盖 |

## 修改文件

| 文件 | 变更 |
|---|---|
| `src/utils/toffee_coverage.py` | 修复 tracker 返回值，移除 2 个不可达仓，修复 probe_miss 的 `_eval_probe_cross` |
| `src/utils/cache_coverage.py` | 同步 `EXPECTED_BINS` 与模型变更 |
| `tests/directed/test_coherence_probe.py` | 添加 probe_hit_valid、probe_hit_dirty、probe_miss_valid、probe_miss_dirty 定向测试 |
| `tests/directed/test_write_hit_wmask.py` | 添加 18 个缺失的 wmask × offset 组合（共 44 个测试，覆盖 48/48 仓） |

## 验证

```bash
source scripts/env.sh
bash scripts/collect_coverage.sh 7 18
# 结果：91/91 点（100%），98/98 仓（100%）
# 86 passed，耗时 42.81s
```
