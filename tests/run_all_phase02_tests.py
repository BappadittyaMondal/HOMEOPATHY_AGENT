"""
Standalone Test Runner for Phase 02: Hahnemannian Case-Taking & Human-in-the-Loop Verification.
"""
import sys
import time
import pytest

def main():
    print("=" * 80)
    print("RUNNING PHASE 02 TEST SUITE: Case-Taking Engine & Clinician Verification Gate")
    print("=" * 80)
    
    start_time = time.perf_counter()
    exit_code = pytest.main([
        "tests/test_phase02.py",
        "-v",
        "--tb=short"
    ])
    elapsed = time.perf_counter() - start_time
    
    print("-" * 80)
    if exit_code == 0:
        print(f"PHASE 02 VERIFICATION SUCCESSFUL: 100% Tests Passed in {elapsed:.3f}s")
        print("Quality Gate Passed: Semantic LSMC extraction verified, Human-in-the-Loop gate validated.")
    else:
        print(f"PHASE 02 VERIFICATION FAILED with exit code {exit_code}")
    print("=" * 80)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
