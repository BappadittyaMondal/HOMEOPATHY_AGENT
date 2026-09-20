"""
Dedicated Test Runner for Phase 51:
Unified Hard Control-Flow Safety Gating Architecture (INV-01, INV-02).
"""
import sys
import time
import pytest


def main():
    print("=" * 80)
    print("RUNNING PHASE 51: UNIFIED HARD CONTROL-FLOW SAFETY GATING ARCHITECTURE")
    print("Validating INV-01, INV-02 & ApprovedDraft Cryptographic Sealing")
    print("=" * 80)

    start_time = time.time()
    exit_code = pytest.main([
        "tests/test_phase51.py",
        "-v",
        "--tb=short"
    ])
    duration = time.time() - start_time

    print("-" * 80)
    if exit_code == 0:
        print(f"Phase 51 Tests PASSED successfully in {duration:.3f}s.")
        print("Status: 100% OPERATIONAL & VERIFIED")
    else:
        print(f"Phase 51 Tests FAILED with exit code {exit_code} in {duration:.3f}s.")
    print("=" * 80)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
