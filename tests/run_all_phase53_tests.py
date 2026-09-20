"""
Dedicated Test Runner for Phase 53:
Comprehensive Emergency Break-Glass & Psychiatric Crisis Firewall (INV-05, INV-06).
"""
import sys
import time
import pytest


def main():
    print("=" * 80)
    print("RUNNING PHASE 53: EMERGENCY BREAK-GLASS & PSYCHIATRIC CRISIS FIREWALL")
    print("Validating INV-05 (Suicidality/Psychosis Lockout) & INV-06 (NEWS2/PEWS)")
    print("=" * 80)

    start_time = time.time()
    exit_code = pytest.main([
        "tests/test_phase53.py",
        "-v",
        "--tb=short"
    ])
    duration = time.time() - start_time

    print("-" * 80)
    if exit_code == 0:
        print(f"Phase 53 Tests PASSED successfully in {duration:.3f}s.")
        print("Status: 100% OPERATIONAL & VERIFIED")
    else:
        print(f"Phase 53 Tests FAILED with exit code {exit_code} in {duration:.3f}s.")
    print("=" * 80)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
