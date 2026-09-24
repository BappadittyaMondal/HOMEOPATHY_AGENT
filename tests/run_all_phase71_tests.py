"""
Dedicated test runner for Phase 71: Vernacular Audio Ingestion & Zero-GPU Edge ASR Decoder Engine.
"""
import sys
import pytest

def run_tests():
    exit_code = pytest.main(["-v", "tests/test_phase71.py"])
    return exit_code

if __name__ == "__main__":
    sys.exit(run_tests())
