# Cache.v Line Map Analysis

## Mapping Strategy

- Followed the `Guide_Doc/dut_line_func_map.md` format and used line ranges from `Cache/Cache.v`.
- Prioritized the validated functional paths first: top-level CPU interface, stage pipeline, refill/writeback, MMIO bypass, probe, flush, reset sweep, SRAM access, and arbitration.
- Kept generated initialization blocks, `RANDOMIZE_*` scaffolding, and other non-functional boilerplate under `IGNORE` so the map stays reviewable.
- Used broader CK spans where the RTL is a generated structural wrapper, and narrower spans where the block has clear behavioral meaning.

## Main Coverage Areas

- `FG-API/FC-API-CPU-SMOKE/CK-API-CPU-READ`: top-level request/response entry and Stage1 handshake logic.
- `FG-API/FC-API-RESET-READY/CK-API-RESET-SWEEP` and `CK-API-RESET-SETTLE`: metadata SRAM reset sweep, reset-aware wrappers, and reset recovery plumbing.
- `FG-CORE-CACHE/FC-CORE-HIT-PATH/CK-CORE-READ-HIT`: hit detection, resident-line access, and steady-state data selection.
- `FG-CORE-CACHE/FC-CORE-REFILL-WRITE-MISS/CK-CORE-READ-MISS`: pipeline staging, miss/refill control, and top-level refill wiring.
- `FG-CORE-CACHE/FC-CORE-REPLACEMENT-EVICTION/CK-CORE-INVALID-WAY` and `CK-CORE-DIRTY-WRITEBACK`: victim selection, dirty eviction, and writeback ordering.
- `FG-CORE-CACHE/FC-CORE-WRITE-MASK-OFFSET/CK-DIR-WMASK-BYTE`: byte/word mask handling and write merge behavior.
- `FG-MMIO-FLUSH-COH/FC-MMIO-BYPASS/CK-MMIO-READ` and `CK-MMIO-WRITE`: MMIO routing and bypass behavior.
- `FG-MMIO-FLUSH-COH/FC-COHERENCE-PROBE/CK-PROBE-HIT-CMD`: probe-hit/miss handling and coherence response path.
- `FG-MMIO-FLUSH-COH/FC-FLUSH-BEHAVIOR/CK-FLUSH-DRAIN` and `CK-FLUSH-RECOVERY`: flush state transitions, drain behavior, and return-to-idle recovery.
- `FG-API/FC-API-BACKPRESSURE/CK-API-REQ-HOLD` and `CK-API-RESP-HOLD`: arbiter steering and ready/valid stability at the API boundary.

## Remaining Refinement Candidates

- `CacheStage2` forward-data forwarding and waymask bookkeeping are mapped conservatively; they could be split further if a future refinement needs more granular hit-vs-forward coverage.
- `CacheStage3` response gating mixes hit, miss, probe, and MMIO control in a few broad spans; this is correct for coverage but still coarse for line-by-line review.
- The top-level wrapper instantiation section is structurally mapped rather than behaviorally decomposed, so it is the best target if a later pass wants finer traceability between stage wiring and specific CKs.
- The generated initial blocks for the SRAM wrappers and top-level pipeline are intentionally ignored; they do not need functional verification, but the ranges should be revisited if the generator changes layout.
