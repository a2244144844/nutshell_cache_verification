from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List

from src.utils import simplebus as sb


MASK_64 = (1 << 64) - 1
DEFAULT_LINE_BASES = (
    0x8000_0000,
    0x8000_2000,
    0x8000_4000,
)
WRITE_MASK_CLASSES = ("byte", "adjacent", "low_half", "high_half", "full", "sparse")
DIRTY_CLOSURE_LINE_BASES = (
    0x8000_0000,
    0x8000_2000,
    0x8000_4000,
    0x8000_6000,
    0x8000_8000,
)


@dataclass(frozen=True)
class RandomCacheOperation:
    index: int
    cmd: int
    addr: int
    user: int
    wdata: int
    wmask: int
    line_base: int
    word_index: int
    mask_class: str
    refill_beats: List[int]

    @property
    def request(self) -> sb.CpuRequest:
        return sb.CpuRequest(
            cmd=self.cmd,
            addr=self.addr,
            wdata=self.wdata,
            wmask=self.wmask,
            user=self.user,
        )


class ReferenceCacheModel:
    def __init__(self):
        self._lines: Dict[int, List[int]] = {}

    def has_line(self, line_base: int) -> bool:
        return line_base in self._lines

    def fill_line(self, line_base: int, word_index: int, refill_beats: List[int]):
        words = [0] * 8
        for beat_index, beat_data in enumerate(refill_beats):
            words[(word_index + beat_index) % 8] = beat_data & MASK_64
        self._lines[line_base] = words

    def read_word(self, addr: int) -> int:
        line_base = addr & ~0x3F
        word_index = (addr >> 3) & 0x7
        if line_base not in self._lines:
            raise KeyError(f"line 0x{line_base:x} is not present in the reference model")
        return self._lines[line_base][word_index]

    def write_word(self, addr: int, wdata: int, wmask: int) -> int:
        line_base = addr & ~0x3F
        word_index = (addr >> 3) & 0x7
        if line_base not in self._lines:
            raise KeyError(f"line 0x{line_base:x} is not present in the reference model")
        updated = sb.mask_write_64(self._lines[line_base][word_index], wdata, wmask)
        self._lines[line_base][word_index] = updated
        return updated


class CacheRandomGenerator:
    def __init__(self, seed: int, line_bases=None):
        self.seed = int(seed)
        self.rng = random.Random(self.seed)
        self.line_bases = [int(base) & ~0x3F for base in (line_bases or DEFAULT_LINE_BASES)]
        self._warmup_index = 0
        self._mask_class_index = 0
        self._write_offset_cycle = [3, 4, 5, 6, 7, 0]

    def _make_refill_beats(self, line_base: int, word_index: int, op_index: int) -> List[int]:
        seed_mix = (self.seed ^ (line_base >> 6) ^ (word_index << 11) ^ (op_index << 19)) & MASK_64
        beats = []
        for beat_index in range(8):
            value = (seed_mix + (beat_index + 1) * 0x0102_0304_0506_0708) & MASK_64
            value ^= ((line_base >> 3) << (beat_index % 7)) & MASK_64
            value ^= ((word_index + beat_index) << 56) & MASK_64
            beats.append(value & MASK_64)
        return beats

    def _make_write_mask(self, mask_class: str, word_index: int) -> int:
        if mask_class == "byte":
            return 1 << (word_index % 8)
        if mask_class == "adjacent":
            return 0x3 << (word_index % 7)
        if mask_class == "low_half":
            return 0x0F
        if mask_class == "high_half":
            return 0xF0
        if mask_class == "full":
            return 0xFF
        if mask_class == "sparse":
            patterns = (0x81, 0x42, 0x24, 0x18, 0x99, 0x66, 0xA5, 0x3C)
            return patterns[word_index % len(patterns)]
        raise ValueError(f"unknown write-mask class: {mask_class}")

    def _make_uniform_refill_beats(self, value: int) -> List[int]:
        return [value & MASK_64 for _ in range(8)]

    def _pick_line_base(self, present_only: bool = True) -> int:
        candidates = self.line_bases
        return candidates[self.rng.randrange(len(candidates))]

    def build_workload(self, steps: int) -> List[RandomCacheOperation]:
        steps = max(0, int(steps))
        ops: List[RandomCacheOperation] = []
        model = ReferenceCacheModel()

        dirty_line_bases = [base & ~0x1FFF for base in DIRTY_CLOSURE_LINE_BASES]
        dirty_fill_values = [
            (0x1100_0000_0000_0000 | (i * 0x0101_0101_0101_0101)) & MASK_64 for i in range(5)
        ]

        dirty_closure = [
            {
                "cmd": sb.READ,
                "addr": dirty_line_bases[0] + 0 * 8,
                "fill": dirty_fill_values[0],
                "word_index": 0,
                "mask_class": "none",
                "refill_beats": self._make_uniform_refill_beats(dirty_fill_values[0]),
            },
            {
                "cmd": sb.READ,
                "addr": dirty_line_bases[1] + 1 * 8,
                "fill": dirty_fill_values[1],
                "word_index": 1,
                "mask_class": "none",
                "refill_beats": self._make_uniform_refill_beats(dirty_fill_values[1]),
            },
            {
                "cmd": sb.READ,
                "addr": dirty_line_bases[2] + 2 * 8,
                "fill": dirty_fill_values[2],
                "word_index": 2,
                "mask_class": "none",
                "refill_beats": self._make_uniform_refill_beats(dirty_fill_values[2]),
            },
            {
                "cmd": sb.READ,
                "addr": dirty_line_bases[3] + 3 * 8,
                "fill": dirty_fill_values[3],
                "word_index": 3,
                "mask_class": "none",
                "refill_beats": self._make_uniform_refill_beats(dirty_fill_values[3]),
            },
            {
                "cmd": sb.WRITE,
                "addr": dirty_line_bases[0] + 4 * 8,
                "fill": dirty_fill_values[0],
                "word_index": 4,
                "mask_class": "byte",
                "refill_beats": [],
            },
            {
                "cmd": sb.WRITE,
                "addr": dirty_line_bases[1] + 5 * 8,
                "fill": dirty_fill_values[1],
                "word_index": 5,
                "mask_class": "adjacent",
                "refill_beats": [],
            },
            {
                "cmd": sb.WRITE,
                "addr": dirty_line_bases[2] + 6 * 8,
                "fill": dirty_fill_values[2],
                "word_index": 6,
                "mask_class": "low_half",
                "refill_beats": [],
            },
            {
                "cmd": sb.WRITE,
                "addr": dirty_line_bases[3] + 7 * 8,
                "fill": dirty_fill_values[3],
                "word_index": 7,
                "mask_class": "high_half",
                "refill_beats": [],
            },
            {
                "cmd": sb.WRITE,
                "addr": dirty_line_bases[0] + 0 * 8,
                "fill": dirty_fill_values[0],
                "word_index": 0,
                "mask_class": "full",
                "refill_beats": [],
            },
            {
                "cmd": sb.WRITE,
                "addr": dirty_line_bases[1] + 1 * 8,
                "fill": dirty_fill_values[1],
                "word_index": 1,
                "mask_class": "sparse",
                "refill_beats": [],
            },
            {
                "cmd": sb.READ,
                "addr": dirty_line_bases[4] + 0 * 8,
                "fill": dirty_fill_values[4],
                "word_index": 0,
                "mask_class": "none",
                "refill_beats": self._make_uniform_refill_beats(dirty_fill_values[4]),
            },
        ]

        for spec in dirty_closure:
            if len(ops) >= steps:
                return ops
            line_base = spec["addr"] & ~0x3F
            if spec["cmd"] == sb.READ:
                op = RandomCacheOperation(
                    index=len(ops),
                    cmd=spec["cmd"],
                    addr=spec["addr"],
                    user=0x080 + len(ops),
                    wdata=0,
                    wmask=0,
                    line_base=line_base,
                    word_index=spec["word_index"],
                    mask_class=spec["mask_class"],
                    refill_beats=spec["refill_beats"],
                )
                ops.append(op)
                model.fill_line(line_base, spec["word_index"], spec["refill_beats"])
            else:
                wmask = self._make_write_mask(spec["mask_class"], spec["word_index"])
                op = RandomCacheOperation(
                    index=len(ops),
                    cmd=spec["cmd"],
                    addr=spec["addr"],
                    user=0x080 + len(ops),
                    wdata=spec["fill"],
                    wmask=wmask,
                    line_base=line_base,
                    word_index=spec["word_index"],
                    mask_class=spec["mask_class"],
                    refill_beats=[],
                )
                ops.append(op)
                model.write_word(spec["addr"], spec["fill"], wmask)

        # Warm each line once to establish a deterministic hit set.
        for line_index, line_base in enumerate(self.line_bases):
            if len(ops) >= steps:
                return ops
            word_index = line_index % 8
            refill_beats = self._make_refill_beats(line_base, word_index, len(ops))
            ops.append(
                RandomCacheOperation(
                    index=len(ops),
                    cmd=sb.READ,
                    addr=line_base + word_index * 8,
                    user=0x100 + len(ops),
                    wdata=0,
                    wmask=0,
                    line_base=line_base,
                    word_index=word_index,
                    mask_class="none",
                    refill_beats=refill_beats,
                )
            )
            model.fill_line(line_base, word_index, refill_beats)

        # Force one write of each class to make the first coverage report useful.
        for mask_index, mask_class in enumerate(WRITE_MASK_CLASSES):
            if len(ops) >= steps:
                return ops
            line_base = self._pick_line_base()
            word_index = self._write_offset_cycle[mask_index % len(self._write_offset_cycle)]
            addr = line_base + word_index * 8
            wdata = self.rng.getrandbits(64)
            wmask = self._make_write_mask(mask_class, word_index)
            ops.append(
                RandomCacheOperation(
                    index=len(ops),
                    cmd=sb.WRITE,
                    addr=addr,
                    user=0x200 + len(ops),
                    wdata=wdata,
                    wmask=wmask,
                    line_base=line_base,
                    word_index=word_index,
                    mask_class=mask_class,
                    refill_beats=[],
                )
            )
            model.write_word(addr, wdata, wmask)

        # Fill the rest with constrained random read/write traffic on the warmed lines.
        while len(ops) < steps:
            line_base = self._pick_line_base()
            word_index = (self.rng.randrange(8) + len(ops)) % 8
            addr = line_base + word_index * 8
            if self.rng.random() < 0.6:
                ops.append(
                    RandomCacheOperation(
                        index=len(ops),
                        cmd=sb.READ,
                        addr=addr,
                        user=0x300 + len(ops),
                        wdata=0,
                        wmask=0,
                        line_base=line_base,
                        word_index=word_index,
                        mask_class="none",
                        refill_beats=[],
                    )
                )
            else:
                mask_class = self.rng.choice(WRITE_MASK_CLASSES)
                wdata = self.rng.getrandbits(64)
                wmask = self._make_write_mask(mask_class, word_index)
                ops.append(
                    RandomCacheOperation(
                        index=len(ops),
                        cmd=sb.WRITE,
                        addr=addr,
                        user=0x300 + len(ops),
                        wdata=wdata,
                        wmask=wmask,
                        line_base=line_base,
                        word_index=word_index,
                        mask_class=mask_class,
                        refill_beats=[],
                    )
                )
        return ops
