# 手动发现：功能覆盖率缺口（2026-06-01）

## 发现背景

运行 `scripts/collect_coverage.sh 7 18` 后，功能覆盖率报告仅显示 **62% 的点覆盖率（57/91）**，明显低于预期。通过检查聚合后的 Toffee 覆盖率数据手动调查此问题。

**解决状态：已完成（2026-06-01）** — 所有缺口已关闭。最终结果：**91/91 点（100%），98/98 仓（100%）**。

## 调查方法

1. 运行 `scripts/collect_coverage.sh 7 18` 重新生成覆盖率
2. 检查 `build/toffee_coverage_aggregated.json` 的逐组逐点分解
3. 交叉引用 `src/utils/toffee_coverage.py` 的覆盖率模型设计
4. 识别每个未覆盖点的根本原因

## 缺口汇总（修复前）

| 类别 | 未覆盖点数 | 根本原因 |
|---|---|---|
| 跟踪器组（模型设计） | 4 | 副作用 lambda 不返回 bool，永久"未覆盖" |
| `cache_write_hit_x_wmask` | 26/48 | 随机流量仅覆盖 48 种 wmask × offset 组合中的 22 种 |
| `cache_probe_x_cache_state` | 4/6 | 缺少针对 valid/dirty cache line 的 probe 测试 |
| **合计** | **34/91** | |

## 详细发现

### 1. 跟踪器组 — 模型层面问题（4 点）✅ 已解决

三个组（`cache_req_tracker`、`cache_write_tracker`、`cache_probe_tracker`）使用 `_mark()` 并传入调用状态捕获函数的 lambda（`_capture_req`、`_capture_write`、`_track_write`、`_capture_probe_req`）。这些函数执行副作用但**从未返回 True**，因此 toffee 标记系统永远无法将其标记为已覆盖。

**修复**：在 `src/utils/toffee_coverage.py` 中为全部四个捕获函数添加 `return True` / `return False`。

### 2. cache_probe_x_cache_state — 缺少测试激励 + 模型问题 ✅ 已解决

覆盖率模型定义了交叉维度仓（probe_hit/miss × empty/valid/dirty）。发现两个问题：

**已修复的模型问题**：
- `probe_hit_empty` — 物理上不可达（probe 不可能命中空行）。**已从模型中移除**。
- `probe_miss_*` — `_eval_probe_cross` 检查被探测行的状态，但对于 miss 而言被探测行始终为空。已修复为检查**整体 cache 状态**（是否存在 dirty/valid 行？）。

**已添加的测试**（`tests/directed/test_coherence_probe.py`）：
- `test_probe_hit_valid_state` — 填充行，probe 同一地址 → probe_hit（valid）
- `test_probe_hit_dirty_state` — 填充 + 写脏行，probe 同一地址 → probe_hit（dirty）
- `test_probe_miss_valid_state` — 填充行 A，probe 行 B → probe_miss（存在 valid 行）
- `test_probe_miss_dirty_state` — 填充 + 写脏行 A，probe 行 B → probe_miss（存在 dirty 行）

### 3. cache_write_hit_x_wmask — 随机覆盖率缺口 ✅ 已解决

48 种组合（6 种 wmask 类别 × 8 个 word offset）。通过 `tests/directed/test_write_hit_wmask.py` 中的 44 个定向测试关闭所有缺口：

| Wmask 类别 | 已覆盖 Offset |
|---|---|
| byte | 0, 1, 2, 3, 4, 5, 6, 7 |
| adjacent | 0, 1, 2, 3, 4, 5, 6, 7 |
| low_half | 0, 1, 2, 3, 4, 5, 6, 7 |
| high_half | 0, 1, 2, 3, 4, 5, 6, 7 |
| full | 0, 1, 2, 3, 4, 5, 6, 7 |
| sparse | 0, 1, 2, 3, 4, 5, 6, 7 |

### 4. cache_miss_x_addr_type — 不可达仓 ✅ 已解决

`miss_mmio` 仓已从模型中移除：MMIO 地址永远不会产生 cache miss（MMIO 完全绕过 cache，通过 `io_mmio_req` 路由）。

## 解决方案汇总

| 类别 | 状态 | 修复方式 |
|---|---|---|
| 4 个 tracker 点 | ✅ 已关闭 | 捕获函数返回 True |
| 4 个 probe × cache_state 点 | ✅ 已关闭 | 修复 `_eval_probe_cross` 语义 + 定向测试 |
| 26 个 write_hit_x_wmask 点 | ✅ 已关闭 | 44 个定向测试覆盖全部 48 种组合 |
| 2 个不可达仓 | ✅ 已移除 | `miss_mmio`、`probe_hit_empty` 从模型中移除 |

## 最终验证

```bash
source scripts/env.sh
bash scripts/collect_coverage.sh 7 18
# 结果：91/91 点（100%），98/98 仓（100%）
# 18 个组全部覆盖，86 个测试通过
```
