"""
Standalone Test Runner for Phase 28: Geriatric Degenerative Disease & Low-Potency Support Engine.
"""
import sys
import time
import pytest

def main():
    print("=" * 80)
    print("RUNNING PHASE 28 TEST SUITE: Geriatric Degenerative Disease & Low-Potency Support Engine")
    print("=" * 80)
    
    start_time = time.perf_counter()
    exit_code = pytest.main([
        "tests/test_phase28.py",
        "-v",
        "--tb=short"
    ])
    elapsed = time.perf_counter() - start_time
    
    print("-" * 80)
    if exit_code == 0:
        print(f"PHASE 28 VERIFICATION SUCCESSFUL: 100% Tests Passed in {elapsed:.3f}s")
        print("Quality Gate Passed: Geriatric vitality thresholds, high-potency blocks, and organ support verified.")
    else:
        print(f"PHASE 28 VERIFICATION FAILED with exit code {exit_code}")
    print("=" * 80)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
