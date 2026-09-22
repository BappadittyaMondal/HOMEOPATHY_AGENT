"""
Phase 61 Dedicated Test Runner: Authoritative Pharmacopoeial Registry Expansion (150 Remedies).
"""
import sys
import time
import pytest

def run_tests():
    start_time = time.perf_counter()
    print("=" * 80)
    print("RUNNING PHASE 61 SUITE: 150-REMEDY CANONICAL PHARMACOPOEIA REGISTRY (INV-16)")
    print("=" * 80)
    
    ret_code = pytest.main(["-v", "tests/test_phase61.py"])
    elapsed = time.perf_counter() - start_time
    
    if ret_code == 0:
        print(f"\nPASS: Phase 61 verified successfully in {elapsed:.3f}s.")
        return 0
    else:
        print(f"\nFAIL: Phase 61 suite failed with exit code {ret_code}.")
        return ret_code

if __name__ == "__main__":
    sys.exit(run_tests())
