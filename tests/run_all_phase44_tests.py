"""
Standalone Test Runner for Phase 44: NABH Homoeopathy 2nd Edition Audit System.
"""
import sys
import time
import pytest

def main():
    print("=" * 80)
    print("RUNNING PHASE 44 TEST SUITE: NABH Homoeopathy 2nd Edition Digital Audit Log")
    print("=" * 80)
    
    start_time = time.perf_counter()
    exit_code = pytest.main([
        "tests/test_phase44.py",
        "-v",
        "--tb=short"
    ])
    elapsed = time.perf_counter() - start_time
    
    print("-" * 80)
    if exit_code == 0:
        print(f"PHASE 44 VERIFICATION SUCCESSFUL: 100% Tests Passed in {elapsed:.3f}s")
        print("Quality Gate Passed: Tamper-evident Merkle/hash-chain ledger and NABH 2nd Edition CQI audit verified.")
    else:
        print(f"PHASE 44 VERIFICATION FAILED with exit code {exit_code}")
    print("=" * 80)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
