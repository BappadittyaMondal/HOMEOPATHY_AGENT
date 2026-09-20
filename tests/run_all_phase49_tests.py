"""
Standalone Test Runner for Phase 49: Hostinger VPS Hardened Deployment Pipeline.
"""
import sys
import time
import pytest

def main():
    print("=" * 80)
    print("RUNNING PHASE 49 TEST SUITE: Hostinger KVM Linux VPS Hardened Deployment")
    print("=" * 80)
    
    start_time = time.perf_counter()
    exit_code = pytest.main([
        "tests/test_phase49.py",
        "-v",
        "--tb=short"
    ])
    elapsed = time.perf_counter() - start_time
    
    print("-" * 80)
    if exit_code == 0:
        print(f"PHASE 49 VERIFICATION SUCCESSFUL: 100% Tests Passed in {elapsed:.3f}s")
        print("Quality Gate Passed: Docker multi-stage build, non-root user, Nginx security, and memory caps verified.")
    else:
        print(f"PHASE 49 VERIFICATION FAILED with exit code {exit_code}")
    print("=" * 80)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
