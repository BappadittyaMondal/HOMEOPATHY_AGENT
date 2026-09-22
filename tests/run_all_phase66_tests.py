"""
Automated Test Runner for Phase 66: Acute-on-Chronic Case Segregation State Machine (INV-18).
"""
import sys
import pytest


def run_phase66_tests() -> int:
    print("=" * 80)
    print("RUNNING PHASE 66: ACUTE-ON-CHRONIC CASE SEGREGATION TEST SUITE (INV-18)")
    print("=" * 80)
    args = [
        "tests/test_phase66.py",
        "-v",
        "--tb=short"
    ]
    return pytest.main(args)


if __name__ == "__main__":
    sys.exit(run_phase66_tests())
