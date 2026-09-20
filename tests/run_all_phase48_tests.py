"""
Standalone Test Runner for Phase 48: Tele-Homoeopathy & DPDP Consent Engine.
"""
import sys
import time
import pytest

def main():
    print("=" * 80)
    print("RUNNING PHASE 48 TEST SUITE: Tele-Homoeopathy & DPDP Consent Engine")
    print("=" * 80)
    
    start_time = time.perf_counter()
    exit_code = pytest.main([
        "tests/test_phase48.py",
        "-v",
        "--tb=short"
    ])
    elapsed = time.perf_counter() - start_time
    
    print("-" * 80)
    if exit_code == 0:
        print(f"PHASE 48 VERIFICATION SUCCESSFUL: 100% Tests Passed in {elapsed:.3f}s")
        print("Quality Gate Passed: NCH Telemedicine Guidelines 2022, DPDP Act 2023 consent, and emergency red-flag blocks verified.")
    else:
        print(f"PHASE 48 VERIFICATION FAILED with exit code {exit_code}")
    print("=" * 80)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
