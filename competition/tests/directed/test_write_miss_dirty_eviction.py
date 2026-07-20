import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

import toffee_test

from src.utils import simplebus as sb


def _uniform_beats(value):
    return [value] * 8


@toffee_test.testcase
async def test_write_miss_dirty_victim_writeback_and_refill(cache_env):
    """WRITE miss to a full dirty set triggers writeback then refill then WRITE_RESP.

    Fills 4 ways of one set, dirties each with a write hit, then sends a WRITE
    to a 5th conflicting address.  The cache must evict a dirty victim
    (WRITE_BURST / WRITE_LAST), fetch the new line (READ_BURST), merge the
    write data, and return WRITE_RESP.
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
            sb.CpuRequest(cmd=sb.READ, addr=line_base, user=0xA00 + index),
            refill_beats=_uniform_beats(fill_value),
        )
        env.scoreboard.check_read_response(response, expected_data=fill_value, expected_user=0xA00 + index)
        env.scoreboard.check_single_read_burst(mem_requests, expected_addr=line_base)

    dirty_writes = [
        (line_bases[0], fill_values[0], 0x01, 0xA10),
        (line_bases[1], fill_values[1], 0x06, 0xA11),
        (line_bases[2], fill_values[2], 0x0F, 0xA12),
        (line_bases[3], fill_values[3], 0xF0, 0xA13),
    ]
    for line_base, fill_value, wmask, user in dirty_writes:
        write, write_mem = env.send_cpu_request(
            sb.CpuRequest(cmd=sb.WRITE, addr=line_base, wdata=fill_value, wmask=wmask, user=user)
        )
        env.scoreboard.check_write_response(write, expected_user=user)
        env.scoreboard.check_no_memory_request(write_mem)

    write_data = 0xCAFE_BABE_DEAD_BEEF
    refill_value = 0x9999_8888_7777_6666
    response, mem_requests = env.send_cpu_request(
        sb.CpuRequest(cmd=sb.WRITE, addr=conflict_base, wdata=write_data, wmask=0xFF, user=0xA20),
        refill_data=refill_value,
    )
    env.scoreboard.check_write_response(response, expected_user=0xA20)

    write_reqs = [req for req in mem_requests if req.cmd in {sb.WRITE_BURST, sb.WRITE_LAST}]
    read_reqs = [req for req in mem_requests if req.cmd == sb.READ_BURST]
    assert write_reqs, "dirty eviction must generate writeback"
    assert write_reqs[-1].cmd == sb.WRITE_LAST
    assert read_reqs, "write miss must generate READ_BURST for refill"
    assert read_reqs[0].cmd == sb.READ_BURST
    assert read_reqs[0].addr == conflict_base
    assert mem_requests.index(write_reqs[0]) < mem_requests.index(read_reqs[0]), \
        "writeback must precede refill"

    victim_addr = write_reqs[0].addr
    assert victim_addr in line_bases, \
        f"victim addr 0x{victim_addr:x} must be one of the original 4 ways"

    r, m = env.send_cpu_request(
        sb.CpuRequest(cmd=sb.READ, addr=conflict_base, user=0xA30),
    )
    env.scoreboard.check_read_response(r, expected_data=write_data, expected_user=0xA30)
    env.scoreboard.check_no_memory_request(m)


@toffee_test.testcase
async def test_write_miss_dirty_eviction_preserves_write_merge(cache_env):
    """Partial-mask WRITE miss with dirty eviction merges write data correctly.

    After dirty eviction + refill, the write data must be merged into the
    refilled line using the write mask.  A subsequent read must return the
    merged result.
    """
    env = cache_env
    env.reset()

    set_base = 0x8000_0000
    conflict_base = set_base + 0x8000
    line_bases = [set_base + index * 0x2000 for index in range(4)]
    fill_values = [
        0xAAAA_AAAA_AAAA_AAAA,
        0xBBBB_BBBB_BBBB_BBBB,
        0xCCCC_CCCC_CCCC_CCCC,
        0xDDDD_DDDD_DDDD_DDDD,
    ]

    for index, (line_base, fill_value) in enumerate(zip(line_bases, fill_values)):
        response, mem_requests = env.send_cpu_request(
            sb.CpuRequest(cmd=sb.READ, addr=line_base, user=0xB00 + index),
            refill_beats=_uniform_beats(fill_value),
        )
        env.scoreboard.check_read_response(response, expected_data=fill_value, expected_user=0xB00 + index)
        env.scoreboard.check_single_read_burst(mem_requests, expected_addr=line_base)

    for line_base in line_bases:
        write, write_mem = env.send_cpu_request(
            sb.CpuRequest(cmd=sb.WRITE, addr=line_base, wdata=0xDEAD_BEEF_CAFE_BABE, wmask=0xFF, user=0xB10)
        )
        env.scoreboard.check_write_response(write, expected_user=0xB10)
        env.scoreboard.check_no_memory_request(write_mem)

    write_wdata = 0x0000_0000_0000_00FF
    write_wmask = 0x01
    refill_data = 0x1111_2222_3333_4444
    response, mem_requests = env.send_cpu_request(
        sb.CpuRequest(cmd=sb.WRITE, addr=conflict_base, wdata=write_wdata, wmask=write_wmask, user=0xB20),
        refill_data=refill_data,
    )
    env.scoreboard.check_write_response(response, expected_user=0xB20)

    assert any(req.cmd == sb.WRITE_BURST for req in mem_requests), "expected dirty writeback"
    assert any(req.cmd == sb.READ_BURST for req in mem_requests), "expected refill READ_BURST"

    expected_merged = sb.mask_write_64(refill_data, write_wdata, write_wmask)
    r, m = env.send_cpu_request(
        sb.CpuRequest(cmd=sb.READ, addr=conflict_base, user=0xB30),
    )
    env.scoreboard.check_read_response(r, expected_data=expected_merged, expected_user=0xB30)
    env.scoreboard.check_no_memory_request(m)


@toffee_test.testcase
async def test_writeback_multi_beat_counter_exercise(cache_env):
    """DIR-020: Multi-beat writeback exercises the writeL2BeatCnt counter path.

    Fills and dirties 4 ways, then sends a WRITE miss to force dirty eviction
    with a full 8-beat writeback.  Drives io_out_mem_req_ready=1 throughout
    so the writeback beat counter increments on each beat.

    Targets CacheStage3 lines:
      550: writeL2BeatCnt increment (TRUE branch: _T_5 & WRITE cmd)
      555: writeL2BeatCnt used as data word index
      626: writeL2BeatCnt reset on WRITE_BURST
    """
    env = cache_env
    env.reset()

    set_base = 0x800F_0000
    conflict_base = set_base + 0x8000
    line_bases = [set_base + idx * 0x2000 for idx in range(4)]

    fill_values = [
        0xAAA0_AAA0_AAA0_AAA0,
        0xBBB1_BBB1_BBB1_BBB1,
        0xCCC2_CCC2_CCC2_CCC2,
        0xDDD3_DDD3_DDD3_DDD3,
    ]

    for idx, (line_base, fill_value) in enumerate(zip(line_bases, fill_values)):
        response, mem_requests = env.send_cpu_request(
            sb.CpuRequest(cmd=sb.READ, addr=line_base, user=0xD00 + idx),
            refill_beats=[fill_value] * 8,
        )
        env.scoreboard.check_read_response(response, expected_data=fill_value, expected_user=0xD00 + idx)

    for line_base in line_bases:
        write, _ = env.send_cpu_request(
            sb.CpuRequest(cmd=sb.WRITE, addr=line_base, wdata=0xFFFF_FFFF_FFFF_FFFF, wmask=0xFF, user=0xD10)
        )
        env.scoreboard.check_write_response(write, expected_user=0xD10)

    write_data = 0xCAFE_BABE_DEAD_BEEF
    refill_value = 0x9999_8888_7777_6666
    response, mem_requests = env.send_cpu_request(
        sb.CpuRequest(cmd=sb.WRITE, addr=conflict_base, wdata=write_data, wmask=0xFF, user=0xD20),
        refill_data=refill_value,
    )
    env.scoreboard.check_write_response(response, expected_user=0xD20)

    write_reqs = [req for req in mem_requests if req.cmd in {sb.WRITE_BURST, sb.WRITE_LAST}]
    read_reqs = [req for req in mem_requests if req.cmd == sb.READ_BURST]
    assert write_reqs, "dirty eviction must generate writeback beats"
    assert write_reqs[-1].cmd == sb.WRITE_LAST, "last writeback beat must be WRITE_LAST"
    assert read_reqs, "write miss must generate READ_BURST refill"

    # Verify writeback beats came before refill
    assert mem_requests.index(write_reqs[0]) < mem_requests.index(read_reqs[0]), \
        "writeback must precede refill"

    # Verify the refilled line has correct merged data
    r, _ = env.send_cpu_request(
        sb.CpuRequest(cmd=sb.READ, addr=conflict_base, user=0xD30),
    )
    env.scoreboard.check_read_response(r, expected_data=write_data, expected_user=0xD30)
