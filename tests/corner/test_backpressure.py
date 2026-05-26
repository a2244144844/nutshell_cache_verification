import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

from src.env.cache_env import CacheEnv
from src.utils import simplebus as sb


def _mem_request_signature(env: CacheEnv):
    mem_req = env.sample_mem_request()
    if mem_req is None:
        return None
    return (mem_req.addr, mem_req.cmd, mem_req.size, mem_req.wmask, mem_req.wdata)


def _cpu_response_signature(env: CacheEnv):
    cpu_resp = env.sample_cpu_response()
    if cpu_resp is None:
        return None
    return (cpu_resp.cmd, cpu_resp.rdata, cpu_resp.user)


def test_memory_request_backpressure_holds_request_until_ready():
    env = CacheEnv.create()

    try:
        env.reset()

        addr = 0x8000_4000
        user = 0x501
        refill_data = 0x1111_2222_3333_4444

        env.set_pin("io_out_mem_req_ready", 0)
        env.drive_cpu_request(sb.CpuRequest(cmd=sb.READ, addr=addr, user=user))

        held_requests = []
        for _ in range(8):
            signature = _mem_request_signature(env)
            if signature is not None:
                held_requests.append(signature)
            env.step(1)

        assert len(held_requests) >= 2, "memory request should remain valid while ready is low"
        assert held_requests[0][0] == addr
        assert held_requests[0][1] == sb.READ_BURST
        assert held_requests[0][2] == 3
        assert all(signature == held_requests[0] for signature in held_requests)

        env.set_pin("io_out_mem_req_ready", 1)

        response = None
        for _ in range(20):
            if env.get_pin("io_out_mem_req_valid") and env.get_pin("io_out_mem_req_ready"):
                env.drive_mem_response(cmd=sb.READ_LAST, rdata=refill_data)
            else:
                env.clear_mem_response()

            response_signature = _cpu_response_signature(env)
            if response_signature is not None:
                response = response_signature
                break

            env.step(1)

        assert response == (sb.READ_LAST, refill_data, user)
    finally:
        env.clear_cpu_request()
        env.clear_mem_response()
        env.finish()


def test_cpu_response_backpressure_holds_response_until_ready():
    env = CacheEnv.create()

    try:
        env.reset()

        addr = 0x8000_5000
        user = 0x601
        refill_data = 0xAAAA_BBBB_CCCC_DDDD

        env.set_pin("io_in_resp_ready", 1)
        env.drive_cpu_request(sb.CpuRequest(cmd=sb.READ, addr=addr, user=user))

        response_valid_signatures = []
        seen_mem_request = False
        response = None

        for _ in range(20):
            mem_signature = _mem_request_signature(env)
            if mem_signature is not None:
                assert mem_signature[0] == addr
                assert mem_signature[1] == sb.READ_BURST
                assert mem_signature[2] == 3
                seen_mem_request = True
                if env.get_pin("io_in_resp_ready"):
                    env.set_pin("io_in_resp_ready", 0)
                env.drive_mem_response(cmd=sb.READ_LAST, rdata=refill_data)
            else:
                env.clear_mem_response()

            if seen_mem_request:
                response_signature = _cpu_response_signature(env)
                if response_signature is not None:
                    response_valid_signatures.append(response_signature)
                    if len(response_valid_signatures) == 2:
                        env.set_pin("io_in_resp_ready", 1)
                if env.get_pin("io_in_resp_ready") and response_signature is not None:
                    response = response_signature
                    break

            env.step(1)

        assert seen_mem_request, "read miss should generate a memory request before the response"
        assert len(response_valid_signatures) >= 2, "CPU response should stay valid while ready is low"
        assert all(signature == (sb.READ_LAST, refill_data, user) for signature in response_valid_signatures)
        assert response == (sb.READ_LAST, refill_data, user)
    finally:
        env.clear_cpu_request()
        env.clear_mem_response()
        env.finish()
