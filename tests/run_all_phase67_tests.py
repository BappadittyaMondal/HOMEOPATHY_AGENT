"""
Automated Test Runner for Phase 67: Dynamic Triplet Keynote Disambiguation Engine.
"""
import sys
import pytest


def run_phase67_tests() -> int:
    print("=" * 80)
    print("RUNNING PHASE 67: DYNAMIC TRIPLET KEYNOTE DISAMBIGUATION TEST SUITE")
    print("=" * 80)
    args = [
        "tests/test_phase67.py",
        "-v",
        "--tb=short"
    ]
    return pytest.main(args)


if __name__ == "__main__":
    sys.exit(run_phase67_tests())
