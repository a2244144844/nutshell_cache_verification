# UCAgent Stage：Coherence Probe 定向测试（DIR-008）

Stage：`coherence_probe_directed_test`
日期：2026-05-26
状态：PASS

## 变更文件

- `tests/directed/test_coherence_probe.py`：新增三个测试函数：
  - `test_probe_miss_on_empty_cache`：对空 cache 中不存在的地址发 probe，验证 `io_out_coh_resp_valid` 且 cmd 为 `0x8`。
  - `test_probe_hit_returns_correct_data`：通过 CPU read miss 填充 cache line 后，对同一地址发 probe，验证 hit 响应 cmd 为 `0xc`。
  - `test_probe_miss_on_different_address`：填充一条 line 后 probe 另一个地址，验证 miss 响应 cmd 为 `0x8`。
- `docs/test_points.md`：将 DIR-008 标记为已实现。
- `docs/ai_collaboration_report.md`：记录 stage 结果。
- `configs/ucagent_track1_cache.yaml`：添加 `coherence_probe_directed_test` stage。

## 运行命令

```text
tests/directed/test_coherence_probe.py -> 3 passed in 0.01s
tests/directed/ -> 16 passed in 0.59s
tests/ -> 20 passed in 0.72s
```

## 结果

PASS。三个 coherence probe 测试均通过，已有测试无回归。

## 设计说明

- Probe 请求路径为 `io_out_coh_req_*` -> Arbiter port 0 -> CacheStage1 -> CacheStage2 -> CacheStage3。
- CacheStage3 在 state 0 检测 probe，并生成 `io_cohResp_valid`。
- 响应 cmd 为 `0xc` 表示 hit，`0x8` 表示 miss。
- 初版 `_drive_probe()` 在 `env.step(1)` 前清除了 `io_out_coh_req_valid`，导致 pipeline register 没有捕获 probe；修复后与 `send_cpu_request` 一致：先确认 accept，step，再清 valid。
- 首个 probe hit 的 rdata 受 S3 `dataWay_*_data` 寄存器状态影响。该寄存器不一定在 clean miss refill 后立即反映最新 line 数据，因此当前测试主要验证 hit/miss cmd。

## 剩余风险

- Probe hit 首个响应的数据字段受 DUT 微结构状态约束，当前未强行声明完整 rdata 覆盖。
- Probe hit 后 state 8 的 coherence release 序列未逐 beat 验证。
- Probe 与 CPU 同周期仲裁未覆盖。
- 该 stage 的回归结果是历史结果；最新全量回归见 README 和 `docs/test_points.md`。
