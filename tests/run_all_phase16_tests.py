"""
Standalone Test Runner for Phase 16: Dynamic Posology Selection Calculus.
"""
import sys
import time
import pytest

def main():
    print("=" * 80)
    print("RUNNING PHASE 16 TEST SUITE: Dynamic Posology Selection Calculus")
    print("=" * 80)
    
    start_time = time.perf_counter()
    exit_code = pytest.main([
        "tests/test_phase16.py",
        "-v",
        "--tb=short"
    ])
    elapsed = time.perf_counter() - start_time
    
    print("-" * 80)
    if exit_code == 0:
        print(f"PHASE 16 VERIFICATION SUCCESSFUL: 100% Tests Passed in {elapsed:.3f}s")
        print("Quality Gate Passed: Centesimal, Decimal, and 50-Millesimal (LM) posology calculus validated.")
        print("MILESTONE 2 (Phases 07-16) FULLY COMPLETED AND VALIDATED.")
    else:
        print(f"PHASE 16 VERIFICATION FAILED with exit code {exit_code}")
    print("=" * 80)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
