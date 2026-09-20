"""
Standalone Test Runner for Phase 43: NCH Act 2020 Digital Signature Gateway.
"""
import sys
import time
import pytest

def main():
    print("=" * 80)
    print("RUNNING PHASE 43 TEST SUITE: NCH Act 2020 RMP Digital Signature Gateway")
    print("=" * 80)
    
    start_time = time.perf_counter()
    exit_code = pytest.main([
        "tests/test_phase43.py",
        "-v",
        "--tb=short"
    ])
    elapsed = time.perf_counter() - start_time
    
    print("-" * 80)
    if exit_code == 0:
        print(f"PHASE 43 VERIFICATION SUCCESSFUL: 100% Tests Passed in {elapsed:.3f}s")
        print("Quality Gate Passed: NCH Act 2020 RMP license check, HMAC-SHA256 signing, and tamper detection verified.")
    else:
        print(f"PHASE 43 VERIFICATION FAILED with exit code {exit_code}")
    print("=" * 80)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
