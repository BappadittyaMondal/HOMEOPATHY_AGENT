"""
Standalone Test Runner for Phase 07: Kent's Repertory Digital Graph Engine.
"""
import sys
import time
import pytest

def main():
    print("=" * 80)
    print("RUNNING PHASE 07 TEST SUITE: Kent's Repertory Digital Graph Engine")
    print("=" * 80)
    
    start_time = time.perf_counter()
    exit_code = pytest.main([
        "tests/test_phase07.py",
        "-v",
        "--tb=short"
    ])
    elapsed = time.perf_counter() - start_time
    
    print("-" * 80)
    if exit_code == 0:
        print(f"PHASE 07 VERIFICATION SUCCESSFUL: 100% Tests Passed in {elapsed:.3f}s")
        print("Quality Gate Passed: 37 Kentian chapters, hierarchical tree, and cross-references verified.")
    else:
        print(f"PHASE 07 VERIFICATION FAILED with exit code {exit_code}")
    print("=" * 80)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
