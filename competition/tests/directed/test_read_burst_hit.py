import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

import toffee_test

from src.utils import simplebus as sb


@toffee_test.testcase
async def test_read_burst_hit_returns_data(cache_env):
    """Read-burst hit: fill a line with known data, send READ_BURST to the
    same address.  The DUT treats READ_BURST as a hit that traverses the
    hitReadBurst path (s_idle -> s_release) and returns a single-beat CPU
    response with the requested word.  Covers lines 513 (hitReadBurst),
    605 (respToL1Fire), 608-610 (respToL1Last counter), 771-772
    (s_release transition), 800 (readBeatCnt advance), and 870
    (respToL1Last increment)."""
    env = cache_env
    env.reset()

    addr = 0x8000_1000
    words = [0x1111_1111_0000_0000 + i for i in range(8)]

    resp, mem = env.send_cpu_request(
        sb.CpuRequest(cmd=sb.READ, addr=addr, user=0x701),
        refill_beats=words,
    )
    env.scoreboard.check_read_response(resp, expected_data=words[0], expected_user=0x701)
    env.scoreboard.check_single_read_burst(mem, expected_addr=addr)

    addr_word_index = (addr >> 3) & 0x7

    env.set_pin("io_in_req_bits_addr", addr)
    env.set_pin("io_in_req_bits_size", 3)
    env.set_pin("io_in_req_bits_cmd", sb.READ_BURST)
    env.set_pin("io_in_req_bits_wmask", 0)
    env.set_pin("io_in_req_bits_wdata", 0)
    env.set_pin("io_in_req_bits_user", 0x702)
    env.set_pin("io_in_req_valid", 1)

    accepted = False
    response = None
    for _ in range(200):
        will_accept = bool(
            env.get_pin("io_in_req_valid")
            and env.get_pin("io_in_req_ready")
        )
        cur_valid = bool(env.get_pin("io_in_resp_valid"))
        if cur_valid and response is None:
            response = (
                env.get_pin("io_in_resp_bits_cmd"),
                env.get_pin("io_in_resp_bits_rdata"),
                env.get_pin("io_in_resp_bits_user"),
            )

        env.step(1)

        if will_accept and not accepted:
            accepted = True
            env.set_pin("io_in_req_valid", 0)

        if accepted and response is not None:
            break

    assert accepted, "READ_BURST request was not accepted"
    assert response is not None, "no response received for READ_BURST request"

    cmd, rdata, user = response
    assert cmd == sb.READ_LAST, f"expected cmd=READ_LAST(6), got {cmd}"
    assert rdata == words[addr_word_index], (
        f"expected rdata=0x{words[addr_word_index]:016x} for word offset {addr_word_index}, "
        f"got 0x{rdata:016x}"
    )
    assert user == 0x702, f"expected user=0x702, got {user}"

    env.set_pin("io_in_req_valid", 0)
    env.step(5)


@toffee_test.testcase
async def test_read_burst_hit_resptol1_counter(cache_env):
    """DIR-018: respToL1Last counter lifecycle.

    Fill a cache line, drive READ_BURST to the hit line, then continue
    stepping well past the CPU response to let the 8-beat internal release
    sequence (state=8 with state2 cycling) fully complete so the
    respToL1Last counter (line 607) reaches 7 (line 608) and triggers
    respToL1Last (line 610).  Also counts CPU/coherence response beats
    and documents single-beat vs multi-beat behavior.

    Target coverage: lines 605 (respToL1Fire), 608 (wrap at 7), 610
    (respToL1Last = ... & wrap_wrap)."""
    env = cache_env
    env.reset()

    addr = 0x8000_1000
    words = [0xAAAA_0000_0000_0000 + i for i in range(8)]

    resp, mem = env.send_cpu_request(
        sb.CpuRequest(cmd=sb.READ, addr=addr, user=0x801),
        refill_beats=words,
    )
    env.scoreboard.check_read_response(resp, expected_data=words[0], expected_user=0x801)
    env.scoreboard.check_single_read_burst(mem, expected_addr=addr)

    addr_word_index = (addr >> 3) & 0x7

    env.set_pin("io_in_req_bits_addr", addr)
    env.set_pin("io_in_req_bits_size", 3)
    env.set_pin("io_in_req_bits_cmd", sb.READ_BURST)
    env.set_pin("io_in_req_bits_wmask", 0)
    env.set_pin("io_in_req_bits_wdata", 0)
    env.set_pin("io_in_req_bits_user", 0x802)
    env.set_pin("io_in_req_valid", 1)

    accepted = False
    cpu_responses = []
    coh_responses = []
    cycle = 0

    for _ in range(500):
        will_accept = bool(
            env.get_pin("io_in_req_valid")
            and env.get_pin("io_in_req_ready")
        )

        cur_cpu_valid = bool(env.get_pin("io_in_resp_valid"))
        if cur_cpu_valid:
            beat = (
                cycle,
                env.get_pin("io_in_resp_bits_cmd"),
                env.get_pin("io_in_resp_bits_rdata"),
                env.get_pin("io_in_resp_bits_user"),
            )
            if beat not in cpu_responses:
                cpu_responses.append(beat)

        cur_coh_valid = bool(env.get_pin("io_out_coh_resp_valid"))
        if cur_coh_valid:
            coh_beat = (
                cycle,
                env.get_pin("io_out_coh_resp_bits_cmd"),
                env.get_pin("io_out_coh_resp_bits_rdata"),
            )
            coh_responses.append(coh_beat)

        env.step(1)
        cycle += 1

        if will_accept and not accepted:
            accepted = True
            env.set_pin("io_in_req_valid", 0)

        if accepted and cpu_responses and cycle >= 100:
            break

    assert accepted, "READ_BURST request was not accepted"
    assert len(cpu_responses) >= 1, "no CPU response received"

    c_cmd, c_rdata, c_user = (
        cpu_responses[0][1],
        cpu_responses[0][2],
        cpu_responses[0][3],
    )
    assert c_cmd == sb.READ_LAST, f"expected cmd=READ_LAST(6), got {c_cmd}"
    assert c_rdata == words[addr_word_index], (
        f"expected rdata=0x{words[addr_word_index]:016x}, "
        f"got 0x{c_rdata:016x}"
    )
    assert c_user == 0x802, f"expected user=0x802, got {c_user}"

    env.set_pin("io_in_req_valid", 0)
    env.step(10)
