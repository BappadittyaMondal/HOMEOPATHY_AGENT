"""
Standalone Test Runner for Phase 24: Nosodes & Sarcodes Safety Protocol.
"""
import sys
import time
import pytest

def main():
    print("=" * 80)
    print("RUNNING PHASE 24 TEST SUITE: Nosodes & Sarcodes Safety Protocol")
    print("=" * 80)
    
    start_time = time.perf_counter()
    exit_code = pytest.main([
        "tests/test_phase24.py",
        "-v",
        "--tb=short"
    ])
    elapsed = time.perf_counter() - start_time
    
    print("-" * 80)
    if exit_code == 0:
        print(f"PHASE 24 VERIFICATION SUCCESSFUL: 100% Tests Passed in {elapsed:.3f}s")
        print("Quality Gate Passed: Nosode acute fever blocks, inter-dose lockout, and septic exceptions verified.")
    else:
        print(f"PHASE 24 VERIFICATION FAILED with exit code {exit_code}")
    print("=" * 80)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
