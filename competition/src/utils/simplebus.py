from dataclasses import dataclass


READ = 0
WRITE = 1
READ_BURST = 2
WRITE_BURST = 3
PREFETCH = 4
WRITE_RESP = 5
READ_LAST = 6
WRITE_LAST = 7
PROBE = 8


CMD_NAMES = {
    READ: "READ",
    WRITE: "WRITE",
    READ_BURST: "READ_BURST",
    WRITE_BURST: "WRITE_BURST",
    PREFETCH: "PREFETCH",
    WRITE_RESP: "WRITE_RESP",
    READ_LAST: "READ_LAST",
    WRITE_LAST: "WRITE_LAST",
    PROBE: "PROBE",
}


@dataclass(frozen=True)
class CpuRequest:
    cmd: int
    addr: int
    size: int = 3
    wmask: int = 0
    wdata: int = 0
    user: int = 0


@dataclass(frozen=True)
class CpuResponse:
    cmd: int
    rdata: int
    user: int
    cycle: int


@dataclass(frozen=True)
class MemRequest:
    addr: int
    cmd: int
    size: int
    wmask: int
    wdata: int
    cycle: int


def mask_write_64(old_data: int, new_data: int, wmask: int) -> int:
    result = old_data & ((1 << 64) - 1)
    for byte_index in range(8):
        if (wmask >> byte_index) & 1:
            shift = byte_index * 8
            result &= ~(0xFF << shift)
            result |= ((new_data >> shift) & 0xFF) << shift
    return result
