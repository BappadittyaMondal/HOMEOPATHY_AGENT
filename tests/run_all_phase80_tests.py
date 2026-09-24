"""
Dedicated test runner for Phase 80: Master Multimodal Verification Suite, Grand Invariant Audit (INV-01 to INV-21) & Milestone 10 Integration.
"""
import sys
import pytest

def run_tests():
    exit_code = pytest.main(["-v", "tests/test_phase80.py"])
    return exit_code

if __name__ == "__main__":
    sys.exit(run_tests())
