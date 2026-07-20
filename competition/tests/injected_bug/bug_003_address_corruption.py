#!/usr/bin/env python3
"""BUG-003: Address corruption — flip bit 20 on write address before DUT sees it.

The reference model tracks the original (correct) address.  When the corrupted
write dirties a line and it is later evicted, the DUT issues a writeback with
the corrupted address, which the scoreboard detects as a mismatch.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

from src.env.cache_env import CacheEnv
from src.utils import simplebus as sb

BUG_ID = "BUG-003"
ADDR_CORRUPT_BIT = 20


class AddrCorruptingEnv(CacheEnv):
    """Wrapper that flips one address bit on every CPU request."""

    def drive_cpu_request(self, request: sb.CpuRequest):
        corrupted = sb.CpuRequest(
            cmd=request.cmd,
            addr=request.addr ^ (1 << ADDR_CORRUPT_BIT),
            size=request.size,
            wmask=request.wmask,
            wdata=request.wdata,
            user=request.user,
        )
        super().drive_cpu_request(corrupted)

    def send_cpu_request(self, request, *, refill_data=0, refill_beats=None, timeout=100):
        corrupted = sb.CpuRequest(
            cmd=request.cmd,
            addr=request.addr ^ (1 << ADDR_CORRUPT_BIT),
            size=request.size,
            wmask=request.wmask,
            wdata=request.wdata,
            user=request.user,
        )
        return super().send_cpu_request(corrupted, refill_data=refill_data,
                                        refill_beats=refill_beats, timeout=timeout)


def _uniform_beats(value: int, count: int = 8) -> list[int]:
    return [value & ((1 << 64) - 1) for _ in range(count)]


def run_scenario(*, inject_bug: bool) -> None:
    cls = AddrCorruptingEnv if inject_bug else CacheEnv
    env = cls.create()
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

        # Fill 4 ways clean
        for line_base, fill_value in zip(line_bases, fill_values):
            env.send_cpu_request(
                sb.CpuRequest(cmd=sb.READ, addr=line_base, user=0x500),
                refill_beats=_uniform_beats(fill_value),
            )

        # Write-hit to dirty all 4 lines
        for line_base, fill_value in zip(line_bases, fill_values):
            env.send_cpu_request(
                sb.CpuRequest(cmd=sb.WRITE, addr=line_base,
                              wmask=0xFF, wdata=fill_value, user=0x510),
            )

        mode = ("enabled: flipping addr bit 20 on all CPU requests"
                if inject_bug else "disabled: clean passthrough")
        print(f"{BUG_ID} mode={mode}", flush=True)

        # Trigger conflict eviction — dirty line should be written back
        refill_value = 0x5555_5555_5555_5555
        response, mem_requests = env.send_cpu_request(
            sb.CpuRequest(cmd=sb.READ, addr=conflict_base, user=0x520),
            refill_beats=_uniform_beats(refill_value),
        )

        if inject_bug:
            # With address corruption, the writeback addr differs.
            try:
                env.scoreboard.check_dirty_writeback_refill(
                    mem_requests,
                    victim_addr=line_bases[0],
                    refill_addr=conflict_base,
                )
            except AssertionError as exc:
                raise AssertionError(
                    f"{BUG_ID} detected: address corruption caused writeback "
                    f"address mismatch (bit {ADDR_CORRUPT_BIT} flipped). "
                    f"Original assertion: {exc}"
                ) from exc
        else:
            write_reqs = [req for req in mem_requests
                          if req.cmd in {sb.WRITE_BURST, sb.WRITE_LAST}]
            read_reqs = [req for req in mem_requests
                         if req.cmd in {sb.READ_BURST, sb.READ_LAST}]
            victim_addr = write_reqs[0].addr
            env.scoreboard.check_dirty_writeback_refill(
                mem_requests,
                victim_addr=victim_addr,
                refill_addr=conflict_base,
                expected_write_data=write_reqs[0].wdata,
            )
            assert victim_addr in line_bases, \
                f"victim 0x{victim_addr:x} not in line_bases"
            env.scoreboard.check_read_response(
                response, expected_data=refill_value, expected_user=0x520)
            print(f"{BUG_ID} recovery path: no corruption, scoreboard checks passed.", flush=True)

    finally:
        env.finish()


def main() -> int:
    parser = argparse.ArgumentParser(description="BUG-003: address corruption injection.")
    parser.add_argument("--disable-bug", action="store_true",
                        help="run with the clean environment (recovery path)")
    args = parser.parse_args()
    run_scenario(inject_bug=not args.disable_bug)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
