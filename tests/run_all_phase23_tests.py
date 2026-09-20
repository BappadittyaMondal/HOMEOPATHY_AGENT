"""
Standalone Test Runner for Phase 23: Classical Second Prescription Decision Engine.
"""
import sys
import time
import pytest

def main():
    print("=" * 80)
    print("RUNNING PHASE 23 TEST SUITE: Classical Second Prescription Decision Engine")
    print("=" * 80)
    
    start_time = time.perf_counter()
    exit_code = pytest.main([
        "tests/test_phase23.py",
        "-v",
        "--tb=short"
    ])
    elapsed = time.perf_counter() - start_time
    
    print("-" * 80)
    if exit_code == 0:
        print(f"PHASE 23 VERIFICATION SUCCESSFUL: 100% Tests Passed in {elapsed:.3f}s")
        print("Quality Gate Passed: Sac Lac rules, repetition, potency escalation, remedy change, and antidoting verified.")
    else:
        print(f"PHASE 23 VERIFICATION FAILED with exit code {exit_code}")
    print("=" * 80)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
