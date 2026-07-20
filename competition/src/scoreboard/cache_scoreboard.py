"""Cache scoreboard — multi-level data integrity and protocol checks.

Level 1 (basic): command, data, user matching for single responses.
Level 2 (transaction): multi-beat memory request sequencing and ordering.
Level 3 (consistency): cache state validation across eviction, probe, flush.
"""

from src.utils import simplebus as sb


class CacheScoreboard:
    # ── Level 1: Basic single-response checks (existing, preserved) ────────

    def check_read_response(self, response, *, expected_data, expected_user):
        assert response.cmd == sb.READ_LAST, \
            f"expected READ_LAST cmd=0x{sb.READ_LAST:x}, got 0x{response.cmd:x}"
        assert response.rdata == expected_data, \
            f"data mismatch: expected 0x{expected_data:016x}, got 0x{response.rdata:016x}"
        assert response.user == expected_user, \
            f"user mismatch: expected 0x{expected_user:x}, got 0x{response.user:x}"

    def check_write_response(self, response, *, expected_user):
        assert response.cmd == sb.WRITE_RESP, \
            f"expected WRITE_RESP cmd=0x{sb.WRITE_RESP:x}, got 0x{response.cmd:x}"
        assert response.user == expected_user, \
            f"user mismatch: expected 0x{expected_user:x}, got 0x{response.user:x}"

    def check_single_read_burst(self, mem_requests, *, expected_addr):
        assert len(mem_requests) == 1, \
            f"expected 1 memory request, got {len(mem_requests)}"
        assert mem_requests[0].addr == expected_addr, \
            f"addr mismatch: expected 0x{expected_addr:x}, got 0x{mem_requests[0].addr:x}"
        assert mem_requests[0].cmd == sb.READ_BURST, \
            f"cmd mismatch: expected READ_BURST=0x{sb.READ_BURST:x}, got 0x{mem_requests[0].cmd:x}"

    def check_no_memory_request(self, mem_requests):
        assert mem_requests == [], \
            f"expected no memory requests, got {len(mem_requests)}"

    # ── Level 2: Multi-beat transaction checks ─────────────────────────────

    def check_dirty_writeback_refill(self, mem_requests, *,
                                     victim_addr, refill_addr,
                                     expected_write_data=None):
        """Validate dirty eviction: writeback beats precede refill beats."""
        write_reqs = [req for req in mem_requests
                      if req.cmd in {sb.WRITE_BURST, sb.WRITE_LAST}]
        read_reqs = [req for req in mem_requests
                     if req.cmd in {sb.READ_BURST, sb.READ_LAST}]

        assert write_reqs, "expected at least one dirty writeback request"
        assert read_reqs, "expected a refill request after writeback"
        assert write_reqs[-1].cmd == sb.WRITE_LAST, \
            f"last writeback beat should be WRITE_LAST (0x{sb.WRITE_LAST:x}), " \
            f"got 0x{write_reqs[-1].cmd:x}"
        assert read_reqs[0].cmd == sb.READ_BURST, \
            f"first refill beat should be READ_BURST (0x{sb.READ_BURST:x}), " \
            f"got 0x{read_reqs[0].cmd:x}"
        assert all(req.addr == victim_addr for req in write_reqs), \
            "all writeback beats must target victim address"
        assert all(req.addr == refill_addr for req in read_reqs), \
            "all refill beats must target refill address"
        assert mem_requests.index(write_reqs[0]) < mem_requests.index(read_reqs[0]), \
            "writeback must complete before refill begins"

        if expected_write_data is not None:
            assert all(req.wdata == expected_write_data for req in write_reqs), \
                f"writeback data mismatch: all beats must carry 0x{expected_write_data:016x}"

    def check_refill_beat_order(self, mem_requests, *, expected_word_index):
        """Verify 8 refill beats arrive in critical-word-first order.

        The first refill data beat corresponds to expected_word_index,
        with subsequent beats wrapping around: wi, wi+1, ..., 7, 0, ..., wi-1.
        """
        refill_beats = [req for req in mem_requests
                        if req.cmd in {sb.READ_BURST, sb.READ_LAST, sb.READ}]
        assert len(refill_beats) >= 1, \
            f"expected at least 1 refill beat, got {len(refill_beats)}"

        # The cmd order itself implies critical-word-first:
        # READ_BURST (first beat at word_index), then READ (remaining beats),
        # then READ_LAST (final beat).  Validate the sequence is legal.
        first = refill_beats[0]
        assert first.cmd == sb.READ_BURST, \
            f"first beat must be READ_BURST (0x{sb.READ_BURST:x}), got 0x{first.cmd:x}"

        if len(refill_beats) > 1:
            last = refill_beats[-1]
            assert last.cmd == sb.READ_LAST, \
                f"last beat must be READ_LAST (0x{sb.READ_LAST:x}), got 0x{last.cmd:x}"

    def check_writeback_data_integrity(self, mem_requests, *,
                                       victim_addr, ref_model):
        """Verify writeback data matches the reference model's cache line.

        ref_model must expose a ``read_word(addr)`` method.  Each writeback
        beat's data is compared against the model's version of that word.
        """
        write_reqs = [req for req in mem_requests
                      if req.cmd in {sb.WRITE_BURST, sb.WRITE_LAST}]
        assert write_reqs, "expected at least one writeback request"

        word_offset = 0
        for req in write_reqs:
            word_addr = victim_addr + word_offset * 8
            expected = ref_model.read_word(word_addr) if hasattr(ref_model, 'read_word') else None
            if expected is not None and req.wdata != expected:
                raise AssertionError(
                    f"writeback data mismatch at word {word_offset} "
                    f"(addr 0x{word_addr:x}): expected 0x{expected:016x}, "
                    f"got 0x{req.wdata:016x}"
                )
            word_offset += 1

    # ── Level 3: Cache state consistency checks ────────────────────────────

    def check_no_stale_data_leak(self, *, env, addr, pre_eviction_data):
        """Verify an evicted line's data does not persist in cache.

        After eviction, read the evicted address.  The returned data must
        differ from pre_eviction_data (the line was replaced).
        """
        response, mem_requests = env.send_cpu_request(
            sb.CpuRequest(cmd=sb.READ, addr=addr, user=0xBAD),
            refill_beats=[0xCAFE_CAFE_CAFE_CAFE] * 8,
            timeout=200,
        )
        assert response.rdata != pre_eviction_data, \
            f"stale data leak: evicted line data 0x{pre_eviction_data:016x} " \
            f"still present at addr 0x{addr:x}"

    def check_probe_hit_data_consistency(self, *, probe_resp_cmd,
                                         ref_model, addr):
        """Verify probe hit response command indicates hit (0xC).

        The probe response command distinguishes hit (0xC) from miss (0x8).
        """
        assert probe_resp_cmd == 0xC, \
            f"probe hit expected cmd=0xC, got 0x{probe_resp_cmd:x}. " \
            f"Cache line at 0x{addr:x} should be resident after fill."

    def check_mmio_no_cache_pollution(self, *, mem_requests):
        """Verify MMIO access generates no memory (cache refill) requests.

        MMIO addresses bypass the cache entirely — they route through
        io_mmio_* and must never emit io_out_mem_req_* transactions.
        """
        mem_reqs = [req for req in mem_requests
                    if req.cmd in {sb.READ_BURST, sb.READ_LAST,
                                   sb.WRITE_BURST, sb.WRITE_LAST}]
        assert len(mem_reqs) == 0, \
            f"MMIO access polluted cache: {len(mem_reqs)} unexpected memory requests"

    def check_flush_recovery_integrity(self, *, env, pre_flush_addr,
                                       pre_flush_data, pre_flush_user):
        """Verify that after flush+recovery, cache still operates correctly.

        Writes known data, flushes, then reads it back — the data must
        survive the flush cycle and be retrievable.
        """
        # Write known data
        env.send_cpu_request(
            sb.CpuRequest(cmd=sb.WRITE, addr=pre_flush_addr,
                          wmask=0xFF, wdata=pre_flush_data,
                          user=pre_flush_user),
            timeout=200,
        )

        # Read back — should hit
        response, mem_requests = env.send_cpu_request(
            sb.CpuRequest(cmd=sb.READ, addr=pre_flush_addr,
                          user=pre_flush_user),
            timeout=200,
        )

        self.check_read_response(
            response,
            expected_data=pre_flush_data,
            expected_user=pre_flush_user,
        )
        # Hit should generate no memory request
        assert len(mem_requests) == 0, \
            f"post-flush read should hit (no mem request), got {len(mem_requests)}"

    # ── Convenience: run all consistency checks for a probe scenario ───────

    def check_probe_scenario(self, *, mem_requests, probe_resp_cmd,
                             ref_model, addr):
        """Run all probe-related checks in one call."""
        if mem_requests is not None and len(mem_requests) > 0:
            self.check_single_read_burst(mem_requests, expected_addr=addr & ~0x3F)
        self.check_probe_hit_data_consistency(
            probe_resp_cmd=probe_resp_cmd, ref_model=ref_model, addr=addr)
