import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

import toffee_test

from src.utils import simplebus as sb


@toffee_test.testcase
async def test_mmio_read_routes_through_mmio_interface(cache_env):
    """MMIO read bypasses cache: routes through io_mmio_*, no memory request."""
    env = cache_env
    env.reset()

    mmio_addr = 0x3000_0000
    mmio_data = 0xDEAD_BEEF_CAFE_BABE

    response, mem_requests, mmio_seen = env.send_mmio_request(
        sb.CpuRequest(cmd=sb.READ, addr=mmio_addr, user=0xA5),
        mmio_resp_data=mmio_data,
    )

    assert mmio_seen, "MMIO request should be forwarded on io_mmio_req"
    assert not mem_requests, f"expected no memory requests for MMIO, got {mem_requests}"

    assert response.cmd == sb.READ_LAST
    assert response.rdata == mmio_data
    assert response.user == 0xA5


@toffee_test.testcase
async def test_mmio_write_routes_through_mmio_interface(cache_env):
    """MMIO write bypasses cache: routes through io_mmio_*, returns WRITE_RESP."""
    env = cache_env
    env.reset()

    mmio_addr = 0x3000_1000
    mmio_wdata = 0x1122_3344_5566_7788

    response, mem_requests, mmio_seen = env.send_mmio_request(
        sb.CpuRequest(cmd=sb.WRITE, addr=mmio_addr, wdata=mmio_wdata, wmask=0xFF, user=0xB5),
    )

    assert mmio_seen, "MMIO write should be forwarded on io_mmio_req"
    assert not mem_requests, f"expected no memory requests for MMIO, got {mem_requests}"

    assert response.cmd == sb.WRITE_RESP
    assert response.user == 0xB5


@toffee_test.testcase
async def test_mmio_read_never_hits_in_cache(cache_env):
    """Repeated MMIO read always goes through io_mmio_*, never hits in cache."""
    env = cache_env
    env.reset()

    mmio_addr = 0x4000_0000
    mmio_data_1 = 0xAAAA_BBBB_CCCC_DDDD
    mmio_data_2 = 0x1111_2222_3333_4444

    response, mem_requests, mmio_seen = env.send_mmio_request(
        sb.CpuRequest(cmd=sb.READ, addr=mmio_addr, user=0x01),
        mmio_resp_data=mmio_data_1,
    )
    assert mmio_seen
    assert not mem_requests
    assert response.rdata == mmio_data_1

    response, mem_requests, mmio_seen = env.send_mmio_request(
        sb.CpuRequest(cmd=sb.READ, addr=mmio_addr, user=0x02),
        mmio_resp_data=mmio_data_2,
    )
    assert mmio_seen, "second MMIO read should still route through MMIO, not cache hit"
    assert not mem_requests
    assert response.rdata == mmio_data_2, "second MMIO should return fresh data, not cached"


@toffee_test.testcase
async def test_mmio_address_in_upper_range(cache_env):
    """MMIO bypass works for addresses in the 0x40000000-0x7FFFFFFF range."""
    env = cache_env
    env.reset()

    mmio_addr = 0x5000_0000
    mmio_data = 0xF00D_F00D_F00D_F00D

    response, mem_requests, mmio_seen = env.send_mmio_request(
        sb.CpuRequest(cmd=sb.READ, addr=mmio_addr, user=0xC0),
        mmio_resp_data=mmio_data,
    )

    assert mmio_seen
    assert not mem_requests
    assert response.cmd == sb.READ_LAST
    assert response.rdata == mmio_data
