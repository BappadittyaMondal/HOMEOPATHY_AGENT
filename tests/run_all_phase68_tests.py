"""
Automated Test Runner for Phase 68: Mental-Somatic Dissociation Index (MSDI / Aphorism 253).
"""
import sys
import pytest


def run_phase68_tests() -> int:
    print("=" * 80)
    print("RUNNING PHASE 68: MENTAL-SOMATIC DISSOCIATION INDEX TEST SUITE (APHORISM 253)")
    print("=" * 80)
    args = [
        "tests/test_phase68.py",
        "-v",
        "--tb=short"
    ]
    return pytest.main(args)


if __name__ == "__main__":
    sys.exit(run_phase68_tests())
