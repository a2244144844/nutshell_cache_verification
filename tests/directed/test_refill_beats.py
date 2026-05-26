import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

from src.env.cache_env import CacheEnv
from src.utils import simplebus as sb


def test_read_miss_refills_full_line_in_burst_order():
    env = CacheEnv.create()

    try:
        env.reset()

        line_base = 0x8000_3000
        start_word = 3
        miss_addr = line_base + start_word * 8
        beats = [0xA000_0000_0000_0000 | i for i in range(8)]

        response, mem_requests = env.send_cpu_request(
            sb.CpuRequest(cmd=sb.READ, addr=miss_addr, user=0x401),
            refill_beats=beats,
        )
        env.scoreboard.check_read_response(response, expected_data=beats[0], expected_user=0x401)
        env.scoreboard.check_single_read_burst(mem_requests, expected_addr=miss_addr)

        expected_by_addr = {}
        for beat_index, data in enumerate(beats):
            word_index = (start_word + beat_index) % 8
            expected_by_addr[line_base + word_index * 8] = data

        for word_index in range(8):
            addr = line_base + word_index * 8
            user = 0x410 + word_index
            hit, hit_mem = env.send_cpu_request(sb.CpuRequest(cmd=sb.READ, addr=addr, user=user))
            env.scoreboard.check_read_response(
                hit,
                expected_data=expected_by_addr[addr],
                expected_user=user,
            )
            env.scoreboard.check_no_memory_request(hit_mem)
    finally:
        env.finish()
