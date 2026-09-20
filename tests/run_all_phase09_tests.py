"""
Standalone Test Runner for Phase 09: BBCR Pathological Indexer.
"""
import sys
import time
import pytest

def main():
    print("=" * 80)
    print("RUNNING PHASE 09 TEST SUITE: BBCR Pathological Indexer")
    print("=" * 80)
    
    start_time = time.perf_counter()
    exit_code = pytest.main([
        "tests/test_phase09.py",
        "-v",
        "--tb=short"
    ])
    elapsed = time.perf_counter() - start_time
    
    print("-" * 80)
    if exit_code == 0:
        print(f"PHASE 09 VERIFICATION SUCCESSFUL: 100% Tests Passed in {elapsed:.3f}s")
        print("Quality Gate Passed: BBCR tissue affinity, laterality, and pathological generals verified.")
    else:
        print(f"PHASE 09 VERIFICATION FAILED with exit code {exit_code}")
    print("=" * 80)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
