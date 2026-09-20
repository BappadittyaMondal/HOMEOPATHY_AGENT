"""
Standalone Test Runner for Phase 03: Kentian Symptom Hierarchy Classifier.
"""
import sys
import time
import pytest

def main():
    print("=" * 80)
    print("RUNNING PHASE 03 TEST SUITE: Kentian Symptom Hierarchy Classifier")
    print("=" * 80)
    
    start_time = time.perf_counter()
    exit_code = pytest.main([
        "tests/test_phase03.py",
        "-v",
        "--tb=short"
    ])
    elapsed = time.perf_counter() - start_time
    
    print("-" * 80)
    if exit_code == 0:
        print(f"PHASE 03 VERIFICATION SUCCESSFUL: 100% Tests Passed in {elapsed:.3f}s")
        print("Quality Gate Passed: Kentian hierarchy weighting (5.0, 4.0, 3.5, 3.0, 2.5, 1.0) validated.")
    else:
        print(f"PHASE 03 VERIFICATION FAILED with exit code {exit_code}")
    print("=" * 80)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
