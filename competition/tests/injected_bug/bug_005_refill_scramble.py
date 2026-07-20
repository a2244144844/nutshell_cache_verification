#!/usr/bin/env python3
"""BUG-005: Refill order scramble — memory response beats arrive out of order.

The DUT expects refill beats in critical-word-first order.  For a read at word
offset 0 this is sequential order.  This injector reverses the beats so data
lands in wrong word positions, causing a data mismatch on read-back.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

from src.env.cache_env import CacheEnv
from src.generator.cache_random import ReferenceCacheModel
from src.utils import simplebus as sb

BUG_ID = "BUG-005"


def _ordered_beats(value: int, count: int = 8) -> list[int]:
    """Generate 8 distinct beats with sequential values."""
    return [(value + i) & ((1 << 64) - 1) for i in range(count)]


def run_scenario(*, inject_bug: bool) -> None:
    env = CacheEnv.create()
    model = ReferenceCacheModel()

    try:
        env.reset()

        addr = 0x8000_0000  # word offset 0 → critical-word-first = sequential
        user = 0x505
        fill_data = 0x5000_0000_0000_0000

        ordered = _ordered_beats(fill_data)
        beats = list(reversed(ordered)) if inject_bug else ordered

        mode = ("enabled: refill beats scrambled (reversed order)"
                if inject_bug else "disabled: correct critical-word-first order")
        print(f"{BUG_ID} mode={mode}", flush=True)

        response, mem_requests = env.send_cpu_request(
            sb.CpuRequest(cmd=sb.READ, addr=addr, user=user),
            refill_beats=beats,
        )

        # Reference model fills with correct (un-scrambled) order
        model.fill_line(addr & ~0x3F, 0, ordered)
        expected_data = model.read_word(addr)

        print(
            f"{BUG_ID} expected_data=0x{expected_data:016x}, actual_data=0x{response.rdata:016x}",
            flush=True,
        )

        try:
            env.scoreboard.check_read_response(
                response, expected_data=expected_data, expected_user=user)
        except AssertionError as exc:
            if inject_bug:
                raise AssertionError(
                    f"{BUG_ID} detected by scoreboard.check_read_response: "
                    f"scrambled refill order caused data mismatch. "
                    f"Expected 0x{expected_data:016x}, got 0x{response.rdata:016x}"
                ) from exc
            raise

        if not inject_bug:
            env.scoreboard.check_single_read_burst(mem_requests, expected_addr=addr)
            print(f"{BUG_ID} recovery path: correct refill order, scoreboard checks passed.",
                  flush=True)

    finally:
        env.finish()


def main() -> int:
    parser = argparse.ArgumentParser(description="BUG-005: refill order scramble injection.")
    parser.add_argument("--disable-bug", action="store_true",
                        help="run with correct refill order (recovery path)")
    args = parser.parse_args()
    run_scenario(inject_bug=not args.disable_bug)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
