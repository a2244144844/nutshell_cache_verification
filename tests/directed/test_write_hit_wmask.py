import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

import toffee_test

from src.utils import simplebus as sb

# Each test independently fills a cache line at a unique base address
# then issues exactly one write hit targeting a specific wmask_class
# and word_offset combination.  Unique bases prevent shared-DUT
# conflicts across toffee fixtures.

_FILL = 0xDEAD_BEEF_CAFE_BABE


def _fill_and_write(env, base, wmask, offset):
    """Fill cache line at *base*, then write-hit it at *offset* with *wmask*."""
    resp, _ = env.send_cpu_request(
        sb.CpuRequest(cmd=sb.READ, addr=base, user=0x900),
        refill_data=_FILL,
    )
    env.scoreboard.check_read_response(resp, expected_data=_FILL, expected_user=0x900)

    addr = base + offset * 8
    resp, _ = env.send_cpu_request(
        sb.CpuRequest(cmd=sb.WRITE, addr=addr, wmask=wmask, wdata=0xFEED_0000_0000_0000, user=0x901),
    )
    env.scoreboard.check_write_response(resp, expected_user=0x901)


# ── byte wmask (single byte) at missing offsets 1,2,5,6,7 ──────────────────

@toffee_test.testcase
async def test_byte_offset_1(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_1000, 0x02, 1)

@toffee_test.testcase
async def test_byte_offset_2(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_1040, 0x04, 2)

@toffee_test.testcase
async def test_byte_offset_5(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_1080, 0x20, 5)

@toffee_test.testcase
async def test_byte_offset_6(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_10C0, 0x40, 6)

@toffee_test.testcase
async def test_byte_offset_7(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_1100, 0x80, 7)

# ── adjacent wmask (two adjacent bytes) at offsets 1,2,3,6,7 ────────────────

@toffee_test.testcase
async def test_adjacent_offset_1(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_1140, 0x06, 1)

@toffee_test.testcase
async def test_adjacent_offset_2(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_1180, 0x0C, 2)

@toffee_test.testcase
async def test_adjacent_offset_3(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_11C0, 0x18, 3)

@toffee_test.testcase
async def test_adjacent_offset_6(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_1200, 0x60, 6)

@toffee_test.testcase
async def test_adjacent_offset_7(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_1240, 0xC0, 7)

# ── low_half wmask (lower 4 bytes) at offsets 1,2,3,4,7 ────────────────────

@toffee_test.testcase
async def test_low_half_offset_1(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_1280, 0x0F, 1)

@toffee_test.testcase
async def test_low_half_offset_2(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_12C0, 0x0F, 2)

@toffee_test.testcase
async def test_low_half_offset_3(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_1300, 0x0F, 3)

@toffee_test.testcase
async def test_low_half_offset_4(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_1340, 0x0F, 4)

@toffee_test.testcase
async def test_low_half_offset_7(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_1380, 0x0F, 7)

# ── high_half wmask (upper 4 bytes) at offsets 1,2,3,4,5 ────────────────────

@toffee_test.testcase
async def test_high_half_offset_1(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_13C0, 0xF0, 1)

@toffee_test.testcase
async def test_high_half_offset_2(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_1400, 0xF0, 2)

@toffee_test.testcase
async def test_high_half_offset_3(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_1440, 0xF0, 3)

@toffee_test.testcase
async def test_high_half_offset_4(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_1480, 0xF0, 4)

@toffee_test.testcase
async def test_high_half_offset_5(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_14C0, 0xF0, 5)

# ── sparse wmask (non-standard pattern 0xAA) at offsets 2,3,4,5,6,7 ────────

@toffee_test.testcase
async def test_sparse_offset_2(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_1500, 0xAA, 2)

@toffee_test.testcase
async def test_sparse_offset_3(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_1540, 0xAA, 3)

@toffee_test.testcase
async def test_sparse_offset_4(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_1580, 0xAA, 4)

@toffee_test.testcase
async def test_sparse_offset_5(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_15C0, 0xAA, 5)

@toffee_test.testcase
async def test_sparse_offset_6(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_1600, 0xAA, 6)

@toffee_test.testcase
async def test_sparse_offset_7(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_1640, 0xAA, 7)

# ── byte wmask at offsets 3,4 ────────────────────────────────────────────

@toffee_test.testcase
async def test_byte_offset_3(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_2000, 0x08, 3)

@toffee_test.testcase
async def test_byte_offset_4(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_2040, 0x10, 4)

# ── adjacent wmask at offsets 0,4,5 ───────────────────────────────────────

@toffee_test.testcase
async def test_adjacent_offset_0(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_2080, 0x03, 0)

@toffee_test.testcase
async def test_adjacent_offset_4(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_20C0, 0x30, 4)

@toffee_test.testcase
async def test_adjacent_offset_5(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_2100, 0x60, 5)

# ── low_half wmask at offsets 0,5,6 ───────────────────────────────────────

@toffee_test.testcase
async def test_low_half_offset_0(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_2140, 0x0F, 0)

@toffee_test.testcase
async def test_low_half_offset_5(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_2180, 0x0F, 5)

@toffee_test.testcase
async def test_low_half_offset_6(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_21C0, 0x0F, 6)

# ── high_half wmask at offsets 0,6,7 ──────────────────────────────────────

@toffee_test.testcase
async def test_high_half_offset_0(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_2200, 0xF0, 0)

@toffee_test.testcase
async def test_high_half_offset_6(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_2240, 0xF0, 6)

@toffee_test.testcase
async def test_high_half_offset_7(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_2280, 0xF0, 7)

# ── full wmask at offsets 2,3,4,6,7 ───────────────────────────────────────

@toffee_test.testcase
async def test_full_offset_2(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_22C0, 0xFF, 2)

@toffee_test.testcase
async def test_full_offset_3(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_2300, 0xFF, 3)

@toffee_test.testcase
async def test_full_offset_4(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_2340, 0xFF, 4)

@toffee_test.testcase
async def test_full_offset_6(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_2380, 0xFF, 6)

@toffee_test.testcase
async def test_full_offset_7(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_23C0, 0xFF, 7)

# ── sparse wmask at offsets 0,1 ───────────────────────────────────────────

@toffee_test.testcase
async def test_sparse_offset_0(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_2400, 0xAA, 0)

@toffee_test.testcase
async def test_sparse_offset_1(cache_env):
    env = cache_env; env.reset()
    _fill_and_write(env, 0x8000_2440, 0xAA, 1)
