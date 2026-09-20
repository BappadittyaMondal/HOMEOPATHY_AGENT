"""
Standalone Test Runner for Phase 10: Pluggable Synthetic Repertory Ingestion Adapter.
"""
import sys
import time
import pytest

def main():
    print("=" * 80)
    print("RUNNING PHASE 10 TEST SUITE: Pluggable Synthetic Repertory Ingestion Adapter")
    print("=" * 80)
    
    start_time = time.perf_counter()
    exit_code = pytest.main([
        "tests/test_phase10.py",
        "-v",
        "--tb=short"
    ])
    elapsed = time.perf_counter() - start_time
    
    print("-" * 80)
    if exit_code == 0:
        print(f"PHASE 10 VERIFICATION SUCCESSFUL: 100% Tests Passed in {elapsed:.3f}s")
        print("Quality Gate Passed: Clean-room IP licensing verified, dynamic graph ingestion validated.")
    else:
        print(f"PHASE 10 VERIFICATION FAILED with exit code {exit_code}")
    print("=" * 80)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
