import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

import toffee_test

from src.utils import simplebus as sb


@toffee_test.testcase
async def test_flush_while_idle(cache_env):
    env = cache_env
    env.reset()

    env.set_pin("io_flush", 0b01)
    env.step(5)

    assert env.get_pin("io_empty") == 1, "io_empty should be high while flush is asserted at idle"

    env.set_pin("io_flush", 0)
    env.step(5)

    addr = 0x8000_1000
    resp, mem = env.send_cpu_request(
        sb.CpuRequest(cmd=sb.READ, addr=addr, user=0x101),
        refill_data=0xCAFE,
    )
    env.scoreboard.check_read_response(resp, expected_data=0xCAFE, expected_user=0x101)
    env.scoreboard.check_single_read_burst(mem, expected_addr=addr)


@toffee_test.testcase
async def test_flush_during_miss(cache_env):
    env = cache_env
    env.reset()

    addr = 0x8000_2000

    env.drive_cpu_request(sb.CpuRequest(cmd=sb.READ, addr=addr, user=0x201))

    env.set_pin("io_flush", 0b01)

    accepted = False
    for _ in range(100):
        env.step(1)
        if env.get_pin("io_in_req_valid") and env.get_pin("io_in_req_ready"):
            accepted = True
            break
    assert accepted, "read miss request was not accepted"

    env.clear_cpu_request()

    assert env.get_pin("io_empty") == 1, "io_empty should be high after flush squashes the accepted request"

    env.set_pin("io_flush", 0)
    env.step(10)

    resp2, mem2 = env.send_cpu_request(
        sb.CpuRequest(cmd=sb.READ, addr=addr, user=0x202),
        refill_data=0xBEEF,
    )
    env.scoreboard.check_read_response(resp2, expected_data=0xBEEF, expected_user=0x202)
    env.scoreboard.check_single_read_burst(mem2, expected_addr=addr)


@toffee_test.testcase
async def test_flush_recovery(cache_env):
    env = cache_env
    env.reset()

    addr_a = 0x8000_3000
    addr_b = 0x8000_4000

    env.set_pin("io_flush", 0b01)
    env.step(5)
    env.set_pin("io_flush", 0)
    env.step(5)

    resp, mem = env.send_cpu_request(
        sb.CpuRequest(cmd=sb.READ, addr=addr_a, user=0x301),
        refill_data=0xDEAD_BEEF_CAFE_BABE,
    )
    env.scoreboard.check_read_response(resp, expected_data=0xDEAD_BEEF_CAFE_BABE, expected_user=0x301)
    env.scoreboard.check_single_read_burst(mem, expected_addr=addr_a)

    write_data = 0x1234_5678_9ABC_DEF0
    wresp, wmem = env.send_cpu_request(
        sb.CpuRequest(cmd=sb.WRITE, addr=addr_a, wdata=write_data, wmask=0xFF, user=0x302),
    )
    env.scoreboard.check_write_response(wresp, expected_user=0x302)
    env.scoreboard.check_no_memory_request(wmem)

    rresp, rmem = env.send_cpu_request(
        sb.CpuRequest(cmd=sb.READ, addr=addr_a, user=0x303),
    )
    env.scoreboard.check_read_response(rresp, expected_data=write_data, expected_user=0x303)
    env.scoreboard.check_no_memory_request(rmem)

    rresp2, mem2 = env.send_cpu_request(
        sb.CpuRequest(cmd=sb.READ, addr=addr_b, user=0x304),
        refill_data=0xAAAA_BBBB_CCCC_DDDD,
    )
    env.scoreboard.check_read_response(rresp2, expected_data=0xAAAA_BBBB_CCCC_DDDD, expected_user=0x304)
    env.scoreboard.check_single_read_burst(mem2, expected_addr=addr_b)


@toffee_test.testcase
async def test_flush_during_miss_then_recover_with_subsequent_request(cache_env):
    """Flush during miss then recover with a new request to a different
    address.  This exercises the needFlush de-assertion path (_T_5 & needFlush
    at line 788) and covers lines 558 (needFlush register) and 788
    (needFlush <= 0)."""
    env = cache_env
    env.reset()

    addr_a = 0x8000_2000
    addr_b = 0x8000_5000

    env.drive_cpu_request(sb.CpuRequest(cmd=sb.READ, addr=addr_a, user=0x401))

    env.set_pin("io_flush", 0b01)

    accepted = False
    for _ in range(100):
        env.step(1)
        if env.get_pin("io_in_req_valid") and env.get_pin("io_in_req_ready"):
            accepted = True
            break
    assert accepted, "read miss request was not accepted"

    env.clear_cpu_request()

    for _ in range(50):
        if env.get_pin("io_empty") == 1:
            break
        env.step(1)
    assert env.get_pin("io_empty") == 1, "io_empty should be high after flush squashes the accepted request"

    env.set_pin("io_flush", 0)
    env.step(10)

    resp, mem = env.send_cpu_request(
        sb.CpuRequest(cmd=sb.READ, addr=addr_b, user=0x402),
        refill_data=0xFEED_FACE_CAFE_BEEF,
    )
    env.scoreboard.check_read_response(resp, expected_data=0xFEED_FACE_CAFE_BEEF, expected_user=0x402)
    env.scoreboard.check_single_read_burst(mem, expected_addr=addr_b)


@toffee_test.testcase
async def test_needflush_assert_and_deassert(cache_env):
    """DIR-017: needFlush full lifecycle with low-level pin control.

    Uses manual pin driving for the second request to ensure step-by-step
    observability of the needFlush clear handshake (_T_5 & needFlush, i.e.
    io_out_ready & io_out_valid & needFlush).  Covers lines 558 (needFlush
    register declaration) and 787-788 (needFlush <= 0)."""
    env = cache_env
    env.reset()

    addr_a = 0x8000_2000
    addr_b = 0x8000_6000

    env.drive_cpu_request(sb.CpuRequest(cmd=sb.READ, addr=addr_a, user=0x501))

    env.set_pin("io_flush", 0b01)

    accepted = False
    for _ in range(100):
        env.step(1)
        if env.get_pin("io_in_req_valid") and env.get_pin("io_in_req_ready"):
            accepted = True
            break
    assert accepted, "read miss request was not accepted"

    env.clear_cpu_request()

    for _ in range(50):
        if env.get_pin("io_empty") == 1:
            break
        env.step(1)
    assert env.get_pin("io_empty") == 1, "io_empty should be high after flush squashes the accepted request"

    env.set_pin("io_flush", 0)
    env.step(10)

    env.set_pin("io_in_req_bits_addr", addr_b)
    env.set_pin("io_in_req_bits_size", 3)
    env.set_pin("io_in_req_bits_cmd", sb.READ)
    env.set_pin("io_in_req_bits_wmask", 0)
    env.set_pin("io_in_req_bits_wdata", 0)
    env.set_pin("io_in_req_bits_user", 0x502)
    env.set_pin("io_in_req_valid", 1)

    env.set_pin("io_out_mem_req_ready", 1)

    accepted_b = False
    mem_req_started = False
    mem_resp_driven = False
    mem_resp_done = False
    response = None

    for cycle in range(300):
        will_accept = bool(
            env.get_pin("io_in_req_valid") and env.get_pin("io_in_req_ready")
        )

        mem_req_valid = bool(env.get_pin("io_out_mem_req_valid"))
        if mem_req_valid and not mem_req_started:
            mem_req_started = True

        if mem_req_started and not mem_resp_driven:
            env.set_pin("io_out_mem_resp_valid", 1)
            env.set_pin("io_out_mem_resp_bits_cmd", sb.READ_LAST)
            env.set_pin("io_out_mem_resp_bits_rdata", 0xCAFE_B0B0_DEAD_BEEF)
            mem_resp_driven = True
        elif mem_resp_done:
            env.set_pin("io_out_mem_resp_valid", 0)

        if mem_resp_driven and not mem_resp_done:
            if bool(env.get_pin("io_out_mem_resp_valid")) and bool(
                env.get_pin("io_out_mem_resp_ready")
            ):
                mem_resp_done = True

        cur_valid = bool(env.get_pin("io_in_resp_valid"))
        if cur_valid and response is None:
            response = (
                env.get_pin("io_in_resp_bits_cmd"),
                env.get_pin("io_in_resp_bits_rdata"),
                env.get_pin("io_in_resp_bits_user"),
            )

        env.step(1)

        if will_accept and not accepted_b:
            accepted_b = True
            env.set_pin("io_in_req_valid", 0)

        if accepted_b and response is not None:
            break

    assert accepted_b, "second read request was not accepted"
    assert mem_req_started, "no memory request generated for second read"
    assert response is not None, "no CPU response received for second read"

    cmd, rdata, user = response
    assert cmd == sb.READ_LAST, f"expected cmd=READ_LAST(6), got {cmd}"
    assert rdata == 0xCAFE_B0B0_DEAD_BEEF, (
        f"expected rdata=0xCAFEB0B0DEADBEEF, got 0x{rdata:016x}"
    )
    assert user == 0x502, f"expected user=0x502, got {user}"

    env.step(5)
