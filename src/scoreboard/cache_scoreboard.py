from src.utils import simplebus as sb


class CacheScoreboard:
    def check_read_response(self, response, *, expected_data, expected_user):
        assert response.cmd == sb.READ_LAST
        assert response.rdata == expected_data
        assert response.user == expected_user

    def check_write_response(self, response, *, expected_user):
        assert response.cmd == sb.WRITE_RESP
        assert response.user == expected_user

    def check_single_read_burst(self, mem_requests, *, expected_addr):
        assert len(mem_requests) == 1
        assert mem_requests[0].addr == expected_addr
        assert mem_requests[0].cmd == sb.READ_BURST

    def check_no_memory_request(self, mem_requests):
        assert mem_requests == []

    def check_dirty_writeback_refill(self, mem_requests, *, victim_addr, refill_addr, expected_write_data=None):
        write_reqs = [req for req in mem_requests if req.cmd in {sb.WRITE_BURST, sb.WRITE_LAST}]
        read_reqs = [req for req in mem_requests if req.cmd in {sb.READ_BURST, sb.READ_LAST}]

        assert write_reqs, "expected at least one dirty writeback request"
        assert read_reqs, "expected a refill request after writeback"
        assert write_reqs[-1].cmd == sb.WRITE_LAST
        assert read_reqs[0].cmd == sb.READ_BURST
        assert all(req.addr == victim_addr for req in write_reqs)
        assert all(req.addr == refill_addr for req in read_reqs)
        assert mem_requests.index(write_reqs[0]) < mem_requests.index(read_reqs[0])

        if expected_write_data is not None:
            assert all(req.wdata == expected_write_data for req in write_reqs)
