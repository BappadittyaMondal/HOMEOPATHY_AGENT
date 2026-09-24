"""
Dedicated test runner for Phase 76: Explicit Vitality Mandate & Low-Reserve Safety Engine (INV-20).
"""
import sys
import pytest

def run_tests():
    exit_code = pytest.main(["-v", "tests/test_phase76.py"])
    return exit_code

if __name__ == "__main__":
    sys.exit(run_tests())
