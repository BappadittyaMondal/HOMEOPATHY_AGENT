"""
Standalone Test Runner for Phase 38: Iatrogenic Drug Suppression & Tautopathic Cleansing Engine.
"""
import sys
import time
import pytest

def main():
    print("=" * 80)
    print("RUNNING PHASE 38 TEST SUITE: Iatrogenic Drug Suppression & Tautopathic Cleansing Engine")
    print("=" * 80)
    
    start_time = time.perf_counter()
    exit_code = pytest.main([
        "tests/test_phase38.py",
        "-v",
        "--tb=short"
    ])
    elapsed = time.perf_counter() - start_time
    
    print("-" * 80)
    if exit_code == 0:
        print(f"PHASE 38 VERIFICATION SUCCESSFUL: 100% Tests Passed in {elapsed:.3f}s")
        print("Quality Gate Passed: Aphorisms 74-76 drug disease detoxification and tautopathic scales verified.")
    else:
        print(f"PHASE 38 VERIFICATION FAILED with exit code {exit_code}")
    print("=" * 80)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
