"""
Standalone Test Runner for Phase 21: Kent's 12 Observations Decision Automaton.
"""
import sys
import time
import pytest

def main():
    print("=" * 80)
    print("RUNNING PHASE 21 TEST SUITE: Kent's 12 Observations Decision Automaton")
    print("=" * 80)
    
    start_time = time.perf_counter()
    exit_code = pytest.main([
        "tests/test_phase21.py",
        "-v",
        "--tb=short"
    ])
    elapsed = time.perf_counter() - start_time
    
    print("-" * 80)
    if exit_code == 0:
        print(f"PHASE 21 VERIFICATION SUCCESSFUL: 100% Tests Passed in {elapsed:.3f}s")
        print("Quality Gate Passed: Kent's Twelve Observations, prognostic states, and clinical actions verified.")
    else:
        print(f"PHASE 21 VERIFICATION FAILED with exit code {exit_code}")
    print("=" * 80)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
