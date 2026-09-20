"""
Standalone Test Runner for Phase 39: Western Emergency Break-Glass Gateway.
"""
import sys
import time
import pytest

def main():
    print("=" * 80)
    print("RUNNING PHASE 39 TEST SUITE: Western Emergency Break-Glass Gateway")
    print("=" * 80)
    
    start_time = time.perf_counter()
    exit_code = pytest.main([
        "tests/test_phase39.py",
        "-v",
        "--tb=short"
    ])
    elapsed = time.perf_counter() - start_time
    
    print("-" * 80)
    if exit_code == 0:
        print(f"PHASE 39 VERIFICATION SUCCESSFUL: 100% Tests Passed in {elapsed:.3f}s")
        print("Quality Gate Passed: qSOFA calculation, STEMI/Surgical abdomen lockouts, and transfer packets verified.")
    else:
        print(f"PHASE 39 VERIFICATION FAILED with exit code {exit_code}")
    print("=" * 80)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
