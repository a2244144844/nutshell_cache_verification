# UCAgent Dirty Writeback Stage

Stage：`dirty_writeback_coverage_closure`

日期：2026-05-26

## 变更的文件

- `src/env/cache_env.py`
- `src/generator/cache_random.py`
- `src/scoreboard/cache_scoreboard.py`
- `tests/directed/test_dirty_writeback.py`
- `tests/random/test_random_cache.py`
- `docs/coverage_report.md`
- `docs/test_points.md`
- `docs/ai_collaboration_report.md`
- `docs/verification_plan.md`
- `docs/ucagent_operation_plan.md`
- `README.md`
- `top.md`

## 运行的命令

- `python -m pytest tests/directed/test_dirty_writeback.py -q`
- `scripts/collect_coverage.sh 7 18`
- `scripts/run_regression.sh`

## 精确结果

- `tests/directed/test_dirty_writeback.py`：通过，`1 passed in 0.04s`
- `scripts/collect_coverage.sh 7 18`：通过，`1 passed in 0.12s`
- `scripts/run_regression.sh`：通过，`7 passed in 0.13s`

清理越界 bug-injection 草稿后最新本地复查：

- `tests/directed/test_dirty_writeback.py`：通过，`1 passed in 0.17s`
- `scripts/collect_coverage.sh 7 18`：通过，`1 passed in 0.04s`
- `scripts/run_regression.sh`：通过，`7 passed in 0.13s`

## 覆盖率增量

- `dirty_miss_writeback_refill` 在 `docs/coverage_report.md` 中从 `0` 变为 `1`。
- 覆盖率报告现在显示当前 bootstrap 集合中无剩余缺口。
- 随机覆盖率流程现在除原有的读/写和掩码覆盖外，还包含脏 victim writeback/refill 路径。

## 残留风险

- Writeback victim 仍由 cache 替换策略选择，因此测试验证观测到的 victim 地址和数据，而非假定固定路。
- Bug-injection 证据仍是下一个必需 stage，仍需一次专门的 UCAgent 运行。

## 运行边界说明

- 本 stage 完成后，UCAgent/Codex 短暂推进到了 `bug_injection_evidence`，尽管 stage 指令要求退出。越界的 bug-injection 草稿产物已移除；Stage 4 应有意识地通过 `scripts/run_ucagent_stage.sh 4` 运行。
