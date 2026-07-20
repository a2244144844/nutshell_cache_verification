import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

import toffee_test

from src.utils import simplebus as sb


def _uniform_beats(value):
    return [value] * 8


@toffee_test.testcase
async def test_write_miss_clean_full_mask(cache_env):
    """CPU WRITE to a cold address triggers READ_BURST, refill, then WRITE_RESP."""
    env = cache_env
    env.reset()

    addr = 0x8000_0000
    write_data = 0xCAFE_BABE_DEAD_BEEF
    refill_data = 0x1122_3344_5566_7788

    response, mem_requests = env.send_cpu_request(
        sb.CpuRequest(cmd=sb.WRITE, addr=addr, wdata=write_data, wmask=0xFF, user=0x701),
        refill_data=refill_data,
    )
    env.scoreboard.check_write_response(response, expected_user=0x701)

    read_reqs = [req for req in mem_requests if req.cmd == sb.READ_BURST]
    assert len(read_reqs) == 1
    assert read_reqs[0].addr == addr

    reread, reread_mem = env.send_cpu_request(
        sb.CpuRequest(cmd=sb.READ, addr=addr, user=0x702),
    )
    env.scoreboard.check_read_response(reread, expected_data=write_data, expected_user=0x702)
    env.scoreboard.check_no_memory_request(reread_mem)


@toffee_test.testcase
async def test_write_miss_partial_mask_merges_with_refill(cache_env):
    """Byte-mask write miss only overwrites selected bytes; rest come from refill."""
    env = cache_env
    env.reset()

    addr = 0x8000_2000
    refill_data = 0xAAAA_BBBB_CCCC_DDDD
    write_data = 0x0000_0000_0000_00FF
    wmask = 0x01

    response, mem_requests = env.send_cpu_request(
        sb.CpuRequest(cmd=sb.WRITE, addr=addr, wdata=write_data, wmask=wmask, user=0x711),
        refill_data=refill_data,
    )
    env.scoreboard.check_write_response(response, expected_user=0x711)

    assert any(req.cmd == sb.READ_BURST for req in mem_requests)

    expected_merged = sb.mask_write_64(refill_data, write_data, wmask)
    reread, reread_mem = env.send_cpu_request(
        sb.CpuRequest(cmd=sb.READ, addr=addr, user=0x712),
    )
    env.scoreboard.check_read_response(reread, expected_data=expected_merged, expected_user=0x712)
    env.scoreboard.check_no_memory_request(reread_mem)


@toffee_test.testcase
async def test_write_miss_8beat_refill_merges_correctly(cache_env):
    """Write miss with full 8-beat refill merges wdata into the target word.

    The cache refills in wrap-around order starting from the access word
    offset (word 5).  Beats are provided in that order.
    """
    env = cache_env
    env.reset()

    start_word = 5
    line_base = 0x8000_4000
    addr = line_base + start_word * 8
    write_data = 0xDEAD_BEEF_CAFE_BABE

    beat_values = [0x0100_0000_0000_0000 | (i * 0x0010_0010_0010_0010) for i in range(8)]
    refill_beats = [beat_values[(start_word + i) % 8] for i in range(8)]

    response, mem_requests = env.send_cpu_request(
        sb.CpuRequest(cmd=sb.WRITE, addr=addr, wdata=write_data, wmask=0xFF, user=0x721),
        refill_beats=refill_beats,
    )
    env.scoreboard.check_write_response(response, expected_user=0x721)

    assert any(req.cmd == sb.READ_BURST for req in mem_requests)

    expected_by_addr = {}
    for beat_index, data in enumerate(refill_beats):
        word_index = (start_word + beat_index) % 8
        expected_by_addr[line_base + word_index * 8] = data
    expected_by_addr[addr] = write_data

    for word_index in range(8):
        r, m = env.send_cpu_request(
            sb.CpuRequest(cmd=sb.READ, addr=line_base + word_index * 8, user=0x730 + word_index),
        )
        env.scoreboard.check_read_response(r, expected_data=expected_by_addr[line_base + word_index * 8], expected_user=0x730 + word_index)
        env.scoreboard.check_no_memory_request(m)
