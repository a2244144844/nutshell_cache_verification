# Bug Injection Stage 输出

日期：2026-05-26

## 变更的文件

- `tests/injected_bug/run_bug_injection.py`
- `docs/bug_tracking.md`
- `docs/test_points.md`
- `docs/ai_collaboration_report.md`
- `docs/verification_plan.md`
- `docs/ucagent_operation_plan.md`
- `README.md`
- `top.md`

## 运行的命令

- `source scripts/env.sh && /Users/zzy/Workspace/ucagent/.venv/bin/python tests/injected_bug/run_bug_injection.py`
- `source scripts/env.sh && /Users/zzy/Workspace/ucagent/.venv/bin/python tests/injected_bug/run_bug_injection.py --disable-bug`
- `scripts/run_regression.sh`

## 精确结果

- `tests/injected_bug/run_bug_injection.py` 以码 `1` 退出。
- 失败由参考模型中预期值的故意损坏触发，并由 `CacheScoreboard.check_read_response()` 检出。
- 失败证据：

  ```text
  BUG-001 mode=enabled: corrupting reference-model read_word() flips bit 0 at addr 0x80000000
  BUG-001 expected_data=0x1122334455667789, actual_data=0x1122334455667788
  AssertionError: BUG-001 detected by scoreboard.check_read_response: reference-model corruption made the expected read data 0x1122334455667789 while the DUT returned 0x1122334455667788 at addr 0x80000000
  ```

- `tests/injected_bug/run_bug_injection.py --disable-bug` 以码 `0` 退出。
- 恢复证据：

  ```text
  BUG-001 mode=disabled: clean reference-model read_word() at addr 0x80000000
  BUG-001 expected_data=0x1122334455667788, actual_data=0x1122334455667788
  BUG-001 recovery path: bug injection disabled, scoreboard checks passed.
  ```

- 输出措辞清理后最新本地复查：`scripts/run_regression.sh` 以 `7 passed in 0.14s` 通过。

## 残留风险

- 注入的故障仅针对参考模型，因此验证的是检错链路和报告机制，而非实际的 RTL 变更。
- 当前 harness 仅覆盖单个受控的不匹配场景；增加额外的注入 bug 可以扩展对其他 scoreboard 和 monitor 路径的覆盖。
- 正常回归保持干净，但 bug harness 必须保持在 `scripts/run_regression.sh` 之外，以免主测试套件继承故意引入的故障模式。
