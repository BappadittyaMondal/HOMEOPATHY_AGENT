"""
Dedicated Test Runner for Phase 59:
Canonical Remedy Registry & Nomenclature Normalization Engine (INV-16 & Statutory Status Banner).
"""
import sys
import time
import pytest


def main():
    print("=" * 80)
    print("RUNNING PHASE 59: CANONICAL REMEDY REGISTRY & NOMENCLATURE ENGINE")
    print("Validating INV-16 (Canonical Nomenclature & Abbreviation Normalization) & Banner")
    print("=" * 80)

    start_time = time.time()
    exit_code = pytest.main([
        "tests/test_phase59.py",
        "-v",
        "--tb=short"
    ])
    duration = time.time() - start_time

    print("-" * 80)
    if exit_code == 0:
        print(f"Phase 59 Tests PASSED successfully in {duration:.3f}s.")
        print("Status: 100% OPERATIONAL & VERIFIED")
    else:
        print(f"Phase 59 Tests FAILED with exit code {exit_code} in {duration:.3f}s.")
    print("=" * 80)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
