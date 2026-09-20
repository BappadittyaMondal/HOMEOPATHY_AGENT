"""
Dedicated Test Runner for Phase 56:
Server-Side Authoritative Authorization (OAuth2/JWT) & Secret Management (INV-10, INV-11).
"""
import sys
import time
import pytest


def main():
    print("=" * 80)
    print("RUNNING PHASE 56: AUTHORITATIVE AUTHORIZATION & SECRET MANAGEMENT")
    print("Validating INV-10 (Bearer JWT Enforcement) & INV-11 (RMP Anti-Spoofing)")
    print("=" * 80)

    start_time = time.time()
    exit_code = pytest.main([
        "tests/test_phase56.py",
        "-v",
        "--tb=short"
    ])
    duration = time.time() - start_time

    print("-" * 80)
    if exit_code == 0:
        print(f"Phase 56 Tests PASSED successfully in {duration:.3f}s.")
        print("Status: 100% OPERATIONAL & VERIFIED")
    else:
        print(f"Phase 56 Tests FAILED with exit code {exit_code} in {duration:.3f}s.")
    print("=" * 80)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
