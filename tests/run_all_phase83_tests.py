"""
Phase 83 Verification Runner: Interactive Responsive HTML5 Dashboard & PDF Exporter.
"""
import sys
import pytest

def run_phase83_verification() -> int:
    print("=" * 80)
    print("   HOMEOPATHY_AGENT VERIFICATION RUNNER: PHASE 83 (HTML5 DASHBOARD & PDF)   ")
    print("=" * 80)
    exit_code = pytest.main(["-v", "tests/test_phase83.py"])
    if exit_code == 0:
        print("\n>>> PHASE 83 VERIFICATION PASSED: HTML5 DASHBOARD & PDF EXPORTER ZERO DEFECT CERTIFIED <<<\n")
    else:
        print("\n>>> PHASE 83 VERIFICATION FAILED: REGRESSIONS DETECTED <<<\n")
    return exit_code

if __name__ == "__main__":
    sys.exit(run_phase83_verification())
