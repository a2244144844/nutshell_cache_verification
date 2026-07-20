from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

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

# Extended address ranges to exercise more SRAM address bits (Stage 13)
EXTENDED_LINE_BASES = (
    0x8000_0000, 0x8000_0040, 0x8000_0080, 0x8000_00C0,
    0x8000_2000, 0x8000_2040, 0x8000_2080, 0x8000_20C0,
    0x8000_4000, 0x8000_4040, 0x8000_4080, 0x8000_40C0,
    0x8000_6000, 0x8000_6040, 0x8000_6080, 0x8000_60C0,
    0x8001_0000, 0x8001_0040, 0x8001_2000, 0x8001_2040,
    0x8002_0000, 0x8002_0040, 0x8002_2000, 0x8002_2040,
    0x8004_0000, 0x8004_0040, 0x8004_2000, 0x8004_2040,
    0x8008_0000, 0x8008_0040, 0x8008_2000, 0x8008_2040,
)

# Stage 17: 64-address extended range for maximal toggle coverage
EXTENDED_LINE_BASES_V2 = (
    0x8000_0000, 0x8000_0040, 0x8000_0080, 0x8000_00C0,
    0x8000_2000, 0x8000_2040, 0x8000_2080, 0x8000_20C0,
    0x8000_4000, 0x8000_4040, 0x8000_4080, 0x8000_40C0,
    0x8000_6000, 0x8000_6040, 0x8000_6080, 0x8000_60C0,
    0x8001_0000, 0x8001_0040, 0x8001_2000, 0x8001_2040,
    0x8002_0000, 0x8002_0040, 0x8002_2000, 0x8002_2040,
    0x8004_0000, 0x8004_0040, 0x8004_2000, 0x8004_2040,
    0x8008_0000, 0x8008_0040, 0x8008_2000, 0x8008_2040,
    0x8010_0000, 0x8010_0040, 0x8010_0080, 0x8010_00C0,
    0x8010_2000, 0x8010_2040, 0x8010_2080, 0x8010_20C0,
    0x8020_0000, 0x8020_0040, 0x8020_0080, 0x8020_00C0,
    0x8020_2000, 0x8020_2040, 0x8020_2080, 0x8020_20C0,
    0x8040_0000, 0x8040_0040, 0x8040_0080, 0x8040_00C0,
    0x8040_2000, 0x8040_2040, 0x8040_2080, 0x8040_20C0,
    0x8080_0000, 0x8080_0040, 0x8080_0080, 0x8080_00C0,
    0x8080_2000, 0x8080_2040, 0x8080_2080, 0x8080_20C0,
)

MMIO_ADDRS = (
    0x3000_0000, 0x3000_0008, 0x3000_0010, 0x3000_0018,
    0x4000_0000, 0x4000_0008, 0x4000_0010, 0x4000_0018,
)

# Diverse data patterns to exercise data bus toggle bits (Stage 13: 16 patterns)
DATA_PATTERNS = (
    0x0000_0000_0000_0000, 0xFFFF_FFFF_FFFF_FFFF,
    0xAAAA_AAAA_AAAA_AAAA, 0x5555_5555_5555_5555,
    0x3333_3333_3333_3333, 0xCCCC_CCCC_CCCC_CCCC,
    0x0F0F_0F0F_0F0F_0F0F, 0xF0F0_F0F0_F0F0_F0F0,
    0x00FF_00FF_00FF_00FF, 0xFF00_FF00_FF00_FF00,
    0x0000_FFFF_0000_FFFF, 0xFFFF_0000_FFFF_0000,
    0x0123_4567_89AB_CDEF, 0xFEDC_BA98_7654_3210,
    0xDEAD_BEEF_CAFE_BABE, 0x8BAD_F00D_FEED_FACE,
)

# Stage 17: 32 data patterns for maximal toggle coverage
DATA_PATTERNS_V2 = (
    0x0000_0000_0000_0000, 0xFFFF_FFFF_FFFF_FFFF,
    0xAAAA_AAAA_AAAA_AAAA, 0x5555_5555_5555_5555,
    0x3333_3333_3333_3333, 0xCCCC_CCCC_CCCC_CCCC,
    0x0F0F_0F0F_0F0F_0F0F, 0xF0F0_F0F0_F0F0_F0F0,
    0x00FF_00FF_00FF_00FF, 0xFF00_FF00_FF00_FF00,
    0x0000_FFFF_0000_FFFF, 0xFFFF_0000_FFFF_0000,
    0x0123_4567_89AB_CDEF, 0xFEDC_BA98_7654_3210,
    0xDEAD_BEEF_CAFE_BABE, 0x8BAD_F00D_FEED_FACE,
    0x0101_0101_0101_0101, 0x8080_8080_8080_8080,
    0x7F7F_7F7F_7F7F_7F7F, 0xFEFE_FEFE_FEFE_FEFE,
    0x0FF0_0FF0_0FF0_0FF0, 0xF00F_F00F_F00F_F00F,
    0xAA55_AA55_AA55_AA55, 0x55AA_55AA_55AA_55AA,
    0xCC33_CC33_CC33_CC33, 0x33CC_33CC_33CC_33CC,
    0x8001_8001_8001_8001, 0x7FFE_7FFE_7FFE_7FFE,
    0x0120_0120_0120_0120, 0xFEDF_FEDF_FEDF_FEDF,
    0x0A0B_0C0D_0E0F_0102, 0xF5F4_F3F2_F1F0_FEFD,
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
    def __init__(self, seed: int, line_bases=None, enable_extended: bool = False,
                 enable_max_toggle: bool = False):
        self.seed = int(seed)
        self.rng = random.Random(self.seed)
        base_bases = [int(base) & ~0x3F for base in (line_bases or DEFAULT_LINE_BASES)]
        if enable_max_toggle:
            self.line_bases = [int(base) & ~0x3F for base in EXTENDED_LINE_BASES_V2]
            self._data_patterns = DATA_PATTERNS_V2
        elif enable_extended:
            self.line_bases = [int(base) & ~0x3F for base in EXTENDED_LINE_BASES]
            self._data_patterns = DATA_PATTERNS
        else:
            self.line_bases = base_bases
            self._data_patterns = DATA_PATTERNS
        self._warmup_index = 0
        self._mask_class_index = 0
        self._write_offset_cycle = [3, 4, 5, 6, 7, 0]
        self._extended = enable_extended or enable_max_toggle

    def _make_refill_beats(self, line_base: int, word_index: int, op_index: int) -> List[int]:
        seed_mix = (self.seed ^ (line_base >> 6) ^ (word_index << 11) ^ (op_index << 19)) & MASK_64
        beats = []
        for beat_index in range(8):
            pattern_idx = (beat_index + op_index) % len(self._data_patterns)
            value = self._data_patterns[pattern_idx]
            value ^= (seed_mix + (beat_index + 1) * 0x0102_0304_0506_0708) & MASK_64
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

    def _build_dirty_closure_ops(self, ops: List[RandomCacheOperation],
                                  model: ReferenceCacheModel, steps: int) -> bool:
        """Returns True if we filled all the way to steps."""
        dirty_line_bases = [base & ~0x1FFF for base in DIRTY_CLOSURE_LINE_BASES]
        dirty_fill_values = [
            (0x1100_0000_0000_0000 | (i * 0x0101_0101_0101_0101)) & MASK_64 for i in range(5)
        ]

        dirty_closure = [
            {"cmd": sb.READ, "addr": dirty_line_bases[0] + 0 * 8, "fill": dirty_fill_values[0],
             "word_index": 0, "mask_class": "none",
             "refill_beats": self._make_uniform_refill_beats(dirty_fill_values[0])},
            {"cmd": sb.READ, "addr": dirty_line_bases[1] + 1 * 8, "fill": dirty_fill_values[1],
             "word_index": 1, "mask_class": "none",
             "refill_beats": self._make_uniform_refill_beats(dirty_fill_values[1])},
            {"cmd": sb.READ, "addr": dirty_line_bases[2] + 2 * 8, "fill": dirty_fill_values[2],
             "word_index": 2, "mask_class": "none",
             "refill_beats": self._make_uniform_refill_beats(dirty_fill_values[2])},
            {"cmd": sb.READ, "addr": dirty_line_bases[3] + 3 * 8, "fill": dirty_fill_values[3],
             "word_index": 3, "mask_class": "none",
             "refill_beats": self._make_uniform_refill_beats(dirty_fill_values[3])},
            {"cmd": sb.WRITE, "addr": dirty_line_bases[0] + 4 * 8, "fill": dirty_fill_values[0],
             "word_index": 4, "mask_class": "byte", "refill_beats": []},
            {"cmd": sb.WRITE, "addr": dirty_line_bases[1] + 5 * 8, "fill": dirty_fill_values[1],
             "word_index": 5, "mask_class": "adjacent", "refill_beats": []},
            {"cmd": sb.WRITE, "addr": dirty_line_bases[2] + 6 * 8, "fill": dirty_fill_values[2],
             "word_index": 6, "mask_class": "low_half", "refill_beats": []},
            {"cmd": sb.WRITE, "addr": dirty_line_bases[3] + 7 * 8, "fill": dirty_fill_values[3],
             "word_index": 7, "mask_class": "high_half", "refill_beats": []},
            {"cmd": sb.WRITE, "addr": dirty_line_bases[0] + 0 * 8, "fill": dirty_fill_values[0],
             "word_index": 0, "mask_class": "full", "refill_beats": []},
            {"cmd": sb.WRITE, "addr": dirty_line_bases[1] + 1 * 8, "fill": dirty_fill_values[1],
             "word_index": 1, "mask_class": "sparse", "refill_beats": []},
            {"cmd": sb.READ, "addr": dirty_line_bases[4] + 0 * 8, "fill": dirty_fill_values[4],
             "word_index": 0, "mask_class": "none",
             "refill_beats": self._make_uniform_refill_beats(dirty_fill_values[4])},
        ]

        for spec in dirty_closure:
            if len(ops) >= steps:
                return True
            line_base = spec["addr"] & ~0x3F
            if spec["cmd"] == sb.READ:
                op = RandomCacheOperation(
                    index=len(ops), cmd=spec["cmd"], addr=spec["addr"],
                    user=0x080 + len(ops), wdata=0, wmask=0,
                    line_base=line_base, word_index=spec["word_index"],
                    mask_class=spec["mask_class"], refill_beats=spec["refill_beats"],
                )
                ops.append(op)
                model.fill_line(line_base, spec["word_index"], spec["refill_beats"])
            else:
                wmask = self._make_write_mask(spec["mask_class"], spec["word_index"])
                op = RandomCacheOperation(
                    index=len(ops), cmd=spec["cmd"], addr=spec["addr"],
                    user=0x080 + len(ops), wdata=spec["fill"], wmask=wmask,
                    line_base=line_base, word_index=spec["word_index"],
                    mask_class=spec["mask_class"], refill_beats=[],
                )
                ops.append(op)
                model.write_word(spec["addr"], spec["fill"], wmask)
        return False

    def _build_warmup_ops(self, ops: List[RandomCacheOperation],
                           model: ReferenceCacheModel, steps: int) -> bool:
        for line_index, line_base in enumerate(self.line_bases):
            if len(ops) >= steps:
                return True
            word_index = line_index % 8
            refill_beats = self._make_refill_beats(line_base, word_index, len(ops))
            ops.append(RandomCacheOperation(
                index=len(ops), cmd=sb.READ,
                addr=line_base + word_index * 8,
                user=0x100 + len(ops), wdata=0, wmask=0,
                line_base=line_base, word_index=word_index,
                mask_class="none", refill_beats=refill_beats,
            ))
            model.fill_line(line_base, word_index, refill_beats)
        return False

    def _build_write_mask_ops(self, ops: List[RandomCacheOperation],
                               model: ReferenceCacheModel, steps: int) -> bool:
        for mask_index, mask_class in enumerate(WRITE_MASK_CLASSES):
            if len(ops) >= steps:
                return True
            line_base = self._pick_line_base()
            word_index = self._write_offset_cycle[mask_index % len(self._write_offset_cycle)]
            addr = line_base + word_index * 8
            wdata = self.rng.getrandbits(64)
            wmask = self._make_write_mask(mask_class, word_index)
            ops.append(RandomCacheOperation(
                index=len(ops), cmd=sb.WRITE, addr=addr,
                user=0x200 + len(ops), wdata=wdata, wmask=wmask,
                line_base=line_base, word_index=word_index,
                mask_class=mask_class, refill_beats=[],
            ))
            model.write_word(addr, wdata, wmask)
        return False

    def _build_mmio_ops(self, ops: List[RandomCacheOperation], steps: int) -> bool:
        """Add MMIO read/write operations to toggle MMIO path signals."""
        mmio_count = min(4, max(1, steps // 20))
        for i in range(mmio_count):
            if len(ops) >= steps:
                return True
            addr = MMIO_ADDRS[i % len(MMIO_ADDRS)]
            if self.rng.random() < 0.5:
                ops.append(RandomCacheOperation(
                    index=len(ops), cmd=sb.READ, addr=addr,
                    user=0x500 + len(ops), wdata=0, wmask=0,
                    line_base=addr & ~0x3F, word_index=(addr >> 3) & 0x7,
                    mask_class="none", refill_beats=[],
                ))
            else:
                wdata = self._data_patterns[i % len(self._data_patterns)]
                ops.append(RandomCacheOperation(
                    index=len(ops), cmd=sb.WRITE, addr=addr,
                    user=0x500 + len(ops), wdata=wdata, wmask=0xFF,
                    line_base=addr & ~0x3F, word_index=(addr >> 3) & 0x7,
                    mask_class="full", refill_beats=[],
                ))
        return False

    def _build_probe_ops(self, ops: List[RandomCacheOperation],
                          model: ReferenceCacheModel, steps: int) -> bool:
        """Add probe operations to toggle coherence path signals."""
        probe_count = min(4, max(1, steps // 25))
        for i in range(probe_count):
            if len(ops) >= steps:
                return True
            line_base = self._pick_line_base()
            word_index = self.rng.randrange(8)
            addr = line_base + word_index * 8
            ops.append(RandomCacheOperation(
                index=len(ops), cmd=sb.PROBE, addr=addr,
                user=0x600 + len(ops), wdata=0, wmask=0,
                line_base=line_base, word_index=word_index,
                mask_class="none", refill_beats=[],
            ))
        return False

    def _build_flush_ops(self, ops: List[RandomCacheOperation], steps: int) -> bool:
        """Add flush markers to exercise flush-related toggle bits."""
        flush_count = min(3, max(1, steps // 30))
        for i in range(flush_count):
            if len(ops) >= steps:
                return True
            # Special marker: cmd=0xF, user=0xF00 indicates flush assert
            ops.append(RandomCacheOperation(
                index=len(ops), cmd=0xF, addr=0,
                user=0xF00 + i, wdata=(1 if i % 2 == 0 else 0), wmask=0,
                line_base=0, word_index=0,
                mask_class="none", refill_beats=[],
            ))
        return False

    def _build_varied_random_ops(self, ops: List[RandomCacheOperation],
                                  model: ReferenceCacheModel, steps: int):
        """Random traffic fill — two modes based on self._extended.

        Non-extended (original): READ/WRITE hits on warmed lines only.
        Extended: Diverse patterns (READ/WRITE hit/miss, READ_BURST, PREFETCH).
        """
        if self._extended:
            self._build_extended_random_ops(ops, model, steps)
        else:
            self._build_basic_random_ops(ops, model, steps)

    def _build_basic_random_ops(self, ops: List[RandomCacheOperation],
                                 model: ReferenceCacheModel, steps: int):
        """Original behavior: READ/WRITE on warmed lines (hits only)."""
        while len(ops) < steps:
            line_base = self._pick_line_base()
            word_index = (self.rng.randrange(8) + len(ops)) % 8
            addr = line_base + word_index * 8
            if self.rng.random() < 0.6:
                ops.append(RandomCacheOperation(
                    index=len(ops), cmd=sb.READ, addr=addr,
                    user=0x300 + len(ops), wdata=0, wmask=0,
                    line_base=line_base, word_index=word_index,
                    mask_class="none", refill_beats=[],
                ))
            else:
                mask_class = self.rng.choice(WRITE_MASK_CLASSES)
                wdata = self.rng.getrandbits(64)
                wmask = self._make_write_mask(mask_class, word_index)
                ops.append(RandomCacheOperation(
                    index=len(ops), cmd=sb.WRITE, addr=addr,
                    user=0x300 + len(ops), wdata=wdata, wmask=wmask,
                    line_base=line_base, word_index=word_index,
                    mask_class=mask_class, refill_beats=[],
                ))

    def _build_extended_random_ops(self, ops: List[RandomCacheOperation],
                                    model: ReferenceCacheModel, steps: int):
        """Extended random traffic with diverse patterns, addresses, and commands."""
        while len(ops) < steps:
            roll = self.rng.random()
            if roll < 0.45:
                # Read hit on a known line
                line_base = self._pick_line_base()
                word_index = self.rng.randrange(8)
                addr = line_base + word_index * 8
                ops.append(RandomCacheOperation(
                    index=len(ops), cmd=sb.READ, addr=addr,
                    user=0x700 + len(ops), wdata=0, wmask=0,
                    line_base=line_base, word_index=word_index,
                    mask_class="none", refill_beats=[],
                ))
            elif roll < 0.70:
                # Write hit with varied data patterns
                line_base = self._pick_line_base()
                word_index = self.rng.randrange(8)
                addr = line_base + word_index * 8
                mask_class = self.rng.choice(WRITE_MASK_CLASSES)
                wdata = self._data_patterns[len(ops) % len(self._data_patterns)]
                wmask = self._make_write_mask(mask_class, word_index)
                ops.append(RandomCacheOperation(
                    index=len(ops), cmd=sb.WRITE, addr=addr,
                    user=0x700 + len(ops), wdata=wdata, wmask=wmask,
                    line_base=line_base, word_index=word_index,
                    mask_class=mask_class, refill_beats=[],
                ))
                model.write_word(addr, wdata, wmask)
            elif roll < 0.80:
                # Read miss (cold line) to exercise refill path
                new_base = (0x8010_0000 + (len(ops) * 0x40)) & 0xFFFF_FFFF
                word_index = self.rng.randrange(8)
                addr = new_base + word_index * 8
                refill_beats = self._make_refill_beats(new_base, word_index, len(ops))
                ops.append(RandomCacheOperation(
                    index=len(ops), cmd=sb.READ, addr=addr,
                    user=0x800 + len(ops), wdata=0, wmask=0,
                    line_base=new_base, word_index=word_index,
                    mask_class="none", refill_beats=refill_beats,
                ))
                model.fill_line(new_base, word_index, refill_beats)
            elif roll < 0.88:
                # Write miss (cold line) to exercise write-miss path
                new_base = (0x8020_0000 + (len(ops) * 0x40)) & 0xFFFF_FFFF
                word_index = self.rng.randrange(8)
                addr = new_base + word_index * 8
                mask_class = self.rng.choice(WRITE_MASK_CLASSES)
                wdata = self._data_patterns[(len(ops) + 1) % len(self._data_patterns)]
                wmask = self._make_write_mask(mask_class, word_index)
                refill_beats = self._make_refill_beats(new_base, word_index, len(ops))
                ops.append(RandomCacheOperation(
                    index=len(ops), cmd=sb.WRITE, addr=addr,
                    user=0x900 + len(ops), wdata=wdata, wmask=wmask,
                    line_base=new_base, word_index=word_index,
                    mask_class=mask_class, refill_beats=refill_beats,
                ))
                model.fill_line(new_base, word_index, refill_beats)
            elif roll < 0.93:
                # READ_BURST on a hit line to exercise burst path
                line_base = self._pick_line_base()
                word_index = self.rng.randrange(8)
                addr = line_base + word_index * 8
                ops.append(RandomCacheOperation(
                    index=len(ops), cmd=sb.READ_BURST, addr=addr,
                    user=0xA00 + len(ops), wdata=0, wmask=0,
                    line_base=line_base, word_index=word_index,
                    mask_class="none", refill_beats=[],
                ))
            else:
                # PREFETCH to exercise prefetch path
                new_base = (0x8030_0000 + (len(ops) * 0x40)) & 0xFFFF_FFFF
                word_index = self.rng.randrange(8)
                addr = new_base + word_index * 8
                refill_beats = self._make_refill_beats(new_base, word_index, len(ops))
                ops.append(RandomCacheOperation(
                    index=len(ops), cmd=sb.PREFETCH, addr=addr,
                    user=0xB00 + len(ops), wdata=0, wmask=0,
                    line_base=new_base, word_index=word_index,
                    mask_class="none", refill_beats=refill_beats,
                ))
                model.fill_line(new_base, word_index, refill_beats)

    def build_workload(self, steps: int) -> List[RandomCacheOperation]:
        steps = max(0, int(steps))
        ops: List[RandomCacheOperation] = []
        model = ReferenceCacheModel()

        if self._build_dirty_closure_ops(ops, model, steps):
            return ops
        if self._build_warmup_ops(ops, model, steps):
            return ops
        if self._build_write_mask_ops(ops, model, steps):
            return ops

        # Add MMIO, probe, and flush operations interspersed
        if self._extended:
            if self._build_mmio_ops(ops, steps):
                return ops
            if self._build_probe_ops(ops, model, steps):
                return ops
            if self._build_flush_ops(ops, steps):
                return ops

        self._build_varied_random_ops(ops, model, steps)
        return ops
