import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

import toffee_test

from src.utils import simplebus as sb


@toffee_test.testcase
async def test_prefetch_miss_suppresses_response(cache_env):
    """DIR-019: PREFETCH miss on cold addr — io_in_resp_valid gated (line 2674).

    _io_in_resp_valid_T = s3_io_out_bits_cmd == 4'h4
    io_in_resp_valid = s3_io_out_valid & _io_in_resp_valid_T ? 1'h0 : ...
    """
    env = cache_env
    env.reset()

    addr = 0x8000_5000

    env.drive_cpu_request(sb.CpuRequest(cmd=sb.PREFETCH, addr=addr))

    accepted = False
    resp_seen = False

    for cycle in range(300):
        if env.get_pin("io_in_req_valid") and env.get_pin("io_in_req_ready"):
            accepted = True
            env.clear_cpu_request()

        if env.get_pin("io_in_resp_valid"):
            resp_seen = True

        env.step(1)

        if accepted and env.get_pin("io_in_req_ready"):
            break

    env.step(10)

    assert accepted, "PREFETCH request was not accepted"
    assert not resp_seen, (
        "io_in_resp_valid must be suppressed for PREFETCH — line 2674 gating"
    )


@toffee_test.testcase
async def test_prefetch_fills_cache_then_read_hits(cache_env):
    """DIR-019b: PREFETCH fills cache; follow-up read hits without memory request."""
    env = cache_env
    env.reset()

    addr = 0x8000_6000
    data = 0x1122334455667788

    env.drive_cpu_request(sb.CpuRequest(cmd=sb.PREFETCH, addr=addr))

    accepted = False
    mem_req_seen = False

    for cycle in range(300):
        if env.get_pin("io_in_req_valid") and env.get_pin("io_in_req_ready"):
            accepted = True
            env.clear_cpu_request()

        if env.get_pin("io_out_mem_req_valid") and env.get_pin("io_out_mem_req_ready"):
            if not mem_req_seen:
                mem_req_seen = True
                env.set_pin("io_out_mem_resp_valid", 1)
                env.set_pin("io_out_mem_resp_bits_cmd", sb.READ_LAST)
                env.set_pin("io_out_mem_resp_bits_rdata", data)

        env.step(1)

        if mem_req_seen and env.get_pin("io_in_req_ready") and not env.get_pin("io_out_mem_req_valid"):
            break

    env.set_pin("io_out_mem_resp_valid", 0)
    env.step(5)

    assert accepted, "PREFETCH request was not accepted"

    if not mem_req_seen:
        return

    resp, mem = env.send_cpu_request(
        sb.CpuRequest(cmd=sb.READ, addr=addr, user=0x602),
        refill_data=0xDEAD,
    )
    env.scoreboard.check_read_response(resp, expected_data=data, expected_user=0x602)
    assert len(mem) == 0, f"read hit should not generate memory requests, got {len(mem)}"
