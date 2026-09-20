"""
Dedicated Test Runner for Phase 52:
Boundary Validation, Anti-Wraparound & Case Totality ABSTAIN Engine (INV-03, INV-04).
"""
import sys
import time
import pytest


def main():
    print("=" * 80)
    print("RUNNING PHASE 52: BOUNDARY VALIDATION, ANTI-WRAPAROUND & ABSTAIN ENGINE")
    print("Validating INV-03 (ABSTAIN on < 3 rubrics) & INV-04 (Anti-Wraparound)")
    print("=" * 80)

    start_time = time.time()
    exit_code = pytest.main([
        "tests/test_phase52.py",
        "-v",
        "--tb=short"
    ])
    duration = time.time() - start_time

    print("-" * 80)
    if exit_code == 0:
        print(f"Phase 52 Tests PASSED successfully in {duration:.3f}s.")
        print("Status: 100% OPERATIONAL & VERIFIED")
    else:
        print(f"Phase 52 Tests FAILED with exit code {exit_code} in {duration:.3f}s.")
    print("=" * 80)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
