# Cache GenSpec Input Bundle

This directory is a read-only overlay for the UCAgent GenSpec workflow. It is
not the executable verification tree.

## DUT Identity

- DUT name: `Cache`
- Main RTL: `Cache.v`
- Auxiliary RTL/config: `Test.v`, `Cache.yaml`
- Source origin: `rtl/dut/` from the Track1 NutShell Cache workspace

## Included Context

The `docs/` directory contains curated project documentation copied from the
current verification workspace:

- DUT selection and interface mapping
- Existing verification needs and FG/FC/CK checkpoint definitions
- Current coverage, test point, and bug-analysis evidence

## Output Policy

Generated GenSpec artifacts are written to `../unity_test/` relative to this
workspace. After review, only non-conflicting artifacts should be copied back to
the main project `unity_test/` directory.
