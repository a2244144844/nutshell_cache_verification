import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

import toffee_test

from src.generator.cache_random import CacheRandomGenerator
from src.utils import simplebus as sb


async def _drive_cpu_request(env, op):
    """Drive a CPU request and handle the response/minimal refill.

    For toggle coverage we don't need strict scoreboard checks —
    we just need to exercise the DUT signals. We drive requests,
    handle memory/mem responses enough to keep the pipeline moving,
    and collect any CPU response.
    """
    env.drive_cpu_request(op.request)
    accepted = False
    response = None
    refill_index = None
    refill_beats = list(op.refill_beats) if op.refill_beats else []

    for _ in range(300):
        if not accepted and env.get_pin("io_in_req_valid") and env.get_pin("io_in_req_ready"):
            accepted = True
            env.clear_cpu_request()

        mem_req_valid = env.get_pin("io_out_mem_req_valid")
        if mem_req_valid and refill_index is None:
            mem_cmd = env.get_pin("io_out_mem_req_bits_cmd")
            if mem_cmd == sb.READ_BURST and refill_beats:
                refill_index = 0
            elif mem_cmd in {sb.WRITE_BURST, sb.WRITE_LAST}:
                env.set_pin("io_out_mem_resp_valid", 1)
                env.set_pin("io_out_mem_resp_bits_cmd", sb.WRITE_RESP)

        if refill_index is not None and refill_index < len(refill_beats):
            env.set_pin("io_out_mem_resp_valid", 1)
            cmd = sb.READ_LAST if refill_index == len(refill_beats) - 1 else sb.READ
            env.set_pin("io_out_mem_resp_bits_cmd", cmd)
            env.set_pin("io_out_mem_resp_bits_rdata", refill_beats[refill_index])
            refill_index += 1
        elif refill_index is not None and refill_index >= len(refill_beats):
            env.set_pin("io_out_mem_resp_valid", 0)

        env.step(1)

        if env.get_pin("io_in_resp_valid") and response is None:
            response = True

        if accepted and response and (refill_index is None or refill_index >= len(refill_beats)):
            env.set_pin("io_out_mem_resp_valid", 0)
            env.step(2)
            return

    env.clear_cpu_request()
    env.set_defaults()
    env.step(5)


async def _handle_mmio(env, op):
    """Drive MMIO read/write."""
    env.drive_cpu_request(op.request)
    accepted = False
    response = None
    mmio_driven = False

    for _ in range(200):
        if not accepted and env.get_pin("io_in_req_valid") and env.get_pin("io_in_req_ready"):
            accepted = True
            env.clear_cpu_request()

        if env.get_pin("io_mmio_req_valid") and not mmio_driven:
            env.set_pin("io_mmio_resp_valid", 1)
            env.set_pin("io_mmio_resp_bits_rdata", 0xDEAD_BEEF_CAFE_BABE)
            mmio_driven = True
        elif mmio_driven and not env.get_pin("io_mmio_req_valid"):
            env.set_pin("io_mmio_resp_valid", 0)

        env.step(1)

        if env.get_pin("io_in_resp_valid") and response is None:
            response = True

        if accepted and response:
            env.step(2)
            return

    env.clear_cpu_request()
    env.set_defaults()
    env.step(5)


async def _drive_probe(env, op):
    """Drive coherence probe through io_out_coh_req_* pins."""
    env.set_pin("io_out_coh_req_bits_addr", op.addr)
    env.set_pin("io_out_coh_req_bits_size", 3)
    env.set_pin("io_out_coh_req_bits_cmd", sb.PROBE)
    env.set_pin("io_out_coh_req_bits_wmask", 0)
    env.set_pin("io_out_coh_req_bits_wdata", 0)
    env.set_pin("io_out_coh_req_valid", 1)

    for _ in range(200):
        env.step(1)
        if env.get_pin("io_out_coh_req_valid") and env.get_pin("io_out_coh_req_ready"):
            env.set_pin("io_out_coh_req_valid", 0)
        if env.get_pin("io_out_coh_resp_valid"):
            env.step(5)
            return

    env.set_pin("io_out_coh_req_valid", 0)


async def _drive_flush(env, op):
    """Assert and deassert io_flush."""
    env.set_pin("io_flush", 0x1)
    env.step(5)
    # Wait for io_empty
    for _ in range(50):
        if env.get_pin("io_empty"):
            break
        env.step(1)
    env.set_pin("io_flush", 0x0)
    env.step(10)


async def _run_seed_workload(env, seed: int, steps: int, extended: bool, max_toggle: bool = False):
    """Run a single-seed workload for toggle coverage."""
    generator = CacheRandomGenerator(seed=seed, enable_extended=extended,
                                     enable_max_toggle=max_toggle)

    for op in generator.build_workload(steps):
        addr_high = (op.addr >> 28) & 0xF
        is_mmio = (addr_high == 0x3) or (4 <= addr_high <= 7)

        if is_mmio and op.cmd in {sb.READ, sb.WRITE}:
            await _handle_mmio(env, op)
        elif op.cmd == sb.PROBE:
            await _drive_probe(env, op)
        elif op.cmd == 0xF:
            await _drive_flush(env, op)
        else:
            await _drive_cpu_request(env, op)

    env.step(5)


@toffee_test.testcase
async def test_multi_seed_random_cache_traffic(cache_env):
    """Multi-seed random traffic for toggle coverage improvement.

    Runs N seeds sequentially in a single test so that Verilator
    accumulates coverage across all seeds. Resets DUT between seeds.
    Uses extended traffic: MMIO, probe, flush, READ_BURST, PREFETCH,
    varied addresses, and varied data patterns.

    Note: Scoreboard checks are intentionally skipped — this test
    focuses exclusively on exercising toggle bits. Functional
    correctness is verified by the regression suite.
    """
    env = cache_env
    seeds_str = os.environ.get("CACHE_RANDOM_SEEDS", "7,13,42,99,256,31,77,128,512,1023")
    steps = int(os.environ.get("CACHE_RANDOM_STEPS", "200"))
    seeds = [int(s.strip()) for s in seeds_str.split(",") if s.strip()]

    for i, seed in enumerate(seeds):
        env.reset()
        await _run_seed_workload(env, seed, steps, extended=True, max_toggle=True)

    env.step(10)
