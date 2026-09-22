"""
Phase 64 Dedicated Test Runner: Clinical Emergency Transfer Dossier Formatter.
"""
import sys
import time
import pytest

def run_tests():
    start_time = time.perf_counter()
    print("=" * 80)
    print("RUNNING PHASE 64 SUITE: CLINICAL EMERGENCY TRANSFER DOSSIER FORMATTER")
    print("=" * 80)
    
    ret_code = pytest.main(["-v", "tests/test_phase64.py"])
    elapsed = time.perf_counter() - start_time
    
    if ret_code == 0:
        print(f"\nPASS: Phase 64 verified successfully in {elapsed:.3f}s.")
        return 0
    else:
        print(f"\nFAIL: Phase 64 suite failed with exit code {ret_code}.")
        return ret_code

if __name__ == "__main__":
    sys.exit(run_tests())
