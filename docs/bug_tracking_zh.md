# Bug 追踪

日期：2026-05-26

## Bug ID

`BUG-001`

## 注入的故障

参考模型 `read_word()` 逻辑中故意损坏，将预期 64 位 refill 数据的 bit `0` 翻转。

## 触发方式

运行：

```sh
source scripts/env.sh && /Users/zzy/Workspace/ucagent/.venv/bin/python tests/injected_bug/run_bug_injection.py
```

该 harness 读取 `0x80000000`，以 `0x1122334455667788` 填充该行，随后将 DUT 响应与损坏后的参考模型结果 `0x1122334455667789` 进行比较。

## 检出路径

`env.scoreboard.check_read_response()` 拒绝不匹配的读响应。

## 失败证据

观测到的命令结果：

```text
BUG-001 mode=enabled: corrupting reference-model read_word() flips bit 0 at addr 0x80000000
BUG-001 expected_data=0x1122334455667789, actual_data=0x1122334455667788
AssertionError: BUG-001 detected by scoreboard.check_read_response: reference-model corruption made the expected read data 0x1122334455667789 while the DUT returned 0x1122334455667788 at addr 0x80000000
```

命令退出状态：`1`

## 清理 / 恢复

通过以下命令关闭注入的故障：

```sh
source scripts/env.sh && /Users/zzy/Workspace/ucagent/.venv/bin/python tests/injected_bug/run_bug_injection.py --disable-bug
```

恢复命令结果：

```text
BUG-001 mode=disabled: clean reference-model read_word() at addr 0x80000000
BUG-001 expected_data=0x1122334455667788, actual_data=0x1122334455667788
BUG-001 recovery path: bug injection disabled, scoreboard checks passed.
```

恢复命令退出状态：`0`
