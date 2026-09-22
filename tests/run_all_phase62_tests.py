"""
Phase 62 Dedicated Test Runner: Oncological Pre-Malignancy Surveillance Gate (INV-17).
"""
import sys
import time
import pytest

def run_tests():
    start_time = time.perf_counter()
    print("=" * 80)
    print("RUNNING PHASE 62 SUITE: ONCOLOGICAL PRE-MALIGNANCY SURVEILLANCE GATE (INV-17)")
    print("=" * 80)
    
    ret_code = pytest.main(["-v", "tests/test_phase62.py"])
    elapsed = time.perf_counter() - start_time
    
    if ret_code == 0:
        print(f"\nPASS: Phase 62 verified successfully in {elapsed:.3f}s.")
        return 0
    else:
        print(f"\nFAIL: Phase 62 suite failed with exit code {ret_code}.")
        return ret_code

if __name__ == "__main__":
    sys.exit(run_tests())
