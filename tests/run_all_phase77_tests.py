"""
Dedicated test runner for Phase 77: Objective Physiological Vitals Gate Engine (INV-21).
"""
import sys
import pytest

def run_tests():
    exit_code = pytest.main(["-v", "tests/test_phase77.py"])
    return exit_code

if __name__ == "__main__":
    sys.exit(run_tests())
