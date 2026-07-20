# Stage 20：一等奖差距闭合 — P2 项

日期：2026-05-31 | 后端：Claude Code CLI | 来源：`docs/gap_analysis_first_prize.md`

## 概述

执行了全部 3 个 P2 项：env.sh 可移植性检查（P2-11）、跨维度覆盖率组（P2-10）和需求可追溯性矩阵（P2-9）。这些项为一等奖提交增加了润色和文档深度。

## 验证门禁

- `scripts/run_regression.sh` → **38 passed**
- `scripts/run_directed.sh` → **27 passed**
- 所有 P2 改动均为增量式——无回归

## 结果

### P2-11：env.sh 可移植性检查

在 `scripts/env.sh` 中为关键工具链路径添加了快速失败的存在性守卫：
- `PICKER_HOME`：缺失时报硬错误（DUT 构建必需）
- `JAVA_HOME`：缺失时报警告（仅 Chisel/Scala 构建需要）

路径已是可移植的（从 `$ROOT_DIR` 派生），因此修复纯粹是提供清晰诊断消息的快速失败守卫。

### P2-10：跨维度覆盖率组

添加了 3 个跨维度功能覆盖率组，组合独立维度以证明多轴验证：

| 跨维度组 | 维度 | 仓数 | 实现 |
|---------|------|------|------|
| `cache_write_hit_x_wmask` | write_mask_class × word_offset | 48（6 掩码 × 8 偏移） | `cache_coverage.py` + `toffee_coverage.py` |
| `cache_miss_x_addr_type` | hit_miss × addr_class（normal/mmio） | 4 | `cache_coverage.py` + `toffee_coverage.py` |
| `cache_probe_x_cache_state` | probe_hit/miss × cache 状态（empty/valid/dirty） | 6 | `cache_coverage.py` + `toffee_coverage.py` |

**Python 层**（`cache_coverage.py`）：扩展了 `EXPECTED_BINS`，增加 3 组跨维度仓集，更新了 `record()` 以自动计算 `write_hit_x_wmask`、`miss_x_addr_type` 和 `probe_x_cache_state` 仓。使用 `_line_dirty` 字典跟踪 probe 状态。

**Toffee 层**（`toffee_coverage.py`）：添加了 3 个跨维度 `CovGroup`（`cache_write_hit_x_wmask`、`cache_miss_x_addr_type`、`cache_probe_x_cache_state`）和 3 个跟踪组（`cache_req_tracker`、`cache_write_tracker`、`cache_probe_tracker`）。状态跟踪辅助方法（`_capture_req`、`_capture_write`、`_capture_probe_req`、`_eval_probe_cross`）跨周期捕获 DUT 引脚状态以评估跨维度条件。将 wmask 分类整合为 `@staticmethod _classify_wmask`。

总功能覆盖率：12 组 → 15 组，31 点 → 58+ 点，37 仓 → 95 仓。

**关键技术挑战**：DUT 的 `io_out_coh_resp_bits` 仅有 `cmd` 和 `rdata` 引脚——没有 `addr`。Probe 地址必须从 `io_out_coh_req_bits_addr`（请求侧）通过 `_capture_probe_req` 捕获并存储在 `_last_probe_addr` 中，供 `_eval_probe_cross` 使用。

### P2-9：需求可追溯性矩阵（RTM）

创建了 `docs/requirements_traceability_matrix.md`，将每个验证需求映射到其测试、覆盖率组和状态：

| 章节 | 需求 | 覆盖率 |
|------|------|--------|
| 核心 Cache | SMK-002~007 | `refill_path` + `cmd_type` 组 |
| 写掩码与字偏移 | DIR-001~002 | `write_mask_class` + `word_offset` 组 |
| Refill 与替换 | DIR-003~005, DIR-011~013, DIR-020 | `refill_path` 全部 6 仓 |
| MMIO 与 Flush | DIR-006~007, DIR-016~017 | `addr_class.mmio` + `flush_timing` |
| 一致性探测 | DIR-008, DIR-014, DIR-021 | `probe_result` |
| 反压 | DIR-009~010 | `backpressure_loc` |
| 读突发与预取 | DIR-015, DIR-018~019, DIR-022 | （结构覆盖率） |
| 随机验证 | CRV-001~005 | 全部 37→95 仓 |
| 故障注入 | BUG-001, BUG-RTL-001, BUG-003~006 | 7 个故障均支持 --disable-bug |
| 覆盖率豁免 | 类别 A~O + T-A~T-F | 48 行 + 3,280 翻转缺失 |

包含最终覆盖率汇总（行 100%、分支 100%、表达式 100%、翻转 88.4%、功能覆盖率 100%）和测试执行汇总（6 个套件，约 60 秒完整复现）。

## 文件变更

| 文件 | 变更 |
|------|------|
| `scripts/env.sh` | P2-11：添加 PICKER_HOME/JAVA_HOME 存在性检查 |
| `src/utils/cache_coverage.py` | P2-10：在 EXPECTED_BINS 中添加 3 组跨维度仓集（58 仓）+ 记录逻辑 |
| `src/utils/toffee_coverage.py` | P2-10：添加 3 个跨维度 CovGroup + 3 个跟踪组及状态跟踪辅助方法 |
| `docs/requirements_traceability_matrix.md` | P2-9：创建 RTM（10 个需求章节，全部测试 + 覆盖率组 + 豁免类别） |
| `docs/test_points.md` | 添加 Stage 20 条目，包含跨维度覆盖率 + RTM + env.sh 内容 |
| `docs/ai_collaboration_report.md` | 添加 Stage 20 条目，记录 P2-9/10/11 |

## 评分影响

| 维度 | 之前（P1 后） | 之后（P0+P1+P2） | 增量 |
|------|--------------|-----------------|------|
| 覆盖率达标（15分） | 13-15 | 14-15 | +1 |
| 工程规范（20分） | 18-20 | 19-20 | +1 |
| **总计（100分）** | **88-99** | **90-100** | **+2** |
