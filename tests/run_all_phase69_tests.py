"""
Automated Test Runner for Phase 69: Static Geospatial Indian District Groundwater Risk Correlator (Geo-Epi).
"""
import sys
import pytest


def run_phase69_tests() -> int:
    print("=" * 80)
    print("RUNNING PHASE 69: GEOSPATIAL GROUNDWATER RISK CORRELATOR TEST SUITE (GEO-EPI)")
    print("=" * 80)
    args = [
        "tests/test_phase69.py",
        "-v",
        "--tb=short"
    ]
    return pytest.main(args)


if __name__ == "__main__":
    sys.exit(run_phase69_tests())
