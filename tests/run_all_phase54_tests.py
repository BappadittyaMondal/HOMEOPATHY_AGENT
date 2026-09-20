"""
Dedicated Test Runner for Phase 54:
Dispensary Physical Verification & ADR Severity Re-ordering (INV-07, INV-08).
"""
import sys
import time
import pytest


def main():
    print("=" * 80)
    print("RUNNING PHASE 54: DISPENSARY VERIFICATION & ADR SEVERITY RE-ORDERING")
    print("Validating INV-07 (Dispensary Match) & INV-08 (Severity-First Ordering)")
    print("=" * 80)

    start_time = time.time()
    exit_code = pytest.main([
        "tests/test_phase54.py",
        "-v",
        "--tb=short"
    ])
    duration = time.time() - start_time

    print("-" * 80)
    if exit_code == 0:
        print(f"Phase 54 Tests PASSED successfully in {duration:.3f}s.")
        print("Status: 100% OPERATIONAL & VERIFIED")
    else:
        print(f"Phase 54 Tests FAILED with exit code {exit_code} in {duration:.3f}s.")
    print("=" * 80)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
