import toffee.funcov as fc

from src.utils import simplebus as sb


class CacheCoverage:
    """Toffee-based functional coverage for the Cache DUT.

    Uses `toffee.funcov.CovGroup` with `add_watch_point` to define coverage
    bins. Bins are evaluated on every clock cycle and latch True once their
    condition is met.

    When *step_ris* is True (default), sampling is driven by ``dut.StepRis``.
    Set *step_ris* to False when toffee manages periodic sampling via
    ``toffee_request.add_cov_groups(..., periodic_sample=True)``.
    """

    def __init__(self, env, step_ris=True):
        self.env = env
        self.dut = env.dut
        self._flags = {}
        self.groups = []
        self._setup(step_ris=step_ris)

    def _mark(self, key, condition):
        if key not in self._flags:
            self._flags[key] = False
        if not self._flags[key] and condition():
            self._flags[key] = True
        return self._flags[key]

    def _req_active(self):
        d = self.dut
        return d.io_in_req_valid.value and d.io_in_req_ready.value

    def _setup(self, step_ris=True):
        d = self.dut

        # ── Group: cmd_type ──────────────────────────────────────────
        g = fc.CovGroup("cache_cmd_type")
        g.add_watch_point(d.io_in_req_bits_cmd, {
            "read": lambda p: self._mark("cmd_read",
                lambda: self._req_active() and p.value == sb.READ),
            "write": lambda p: self._mark("cmd_write",
                lambda: self._req_active() and p.value == sb.WRITE),
        }, name="cmd_type")
        g.add_watch_point(d.io_out_coh_req_valid, {
            "probe": lambda p: self._mark("cmd_probe",
                lambda: p.value and d.io_out_coh_req_ready.value and d.io_out_coh_req_bits_cmd.value == sb.PROBE),
        }, name="cmd_type_coh")
        self.groups.append(g)

        # ── Group: hit_miss ──────────────────────────────────────────
        g = fc.CovGroup("cache_hit_miss")
        g.add_watch_point(d.io_out_mem_req_valid, {
            "miss": lambda p: self._mark("miss",
                lambda: p.value and d.io_out_mem_req_bits_cmd.value in {sb.READ_BURST, sb.WRITE_BURST}),
        }, name="hit_miss_mem")
        g.add_watch_point(d.io_in_resp_valid, {
            "hit": lambda p: self._mark("hit",
                lambda: p.value and d.io_in_resp_ready.value),
        }, name="hit_miss_resp")
        self.groups.append(g)

        # ── Group: write_mask_class ──────────────────────────────────
        def _wmask_bin(mask_val):
            if mask_val == 0:
                return "none"
            if mask_val in {1 << i for i in range(8)}:
                return "byte"
            if mask_val in {0x03, 0x06, 0x0C, 0x18, 0x30, 0x60, 0xC0}:
                return "adjacent"
            if mask_val == 0x0F:
                return "low_half"
            if mask_val == 0xF0:
                return "high_half"
            if mask_val == 0xFF:
                return "full"
            return "sparse"

        wmask_classes = ["none", "byte", "adjacent", "low_half", "high_half", "full", "sparse"]
        g = fc.CovGroup("cache_write_mask_class")
        for cls_name in wmask_classes:
            g.add_watch_point(d.io_in_req_bits_wmask, {
                cls_name: (lambda cn: lambda p: self._mark(f"wmask_{cn}",
                    lambda: self._req_active() and _wmask_bin(p.value) == cn))(cls_name),
            }, name=f"wmask_{cls_name}")
        self.groups.append(g)

        # ── Group: addr_class ────────────────────────────────────────
        g = fc.CovGroup("cache_addr_class")
        g.add_watch_point(d.io_in_req_bits_addr, {
            "normal": lambda p: self._mark("addr_normal",
                lambda: self._req_active() and not self._is_mmio(p.value)),
            "mmio": lambda p: self._mark("addr_mmio",
                lambda: self._req_active() and self._is_mmio(p.value)),
        }, name="addr_class")
        self.groups.append(g)

        # ── Group: refill_path ───────────────────────────────────────
        g = fc.CovGroup("cache_refill_path")
        g.add_watch_point(d.io_out_mem_req_valid, {
            "writeback": lambda p: self._mark("wb_seen",
                lambda: p.value and d.io_out_mem_req_bits_cmd.value in {sb.WRITE_BURST, sb.WRITE_LAST}),
        }, name="refill_wb")
        g.add_watch_point(d.io_out_mem_req_valid, {
            "clean_miss_refill": lambda p: self._mark("clean_miss",
                lambda: p.value and d.io_out_mem_req_bits_cmd.value == sb.READ_BURST and not self._flags.get("wb_seen", False)),
            "dirty_miss_writeback_refill": lambda p: self._mark("dirty_miss",
                lambda: self._flags.get("wb_seen", False) and p.value and d.io_out_mem_req_bits_cmd.value == sb.READ_BURST),
        }, name="refill_path_mem")
        g.add_watch_point(d.io_mmio_req_valid, {
            "mmio": lambda p: self._mark("mmio_path", lambda: p.value),
        }, name="refill_path_mmio")
        self.groups.append(g)

        # ── Group: backpressure ──────────────────────────────────────
        g = fc.CovGroup("cache_backpressure")
        g.add_watch_point(d.io_in_resp_ready, {
            "cpu_resp": lambda p: self._mark("bp_cpu",
                lambda: p.value == 0 and d.io_in_resp_valid.value),
        }, name="bp_cpu")
        g.add_watch_point(d.io_out_mem_req_ready, {
            "mem_req": lambda p: self._mark("bp_mem",
                lambda: p.value == 0 and d.io_out_mem_req_valid.value),
        }, name="bp_mem")
        self.groups.append(g)

        # ── Aux: request-accepted tracker (must be before flush group) ──
        g = fc.CovGroup("cache_req_accepted")
        g.add_watch_point(d.io_in_req_ready, {
            "accepted": lambda p: self._mark("req_accepted",
                lambda: p.value and d.io_in_req_valid.value),
        }, name="req_accepted")
        self.groups.append(g)

        # ── Group: coherence_probe ─────────────────────────────────────
        g = fc.CovGroup("cache_coherence_probe")
        g.add_watch_point(d.io_out_coh_resp_valid, {
            "probe_hit": lambda p: self._mark("probe_hit",
                lambda: p.value and d.io_out_coh_resp_bits_cmd.value == 0xc),
            "probe_miss": lambda p: self._mark("probe_miss",
                lambda: p.value and d.io_out_coh_resp_bits_cmd.value == 0x8),
        }, name="probe_result")
        self.groups.append(g)

        # ── Group: write_miss ──────────────────────────────────────────
        g = fc.CovGroup("cache_write_miss")
        g.add_watch_point(d.io_in_req_ready, {
            "write_req": lambda p: self._mark("write_req",
                lambda: p.value and d.io_in_req_valid.value and d.io_in_req_bits_cmd.value == sb.WRITE),
        }, name="wr_req_accepted")
        g.add_watch_point(d.io_out_mem_req_valid, {
            "clean": lambda p: self._mark("write_miss_clean",
                lambda: self._flags.get("write_req", False) and p.value
                    and d.io_out_mem_req_bits_cmd.value == sb.READ_BURST
                    and not self._flags.get("wb_seen", False)),
            "dirty": lambda p: self._mark("write_miss_dirty",
                lambda: self._flags.get("write_req", False) and p.value
                    and d.io_out_mem_req_bits_cmd.value == sb.READ_BURST
                    and self._flags.get("wb_seen", False)),
        }, name="write_miss_mem")
        self.groups.append(g)

        # ── Group: clean_eviction ──────────────────────────────────────
        self._clean_refill_count = 0
        g = fc.CovGroup("cache_clean_eviction")

        def _inc_clean_and_check(cond):
            if cond() and not self._flags.get("clean_eviction", False):
                if not self._flags.get("wb_seen", False):
                    self._clean_refill_count += 1
                    if self._clean_refill_count >= 5:
                        self._flags["clean_eviction"] = True
                        return True
            return self._flags.get("clean_eviction", False)

        g.add_watch_point(d.io_out_mem_req_valid, {
            "clean_eviction": lambda p: _inc_clean_and_check(
                lambda: p.value and d.io_out_mem_req_bits_cmd.value == sb.READ_BURST),
        }, name="clean_eviction_detect")
        self.groups.append(g)

        # ── Group: flush ─────────────────────────────────────────────
        g = fc.CovGroup("cache_flush")
        g.add_watch_point(d.io_flush, {
            "idle": lambda p: self._mark("flush_idle",
                lambda: p.value != 0 and d.io_empty.value),
            "after_accept": lambda p: self._mark("flush_active",
                lambda: p.value != 0 and self._flags.get("req_accepted", False)),
        }, name="flush")
        self.groups.append(g)

        # ── Group: word_offset ───────────────────────────────────────
        g = fc.CovGroup("cache_word_offset")
        for i in range(8):
            g.add_watch_point(d.io_in_req_bits_addr, {
                str(i): (lambda off: lambda p: self._mark(f"wo_{off}",
                    lambda: self._req_active() and ((p.value >> 3) & 0x7) == off))(i),
            }, name=f"wo_{i}")
        self.groups.append(g)

        # ── Hook sampling ────────────────────────────────────────────
        if step_ris:
            d.StepRis(lambda _: [g.sample() for g in self.groups])

    @staticmethod
    def _is_mmio(addr):
        return ((addr ^ 0x30000000) & 0xF0000000) == 0 or \
               ((addr ^ 0x40000000) & 0xC0000000) == 0

    def mark_test(self, test_func, *, group=None, point=None, bin_name="*"):
        """Associate *test_func* with one or more coverage points.

        When *group* is given only that group is marked. When *point* is
        given only that point within the group(s) is marked.  *bin_name*
        defaults to ``"*"`` (all bins of the point).
        """
        for g in self.groups:
            if group is not None and g.name != group:
                continue
            for pt_name in g.cover_points():
                if point is not None and pt_name != point:
                    continue
                g.mark_function(pt_name, test_func, bin_name, raise_error=False)

    def as_dict(self):
        return {g.name: dict(g.as_dict()) for g in self.groups}

    def clear(self):
        for g in self.groups:
            g.clear()
