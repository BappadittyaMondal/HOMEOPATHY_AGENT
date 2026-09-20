"""
Standalone Test Runner for Phase 05: Boenninghausen Complete Symptom Parser.
"""
import sys
import time
import pytest

def main():
    print("=" * 80)
    print("RUNNING PHASE 05 TEST SUITE: Boenninghausen Complete Symptom Parser (LSMC)")
    print("=" * 80)
    
    start_time = time.perf_counter()
    exit_code = pytest.main([
        "tests/test_phase05.py",
        "-v",
        "--tb=short"
    ])
    elapsed = time.perf_counter() - start_time
    
    print("-" * 80)
    if exit_code == 0:
        print(f"PHASE 05 VERIFICATION SUCCESSFUL: 100% Tests Passed in {elapsed:.3f}s")
        print("Quality Gate Passed: 4-part Boenninghausen complete symptom deconstruction and Grand Generalization validated.")
    else:
        print(f"PHASE 05 VERIFICATION FAILED with exit code {exit_code}")
    print("=" * 80)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
