"""Standard UCAgent functional coverage wrapper for Cache.

The coverage model itself lives in ``src.utils.toffee_coverage``.  This file
adapts it to the expected ``get_coverage_groups(dut)`` entry point.
"""

from pathlib import Path
from types import SimpleNamespace
import sys


ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.env.cache_env import CacheEnv
from src.utils.toffee_coverage import CacheCoverage


def _as_env(dut):
    if isinstance(dut, CacheEnv):
        return dut
    return SimpleNamespace(dut=dut)


def get_coverage_groups(dut):
    """Return Toffee CovGroup objects for a CacheEnv or raw Picker DUT."""
    coverage = CacheCoverage(_as_env(dut), step_ris=False)
    return coverage.groups


def create_coverage(dut):
    """Return the full CacheCoverage object when callers need report helpers."""
    return CacheCoverage(_as_env(dut), step_ris=False)
