import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

import toffee_test

from src.utils import simplebus as sb


@toffee_test.testcase
async def test_partial_write_masks_update_selected_bytes(cache_env):
    env = cache_env
    env.reset()

    addr = 0x8000_1000
    expected = 0x0011_2233_4455_6677

    miss, miss_mem = env.send_cpu_request(
        sb.CpuRequest(cmd=sb.READ, addr=addr, user=0x201),
        refill_data=expected,
    )
    env.scoreboard.check_read_response(miss, expected_data=expected, expected_user=0x201)
    env.scoreboard.check_single_read_burst(miss_mem, expected_addr=addr)

    writes = [
        (0x1, 0xFFFF_FFFF_FFFF_FFAA, 0x202),
        (0x6, 0xFFFF_FFFF_FFBB_CCFF, 0x203),
        (0xF0, 0xDDCC_BBAA_FFFF_FFFF, 0x204),
        (0x99, 0xEEFF_FFFF_FFFF_0099, 0x205),
    ]

    for wmask, wdata, user in writes:
        expected = sb.mask_write_64(expected, wdata, wmask)
        write, write_mem = env.send_cpu_request(
            sb.CpuRequest(cmd=sb.WRITE, addr=addr, wdata=wdata, wmask=wmask, user=user)
        )
        env.scoreboard.check_write_response(write, expected_user=user)
        env.scoreboard.check_no_memory_request(write_mem)

        read, read_mem = env.send_cpu_request(
            sb.CpuRequest(cmd=sb.READ, addr=addr, user=user + 0x100)
        )
        env.scoreboard.check_read_response(read, expected_data=expected, expected_user=user + 0x100)
        env.scoreboard.check_no_memory_request(read_mem)
