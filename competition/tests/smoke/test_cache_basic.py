import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

import toffee_test

from src.utils import simplebus as sb


@toffee_test.testcase
async def test_read_miss_hit_and_write_hit_smoke(cache_env):
    env = cache_env
    env.reset()

    addr = 0x8000_0000
    fill_data = 0x1122_3344_5566_7788
    write_data = 0xAABB_CCDD_EEFF_0011

    miss, miss_mem = env.send_cpu_request(
        sb.CpuRequest(cmd=sb.READ, addr=addr, user=0x101),
        refill_data=fill_data,
    )
    env.scoreboard.check_read_response(miss, expected_data=fill_data, expected_user=0x101)
    env.scoreboard.check_single_read_burst(miss_mem, expected_addr=addr)

    hit, hit_mem = env.send_cpu_request(
        sb.CpuRequest(cmd=sb.READ, addr=addr, user=0x102),
        refill_data=0xDEAD,
    )
    env.scoreboard.check_read_response(hit, expected_data=fill_data, expected_user=0x102)
    env.scoreboard.check_no_memory_request(hit_mem)

    write, write_mem = env.send_cpu_request(
        sb.CpuRequest(cmd=sb.WRITE, addr=addr, wdata=write_data, wmask=0xFF, user=0x103)
    )
    env.scoreboard.check_write_response(write, expected_user=0x103)
    env.scoreboard.check_no_memory_request(write_mem)

    reread, reread_mem = env.send_cpu_request(
        sb.CpuRequest(cmd=sb.READ, addr=addr, user=0x104),
        refill_data=0xBEEF,
    )
    env.scoreboard.check_read_response(reread, expected_data=write_data, expected_user=0x104)
    env.scoreboard.check_no_memory_request(reread_mem)
