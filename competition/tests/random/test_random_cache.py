import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

import toffee_test

from src.generator.cache_random import CacheRandomGenerator, ReferenceCacheModel
from src.utils import simplebus as sb
from src.utils.cache_coverage import CacheCoverageCollector


@toffee_test.testcase
async def test_constrained_random_cache_traffic(cache_env):
    env = cache_env
    seed = int(os.environ.get("CACHE_RANDOM_SEED", "7"))
    steps = int(os.environ.get("CACHE_RANDOM_STEPS", "18"))

    coverage = CacheCoverageCollector()
    generator = CacheRandomGenerator(seed=seed)
    model = ReferenceCacheModel()

    env.reset()

    for op in generator.build_workload(steps):
        if op.cmd == sb.READ and not model.has_line(op.line_base):
            response, mem_requests = env.send_cpu_request(op.request, refill_beats=op.refill_beats)
            env.scoreboard.check_read_response(response, expected_data=op.refill_beats[0], expected_user=op.user)
            write_reqs = [req for req in mem_requests if req.cmd in {sb.WRITE_BURST, sb.WRITE_LAST}]
            if write_reqs:
                victim_addr = write_reqs[0].addr
                victim_data = write_reqs[0].wdata
                env.scoreboard.check_dirty_writeback_refill(
                    mem_requests,
                    victim_addr=victim_addr,
                    refill_addr=op.addr,
                    expected_write_data=victim_data,
                )
            else:
                env.scoreboard.check_single_read_burst(mem_requests, expected_addr=op.addr)
            model.fill_line(op.line_base, op.word_index, op.refill_beats)
        elif op.cmd == sb.READ:
            response, mem_requests = env.send_cpu_request(op.request)
            expected_data = model.read_word(op.addr)
            env.scoreboard.check_read_response(response, expected_data=expected_data, expected_user=op.user)
            env.scoreboard.check_no_memory_request(mem_requests)
        else:
            model.write_word(op.addr, op.wdata, op.wmask)
            response, mem_requests = env.send_cpu_request(op.request)
            env.scoreboard.check_write_response(response, expected_user=op.user)
            env.scoreboard.check_no_memory_request(mem_requests)

        coverage.record(request=op.request, mem_requests=mem_requests, response=response)

    coverage_json = os.environ.get("CACHE_COVERAGE_JSON")
    if coverage_json:
        coverage.write_json(coverage_json)
