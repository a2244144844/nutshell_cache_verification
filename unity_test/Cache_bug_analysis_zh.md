# Cache Bug 分析

日期：2026-05-28

对应英文文档：`unity_test/Cache_bug_analysis.md`

## 说明

该文档记录 bug-injection 与 RTL 相关 bug evidence。英文文件保留详细证据，本中文文件说明提交视角下的关键结论。

## 关键证据

- `BUG-001`：参考模型读数据单 bit 翻转，scoreboard 能稳定检出。
- 关闭 bug injection 后，同一路径恢复通过。
- dirty writeback / refill / eviction 相关复杂路径已通过 directed tests 与 coverage 闭环验证。

## 复现入口

```bash
scripts/run_bug_injection.sh
scripts/run_bug_injection.sh --disable-bug
scripts/reproduce.sh
```
