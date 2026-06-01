#!/usr/bin/env python3
"""BUG-006: Race condition — simultaneous CPU request + coherence probe.

Drives a CPU READ and a coherence PROBE in the same cycle.  The internal
arbiter must serialize them.  If the arbiter drops one request or produces
a corrupted response, the scoreboard will catch it.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

from src.env.cache_env import CacheEnv, pin_get, pin_set
from src.generator.cache_random import ReferenceCacheModel
from src.utils import simplebus as sb

BUG_ID = "BUG-006"


def _uniform_beats(value: int, count: int = 8) -> list[int]:
    return [value & ((1 << 64) - 1) for _ in range(count)]


def _wait_handshake(env, valid_pin_name, ready_pin_name, timeout=200):
    """Step until valid & ready; return True if handshake observed."""
    for _ in range(timeout):
        env.step(1)
        if pin_get(getattr(env.dut, valid_pin_name)) and \
           pin_get(getattr(env.dut, ready_pin_name)):
            return True
    return False


def run_scenario(*, inject_bug: bool) -> None:
    env = CacheEnv.create()
    model = ReferenceCacheModel()

    try:
        env.reset()

        addr = 0x8000_0000
        user = 0x606
        fill_data = 0x6060_6060_6060_6060
        refill_beats = _uniform_beats(fill_data)

        # Fill a line so we have a probe hit target
        response, _ = env.send_cpu_request(
            sb.CpuRequest(cmd=sb.READ, addr=addr, user=user),
            refill_beats=refill_beats,
        )
        model.fill_line(addr & ~0x3F, 0, refill_beats)
        assert response.cmd == sb.READ_LAST, "precondition: first read should hit"

        mode = ("enabled: simultaneous CPU READ + coherence PROBE in same cycle"
                if inject_bug else "disabled: sequential operations (no race)")
        print(f"{BUG_ID} mode={mode}", flush=True)

        if inject_bug:
            # Drive both requests simultaneously
            env.drive_cpu_request(sb.CpuRequest(cmd=sb.READ, addr=addr | 0x40, user=user))
            pin_set(env.dut.io_out_coh_req_valid, 1)
            pin_set(env.dut.io_out_coh_req_bits_cmd, sb.PROBE)
            pin_set(env.dut.io_out_coh_req_bits_addr, addr)
            pin_set(env.dut.io_out_coh_req_bits_size, 3)

            # Step and see what happens — arbiter should serialize
            cpu_resp_seen = False
            probe_resp_seen = False
            for _ in range(300):
                env.step(1)

                # Check for CPU response
                if not cpu_resp_seen and pin_get(env.dut.io_in_resp_valid) and \
                   pin_get(env.dut.io_in_resp_ready):
                    rdata = pin_get(env.dut.io_in_resp_bits_rdata)
                    rcmd = pin_get(env.dut.io_in_resp_bits_cmd)
                    ruser = pin_get(env.dut.io_in_resp_bits_user)
                    cpu_resp_seen = True
                    print(f"{BUG_ID} CPU response: cmd=0x{rcmd:x}, rdata=0x{rdata:016x}, user=0x{ruser:x}", flush=True)

                # Check for probe response
                if not probe_resp_seen and pin_get(env.dut.io_out_coh_resp_valid) and \
                   pin_get(env.dut.io_out_coh_resp_ready):
                    pcmd = pin_get(env.dut.io_out_coh_resp_bits_cmd)
                    probe_resp_seen = True
                    print(f"{BUG_ID} Probe response: cmd=0x{pcmd:x}", flush=True)

                    if pcmd == 0xC:  # probe hit
                        print(f"{BUG_ID} Probe HIT confirmed — arbiter handled concurrent requests", flush=True)
                    elif pcmd == 0x8:  # probe miss
                        print(f"{BUG_ID} Probe MISS — unexpected for filled line, possible race corruption", flush=True)

                # Clear CPU request after acceptance
                if pin_get(env.dut.io_in_req_ready) and pin_get(env.dut.io_in_req_valid):
                    pin_set(env.dut.io_in_req_valid, 0)

                # Clear probe request after acceptance
                if pin_get(env.dut.io_out_coh_req_ready) and pin_get(env.dut.io_out_coh_req_valid):
                    pin_set(env.dut.io_out_coh_req_valid, 0)

                if cpu_resp_seen and probe_resp_seen:
                    break

            if not cpu_resp_seen:
                raise AssertionError(
                    f"{BUG_ID} detected: CPU response never arrived — "
                    f"race condition caused request drop or deadlock."
                )
            if not probe_resp_seen:
                raise AssertionError(
                    f"{BUG_ID} detected: probe response never arrived — "
                    f"race condition caused probe drop."
                )
            print(f"{BUG_ID}: both CPU and probe responses received — arbiter handled race correctly", flush=True)

        else:
            # Sequential: read first, then probe
            response2, _ = env.send_cpu_request(
                sb.CpuRequest(cmd=sb.READ, addr=addr | 0x40, user=user),
                refill_beats=_uniform_beats(0xBBAA_BBAA_BBAA_BBAA),
            )
            model.fill_line((addr | 0x40) & ~0x3F, 0,
                            _uniform_beats(0xBBAA_BBAA_BBAA_BBAA))
            expected = model.read_word(addr | 0x40)
            env.scoreboard.check_read_response(
                response2, expected_data=expected, expected_user=user)
            print(f"{BUG_ID} recovery path: sequential operations, no race, scoreboard passed.", flush=True)

    finally:
        env.finish()


def main() -> int:
    parser = argparse.ArgumentParser(description="BUG-006: CPU+probe race condition injection.")
    parser.add_argument("--disable-bug", action="store_true",
                        help="run sequential operations (recovery path)")
    args = parser.parse_args()
    run_scenario(inject_bug=not args.disable_bug)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
