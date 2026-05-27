# Cache Functions And Checks

## DUT Overall Function

The DUT is NutShell `Cache.v`, exported through Picker as `DUTCache`.
The verification target is a simple-bus cache block with CPU request/response,
memory refill/writeback, MMIO bypass, flush, and coherence probe interfaces.
The checks below are written in the UCAgent `FG/FC/CK` structure so that
`UnityChipCheckerLabelStructure` can parse the verification intent directly.

## Function Groups And Checkpoints

### Test API And Smoke Flow

<FG-API>

This group covers the reusable Python verification APIs and the basic
end-to-end cache flow used by the rest of the tests.

#### DUT Creation And Harness

<FC-API-HARNESS>

The harness loads the Picker-generated `DUTCache`, drives reset, creates
waveforms, and provides reusable request/response helpers.

- <CK-API-DUT-CREATE> `tests/conftest.py` and `src/env/cache_env.py` create a live DUT with deterministic reset.
- <CK-API-WAVE-DUMP> Directed and regression runs emit VCD files under `build/reports/`.
- <CK-API-HELPERS> `CacheEnv` exposes CPU, memory, MMIO, flush, and probe helper methods.

#### Smoke Read And Write

<FC-API-SMOKE>

The smoke test proves that a cold miss refills a line and later hits can use
the cached data.

- <CK-SMK-RESET-READY> Reset release leaves the CPU request path ready.
- <CK-SMK-READ-MISS> A cold read miss emits a memory `READ_BURST`.
- <CK-SMK-REFILL-LAST> The final refill beat returns `READ_LAST`.
- <CK-SMK-USER-METADATA> User metadata is preserved across the transaction.
- <CK-SMK-READ-HIT> A later read to the same line returns hit data.
- <CK-SMK-WRITE-HIT> A write hit returns `WRITE_RESP`.
- <CK-SMK-RAW-HIT> A read after write returns updated data.

### Core Cache Behavior

<FG-CORE-CACHE>

This group covers normal cacheable traffic, refill ordering, write masks,
replacement behavior, and writeback paths.

#### Write Mask And Offset Handling

<FC-WRITE-MASK-OFFSET>

The cache must merge partial writes with existing line contents and preserve
independent words within a line.

- <CK-DIR-WMASK-BYTE> Byte write masks update only selected bytes.
- <CK-DIR-WMASK-HALF> Half-word write masks update only selected bytes.
- <CK-DIR-WMASK-WORD> Full-word masks update the selected word.
- <CK-DIR-WORD-OFFSET> Same-line word offsets remain independent on hits.

#### Refill And Write Miss Handling

<FC-REFILL-WRITE-MISS>

Read and write misses must request the full refill burst, merge write data
when needed, and return the expected CPU response.

- <CK-DIR-REFILL-BEATS> Multi-beat refill data is consumed in burst order.
- <CK-DIR-WMISS-CLEAN-FULL> Clean write miss with full mask refills and updates the target word.
- <CK-DIR-WMISS-PARTIAL> Partial write miss merges write data with refill data.
- <CK-DIR-WMISS-REFILL-MERGE> Refilled line contents remain coherent after write miss completion.

#### Replacement And Eviction

<FC-REPLACEMENT-EVICTION>

Replacement should prefer invalid ways before random victim selection and
write back dirty victims before refilling a conflicting line.

- <CK-DIR-INVALID-WAY-SINGLE> A single invalid way is selected before valid victims.
- <CK-DIR-INVALID-WAY-THREE> Highest available invalid way priority is covered with three filled ways.
- <CK-DIR-CLEAN-EVICTION> Clean eviction replaces the victim without writeback.
- <CK-DIR-DIRTY-WRITEBACK> Dirty victim eviction emits writeback before refill.
- <CK-DIR-DIRTY-MERGE> Write miss after dirty eviction preserves the new write merge.

### MMIO Flush And Coherence

<FG-MMIO-FLUSH-COH>

This group covers non-cacheable bypass behavior, flush recovery, and coherence
probe responses.

#### MMIO Bypass

<FC-MMIO-BYPASS>

MMIO requests should bypass cache allocation and route through the MMIO
interface.

- <CK-DIR-MMIO-READ> MMIO read routes through the MMIO interface.
- <CK-DIR-MMIO-WRITE> MMIO write routes through the MMIO interface.
- <CK-DIR-MMIO-NO-HIT> MMIO read does not create a later cache hit.
- <CK-DIR-MMIO-UPPER> Upper MMIO address range is covered.

#### Flush Behavior

<FC-FLUSH-BEHAVIOR>

Flush must leave the pipeline empty and allow normal traffic after recovery.

- <CK-DIR-FLUSH-IDLE> Flush while idle keeps `io_empty` asserted.
- <CK-DIR-FLUSH-MISS> Flush during an in-flight miss drains the pipeline.
- <CK-DIR-FLUSH-RECOVERY> Normal traffic works after flush deassertion.

#### Coherence Probe

<FC-COHERENCE-PROBE>

The coherence probe path should report miss for absent lines and hit with data
for resident lines.

- <CK-DIR-PROBE-EMPTY-MISS> Probe miss is detected on an empty cache.
- <CK-DIR-PROBE-DIFFERENT-MISS> Probe miss is detected for a different resident line.
- <CK-DIR-PROBE-HIT-DATA> Probe hit returns the cached line data.

### Backpressure And Constrained Random

<FG-BACKPRESSURE-CRV>

This group covers ready/valid stability under backpressure and deterministic
constrained-random traffic with functional coverage.

#### Backpressure

<FC-BACKPRESSURE>

The DUT must hold requests and responses while the opposite side deasserts
ready.

- <CK-CORNER-MEM-REQ-HOLD> Memory request remains stable while `io_out_mem_req_ready` is low.
- <CK-CORNER-CPU-RESP-HOLD> CPU response remains available while `io_in_resp_ready` is low.

#### Constrained Random And Coverage

<FC-CRV-COVERAGE>

The random flow generates deterministic legal cache traffic, checks it with a
reference model, and records coverage bins.

- <CK-CRV-DETERMINISTIC> Random tests are seed-controlled and reproducible.
- <CK-CRV-REFMODEL> Random read/write results are checked against a reference model.
- <CK-CRV-COMMAND-BINS> Coverage records read/write command bins.
- <CK-CRV-HITMISS-BINS> Coverage records hit/miss proxy bins.
- <CK-CRV-MASK-OFFSET-BINS> Coverage records write-mask and word-offset bins.
- <CK-CRV-TOFFEE-CLOSURE> Toffee coverage reaches all tracked groups and bins.

### Bug Evidence And Reporting

<FG-EVIDENCE>

This group ties the executable tests to bug-injection evidence, reports, and
reproducibility.

#### Bug Injection Evidence

<FC-BUG-INJECTION>

The controlled bug-injection flow demonstrates that the verification
environment can detect a known faulty behavior without permanently modifying
the RTL.

- <CK-BUG-INJECT-TRIGGER> The injected scenario has a documented trigger.
- <CK-BUG-INJECT-DETECT> The scoreboard or checker reports the expected failure.
- <CK-BUG-INJECT-RECOVER> Normal regression remains clean after disabling injection.

#### Reproducibility And Reports

<FC-REPORTING>

The project keeps command results, coverage, waveforms, and UCAgent stage
evidence traceable from the top-level documents.

- <CK-REPORT-REGRESSION> `scripts/run_regression.sh` result is recorded.
- <CK-REPORT-REPRODUCE> `scripts/reproduce.sh` is the one-command reproducibility entry.
- <CK-REPORT-COVERAGE> Coverage reports list current bins and gaps.
- <CK-REPORT-UCAGENT> `docs/ucagent_output/` records UCAgent-driven stages.

## Current Results

```text
scripts/run_directed.sh -> 23 passed in 1.05s
scripts/run_regression.sh -> 26 passed in 1.34s
Toffee functional coverage -> 12 groups, 31 points, 37 bins, all covered
```
