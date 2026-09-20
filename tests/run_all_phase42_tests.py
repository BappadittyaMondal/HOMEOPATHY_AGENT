"""
Standalone Test Runner for Phase 42: Dual-Coding Engine.
"""
import sys
import time
import pytest

def main():
    print("=" * 80)
    print("RUNNING PHASE 42 TEST SUITE: WHO ICD-11 TM1 & Western ICD-10 Dual-Coding Engine")
    print("=" * 80)
    
    start_time = time.perf_counter()
    exit_code = pytest.main([
        "tests/test_phase42.py",
        "-v",
        "--tb=short"
    ])
    elapsed = time.perf_counter() - start_time
    
    print("-" * 80)
    if exit_code == 0:
        print(f"PHASE 42 VERIFICATION SUCCESSFUL: 100% Tests Passed in {elapsed:.3f}s")
        print("Quality Gate Passed: WHO ICD-11 TM1, Ayush Grid NAMASTE, and Western ICD-10 dual-coding verified.")
    else:
        print(f"PHASE 42 VERIFICATION FAILED with exit code {exit_code}")
    print("=" * 80)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
