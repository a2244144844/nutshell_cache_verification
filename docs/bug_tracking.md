# Bug Tracking

Date: 2026-05-26

## Bug ID

`BUG-001`

## Injected Fault

Corrupted reference-model `read_word()` logic flips bit `0` of the expected 64-bit refill data.

## Trigger

Run:

```sh
source scripts/env.sh && /Users/zzy/Workspace/ucagent/.venv/bin/python tests/injected_bug/run_bug_injection.py
```

The harness reads `0x80000000`, refills it with `0x1122334455667788`, then compares the DUT response against the corrupted reference model result `0x1122334455667789`.

## Detection Path

`env.scoreboard.check_read_response()` rejects the mismatched read response.

## Failure Evidence

Observed command result:

```text
BUG-001 mode=enabled: corrupting reference-model read_word() flips bit 0 at addr 0x80000000
BUG-001 expected_data=0x1122334455667789, actual_data=0x1122334455667788
AssertionError: BUG-001 detected by scoreboard.check_read_response: reference-model corruption made the expected read data 0x1122334455667789 while the DUT returned 0x1122334455667788 at addr 0x80000000
```

Command exit status: `1`

## Cleanup / Recovery

Disable the injected fault with:

```sh
source scripts/env.sh && /Users/zzy/Workspace/ucagent/.venv/bin/python tests/injected_bug/run_bug_injection.py --disable-bug
```

Recovery command result:

```text
BUG-001 mode=disabled: clean reference-model read_word() at addr 0x80000000
BUG-001 expected_data=0x1122334455667788, actual_data=0x1122334455667788
BUG-001 recovery path: bug injection disabled, scoreboard checks passed.
```

Recovery command exit status: `0`
