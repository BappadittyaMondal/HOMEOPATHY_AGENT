"""
Standalone Test Runner for Phase 17: HPI Monograph Database.
"""
import sys
import time
import pytest

def main():
    print("=" * 80)
    print("RUNNING PHASE 17 TEST SUITE: HPI Monograph Database")
    print("=" * 80)
    
    start_time = time.perf_counter()
    exit_code = pytest.main([
        "tests/test_phase17.py",
        "-v",
        "--tb=short"
    ])
    elapsed = time.perf_counter() - start_time
    
    print("-" * 80)
    if exit_code == 0:
        print(f"PHASE 17 VERIFICATION SUCCESSFUL: 100% Tests Passed in {elapsed:.3f}s")
        print("Quality Gate Passed: HPI official monographs, Schedule E(1) status, and minimum potencies verified.")
    else:
        print(f"PHASE 17 VERIFICATION FAILED with exit code {exit_code}")
    print("=" * 80)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
