"""
Standalone Test Runner for Phase 04: Strange, Rare, and Peculiar (SRP) Isolation Kernel.
"""
import sys
import time
import pytest

def main():
    print("=" * 80)
    print("RUNNING PHASE 04 TEST SUITE: Strange, Rare, and Peculiar (SRP - Aphorism 153)")
    print("=" * 80)
    
    start_time = time.perf_counter()
    exit_code = pytest.main([
        "tests/test_phase04.py",
        "-v",
        "--tb=short"
    ])
    elapsed = time.perf_counter() - start_time
    
    print("-" * 80)
    if exit_code == 0:
        print(f"PHASE 04 VERIFICATION SUCCESSFUL: 100% Tests Passed in {elapsed:.3f}s")
        print("Quality Gate Passed: Aphorism 153 clinical paradox isolation and discriminative weighting verified.")
    else:
        print(f"PHASE 04 VERIFICATION FAILED with exit code {exit_code}")
    print("=" * 80)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
