"""
Standalone Test Runner for Phase 22: Hering's Law Directional Vector Engine.
"""
import sys
import time
import pytest

def main():
    print("=" * 80)
    print("RUNNING PHASE 22 TEST SUITE: Hering's Law Directional Vector Engine")
    print("=" * 80)
    
    start_time = time.perf_counter()
    exit_code = pytest.main([
        "tests/test_phase22.py",
        "-v",
        "--tb=short"
    ])
    elapsed = time.perf_counter() - start_time
    
    print("-" * 80)
    if exit_code == 0:
        print(f"PHASE 22 VERIFICATION SUCCESSFUL: 100% Tests Passed in {elapsed:.3f}s")
        print("Quality Gate Passed: 4D vector calculus, suppression detection, and organ hierarchy verified.")
    else:
        print(f"PHASE 22 VERIFICATION FAILED with exit code {exit_code}")
    print("=" * 80)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
