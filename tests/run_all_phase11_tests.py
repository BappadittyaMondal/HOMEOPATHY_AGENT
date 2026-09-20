"""
Standalone Test Runner for Phase 11: IRF Entropy Weighting Kernel.
"""
import sys
import time
import pytest

def main():
    print("=" * 80)
    print("RUNNING PHASE 11 TEST SUITE: Inverse Rubric Frequency (IRF) Entropy Kernel")
    print("=" * 80)
    
    start_time = time.perf_counter()
    exit_code = pytest.main([
        "tests/test_phase11.py",
        "-v",
        "--tb=short"
    ])
    elapsed = time.perf_counter() - start_time
    
    print("-" * 80)
    if exit_code == 0:
        print(f"PHASE 11 VERIFICATION SUCCESSFUL: 100% Tests Passed in {elapsed:.3f}s")
        print("Quality Gate Passed: IRF entropy scaling and composite vector formulation verified.")
    else:
        print(f"PHASE 11 VERIFICATION FAILED with exit code {exit_code}")
    print("=" * 80)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
