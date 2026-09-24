"""
Dedicated test runner for Phase 78: Observability, Health Probes & Prometheus APM Metrics.
"""
import sys
import pytest

def run_tests():
    exit_code = pytest.main(["-v", "tests/test_phase78.py"])
    return exit_code

if __name__ == "__main__":
    sys.exit(run_tests())
