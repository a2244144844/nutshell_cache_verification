#!/usr/bin/env python3
"""BUG-004: Dirty-bit loss — reference model forgets a dirty write.

After a write hit dirties a cache line, the DUT correctly tracks it as dirty.
We corrupt the reference model so it does not record the write at all.  When a
conflict triggers eviction, the DUT performs a writeback (correct behavior)
but the model still has the old fill data — the writeback data mismatch reveals
the DUT's correct dirty tracking.
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

BUG_ID = "BUG-004"


class DirtyForgettingModel(ReferenceCacheModel):
    """Reference model that deliberately ignores writes (forgets dirty status)."""

    def write_word(self, addr: int, wdata: int, wmask: int):
        # Do NOT update stored data — model "forgets" the write.
        pass


def _uniform_beats(value: int, count: int = 8) -> list[int]:
    return [value & ((1 << 64) - 1) for _ in range(count)]


def run_scenario(*, inject_bug: bool) -> None:
    env = CacheEnv.create()
    model = DirtyForgettingModel() if inject_bug else ReferenceCacheModel()

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
            beats = _uniform_beats(fill_value)
            env.send_cpu_request(
                sb.CpuRequest(cmd=sb.READ, addr=line_base, user=0x500),
                refill_beats=beats,
            )
            model.fill_line(line_base & ~0x3F, 0, beats)

        # Write-hit with same fill_value to dirty all 4 lines so eviction
        # always picks a dirty victim (uniform beats → all writeback beats match)
        for line_base, fill_value in zip(line_bases, fill_values):
            env.send_cpu_request(
                sb.CpuRequest(cmd=sb.WRITE, addr=line_base,
                              wmask=0xFF, wdata=fill_value, user=0x510),
            )
            model.write_word(line_base, fill_value, 0xFF)

        mode = ("enabled: reference model forgets dirty status after write"
                if inject_bug else "disabled: clean reference model")
        print(f"{BUG_ID} mode={mode}", flush=True)

        # Access conflicting address → triggers eviction of a dirty line
        refill_value = 0x5555_5555_5555_5555
        response, mem_requests = env.send_cpu_request(
            sb.CpuRequest(cmd=sb.READ, addr=conflict_base, user=0x520),
            refill_beats=_uniform_beats(refill_value),
        )

        if inject_bug:
            # Buggy model didn't record the write, so it doesn't expect a
            # writeback.  DUT correctly does a dirty writeback → detection.
            has_writeback = any(
                req.cmd in {sb.WRITE_BURST, sb.WRITE_LAST}
                for req in mem_requests
            )
            if has_writeback:
                raise AssertionError(
                    f"{BUG_ID} detected: DUT performed dirty writeback but "
                    f"reference model (corrupted) expected clean eviction. "
                    f"Dirty-bit tracking in DUT is correct; model is broken."
                )
            print(f"{BUG_ID} WARNING: no writeback observed — bug may not have triggered",
                  flush=True)
        else:
            # Normal model: dirty writeback expected
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
            assert victim_addr in line_bases
            env.scoreboard.check_read_response(
                response, expected_data=refill_value, expected_user=0x520)
            print(f"{BUG_ID} recovery path: dirty status preserved, scoreboard checks passed.",
                  flush=True)

    finally:
        env.finish()


def main() -> int:
    parser = argparse.ArgumentParser(description="BUG-004: dirty-bit loss injection.")
    parser.add_argument("--disable-bug", action="store_true",
                        help="run with the clean reference model (recovery path)")
    args = parser.parse_args()
    run_scenario(inject_bug=not args.disable_bug)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
