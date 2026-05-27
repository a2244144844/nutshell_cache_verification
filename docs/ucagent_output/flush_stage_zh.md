# UCAgent Stage：Flush 行为定向测试（DIR-007）

Stage：`flush_directed_test`
日期：2026-05-26
状态：PASS

## 变更文件

- `tests/directed/test_flush_behavior.py`：新增三个测试函数：
  - `test_flush_while_idle`：空闲时 assert `io_flush`，验证 `io_empty`，deassert 后验证 cache ready。
  - `test_flush_during_miss`：在 read miss 被 pipeline 捕获前 assert `io_flush`，验证 `io_empty` 保持高电平并验证恢复。
  - `test_flush_recovery`：flush deassert 后验证 read miss、write hit 和 read-after-write 正常工作。
- `docs/test_points.md`：将 DIR-007 标记为已实现。
- `docs/ai_collaboration_report.md`：记录 stage 结果。

## 运行命令

```text
tests/directed/test_flush_behavior.py -> 3 passed in 0.05s
tests/directed/ -> 13 passed in 0.12s
tests/smoke/ + tests/directed/ + tests/corner/ -> 16 passed in 0.13s
```

## 结果

PASS。三个 flush 行为测试均通过，已有测试无回归。

## 设计说明

- `io_flush[1]` 连接到 CacheStage3，但 D-cache 配置下存在 Chisel assertion：`assert(!(!ro.B && io.flush))`。由于本 DUT `ro.B=false`，测试只能安全使用 `io_flush[0]`。
- `io_flush[0]` 在 pipeline valid register 捕获请求的同一上升沿采样。要 squash in-flight 请求，必须在 pipeline 捕获该请求之前 assert flush。
- `io_empty` 定义为 `~s2_io_in_valid & ~s3_io_in_valid`。使用 `io_flush=0b01` 只能清除 S1 到 S2 valid register，不会测试 Stage3 的 `needFlush` 机制。

## 剩余风险

- `io_flush[1]` 和 CacheStage3 refill/writeback 中途 flush 未覆盖，因为当前 D-cache 实例会触发断言。
- 该 stage 的回归结果是历史结果；最新全量回归见 README 和 `docs/test_points.md`。
