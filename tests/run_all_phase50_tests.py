"""
Standalone Test Runner for Phase 50: Master End-to-End Clinical Verification Suite & Zero-Defect Audit Certification.
"""
import sys
import time
import pytest

def main():
    print("=" * 80)
    print("RUNNING PHASE 50 TEST SUITE: Master End-to-End Clinical Verification Suite")
    print("=" * 80)
    
    start_time = time.perf_counter()
    exit_code = pytest.main([
        "tests/test_phase50.py",
        "-v",
        "--tb=short"
    ])
    elapsed = time.perf_counter() - start_time
    
    print("-" * 80)
    if exit_code == 0:
        print(f"PHASE 50 VERIFICATION SUCCESSFUL: 100% Tests Passed in {elapsed:.3f}s")
        print("Quality Gate Passed: End-to-end 15-stage clinical lifecycle, DPDP consent, emergency lockout,")
        print("repertorization, posology, NCH digital signature, EDU dispensing, Hering's law,")
        print("Kent's 12 observations, and NABH cryptographic audit ledger verified.")
    else:
        print(f"PHASE 50 VERIFICATION FAILED with exit code {exit_code}")
    print("=" * 80)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
