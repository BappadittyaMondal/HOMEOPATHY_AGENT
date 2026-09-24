"""
Dedicated test runner for Phase 79: Distributed Outbox Background Consumer & Sync Worker.
"""
import sys
import pytest

def run_tests():
    exit_code = pytest.main(["-v", "tests/test_phase79.py"])
    return exit_code

if __name__ == "__main__":
    sys.exit(run_tests())
