"""
Dedicated test runner for Phase 73: Multi-Parameter Laboratory Diagnostic Report Parser.
"""
import sys
import pytest

def run_tests():
    exit_code = pytest.main(["-v", "tests/test_phase73.py"])
    return exit_code

if __name__ == "__main__":
    sys.exit(run_tests())
