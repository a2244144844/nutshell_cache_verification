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

## RTL Line Coverage Status

Verilator RTL line coverage is collected via the `-c` flag in Picker export. Results are available in:

- HTML (funcov + line): `build/reports/cache_coverage.html`
- LCOV HTML: `build/reports/line_dat/index.html`
- Markdown: `docs/coverage_report.md`

Current result:

```text
Line coverage: 1359/1364 (99.6%)
Toffee funcov: 12 groups, 31 points, 37 bins (100%)
Waived (Categories A-G + J): 16 DUT lines + entire Picker wrapper (*Cache_top*)
Remaining uncovered: 5 lines
```

### Waiver Summary

Waivers are applied via `ignore_patterns` in `tests/conftest.py` (see `docs/coverage_waiver_rationale.md` for full rationale):

| Category | Lines | Count | Description |
|---|---|---|---|
| A, E | 263, 877, 901, 925, 949 | 5 | Assertion `$fwrite` failure messages — unreachable by design |
| B, G | 138, 411, 524, 2267, 2418 | 5 | D-cache forwarding signals — I-cache = always 0 |
| D | 2861-2862 | 2 | `io_flush[1]` pipeline kill — blocked by D-cache assertion |
| F | 240-241 | 2 | LFSR all-zero dead state — unreachable without corruption |
| J | 420, 460, 2276, 2316 | 4 | CacheStage3 D-cache ports — structurally unreachable in I-cache configuration |
| **Waived subtotal** | | **16** | (line 263 counted once for A+E) |
| `*Cache_top*` | entire file | — | Picker-generated DPI wrapper (not DUT code) |

### Remaining Uncovered Lines

5 residual lines remain uncovered after Category J waiver and DIR-014/015/016 coverage closure. See `docs/line_coverage_closure_plan.md` and `docs/coverage_waiver_rationale.md` for detailed analysis.
