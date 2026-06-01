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

    @staticmethod
    def _classify_wmask(mask_val: int):
        """Classify a write mask into one of the standard categories."""
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

    @staticmethod
    def _is_mmio(addr):
        return ((addr ^ 0x30000000) & 0xF0000000) == 0 or \
               ((addr ^ 0x40000000) & 0xC0000000) == 0

    def _capture_req(self, addr_val):
        """Capture last request address (for miss_x_addr_type cross-dimension)."""
        if self._req_active():
            self._last_req_addr = addr_val
            return True
        return False

    def _capture_write(self, wmask_val):
        """Capture pending write request mask/offset (for write_hit_x_wmask cross-dimension)."""
        d = self.dut
        captured = False
        if self._req_active() and d.io_in_req_bits_cmd.value == sb.WRITE:
            wmask_class = self._classify_wmask(wmask_val)
            if wmask_class != "none":
                self._pending_write_wmask = wmask_class
                self._pending_write_offset = (d.io_in_req_bits_addr.value >> 3) & 0x7
                captured = True
        # Clear pending when a memory request fires (write miss, not hit)
        if d.io_out_mem_req_valid.value and d.io_out_mem_req_ready.value:
            self._pending_write_wmask = None
            self._pending_write_offset = None
        return captured

    def _capture_probe_req(self, addr_val):
        """Capture probe request address (for probe_x_cache_state cross-dimension)."""
        d = self.dut
        if d.io_out_coh_req_valid.value and d.io_out_coh_req_ready.value:
            self._last_probe_addr = addr_val
            return True
        return False

    def _track_fill(self, resp_valid_cond):
        """Track line fills for cache state cross-dimension."""
        d = self.dut
        if resp_valid_cond and d.io_in_resp_bits_cmd.value in {sb.READ_LAST, sb.READ_BURST}:
            lb = self._last_req_addr & ~0x3F
            if not self._is_mmio(self._last_req_addr):
                self._line_valid[lb] = True
            return True
        return False

    def _track_write(self):
        """Track write hits to mark lines dirty."""
        d = self.dut
        if self._req_active() and d.io_in_req_bits_cmd.value == sb.WRITE and d.io_in_req_bits_wmask.value != 0:
            addr = d.io_in_req_bits_addr.value
            if not self._is_mmio(addr):
                self._line_dirty[addr & ~0x3F] = True
                return True
        return False

    def _eval_probe_cross(self, result: str, state: str) -> bool:
        """Evaluate probe_x_cache_state cross-dimension bin.

        For probe_hit: state refers to the hit line's cache state.
        For probe_miss: state refers to the overall cache state (any dirty/valid/empty).
        """
        d = self.dut
        if not (d.io_out_coh_resp_valid.value and d.io_out_coh_resp_ready.value):
            return False
        cmd = d.io_out_coh_resp_bits_cmd.value
        is_hit = (cmd == 0xC)
        actual_result = "probe_hit" if is_hit else "probe_miss"
        if actual_result != result:
            return False
        if is_hit:
            # Hit: check the state of the line being probed
            line_base = getattr(self, '_last_probe_addr', 0) & ~0x3F
            if self._line_dirty.get(line_base, False):
                actual_state = "dirty"
            elif line_base in self._line_valid:
                actual_state = "valid"
            else:
                actual_state = "empty"
        else:
            # Miss: check overall cache state (any dirty/valid lines?)
            if any(self._line_dirty.values()):
                actual_state = "dirty"
            elif self._line_valid:
                actual_state = "valid"
            else:
                actual_state = "empty"
        return actual_state == state

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
        wmask_classes = ["none", "byte", "adjacent", "low_half", "high_half", "full", "sparse"]
        g = fc.CovGroup("cache_write_mask_class")
        for cls_name in wmask_classes:
            g.add_watch_point(d.io_in_req_bits_wmask, {
                cls_name: (lambda cn: lambda p: self._mark(f"wmask_{cn}",
                    lambda: self._req_active() and self._classify_wmask(p.value) == cn))(cls_name),
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

        # ═══════════════════════════════════════════════════════════════
        # State tracking for cross-dimension groups
        # Must be initialized BEFORE tracker groups and cross-dim groups
        # ═══════════════════════════════════════════════════════════════

        self._pending_write_wmask = None
        self._pending_write_offset = None
        self._last_req_addr = 0
        self._last_probe_addr = 0
        self._line_valid = {}
        self._line_dirty = {}

        # ── Tracker groups (MUST run BEFORE cross-dim groups so pending
        #    state is up-to-date when write_hit_x_wmask / miss_x_addr_type /
        #    probe_x_cache_state evaluate their watch points) ──
        g = fc.CovGroup("cache_req_tracker")
        g.add_watch_point(d.io_in_req_bits_addr, {
            "track": lambda p: self._capture_req(p.value),
        }, name="req_tracker")
        g.add_watch_point(d.io_in_resp_valid, {
            "track": lambda p: self._track_fill(p.value),
        }, name="fill_tracker")
        self.groups.append(g)

        g = fc.CovGroup("cache_write_tracker")
        g.add_watch_point(d.io_in_req_bits_wmask, {
            "track": lambda p: self._capture_write(p.value),
        }, name="write_tracker")
        g.add_watch_point(d.io_in_req_bits_cmd, {
            "track": lambda p: self._track_write(),
        }, name="write_dirty_tracker")
        self.groups.append(g)

        g = fc.CovGroup("cache_probe_tracker")
        g.add_watch_point(d.io_out_coh_req_bits_addr, {
            "track": lambda p: self._capture_probe_req(p.value),
        }, name="probe_tracker")
        self.groups.append(g)

        # ═══════════════════════════════════════════════════════════════
        # Cross-Dimension Coverage Groups
        # ═══════════════════════════════════════════════════════════════

        # ── Cross-Dim: write_hit_x_wmask (48 bins) ──────────────────
        # Write hits: WRITE request accepted → response arrives without mem_req
        g = fc.CovGroup("cache_write_hit_x_wmask")
        cross_wmask_classes = ["byte", "adjacent", "low_half", "high_half", "full", "sparse"]
        for wc in cross_wmask_classes:
            for off in range(8):
                bin_name = f"{wc}_{off}"
                g.add_watch_point(d.io_in_resp_valid, {
                    bin_name: (lambda _wc=wc, _off=off: lambda p: self._mark(f"wxw_{_wc}_{_off}",
                        lambda: p.value and d.io_in_resp_ready.value
                            and d.io_in_resp_bits_cmd.value == sb.WRITE_RESP
                            and self._pending_write_wmask == _wc
                            and self._pending_write_offset == _off))(),
                }, name=f"wxw_{wc}_{off}")
        self.groups.append(g)

        # ── Cross-Dim: miss_x_addr_type (4 bins) ────────────────────
        g = fc.CovGroup("cache_miss_x_addr_type")
        g.add_watch_point(d.io_out_mem_req_valid, {
            "miss_normal": lambda p: self._mark("mxat_miss_normal",
                lambda: p.value and d.io_out_mem_req_bits_cmd.value in {sb.READ_BURST, sb.WRITE_BURST}
                    and not self._is_mmio(self._last_req_addr)),
        }, name="miss_x_addr_mem")
        g.add_watch_point(d.io_in_resp_valid, {
            "hit_normal": lambda p: self._mark("mxat_hit_normal",
                lambda: p.value and d.io_in_resp_ready.value
                    and not self._is_mmio(self._last_req_addr)),
            "hit_mmio": lambda p: self._mark("mxat_hit_mmio",
                lambda: p.value and d.io_in_resp_ready.value
                    and self._is_mmio(self._last_req_addr)),
        }, name="miss_x_addr_resp")
        self.groups.append(g)

        # ── Cross-Dim: probe_x_cache_state (5 bins) ─────────────────
        # probe_hit_empty is physically unreachable (probe cannot hit an empty line).
        g = fc.CovGroup("cache_probe_x_cache_state")
        for result, states in [("probe_hit", ("valid", "dirty")),
                                ("probe_miss", ("empty", "valid", "dirty"))]:
            for state in states:
                bin_name = f"{result}_{state}"
                g.add_watch_point(d.io_out_coh_resp_valid, {
                    bin_name: (lambda r=result, s=state: lambda p: self._mark(f"pxs_{r}_{s}",
                        lambda: self._eval_probe_cross(r, s)))(result, state),
                }, name=f"pxs_{result}_{state}")
        self.groups.append(g)

        # ── Hook sampling ────────────────────────────────────────────
        if step_ris:
            d.StepRis(lambda _: [g.sample() for g in self.groups])

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
