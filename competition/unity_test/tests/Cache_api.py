"""Standard UCAgent API wrapper for the Cache DUT.

This module is intentionally thin: the real verification behavior remains in
``src.env.cache_env.CacheEnv`` and this file only exposes the conventional
``api_cache_*`` surface expected by UCAgent checkers.
"""

from pathlib import Path
import sys

import pytest


ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.env.cache_env import CacheEnv
from src.utils import simplebus as sb


def create_dut(request=None, *, coverage=False, reset=True):
    """Create a Cache verification environment.

    ``request`` is accepted for compatibility with UCAgent fixture checkers and
    pytest-style factory calls; the current Picker DUT does not require it.
    """
    _ = request
    env = CacheEnv.create(coverage=coverage)
    if reset:
        env.reset()
    return env


@pytest.fixture
def cache_env():
    env = create_dut()
    try:
        yield env
    finally:
        env.finish()


@pytest.fixture
def dut(cache_env):
    return cache_env.dut


def api_cache_reset(env, *, timeout=160):
    return env.reset(timeout=timeout)


def api_cache_step(env, cycles=1):
    return env.step(cycles)


def api_cache_set_pin(env, name, value):
    return env.set_pin(name, value)


def api_cache_get_pin(env, name):
    return env.get_pin(name)


def api_cache_cpu_request(*, cmd, addr, size=3, wmask=0, wdata=0, user=0):
    return sb.CpuRequest(cmd=cmd, addr=addr, size=size, wmask=wmask, wdata=wdata, user=user)


def api_cache_read_request(addr, *, size=3, user=0):
    return api_cache_cpu_request(cmd=sb.READ, addr=addr, size=size, user=user)


def api_cache_write_request(addr, data, *, size=3, wmask=0xFF, user=0):
    return api_cache_cpu_request(
        cmd=sb.WRITE,
        addr=addr,
        size=size,
        wmask=wmask,
        wdata=data,
        user=user,
    )


def api_cache_drive_cpu_request(env, request):
    return env.drive_cpu_request(request)


def api_cache_clear_cpu_request(env):
    return env.clear_cpu_request()


def api_cache_send_cpu_request(env, request, *, refill_data=0, refill_beats=None, timeout=100):
    return env.send_cpu_request(
        request,
        refill_data=refill_data,
        refill_beats=refill_beats,
        timeout=timeout,
    )


def api_cache_send_mmio_request(env, request, *, mmio_resp_data=0, write_resp_ok=True, timeout=200):
    return env.send_mmio_request(
        request,
        mmio_resp_data=mmio_resp_data,
        write_resp_ok=write_resp_ok,
        timeout=timeout,
    )


def api_cache_drive_mem_response(env, *, cmd, rdata=0):
    return env.drive_mem_response(cmd=cmd, rdata=rdata)


def api_cache_clear_mem_response(env):
    return env.clear_mem_response()


def api_cache_sample_mem_request(env):
    return env.sample_mem_request()


def api_cache_sample_mmio_request(env):
    return env.sample_mmio_request()


def api_cache_sample_cpu_response(env):
    return env.sample_cpu_response()


READ = sb.READ
WRITE = sb.WRITE
READ_BURST = sb.READ_BURST
WRITE_BURST = sb.WRITE_BURST
WRITE_RESP = sb.WRITE_RESP
READ_LAST = sb.READ_LAST
WRITE_LAST = sb.WRITE_LAST
PROBE = sb.PROBE
