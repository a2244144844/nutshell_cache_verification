import sys
import json
import re
from pathlib import Path

import pytest
import toffee_test

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.env.cache_env import CacheEnv, load_dut_class
from src.utils.toffee_coverage import CacheCoverage


def _coverage_file_for_node(nodeid: str) -> Path:
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", nodeid).strip("_")
    return ROOT_DIR / "build" / "coverage" / f"{safe_name}.json"


@toffee_test.fixture
def cache_env(toffee_request, request: pytest.FixtureRequest):
    # Line coverage waivers (see docs/coverage_waiver_rationale.md):
    #   Category A/E: Assertion $fwrite failure messages (unreachable by design)
    #   Category B/G: D-cache forwarding signals (I-cache = always 0)
    #   Category D: io_flush[1] pipeline kill + needFlush register (blocked by D-cache assertion)
    #   Category F: LFSR all-zero dead state (unreachable without corruption)
    #   Category I: needFlush de-assertion (merged into Category D)
    #   Category J: CacheStage3 D-cache ports (structurally unreachable in I-cache)
    #   Category K: respToL1Last counter (I-cache single-beat limitation)
    #
    # Branch coverage waivers (Stage 12 — see docs/coverage_waiver_rationale.md):
    #   Category L: CacheStage2 forward-meta multiplexers (I-cache = always inactive)
    #   Category M: CacheStage3 D-cache forwarding + Chisel assertion branches
    #   Category N: DIR-019/020/021/022 target branches — unreachable in I-cache
    #     (writeL2BeatCnt, probe hit release, MMIO state, state2 false case, PREFETCH output)
    #
    # Expr coverage waivers (Stage 16 — see docs/coverage_waiver_rationale.md):
    #   Category O: Expr closure — assertion/dead-logic conditions unreachable in I-cache
    dut = toffee_request.create_dut(load_dut_class(),
        ignore_patterns=[
            "*Cache_top*",
            "Cache.v:138,148,150,152,202-207,240-241,262,263,274,411,420,460,524,532,550,555,558,605,608,610,626,768,777,787,788,796,824,876,877,889,900,901,913,924,925,937,948,949,961,2267,2276,2316,2418,2674,2861-2862",
        ])
    env = CacheEnv(dut, coverage=False)
    cov = CacheCoverage(env, step_ris=False)
    toffee_request.add_cov_groups(cov.groups, periodic_sample=True)
    cov.mark_test(request.node.nodeid)
    try:
        yield env
    finally:
        coverage_path = _coverage_file_for_node(request.node.nodeid)
        coverage_path.parent.mkdir(parents=True, exist_ok=True)
        coverage_path.write_text(json.dumps(cov.as_dict(), indent=2), encoding="utf-8")
        env.finish()
