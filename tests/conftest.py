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
    #   Category D: io_flush[1] pipeline kill (blocked by D-cache assertion)
    #   Category F: LFSR all-zero dead state (unreachable without corruption)
    dut = toffee_request.create_dut(load_dut_class(),
        ignore_patterns=[
            "*Cache_top*",
            "Cache.v:138,240-241,263,411,420,460,524,877,901,925,949,2267,2276,2316,2418,2861-2862",
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
