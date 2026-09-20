"""
Standalone Test Runner for Phase 47: Pharmacovigilance & ADR Surveillance System.
"""
import sys
import time
import pytest

def main():
    print("=" * 80)
    print("RUNNING PHASE 47 TEST SUITE: Pharmacovigilance & ADR Surveillance System")
    print("=" * 80)
    
    start_time = time.perf_counter()
    exit_code = pytest.main([
        "tests/test_phase47.py",
        "-v",
        "--tb=short"
    ])
    elapsed = time.perf_counter() - start_time
    
    print("-" * 80)
    if exit_code == 0:
        print(f"PHASE 47 VERIFICATION SUCCESSFUL: 100% Tests Passed in {elapsed:.3f}s")
        print("Quality Gate Passed: Aggravation vs ADR classification and statutory batch quarantines verified.")
    else:
        print(f"PHASE 47 VERIFICATION FAILED with exit code {exit_code}")
    print("=" * 80)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
