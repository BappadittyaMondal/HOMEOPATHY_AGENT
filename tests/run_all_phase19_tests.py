"""
Standalone Test Runner for Phase 19: Toxicology Limits & Alkaloid Safety Firewall.
"""
import sys
import time
import pytest

def main():
    print("=" * 80)
    print("RUNNING PHASE 19 TEST SUITE: Toxicology Limits & Alkaloid Safety Firewall")
    print("=" * 80)
    
    start_time = time.perf_counter()
    exit_code = pytest.main([
        "tests/test_phase19.py",
        "-v",
        "--tb=short"
    ])
    elapsed = time.perf_counter() - start_time
    
    print("-" * 80)
    if exit_code == 0:
        print(f"PHASE 19 VERIFICATION SUCCESSFUL: 100% Tests Passed in {elapsed:.3f}s")
        print("Quality Gate Passed: 20-point toxic limits, Schedule E(1) block, and dilution conversion verified.")
    else:
        print(f"PHASE 19 VERIFICATION FAILED with exit code {exit_code}")
    print("=" * 80)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
