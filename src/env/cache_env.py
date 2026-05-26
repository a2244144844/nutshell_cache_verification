import importlib
import sys
from pathlib import Path

from src.monitor.cache_monitor import CacheMonitor
from src.scoreboard.cache_scoreboard import CacheScoreboard
from src.utils import simplebus as sb


ROOT_DIR = Path(__file__).resolve().parents[2]
PICKER_BUILD_DIR = ROOT_DIR / "build" / "picker_cache"


def load_dut_class(build_dir=PICKER_BUILD_DIR):
    build_dir = Path(build_dir)
    if not (build_dir / "__init__.py").exists():
        raise FileNotFoundError(f"Picker Cache DUT is not exported: {build_dir}")
    sys.path.insert(0, str(build_dir.parent))
    return importlib.import_module(build_dir.name).DUTCache


def pin_get(pin):
    return int(pin.value)


def pin_set(pin, value):
    pin.value = value


class CacheEnv:
    def __init__(self, dut):
        self.dut = dut
        self.monitor = CacheMonitor()
        self.scoreboard = CacheScoreboard()
        self.dut.InitClock("clock")
        self.set_defaults()

    @classmethod
    def create(cls):
        return cls(load_dut_class()())

    def finish(self):
        self.dut.Finish()

    def step(self, cycles=1):
        self.dut.Step(cycles)

    def set_defaults(self):
        defaults = {
            "io_in_req_valid": 0,
            "io_in_resp_ready": 1,
            "io_flush": 0,
            "io_out_mem_req_ready": 1,
            "io_out_mem_resp_valid": 0,
            "io_out_mem_resp_bits_cmd": 0,
            "io_out_mem_resp_bits_rdata": 0,
            "io_out_coh_req_valid": 0,
            "io_out_coh_resp_ready": 1,
            "io_mmio_req_ready": 1,
            "io_mmio_resp_valid": 0,
            "io_mmio_resp_bits_cmd": 0,
            "io_mmio_resp_bits_rdata": 0,
        }
        for name, value in defaults.items():
            pin_set(getattr(self.dut, name), value)

    def set_pin(self, name, value):
        pin_set(getattr(self.dut, name), value)

    def get_pin(self, name):
        return pin_get(getattr(self.dut, name))

    def drive_cpu_request(self, request: sb.CpuRequest):
        pin_set(self.dut.io_in_req_bits_addr, request.addr)
        pin_set(self.dut.io_in_req_bits_size, request.size)
        pin_set(self.dut.io_in_req_bits_cmd, request.cmd)
        pin_set(self.dut.io_in_req_bits_wmask, request.wmask)
        pin_set(self.dut.io_in_req_bits_wdata, request.wdata)
        pin_set(self.dut.io_in_req_bits_user, request.user)
        pin_set(self.dut.io_in_req_valid, 1)

    def clear_cpu_request(self):
        pin_set(self.dut.io_in_req_valid, 0)

    def drive_mem_response(self, *, cmd, rdata=0):
        pin_set(self.dut.io_out_mem_resp_valid, 1)
        pin_set(self.dut.io_out_mem_resp_bits_cmd, cmd)
        pin_set(self.dut.io_out_mem_resp_bits_rdata, rdata)

    def clear_mem_response(self):
        pin_set(self.dut.io_out_mem_resp_valid, 0)

    def sample_mem_request(self):
        if not pin_get(self.dut.io_out_mem_req_valid):
            return None
        return sb.MemRequest(
            addr=pin_get(self.dut.io_out_mem_req_bits_addr),
            cmd=pin_get(self.dut.io_out_mem_req_bits_cmd),
            size=pin_get(self.dut.io_out_mem_req_bits_size),
            wmask=pin_get(self.dut.io_out_mem_req_bits_wmask),
            wdata=pin_get(self.dut.io_out_mem_req_bits_wdata),
            cycle=0,
        )

    def sample_cpu_response(self):
        if not pin_get(self.dut.io_in_resp_valid):
            return None
        return sb.CpuResponse(
            cmd=pin_get(self.dut.io_in_resp_bits_cmd),
            rdata=pin_get(self.dut.io_in_resp_bits_rdata),
            user=pin_get(self.dut.io_in_resp_bits_user),
            cycle=0,
        )

    def reset(self, timeout=160):
        pin_set(self.dut.reset, 1)
        self.step(5)
        pin_set(self.dut.reset, 0)

        for _ in range(timeout):
            self.step(1)
            if pin_get(self.dut.io_in_req_ready):
                self.monitor.clear()
                return
        raise TimeoutError("Cache did not become ready after reset")

    def send_cpu_request(self, request: sb.CpuRequest, *, refill_data=0, refill_beats=None, timeout=100):
        pin_set(self.dut.io_in_req_bits_addr, request.addr)
        pin_set(self.dut.io_in_req_bits_size, request.size)
        pin_set(self.dut.io_in_req_bits_cmd, request.cmd)
        pin_set(self.dut.io_in_req_bits_wmask, request.wmask)
        pin_set(self.dut.io_in_req_bits_wdata, request.wdata)
        pin_set(self.dut.io_in_req_bits_user, request.user)
        pin_set(self.dut.io_in_req_valid, 1)

        accepted = False
        refill_beats = list(refill_beats) if refill_beats is not None else [refill_data]
        refill_index = None
        response = None
        mem_requests = []

        for cycle in range(timeout):
            will_accept = pin_get(self.dut.io_in_req_valid) and pin_get(self.dut.io_in_req_ready)
            mem_req_valid = pin_get(self.dut.io_out_mem_req_valid)
            mem_req_cmd = None
            if mem_req_valid:
                mem_req = sb.MemRequest(
                    addr=pin_get(self.dut.io_out_mem_req_bits_addr),
                    cmd=pin_get(self.dut.io_out_mem_req_bits_cmd),
                    size=pin_get(self.dut.io_out_mem_req_bits_size),
                    wmask=pin_get(self.dut.io_out_mem_req_bits_wmask),
                    wdata=pin_get(self.dut.io_out_mem_req_bits_wdata),
                    cycle=cycle,
                )
                mem_req_cmd = mem_req.cmd
                mem_requests.append(mem_req)
                self.monitor.record_mem_request(mem_req)

            refill_active = refill_index is not None and refill_index < len(refill_beats)
            if refill_active:
                pin_set(self.dut.io_out_mem_resp_valid, 1)
                cmd = sb.READ_LAST if refill_index == len(refill_beats) - 1 else sb.READ
                pin_set(self.dut.io_out_mem_resp_bits_cmd, cmd)
                pin_set(self.dut.io_out_mem_resp_bits_rdata, refill_beats[refill_index])
            elif mem_req_valid and mem_req_cmd in {sb.WRITE_BURST, sb.WRITE_LAST}:
                pin_set(self.dut.io_out_mem_resp_valid, 1)
                pin_set(self.dut.io_out_mem_resp_bits_cmd, sb.WRITE_RESP)
                pin_set(self.dut.io_out_mem_resp_bits_rdata, 0)
            else:
                pin_set(self.dut.io_out_mem_resp_valid, 0)

            self.step(1)

            if will_accept and not accepted:
                accepted = True
                pin_set(self.dut.io_in_req_valid, 0)
                self.monitor.record_cpu_request(request, cycle)

            if refill_active:
                refill_index += 1
            elif mem_req_valid and refill_index is None and mem_req_cmd == sb.READ_BURST:
                refill_index = 0

            if pin_get(self.dut.io_in_resp_valid) and response is None:
                response = sb.CpuResponse(
                    cmd=pin_get(self.dut.io_in_resp_bits_cmd),
                    rdata=pin_get(self.dut.io_in_resp_bits_rdata),
                    user=pin_get(self.dut.io_in_resp_bits_user),
                    cycle=cycle,
                )
                self.monitor.record_cpu_response(response)

            refill_done = refill_index is None or refill_index >= len(refill_beats)
            if response is not None and refill_done:
                pin_set(self.dut.io_out_mem_resp_valid, 0)
                self.step(1)
                return response, mem_requests

        raise TimeoutError(
            f"Cache request timed out: cmd={request.cmd}, addr=0x{request.addr:x}, accepted={accepted}"
        )
