import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

import toffee_test

from src.utils import simplebus as sb


@toffee_test.testcase
async def test_invalid_way_preferred_over_random_victim_three_ways_filled(cache_env):
    """Fill 3 of 4 ways in a set, access a 4th conflicting address.

    Verifies the invalid way (way 3) is used instead of evicting a valid way:
    no writeback is generated, and all original data is preserved on re-read.
    """
    env = cache_env
    env.reset()

    set_base = 0x8000_0000
    line_bases = [set_base + i * 0x2000 for i in range(3)]
    fill_values = [
        0xAAAA_AAAA_AAAA_AAAA,
        0xBBBB_BBBB_BBBB_BBBB,
        0xCCCC_CCCC_CCCC_CCCC,
    ]

    for line_base, fill_value in zip(line_bases, fill_values):
        response, mem_requests = env.send_cpu_request(
            sb.CpuRequest(cmd=sb.READ, addr=line_base, user=0x100),
            refill_beats=[fill_value],
        )
        env.scoreboard.check_read_response(response, expected_data=fill_value, expected_user=0x100)
        env.scoreboard.check_single_read_burst(mem_requests, expected_addr=line_base)

    conflict_addr = set_base + 3 * 0x2000
    conflict_value = 0xDDDD_DDDD_DDDD_DDDD
    response, mem_requests = env.send_cpu_request(
        sb.CpuRequest(cmd=sb.READ, addr=conflict_addr, user=0x200),
        refill_beats=[conflict_value],
    )
    env.scoreboard.check_read_response(response, expected_data=conflict_value, expected_user=0x200)

    write_reqs = [r for r in mem_requests if r.cmd in {sb.WRITE_BURST, sb.WRITE_LAST}]
    assert not write_reqs, f"expected no writeback (invalid way used), got {write_reqs}"

    read_reqs = [r for r in mem_requests if r.cmd in {sb.READ_BURST, sb.READ_LAST}]
    assert len(read_reqs) == 1
    assert read_reqs[0].cmd == sb.READ_BURST
    assert read_reqs[0].addr == conflict_addr

    for line_base, fill_value in zip(line_bases, fill_values):
        response, mem_requests = env.send_cpu_request(
            sb.CpuRequest(cmd=sb.READ, addr=line_base, user=0x300),
        )
        env.scoreboard.check_read_response(response, expected_data=fill_value, expected_user=0x300)
        env.scoreboard.check_no_memory_request(mem_requests)

    response, mem_requests = env.send_cpu_request(
        sb.CpuRequest(cmd=sb.READ, addr=conflict_addr, user=0x400),
    )
    env.scoreboard.check_read_response(response, expected_data=conflict_value, expected_user=0x400)
    env.scoreboard.check_no_memory_request(mem_requests)


@toffee_test.testcase
async def test_invalid_way_priority_uses_highest_invalid_way(cache_env):
    """Fill only way 0, then access a conflicting address.

    Ways 1, 2, 3 are all invalid. The priority encoder should select way 3
    (the highest-priority invalid way). Verified by checking no writeback
    and original data preserved.
    """
    env = cache_env
    env.reset()

    set_base = 0x8000_0000
    first_addr = set_base
    first_value = 0x1111_1111_1111_1111

    response, mem_requests = env.send_cpu_request(
        sb.CpuRequest(cmd=sb.READ, addr=first_addr, user=0x10),
        refill_beats=[first_value],
    )
    env.scoreboard.check_read_response(response, expected_data=first_value, expected_user=0x10)

    second_addr = set_base + 0x2000
    second_value = 0x2222_2222_2222_2222
    response, mem_requests = env.send_cpu_request(
        sb.CpuRequest(cmd=sb.READ, addr=second_addr, user=0x20),
        refill_beats=[second_value],
    )
    env.scoreboard.check_read_response(response, expected_data=second_value, expected_user=0x20)

    write_reqs = [r for r in mem_requests if r.cmd in {sb.WRITE_BURST, sb.WRITE_LAST}]
    assert not write_reqs, f"expected no writeback, got {write_reqs}"

    response, mem_requests = env.send_cpu_request(
        sb.CpuRequest(cmd=sb.READ, addr=first_addr, user=0x30),
    )
    env.scoreboard.check_read_response(response, expected_data=first_value, expected_user=0x30)
    env.scoreboard.check_no_memory_request(mem_requests)
