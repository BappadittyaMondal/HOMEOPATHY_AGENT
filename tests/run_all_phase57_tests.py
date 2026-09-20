"""
Dedicated Test Runner for Phase 57:
Obstetric Gestational Trimester Contraindication Firewall & Pediatric Consent (INV-12, INV-13).
"""
import sys
import time
import pytest


def main():
    print("=" * 80)
    print("RUNNING PHASE 57: OBSTETRIC FIREWALL & PEDIATRIC GUARDIAN CONSENT")
    print("Validating INV-12 (Obstetric Abortifacient Blocker) & INV-13 (DPDP Act Consent)")
    print("=" * 80)

    start_time = time.time()
    exit_code = pytest.main([
        "tests/test_phase57.py",
        "-v",
        "--tb=short"
    ])
    duration = time.time() - start_time

    print("-" * 80)
    if exit_code == 0:
        print(f"Phase 57 Tests PASSED successfully in {duration:.3f}s.")
        print("Status: 100% OPERATIONAL & VERIFIED")
    else:
        print(f"Phase 57 Tests FAILED with exit code {exit_code} in {duration:.3f}s.")
    print("=" * 80)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
