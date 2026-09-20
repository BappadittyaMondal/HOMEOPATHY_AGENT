"""
Dedicated Test Runner for Phase 60:
Master Operational Invariant Verification Suite (INV-01 to INV-16).
"""
import sys
import time
import pytest


def main():
    print("=" * 80)
    print("RUNNING PHASE 60: MASTER OPERATIONAL INVARIANT VERIFICATION SUITE")
    print("Validating all 16 concrete Negative Operational Invariants (INV-01 to INV-16)")
    print("=" * 80)

    start_time = time.time()
    exit_code = pytest.main([
        "tests/test_invariants.py",
        "-v",
        "--tb=short"
    ])
    duration = time.time() - start_time

    print("-" * 80)
    if exit_code == 0:
        print(f"Phase 60 Tests PASSED successfully in {duration:.3f}s.")
        print("Status: 100% OPERATIONAL & ZERO INVARIANT VIOLATIONS DETECTED")
    else:
        print(f"Phase 60 Tests FAILED with exit code {exit_code} in {duration:.3f}s.")
    print("=" * 80)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
