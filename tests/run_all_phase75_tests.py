"""
Dedicated test runner for Phase 75: Master Multimodal Verification Suite, Grand Invariant Audit (INV-01 to INV-19) & Milestone 9 Integration.
"""
import sys
import pytest

def run_tests():
    exit_code = pytest.main(["-v", "tests/test_phase75.py"])
    return exit_code

if __name__ == "__main__":
    sys.exit(run_tests())
