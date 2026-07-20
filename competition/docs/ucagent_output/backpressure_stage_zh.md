# Backpressure Stage

Stage 名称：`backpressure_directed_tests`

变更的文件：

- `src/env/cache_env.py`
- `tests/corner/test_backpressure.py`
- `scripts/run_regression.sh`
- `docs/test_points.md`
- `docs/ai_collaboration_report.md`

运行的命令：

```sh
scripts/run_regression.sh
```

精确结果：

```text
PASS: 6 passed in 0.16s
```

残留风险：

- 本 stage 仅覆盖 CPU 响应路径和内存请求路径上的读缺失反压。
- MMIO、flush 和 coherence 在 stall 条件下的交互仍需单独的定向覆盖。
- 环境辅助方法有意保持底层；后续测试可能需要为重复握手循环增加小型共享工具函数。
