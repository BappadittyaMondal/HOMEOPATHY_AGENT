"""
Automated Test Runner for Phase 70: Master Pipeline Unified Integration & SQLite Concurrency Hardening.
"""
import sys
import pytest


def run_phase70_tests() -> int:
    print("=" * 80)
    print("RUNNING PHASE 70: MASTER PIPELINE UNIFIED INTEGRATION & SQLITE HARDENING")
    print("=" * 80)
    args = [
        "tests/test_phase70.py",
        "-v",
        "--tb=short"
    ]
    return pytest.main(args)


if __name__ == "__main__":
    sys.exit(run_phase70_tests())
