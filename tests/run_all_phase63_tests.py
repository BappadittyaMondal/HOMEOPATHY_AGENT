"""
Phase 63 Dedicated Test Runner: Heavy Metal & Environmental Trace Element Toxicology Gateway.
"""
import sys
import time
import pytest

def run_tests():
    start_time = time.perf_counter()
    print("=" * 80)
    print("RUNNING PHASE 63 SUITE: HEAVY METAL & ENVIRONMENTAL TRACE ELEMENT TOXICOLOGY (INV-14)")
    print("=" * 80)
    
    ret_code = pytest.main(["-v", "tests/test_phase63.py"])
    elapsed = time.perf_counter() - start_time
    
    if ret_code == 0:
        print(f"\nPASS: Phase 63 verified successfully in {elapsed:.3f}s.")
        return 0
    else:
        print(f"\nFAIL: Phase 63 suite failed with exit code {ret_code}.")
        return ret_code

if __name__ == "__main__":
    sys.exit(run_tests())
