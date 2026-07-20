#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

from src.env.cache_env import CacheEnv
from src.generator.cache_random import ReferenceCacheModel
from src.utils import simplebus as sb

BUG_ID = "BUG-001"


def _uniform_beats(value: int) -> list[int]:
    return [value & ((1 << 64) - 1) for _ in range(8)]


class CorruptingReferenceModel(ReferenceCacheModel):
    def read_word(self, addr: int) -> int:
        return super().read_word(addr) ^ 0x1


def run_scenario(*, inject_bug: bool) -> None:
    env = CacheEnv.create()
    clean_model = ReferenceCacheModel()
    corrupt_model = CorruptingReferenceModel()

    try:
        env.reset()

        addr = 0x8000_0000
        user = 0x701
        fill_data = 0x1122_3344_5566_7788
        refill_beats = _uniform_beats(fill_data)
        line_base = addr & ~0x3F

        response, mem_requests = env.send_cpu_request(
            sb.CpuRequest(cmd=sb.READ, addr=addr, user=user),
            refill_beats=refill_beats,
        )

        clean_model.fill_line(line_base, 0, refill_beats)
        corrupt_model.fill_line(line_base, 0, refill_beats)
        expected_data = corrupt_model.read_word(addr) if inject_bug else clean_model.read_word(addr)

        mode = "enabled: corrupting reference-model read_word() flips bit 0" if inject_bug else "disabled: clean reference-model read_word()"
        print(f"{BUG_ID} mode={mode} at addr 0x{addr:08x}", flush=True)
        print(
            f"{BUG_ID} expected_data=0x{expected_data:016x}, actual_data=0x{response.rdata:016x}",
            flush=True,
        )

        try:
            env.scoreboard.check_read_response(response, expected_data=expected_data, expected_user=user)
        except AssertionError as exc:
            if inject_bug:
                raise AssertionError(
                    f"{BUG_ID} detected by scoreboard.check_read_response: "
                    f"reference-model corruption made the expected read data 0x{expected_data:016x} "
                    f"while the DUT returned 0x{response.rdata:016x} at addr 0x{addr:08x}"
                ) from exc
            raise

        env.scoreboard.check_single_read_burst(mem_requests, expected_addr=addr)
        print(f"{BUG_ID} recovery path: bug injection disabled, scoreboard checks passed.", flush=True)
    finally:
        env.finish()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the controlled Cache bug injection scenario.")
    parser.add_argument(
        "--disable-bug",
        action="store_true",
        help="run the same flow with the clean reference model so the harness passes",
    )
    args = parser.parse_args()

    run_scenario(inject_bug=not args.disable_bug)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
