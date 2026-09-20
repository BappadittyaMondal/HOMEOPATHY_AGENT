"""
Standalone Test Runner for Phase 14: Four-Dimensional Miasmatic Simplex Classifier.
"""
import sys
import time
import pytest

def main():
    print("=" * 80)
    print("RUNNING PHASE 14 TEST SUITE: Four-Dimensional Miasmatic Simplex Classifier")
    print("=" * 80)
    
    start_time = time.perf_counter()
    exit_code = pytest.main([
        "tests/test_phase14.py",
        "-v",
        "--tb=short"
    ])
    elapsed = time.perf_counter() - start_time
    
    print("-" * 80)
    if exit_code == 0:
        print(f"PHASE 14 VERIFICATION SUCCESSFUL: 100% Tests Passed in {elapsed:.3f}s")
        print("Quality Gate Passed: 4D Miasmatic Simplex projection and Anti-Miasmatic Concordance (MCS) validated.")
    else:
        print(f"PHASE 14 VERIFICATION FAILED with exit code {exit_code}")
    print("=" * 80)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
