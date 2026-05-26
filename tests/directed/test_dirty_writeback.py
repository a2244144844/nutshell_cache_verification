import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

from src.env.cache_env import CacheEnv
from src.utils import simplebus as sb


def _uniform_beats(value):
    return [value] * 8


def test_dirty_victim_writeback_refills_on_set_conflict():
    env = CacheEnv.create()

    try:
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
                sb.CpuRequest(cmd=sb.READ, addr=line_base, user=0x500 + index),
                refill_beats=_uniform_beats(fill_value),
            )
            env.scoreboard.check_read_response(response, expected_data=fill_value, expected_user=0x500 + index)
            env.scoreboard.check_single_read_burst(mem_requests, expected_addr=line_base)

        dirty_writes = [
            (line_bases[0], fill_values[0], 0x01, 0x510),
            (line_bases[1], fill_values[1], 0x06, 0x511),
            (line_bases[2], fill_values[2], 0x0F, 0x512),
            (line_bases[3], fill_values[3], 0xF0, 0x513),
        ]

        for line_base, fill_value, wmask, user in dirty_writes:
            write, write_mem = env.send_cpu_request(
                sb.CpuRequest(cmd=sb.WRITE, addr=line_base, wdata=fill_value, wmask=wmask, user=user)
            )
            env.scoreboard.check_write_response(write, expected_user=user)
            env.scoreboard.check_no_memory_request(write_mem)

        refill_value = 0x5555_5555_5555_5555
        response, mem_requests = env.send_cpu_request(
            sb.CpuRequest(cmd=sb.READ, addr=conflict_base, user=0x520),
            refill_beats=_uniform_beats(refill_value),
        )
        env.scoreboard.check_read_response(response, expected_data=refill_value, expected_user=0x520)
        write_reqs = [req for req in mem_requests if req.cmd in {sb.WRITE_BURST, sb.WRITE_LAST}]
        read_reqs = [req for req in mem_requests if req.cmd in {sb.READ_BURST, sb.READ_LAST}]
        victim_data = write_reqs[0].wdata
        victim_addr = write_reqs[0].addr

        env.scoreboard.check_dirty_writeback_refill(
            mem_requests,
            victim_addr=victim_addr,
            refill_addr=conflict_base,
            expected_write_data=victim_data,
        )

        assert victim_addr in line_bases
        assert victim_data in set(fill_values)
        assert len(read_reqs) == 1
        assert read_reqs[0].cmd == sb.READ_BURST
        assert read_reqs[0].addr == conflict_base
    finally:
        env.finish()
