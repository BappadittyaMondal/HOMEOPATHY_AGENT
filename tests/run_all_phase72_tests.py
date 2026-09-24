"""
Dedicated test runner for Phase 72: Interactive Hahnemannian Case-Taking Dialogue Engine.
"""
import sys
import pytest

def run_tests():
    exit_code = pytest.main(["-v", "tests/test_phase72.py"])
    return exit_code

if __name__ == "__main__":
    sys.exit(run_tests())
