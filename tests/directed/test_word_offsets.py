import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

import toffee_test

from src.utils import simplebus as sb


@toffee_test.testcase
async def test_same_line_word_offsets_are_independent_on_hits(cache_env):
    env = cache_env
    env.reset()

    line_base = 0x8000_2000
    first_word = 0x0102_0304_0506_0708

    miss, miss_mem = env.send_cpu_request(
        sb.CpuRequest(cmd=sb.READ, addr=line_base, user=0x301),
        refill_data=first_word,
    )
    env.scoreboard.check_read_response(miss, expected_data=first_word, expected_user=0x301)
    env.scoreboard.check_single_read_burst(miss_mem, expected_addr=line_base)

    expected_by_addr = {line_base: first_word}
    for word_index in range(1, 8):
        addr = line_base + word_index * 8
        data = 0x1000_0000_0000_0000 | (word_index * 0x0101_0101_0101_0101)
        user = 0x310 + word_index
        expected_by_addr[addr] = data

        write, write_mem = env.send_cpu_request(
            sb.CpuRequest(cmd=sb.WRITE, addr=addr, wdata=data, wmask=0xFF, user=user)
        )
        env.scoreboard.check_write_response(write, expected_user=user)
        env.scoreboard.check_no_memory_request(write_mem)

    for word_index in range(8):
        addr = line_base + word_index * 8
        user = 0x330 + word_index
        read, read_mem = env.send_cpu_request(sb.CpuRequest(cmd=sb.READ, addr=addr, user=user))
        env.scoreboard.check_read_response(
            read,
            expected_data=expected_by_addr[addr],
            expected_user=user,
        )
        env.scoreboard.check_no_memory_request(read_mem)
