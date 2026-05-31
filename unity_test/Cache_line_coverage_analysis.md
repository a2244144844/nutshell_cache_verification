# Cache Line Coverage Analysis

## Coverage Artifacts

| Artifact | Path |
| --- | --- |
| Functional coverage report | `docs/coverage_report.md` |
| Chinese coverage mirror | `docs/coverage_report_zh.md` |
| HTML report | `build/reports/cache_coverage.html` |
| Coverage utility | `src/utils/cache_coverage.py` |
| Toffee coverage utility | `src/utils/toffee_coverage.py` |

## Functional Coverage Result

```text
Toffee funcov: 12 groups, 31 points, 37 bins -> 100% covered
Marked Points: 31/31 (100%) -> 26/26 Marked Functions (100%)
```

## Covered Groups

| Group | Covered Examples |
| --- | --- |
| Command type | read, write, probe |
| Hit/miss proxy | hit, miss |
| Write mask class | none, byte, adjacent, low half, high half, full, sparse |
| Word offset | offsets 0 through 7 |
| Refill path | clean miss refill, read hit, write hit, dirty miss writeback/refill |
| Address class | normal memory, MMIO |
| Backpressure | CPU response, memory request |
| Flush | idle, after request accept |
| Coherence probe | probe hit, probe miss |
| Write miss | clean write miss, dirty write miss |
| Clean eviction | clean victim replacement without writeback |

## Legacy Random Collector Note

The legacy random collector still reports some write-miss bins as gaps because the constrained-random generator only produces write-hit traffic. Those paths are closed in the Toffee coverage model through directed tests:

- `tests/directed/test_write_miss.py`
- `tests/directed/test_clean_eviction.py`
- `tests/directed/test_write_miss_dirty_eviction.py`

## RTL Coverage Status (Final)

Verilator RTL coverage is collected via the `-c` flag in Picker export. Results are available in:

- HTML (funcov + line): `build/reports/cache_coverage.html`
- LCOV HTML: `build/reports/line_dat/index.html`
- Markdown: `docs/coverage_report.md`

Final result:

```text
Line coverage:   1359/1359 (100.0%)
Branch coverage: 471/471 (100.0%)
Toggle coverage: 24947/28227 (88.4%)
Toffee funcov:   12 groups, 31 points, 37 bins (100%)
Waived lines:    42 lines (Categories A-N)
Waived toggles:  3280 toggles (Categories T-A–T-F, documentation-based)
```

### Final Waiver Summary

Line/branch waivers are applied via `ignore_patterns` in `tests/conftest.py` (see `docs/coverage_waiver_rationale.md` for full rationale):

| Category | Lines | Count | Description |
|---|---|---|---|
| A, E | 263, 877, 901, 925, 949 | 5 | Assertion `$fwrite` failure messages — unreachable by design |
| B, G | 138, 411, 524, 2267, 2418 | 5 | D-cache forwarding signals — I-cache = always 0 |
| D | 2861-2862 | 2 | `io_flush[1]` pipeline kill — blocked by D-cache assertion |
| F | 240-241 | 2 | LFSR all-zero dead state — unreachable without corruption |
| J | 420, 460, 2276, 2316 | 4 | CacheStage3 D-cache ports — structurally unreachable in I-cache configuration |
| H, I, K, L, M, N | (see rationale doc) | 24 | Additional line/branch waivers — structurally unreachable or false-path |
| **Waived subtotal** | | **42** | |

Toggle waivers are documented in `docs/toggle_coverage_waiver.md`.

### Coverage Closure Timeline

- Stage 9 (`line_coverage_closure`): DIR-014/015/016 → line 99.6%
- Stage 11 (`line_coverage_100`): DIR-017 (needFlush), DIR-018 (respToL1Last) → line 100.0%
- Stage 12 (`branch_coverage_closure`): DIR-019 (PREFETCH), DIR-020 (writeback counters), DIR-021 (internal probe), DIR-022 (state2) → branch 100.0%
- Stage 13 (`toggle_coverage_improvement`): Multi-seed random traffic → toggle 87.8%

No remaining uncovered lines or branches after waiver application.
