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

---

## Bug ID

`BUG-RTL-001`

## 注入的故障

RTL 级损坏，位于 `CacheStage3` 状态机决策逻辑（`rtl/dut/Cache.v` 第 615 行）：将脏写回状态跳转从条件判断（`meta_dirty ? 4'h3 : 4'h1`）改为无条件 refill（`4'h1`）。这导致 cache 在每次缺失时跳过脏写回状态（`4'h3`）直接进入 refill（`4'h1`），脏 victim 数据被静默丢弃。

## 触发方式

使用修改后的 RTL 重新构建：

```sh
scripts/export_cache_dut.sh
```

然后运行脏写回测试：

```sh
source scripts/env.sh && /Users/zzy/Workspace/ucagent/.venv/bin/python -m pytest tests/directed/test_dirty_writeback.py -v
```

或运行完整回归以查看影响范围：

```sh
scripts/run_regression.sh
```

## 检出路径

`test_dirty_writeback.py` 第 61 行期望在 set 冲突缺失驱逐脏行后，`write_reqs` 中至少存在一个 `WRITE_BURST`/`WRITE_LAST` 内存请求。由于 RTL bug 导致 cache 完全跳过写回，`write_reqs` 为空列表——访问 `write_reqs[0]` 触发 `IndexError`。

## 失败证据

```text
tests/directed/test_dirty_writeback.py::test_dirty_victim_writeback_refills_on_set_conflict FAILED

write_reqs = [req for req in mem_requests if req.cmd in {sb.WRITE_BURST, sb.WRITE_LAST}]
read_reqs = [req for req in mem_requests if req.cmd in {sb.READ_BURST, sb.READ_LAST}]
>   victim_data = write_reqs[0].wdata
                  ^^^^^^^^^^^^^
E   IndexError: list index out of range

tests/directed/test_dirty_writeback.py:61: IndexError
```

Bug 激活时的回归结果：`1 failed, 6 passed in 0.10s`——仅 `test_dirty_writeback` 失败；其余测试（smoke、word-offsets、write-masks、refill-beats、backpressure）均通过，因为它们不涉及脏 eviction 路径。

## 清理 / 恢复

恢复原始 RTL 行并重新构建：

```sh
# Cache.v 第 615 行从：
#   wire [3:0] _state_T_3 = 4'h1; // BUG
# 恢复为：
#   wire [3:0] _state_T_3 = meta_dirty ? 4'h3 : 4'h1;

scripts/export_cache_dut.sh
scripts/run_regression.sh
```

恢复结果：`7 passed in 0.07s`。
