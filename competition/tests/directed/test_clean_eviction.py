import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

import toffee_test

from src.utils import simplebus as sb


def _uniform_beats(value):
    return [value] * 8


@toffee_test.testcase
async def test_clean_eviction_replaces_victim_without_writeback(cache_env):
    """Fill 4 clean ways, then access a 5th conflicting address.

    The cache must replace one clean victim without issuing a writeback
    (no WRITE_BURST / WRITE_LAST), fetch the new line via READ_BURST, and
    preserve at least some of the original ways.  Re-reading with correct
    refill data avoids cascading evictions.
    """
    env = cache_env
    env.reset()

    set_base = 0x8000_0000
    conflict_base = set_base + 0x8000
    line_bases = [set_base + index * 0x2000 for index in range(4)]
    fill_values = [
        0x1111_1111_1111_1111,
        0x2222_2222_2222_2222,
        0x3333_3333_3333_3333,
        0x4444_4444_4444_4444,
    ]

    for index, (line_base, fill_value) in enumerate(zip(line_bases, fill_values)):
        response, mem_requests = env.send_cpu_request(
            sb.CpuRequest(cmd=sb.READ, addr=line_base, user=0x800 + index),
            refill_beats=_uniform_beats(fill_value),
        )
        env.scoreboard.check_read_response(response, expected_data=fill_value, expected_user=0x800 + index)
        env.scoreboard.check_single_read_burst(mem_requests, expected_addr=line_base)

    refill_value = 0x5555_5555_5555_5555
    response, mem_requests = env.send_cpu_request(
        sb.CpuRequest(cmd=sb.READ, addr=conflict_base, user=0x810),
        refill_beats=_uniform_beats(refill_value),
    )
    env.scoreboard.check_read_response(response, expected_data=refill_value, expected_user=0x810)

    write_reqs = [req for req in mem_requests if req.cmd in {sb.WRITE_BURST, sb.WRITE_LAST}]
    assert len(write_reqs) == 0, "clean eviction must not generate writeback"

    read_reqs = [req for req in mem_requests if req.cmd == sb.READ_BURST]
    assert len(read_reqs) == 1
    assert read_reqs[0].addr == conflict_base

    evicted = 0
    surviving = 0
    for index, (line_base, fill_value) in enumerate(zip(line_bases, fill_values)):
        r, m = env.send_cpu_request(
            sb.CpuRequest(cmd=sb.READ, addr=line_base, user=0x820 + index),
            refill_data=fill_value,
        )
        if not m:
            surviving += 1
            env.scoreboard.check_read_response(r, expected_data=fill_value, expected_user=0x820 + index)
        else:
            evicted += 1

    assert evicted >= 1, f"expected at least 1 evicted way, got {evicted}"
    assert surviving >= 1, f"expected at least 1 surviving way, got {surviving}"

    r, m = env.send_cpu_request(
        sb.CpuRequest(cmd=sb.READ, addr=conflict_base, user=0x830),
    )
    env.scoreboard.check_read_response(r, expected_data=refill_value, expected_user=0x830)
    env.scoreboard.check_no_memory_request(m)


@toffee_test.testcase
async def test_clean_eviction_all_surviving_ways_untouched(cache_env):
    """After clean eviction, non-evicted ways must still return original data.

    This test fills 4 ways with distinct per-word data and checks every word
    of each surviving line to catch partial-line corruption.
    """
    env = cache_env
    env.reset()

    set_base = 0x8000_0000
    conflict_base = set_base + 0x8000
    line_bases = [set_base + index * 0x2000 for index in range(4)]

    refill_by_line = {}
    for index, line_base in enumerate(line_bases):
        beats = [0xA000_0000_0000_0000 | (index << 40) | (w << 16) for w in range(8)]
        response, mem_requests = env.send_cpu_request(
            sb.CpuRequest(cmd=sb.READ, addr=line_base, user=0x900 + index),
            refill_beats=beats,
        )
        env.scoreboard.check_read_response(response, expected_data=beats[0], expected_user=0x900 + index)
        env.scoreboard.check_single_read_burst(mem_requests, expected_addr=line_base)
        refill_by_line[line_base] = {line_base + w * 8: data for w, data in enumerate(beats)}

    new_beats = [0xBBBB_0000_0000_0000 | (w * 0x0100_0000_0000_0000) for w in range(8)]
    response, mem_requests = env.send_cpu_request(
        sb.CpuRequest(cmd=sb.READ, addr=conflict_base, user=0x910),
        refill_beats=new_beats,
    )
    env.scoreboard.check_read_response(response, expected_data=new_beats[0], expected_user=0x910)
    assert not [req for req in mem_requests if req.cmd in {sb.WRITE_BURST, sb.WRITE_LAST}]

    new_refill = {}
    for w, data in enumerate(new_beats):
        new_refill[conflict_base + w * 8] = data

    for line_base, expected_words in refill_by_line.items():
        r, m = env.send_cpu_request(
            sb.CpuRequest(cmd=sb.READ, addr=line_base, user=0x920),
        )
        if m:
            continue
        for word_offset in range(8):
            addr = line_base + word_offset * 8
            r2, m2 = env.send_cpu_request(
                sb.CpuRequest(cmd=sb.READ, addr=addr, user=0x930 + word_offset),
            )
            env.scoreboard.check_read_response(
                r2,
                expected_data=expected_words[addr],
                expected_user=0x930 + word_offset,
            )
            env.scoreboard.check_no_memory_request(m2)

    for addr, expected in new_refill.items():
        r, m = env.send_cpu_request(
            sb.CpuRequest(cmd=sb.READ, addr=addr, user=0x940),
        )
        if not m:
            env.scoreboard.check_read_response(r, expected_data=expected, expected_user=0x940)
            env.scoreboard.check_no_memory_request(m)
