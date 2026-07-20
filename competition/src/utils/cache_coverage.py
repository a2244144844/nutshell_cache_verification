from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List

from src.utils import simplebus as sb


EXPECTED_BINS = {
    "cmd_type": ("read", "write", "probe"),
    "hit_miss_proxy": ("hit", "miss"),
    "write_mask_class": ("none", "byte", "adjacent", "low_half", "high_half", "full", "sparse"),
    "word_offset": tuple(str(i) for i in range(8)),
    "refill_path": ("clean_miss_refill", "read_hit", "write_hit", "dirty_miss_writeback_refill",
                     "write_miss_clean_refill", "write_miss_dirty_refill"),
    "write_miss": ("clean", "dirty", "none"),
    # Cross-dimension groups (P2-10)
    "write_hit_x_wmask": tuple(f"{m}_{o}" for m in ("byte", "adjacent", "low_half", "high_half", "full", "sparse")
                                for o in range(8)),
    "miss_x_addr_type": ("hit_normal", "hit_mmio", "miss_normal"),
    "probe_x_cache_state": ("probe_hit_valid", "probe_hit_dirty",
                            "probe_miss_empty", "probe_miss_valid", "probe_miss_dirty"),
}


def classify_write_mask(wmask: int) -> str:
    if wmask == 0:
        return "none"
    if wmask in {1 << i for i in range(8)}:
        return "byte"
    if wmask in {0x3, 0x6, 0xC, 0x18, 0x30, 0x60}:
        return "adjacent"
    if wmask == 0x0F:
        return "low_half"
    if wmask == 0xF0:
        return "high_half"
    if wmask == 0xFF:
        return "full"
    return "sparse"


def classify_refill_path(request: sb.CpuRequest, mem_requests) -> str:
    if mem_requests:
        has_writeback = any(req.cmd in {sb.WRITE_BURST, sb.WRITE_LAST} for req in mem_requests)
        if request.cmd == sb.WRITE:
            return "write_miss_dirty_refill" if has_writeback else "write_miss_clean_refill"
        return "dirty_miss_writeback_refill" if has_writeback else "clean_miss_refill"
    return "read_hit" if request.cmd == sb.READ else "write_hit"


class CacheCoverageCollector:
    def __init__(self):
        self.counters = {name: Counter() for name in EXPECTED_BINS}
        self.transactions = []
        self._line_dirty: Dict[int, bool] = {}

    @staticmethod
    def _is_mmio(addr: int) -> bool:
        return ((addr ^ 0x30000000) & 0xF0000000) == 0 or \
               ((addr ^ 0x40000000) & 0xC0000000) == 0

    def record(self, *, request: sb.CpuRequest, mem_requests, response):
        hit_miss_proxy = "hit" if not mem_requests else "miss"
        refill_path = classify_refill_path(request, mem_requests)
        has_writeback = any(req.cmd in {sb.WRITE_BURST, sb.WRITE_LAST} for req in mem_requests)
        if request.cmd == sb.WRITE and mem_requests:
            write_miss = "dirty" if has_writeback else "clean"
        else:
            write_miss = "none"
        cmd_type = "read" if request.cmd == sb.READ else ("write" if request.cmd == sb.WRITE else "probe")
        wmask_class = classify_write_mask(request.wmask)
        word_offset = str((request.addr >> 3) & 0x7)
        line_base = request.addr & ~0x3F
        is_mmio = self._is_mmio(request.addr)
        addr_class = "mmio" if is_mmio else "normal"

        entry = {
            "cmd_type": cmd_type,
            "hit_miss_proxy": hit_miss_proxy,
            "write_mask_class": wmask_class,
            "word_offset": word_offset,
            "refill_path": refill_path,
            "write_miss": write_miss,
            "user": request.user,
            "response_cmd": response.cmd,
            # Cross-dimension (P2-10)
            "write_hit_x_wmask": (f"{wmask_class}_{word_offset}"
                                  if cmd_type == "write" and hit_miss_proxy == "hit" and wmask_class != "none"
                                  else None),
            "miss_x_addr_type": f"{hit_miss_proxy}_{addr_class}",
        }
        # Track dirty state for probe cross-dimension
        if cmd_type == "write" and request.wmask != 0 and not is_mmio:
            self._line_dirty[line_base] = True
        if cmd_type == "probe":
            dirty = self._line_dirty.get(line_base, False)
            valid = line_base in self._line_dirty
            if hit_miss_proxy == "hit":
                state = "dirty" if dirty else ("valid" if valid else "empty")
            else:
                state = "dirty" if dirty else ("valid" if valid else "empty")
            entry["probe_x_cache_state"] = f"probe_{hit_miss_proxy}_{state}"

        self.transactions.append(entry)
        for key, value in entry.items():
            if key in self.counters and value is not None:
                self.counters[key][value] += 1

    def summary(self) -> Dict[str, Dict[str, int]]:
        return {name: dict(counter) for name, counter in self.counters.items()}

    def load_summary(self, summary: Dict[str, Dict[str, int]]):
        for name, bins in summary.items():
            if name not in self.counters:
                continue
            self.counters[name].update(bins)

    def to_json(self) -> Dict[str, object]:
        return {"transactions": self.transactions, "summary": self.summary()}

    def write_json(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_json(), indent=2, sort_keys=True), encoding="utf-8")

    def render_markdown(self, *, seed: int, steps: int, commands_run: Iterable[str]) -> str:
        summary = self.summary()
        lines: List[str] = []
        lines.append("# Coverage Report")
        lines.append("")
        lines.append(f"Seed: `{seed}`")
        lines.append(f"Transactions: `{steps}`")
        lines.append("")
        lines.append("## Commands")
        for command in commands_run:
            lines.append(f"- `{command}`")
        lines.append("")

        for bin_name, expected_bins in EXPECTED_BINS.items():
            lines.append(f"## {bin_name.replace('_', ' ').title()}")
            lines.append("")
            lines.append("| Bin | Count | Status |")
            lines.append("| --- | ---: | --- |")
            counts = summary.get(bin_name, {})
            for bin_value in expected_bins:
                count = counts.get(bin_value, 0)
                status = "covered" if count else "gap"
                lines.append(f"| `{bin_value}` | {count} | {status} |")
            lines.append("")

        lines.append("## Gaps And Next Actions")
        lines.append("")
        gaps = []
        if summary.get("refill_path", {}).get("dirty_miss_writeback_refill", 0) == 0:
            gaps.append("- Dirty miss writeback/refill path not observed. Add a directed eviction test that fills all 4 ways of one set, dirties them, and then accesses a 5th conflicting line.")
        if summary.get("hit_miss_proxy", {}).get("miss", 0) == 0:
            gaps.append("- No miss was observed. Force at least one cold read in the workload.")
        if summary.get("write_mask_class", {}).get("sparse", 0) == 0:
            gaps.append("- Sparse write-mask class was not observed. Add a write using a non-contiguous mask such as `0x99` or `0xA5`.")
        if summary.get("word_offset", {}).get("7", 0) == 0:
            gaps.append("- Word offset 7 was not observed. Extend the offset schedule to include the last word in the line.")
        if not gaps:
            gaps.append("- No immediate functional-coverage gaps remain in the current bootstrap set.")
        lines.extend(gaps)
        lines.append("")
        return "\n".join(lines)
