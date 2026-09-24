"""
Dedicated test runner for Phase 74: Distributed Event Outbox & S3 Object Storage Gateway.
"""
import sys
import pytest

def run_tests():
    exit_code = pytest.main(["-v", "tests/test_phase74.py"])
    return exit_code

if __name__ == "__main__":
    sys.exit(run_tests())
