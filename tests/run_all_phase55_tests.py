"""
Dedicated Test Runner for Phase 55:
True Database Persistence for Milestone 5 Stores (INV-09).
"""
import sys
import time
import pytest


def main():
    print("=" * 80)
    print("RUNNING PHASE 55: TRUE DATABASE PERSISTENCE (SQLITE WAL HARDENING)")
    print("Validating INV-09 (Durability of Audit Ledger, Dispensary, and EHR Stores)")
    print("=" * 80)

    start_time = time.time()
    exit_code = pytest.main([
        "tests/test_phase55.py",
        "-v",
        "--tb=short"
    ])
    duration = time.time() - start_time

    print("-" * 80)
    if exit_code == 0:
        print(f"Phase 55 Tests PASSED successfully in {duration:.3f}s.")
        print("Status: 100% OPERATIONAL & VERIFIED")
    else:
        print(f"Phase 55 Tests FAILED with exit code {exit_code} in {duration:.3f}s.")
    print("=" * 80)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
