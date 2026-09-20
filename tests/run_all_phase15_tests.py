"""
Standalone Test Runner for Phase 15: Susceptibility & Vital Force Assessment Engine.
"""
import sys
import time
import pytest

def main():
    print("=" * 80)
    print("RUNNING PHASE 15 TEST SUITE: Susceptibility & Vital Force Engine")
    print("=" * 80)
    
    start_time = time.perf_counter()
    exit_code = pytest.main([
        "tests/test_phase15.py",
        "-v",
        "--tb=short"
    ])
    elapsed = time.perf_counter() - start_time
    
    print("-" * 80)
    if exit_code == 0:
        print(f"PHASE 15 VERIFICATION SUCCESSFUL: 100% Tests Passed in {elapsed:.3f}s")
        print("Quality Gate Passed: Posology scaling factor sigma = (S*V)/(Delta_T+1) validated.")
    else:
        print(f"PHASE 15 VERIFICATION FAILED with exit code {exit_code}")
    print("=" * 80)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
