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

RTL line coverage is not currently collected. The active flow uses Picker-exported Verilator/Python simulation, which gives practical functional coverage but not an RTL line-coverage report in this workspace.

Submission interpretation:

- Functional coverage is closed in the Toffee model.
- RTL line coverage remains a known limitation and is recorded as a residual risk in `docs/ucagent_output/final_report_stage.md`.
- The project should not claim a numerical RTL line-coverage percentage unless a VCS/Verilator line-coverage flow is added later.
