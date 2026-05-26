# Backpressure Stage

Stage name: `backpressure_directed_tests`

Files changed:

- `src/env/cache_env.py`
- `tests/corner/test_backpressure.py`
- `scripts/run_regression.sh`
- `docs/test_points.md`
- `docs/ai_collaboration_report.md`

Command run:

```sh
scripts/run_regression.sh
```

Exact result:

```text
PASS: 6 passed in 0.16s
```

Remaining risks:

- The stage covers read-miss backpressure on the CPU response path and memory request path only.
- MMIO, flush, and coherence interactions under stall conditions still need separate directed coverage.
- The environment helpers are intentionally low-level; future tests may want small shared utilities for repeated handshake loops.
