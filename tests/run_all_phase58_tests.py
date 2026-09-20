"""
Dedicated Test Runner for Phase 58:
Clinical Pathology Diagnostic Engine (CPDE) & Laboratory Panic Gateway (INV-14, INV-15).
"""
import sys
import time
import pytest


def main():
    print("=" * 80)
    print("RUNNING PHASE 58: CLINICAL PATHOLOGY DIAGNOSTIC ENGINE & LAB PANIC GATEWAY")
    print("Validating INV-14 (Lab Panic Gate) & INV-15 (Aphorism 186 Surgical Boundaries)")
    print("=" * 80)

    start_time = time.time()
    exit_code = pytest.main([
        "tests/test_phase58.py",
        "-v",
        "--tb=short"
    ])
    duration = time.time() - start_time

    print("-" * 80)
    if exit_code == 0:
        print(f"Phase 58 Tests PASSED successfully in {duration:.3f}s.")
        print("Status: 100% OPERATIONAL & VERIFIED")
    else:
        print(f"Phase 58 Tests FAILED with exit code {exit_code} in {duration:.3f}s.")
    print("=" * 80)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
