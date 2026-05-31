# Stage 11：行覆盖率 100% — DIR-017 与 DIR-018 结果

日期：2026-05-31 | Agent：UCAgent + Claude Code | Stage 索引：11

对应英文文档：`docs/ucagent_output/line_coverage_100_stage.md`

---

## 变更文件

| 文件 | 变更 |
|---|---|
| `tests/directed/test_flush_behavior.py` | 新增 `test_needflush_assert_and_deassert`（DIR-017） |
| `tests/directed/test_read_burst_hit.py` | 新增 `test_read_burst_hit_resptol1_counter`（DIR-018） |
| `tests/conftest.py` | 在 `ignore_patterns` 中添加第 605,608,610 行（P2 豁免） |
| `docs/test_points.md` | 新增 DIR-017 和 DIR-018 条目 |
| `docs/coverage_waiver_rationale.md` | 新增 Category K（respToL1Last 计数器） |
| `docs/coverage_closure_final.md` | 更新 Part 1，添加 Stage 11 结果 |
| `docs/ai_collaboration_report.md` | 新增 Stage 11 条目 |
| `docs/ucagent_output/line_coverage_100_stage.md` | 英文主文件 |

---

## 执行命令

### 1. DIR-017 测试（needFlush 生命周期）

```
source scripts/env.sh && python -m pytest tests/directed/test_flush_behavior.py::test_needflush_assert_and_deassert -v
结果：PASSED [100%]
```

### 2. DIR-018 测试（respToL1Last 计数器）

```
source scripts/env.sh && python -m pytest tests/directed/test_read_burst_hit.py::test_read_burst_hit_resptol1_counter -v
结果：PASSED [100%]
```

### 3. 完整回归

```
scripts/run_regression.sh
结果：32 passed in 8.34s
```

### 4. 覆盖率采集

```
scripts/collect_coverage.sh 7 18
结果：32 passed, Line: 1359/1359 (100.0%)
```

---

## 覆盖增量

| 指标 | Stage 11 前 | Stage 11 初始 | D 类扩展豁免后 |
|---|---|---|---|
| 行覆盖率 | 1359/1364 (99.6%) | 1359/1361 (99.9%) | **1359/1359 (100.0%)** |
| 未覆盖行 | 5 (558, 605, 608, 610, 788) | 2 (558, 788) | **0** |
| 已豁免行 | 16 | 19 (+605,608,610) | **21** (+558, 788) |
| 定向测试 | 26 | 28 (+2: DIR-017, DIR-018) | 28 |

---

## DIR-017：needFlush 完整生命周期 — 结果

**测试：** `test_needflush_assert_and_deassert`（位于 `tests/directed/test_flush_behavior.py`）
**目标：** 第 558, 787-788 行
**优先级：** P0 → P2（已豁免，2026-05-31）
**结果：** PASS

测试覆盖完整的 needFlush 生命周期：
1. 向冷地址 A 发送 READ
2. 在接受窗口期间断言 `io_flush=0b01` → needFlush=1
3. 等待 `io_empty==1`（pipeline 排空）
4. 取消 `io_flush`，步进 10 个周期
5. 使用低级引脚控制向冷地址 B 驱动新 READ
6. 逐周期步进，捕获 `io_in_resp_valid` 节拍
7. 验证响应数据和 user 字段正确

**最终结论（2026-05-31）：** 进一步 RTL 分析确认第 558 和 788 行在 I-cache 模式下**结构上不可达**。根因：
- `Cache.v:2786`：`assign s3_io_flush = io_flush[1];` — CacheStage3 的 `io_flush` 硬连接至 `io_flush[1]`
- 在 I-cache 中，断言 `assert(!(!ro.B && io.flush))` 阻止 `io_flush[1]` 被置位
- 因此 CacheStage3 的 `io_flush` 恒为 0，`_GEN_1` 退化为自循环（`needFlush <= needFlush`），`needFlush` 永远不离开其复位值 0
- 与第 2861-2862 行相同的根因（Category D，已豁免）
- **已豁免为 Category D 扩展。** 行覆盖率 → **1359/1359（100.0%）**。

---

## DIR-018：respToL1Last 计数器 — 结果

**测试：** `test_read_burst_hit_resptol1_counter`（位于 `tests/directed/test_read_burst_hit.py`）
**目标：** 第 605, 608, 610 行
**优先级：** P1 → P2（已豁免）
**结果：** PASS

测试覆盖 READ_BURST 命中路径：
1. 用 8 个不同的 word 值填充 cache line
2. 以 `io_in_resp_ready=1` 向命中行驱动 READ_BURST
3. 捕获所有 CPU 响应节拍（`io_in_resp_*`）
4. 捕获一致性释放节拍（`io_out_coh_resp_*`）

**发现：**
- `io_in_resp_*` 上只有单拍 CPU 响应（I-cache 限制）
- 一致性释放节拍在 `io_out_coh_resp_*` 上观测到，但不驱动 `respToL1Last` 计数器
- `respToL1Last` 计数器需要多拍 CPU 响应路径，仅在 D-cache 模式下可用
- 8 拍释放改用 `releaseLast` 计数器（第 598-602 行），通过一致性端口

**状态：P2 已豁免。** 第 605, 608, 610 行已加入 `tests/conftest.py` 的 `ignore_patterns`，并在 `docs/coverage_waiver_rationale.md` 中记录为 Category K。

---

## 豁免汇总

### 新增豁免（Category K）

| 行号 | 信号 | 依据 |
|---|---|---|
| 605 | `respToL1Fire` | 需要多拍 CPU 响应 — I-cache 仅单拍 |
| 608 | `respToL1Last_wrap_wrap` | 计数器在 7 处翻转 — 需要 8+ 拍 CPU 响应 |
| 610 | `respToL1Last` | 最后节拍标记 — 计数器在 I-cache 中永远达不到翻转 |

### 最终未覆盖行

**全部行已覆盖。** 此前剩余的 2 行（558, 788）在确认与第 2861-2862 行共享同一根因（io_flush[1] 被 D-cache 断言阻断）后，已作为 Category D 扩展豁免。行覆盖率：**1359/1359（100.0%）**。

### 当前 conftest.py 中的 ignore_patterns

```
Cache.v:138,148,150,152,202-207,240-241,262,263,411,420,460,524,532,550,555,558,605,608,610,626,768,777,788,796,824,876,877,900,901,924,925,948,949,2267,2276,2316,2418,2674,2861-2862
（A-N 共 38 条）
```

---

## 说明

- **行覆盖率达成：** 1359/1359（100.0%）— 所有 RTL 行均已通过定向测试覆盖或附文档化依据豁免。详见 `docs/coverage_waiver_rationale.md` 获取每个类别的完整分析。
- **分支覆盖率闭环（Stage 12）：** 应用 8 条额外 P2 分支豁免（Category N）后，471/471（100.0%）。详见 `docs/ucagent_output/branch_coverage_closure_stage.md` 获取 DIR-019 至 DIR-022 的实现详情。
- **toffee-test fixture 限制：** 在单个 pytest 会话中运行多个测试时，第二个测试会因 DUT 生命周期问题挂起。解决方法：在每次单独测试运行前删除 `VCache_coverage.dat`，或使用 `scripts/collect_coverage.sh` 在单个 pytest 进程中运行所有测试。
- **Verilator 覆盖率文件：** `VCache_coverage.dat` 以只读权限写入 CWD。在单独测试运行之间删除此文件以避免 `%Error: Can't write 'VCache_coverage.dat'`。
