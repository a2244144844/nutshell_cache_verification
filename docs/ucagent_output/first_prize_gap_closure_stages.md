# First-Prize Gap Closure Stages (P0/P1/P2)

**Project**: Track1 NutShell Cache Verification  
**Period**: 2026-05-31  
**Backend**: UCAgent + Claude Code CLI  
**Source**: `docs/gap_analysis_first_prize.md`

---

## Overview

This document consolidates the three gap-closure stage artifacts (Stages 18-20) that executed the P0, P1, and P2 action items from the first-prize gap analysis. These stages added polish, documentation depth, and submission-ready artifacts beyond the core verification closure.

| Stage | Config Key | Date | Focus |
|-------|------------|------|-------|
| 18 | `first_prize_gap_closure_p0` | 2026-05-31 | Core submission readiness (4 items) |
| 19 | `first_prize_gap_closure_p1` | 2026-05-31 | AI collaboration evidence depth (4 items) |
| 20 | `first_prize_gap_closure_p2` | 2026-05-31 | Polish & traceability (3 items) |

**Scoring Impact**: 76-85 → 90-100 (+14-24 points total)

---

## Stage 18: P0 Items — Core Submission Readiness

### P0-3: README Reviewer Quick Start
**Files**: `README.md`, `README_zh.md`

- Added 3-command quick start at top of both files:
  ```bash
  make reproduce        # One-command full validation
  open build/reports/rtl_coverage.html  # RTL coverage
  open build/reports/cache_coverage.html  # Funcov
  ```
- Synced all stale numbers:
  - Directed: 26 → 27 (later 28, 33)
  - Regression: 26 → 37 (later 38)
  - RTL Line: 99.6% → 100.0%
  - RTL Branch: 95.3% → 100.0%
  - RTL Expr: 95.6% → 100.0%
  - Toggle: 87.8% → 88.4%

### P0-4: verification_plan.md Data Sync
**File**: `docs/verification_plan.md`

- Updated Phase 2/3/4/5 results with final RTL coverage metrics
- Added complete waiver category documentation (A-O, T-A~T-F)
- Aligned phase status with actual test counts (38 tests)
- Documented reproducibility: `make clean && make reproduce -> PASS`

### P0-2: Bug Injection Expansion (2 → 7 bugs)
**Files**: `tests/injected_bug/run_bug_injection.py`, `docs/bug_tracking.md`

| Bug ID | Type | Injection Point | Detection |
|--------|------|-----------------|-----------|
| BUG-001 | Reference model data corruption | `read_word()` bit-0 flip | Scoreboard read check |
| BUG-003 | Address corruption | Request address bit flip | Scoreboard addr mismatch |
| BUG-004 | Dirty-bit loss in model | Reference model dirty tracking | Scoreboard writeback check |
| BUG-005 | Refill data scramble | Refill beat reordering | Scoreboard data check |
| BUG-006 | Request race condition | Concurrent req/resp timing | Monitor/Scoreboard |
| BUG-RTL-001 | RTL dirty-writeback bypass | `Cache.v:615` state transition | `test_dirty_writeback.py` |

- Each bug has `--disable-bug` recovery path (exit 0)
- Normal regression remains clean (38 passed)

### P0-1: Scoreboard Rewrite (35 → 194 lines)
**File**: `src/scoreboard/cache_scoreboard.py`

| Level | Methods | Purpose |
|-------|---------|---------|
| Basic | 6 | Single-transaction read/write/probe/MMIO/flush/response checks |
| Transaction | 4 | Multi-beat sequences, write-miss merge, eviction integrity |
| Consistency | 3 | Cross-transaction invariants, state machine protocol |

- All existing method signatures preserved (backward compatible)
- New methods used by directed tests for deeper checking

**Stage 18 Result**: `scripts/run_regression.sh` → 38 passed

---

## Stage 19: P1 Items — AI Collaboration Evidence Depth

### P1-8: Step 30 Attribution Fix
**File**: `docs/ai_collaboration_report.md`

Rewrote Step 30 to accurately reflect:
- **Human** discovered LCOV HTML (85%) vs `code_coverage.json` (95.3%) discrepancy
- **Human** directed WorkBuddy to trace toffee-test source (`processor.py:40`, `models.py`, `__init__.py:34`)
- **AI (WorkBuddy)** confirmed pipeline gap: `convert_line_coverage()` computes correct RTL data but `genhtml` only consumes C++-level `merged.info`
- Joint decision: Use RTL-level JSON as authoritative, generate `rtl_coverage.html` workaround, document gap

### P1-7: AI Effective Contributions Table
**File**: `docs/ai_collaboration_report.md`

Added 6-entry table of AI successes:
1. **UCAgent Stage Orchestration** — 18 stages via Codex/Claude Code
2. **GenSpec Specification Generation** — Spec chain + FG/FC/CK + line map
3. **Directed Test Scaffolding** — 27 tests with correct Pin/signal API
4. **Coverage Waiver Analysis** — Traced toffee-test source for branch gap
5. **RTL Coverage HTML Generation** — Submission-ready visualization
6. **Multi-Seed Toggle Test Design** — Framework + waiver categories

### P1-5: Expanded Defect Analysis (5 Before/After Cases)
**File**: `docs/ai_collaboration_report.md`

| Case | AI Raw Output | Human Discovery | Correction | Before→After |
|------|---------------|-----------------|------------|--------------|
| 1. DUT Boundary | Full NutShell RTL (~200 files) | Picker `example/Cache` is DUT | Fixed to `rtl/dut/Cache.v` | 0 pass → 1 pass |
| 2. Probe Timing | Clear valid BEFORE step(1) | Pipeline needs valid ACROSS clock edge | Drive→step→clear | Timeout → 3 pass |
| 3. Shallow CRV | 3 line bases, different sets | No set conflict → no eviction | 5 addresses same set + dirty | dirty_miss=0 → 1 |
| 4. Bug Injection | Modify `Cache.v` line 615 | Permanent RTL corruption risk | Python-layer + disable flag | No recovery → --disable-bug |
| 5. Flush Overreach | Assert `io_flush=0b11` | D-cache assertion blocks `io_flush[1]` | Use `io_flush=0b01` only | Crash → 4 pass |

### P1-6: Prompt Iteration Case Studies (3 Examples)
**File**: `docs/ai_collaboration_report.md`

1. **Dirty Writeback**: "Constrained random" → concrete microarch scenario (fill 4 ways, dirty victim, 5th access)
2. **Bug Safety**: "Inject bug" → "Python layer only, --disable-bug recovery path required"
3. **Probe Timing**: "Drive probe" → "Valid must span clock edge, clear AFTER step() like send_cpu_request"

**Stage 19 Result**: `scripts/run_regression.sh` → 38 passed (no regressions)

---

## Stage 20: P2 Items — Polish & Traceability

### P2-11: env.sh Portability Check
**File**: `scripts/env.sh`

Added fail-fast existence guards:
```bash
# PICKER_HOME: hard error if missing (required for DUT build)
if [ ! -d "$PICKER_HOME" ]; then
    echo "ERROR: PICKER_HOME not found at $PICKER_HOME" >&2
    return 1
fi

# JAVA_HOME: warning if missing (only for Chisel/Scala builds)
if [ ! -d "$JAVA_HOME" ]; then
    echo "WARN: JAVA_HOME not set; Chisel/Scala builds will fail" >&2
fi
```
Paths already portable (derived from `$ROOT_DIR`); this adds clear diagnostics.

### P2-10: Cross-Dimension Coverage Groups
**Files**: `src/utils/cache_coverage.py`, `src/utils/toffee_coverage.py`

| Cross Group | Dimensions | Bins | Purpose |
|-------------|------------|------|---------|
| `cache_write_hit_x_wmask` | write_mask_class × word_offset | 48 (6×8) | Write hit with specific mask at specific offset |
| `cache_miss_x_addr_type` | hit_miss × addr_class | 4 | Hit/miss cross normal/MMIO |
| `cache_probe_x_cache_state` | probe_hit/miss × cache_state | 6 | Probe result cross cache state at probe time |

**Python-level** (`cache_coverage.py`): Extended `EXPECTED_BINS` with 58 cross-dim bins; updated `record()` to compute automatically via `_line_dirty` tracking.

**Toffee-level** (`toffee_coverage.py`): 3 new `CovGroup`s + 3 tracker groups (`cache_req_tracker`, `cache_write_tracker`, `cache_probe_tracker`). State helpers: `_capture_req`, `_capture_write`, `_capture_probe_req`, `_eval_probe_cross`. Consolidated wmask classification into `@staticmethod _classify_wmask`.

**Key challenge**: DUT `io_out_coh_resp_bits` lacks `addr`; probe address captured from request side via `_capture_probe_req` → `_last_probe_addr`.

**Result**: 12 → 15 groups, 31 → 58+ points, 37 → 95 bins. Cross-dim bins exercised by multi-seed random traffic.

### P2-9: Requirements Traceability Matrix (RTM)
**File**: `docs/requirements_traceability_matrix.md`

10 requirement sections mapping every test, coverage group, and waiver:

| Section | Test Points | Coverage Groups |
|---------|-------------|-----------------|
| Core Cache | SMK-002~007 | `refill_path`, `cmd_type` |
| Write Mask & Word Offset | DIR-001~002 | `write_mask_class`, `word_offset` |
| Refill & Replacement | DIR-003~005, 011~013, 020 | `refill_path` (6 bins) |
| MMIO & Flush | DIR-006~007, 016~017 | `addr_class.mmio`, `flush_timing` |
| Coherence Probe | DIR-008, 014, 021 | `probe_result` |
| Backpressure | DIR-009~010 | `backpressure_loc` |
| Read Burst & Prefetch | DIR-015, 018~019, 022 | Structural |
| Random Verification | CRV-001~005 | All 95 bins |
| Bug Injection | BUG-001, RTL-001, 003~006 | 7 bugs + disable paths |
| Coverage Waivers | Categories A~O + T-A~T-F | 48 lines + 3,280 toggle |

Includes final coverage summary table and test execution timing (~60s full reproduce).

**Stage 20 Result**: `scripts/run_regression.sh` → 38 passed; `scripts/run_directed.sh` → 27 passed

---

## Cumulative Scoring Impact

| Dimension | Base | After P0 | After P1 | After P2 | Total Delta |
|-----------|------|----------|----------|----------|-------------|
| 覆盖率达标 (15) | 13-15 | +1-2 | — | +1 | **+2-3** |
| 人工干预与优化 (25) | 15-18 | +3 | +1-2 | — | **+4-5** |
| 工程规范 (20) | 16-17 | +1-2 | — | +1 | **+2-3** |
| **Total (100)** | **76-85** | **87-98** | **88-99** | **90-100** | **+14-24** |

---

## Files Changed Summary

| File | P0 | P1 | P2 |
|------|----|----|----|
| `README.md` / `README_zh.md` | ✅ | — | — |
| `docs/verification_plan.md` | ✅ | — | — |
| `tests/injected_bug/run_bug_injection.py` | ✅ | — | — |
| `docs/bug_tracking.md` | ✅ | — | — |
| `src/scoreboard/cache_scoreboard.py` | ✅ | — | — |
| `docs/ai_collaboration_report.md` | ✅ | ✅ | ✅ |
| `scripts/env.sh` | — | — | ✅ |
| `src/utils/cache_coverage.py` | — | — | ✅ |
| `src/utils/toffee_coverage.py` | — | — | ✅ |
| `docs/requirements_traceability_matrix.md` | — | — | ✅ |
| `docs/test_points.md` | — | — | ✅ |

---

## Verification Gates (All Pass)

```bash
# Stage 18
scripts/run_regression.sh → 38 passed

# Stage 19
scripts/run_regression.sh → 38 passed

# Stage 20
scripts/run_regression.sh → 38 passed
scripts/run_directed.sh   → 27 passed
scripts/collect_coverage_multi.sh → 38 passed
```

---

## Final Coverage (Post All Stages)

```
Line:   1359/1359 = 100.0%
Branch: 471/471  = 100.0%
Expr:   131/131 = 100.0%  (6 expr waived, Category O)
Toggle: 24947/28227 = 88.4%  (3,280 waived, T-A~T-F)
Funcov: 15 groups, 95 bins, 100% covered
Tests:  38 passed, 0 failures
```

All artifacts ready for first-prize submission.