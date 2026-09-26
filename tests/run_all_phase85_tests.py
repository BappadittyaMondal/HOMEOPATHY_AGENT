"""
Phase 85 Verification Runner: Master Report Facade, API Integration & Grand Verification.
"""
import sys
import pytest

def run_phase85_verification() -> int:
    print("=" * 80)
    print("   HOMEOPATHY_AGENT VERIFICATION RUNNER: PHASE 85 (MASTER REPORT FACADE & API) ")
    print("=" * 80)
    exit_code = pytest.main(["-v", "tests/test_phase85.py"])
    if exit_code == 0:
        print("\n>>> PHASE 85 VERIFICATION PASSED: MASTER REPORT FACADE & REST API CERTIFIED <<<\n")
    else:
        print("\n>>> PHASE 85 VERIFICATION FAILED: REGRESSIONS DETECTED <<<\n")
    return exit_code

if __name__ == "__main__":
    sys.exit(run_phase85_verification())
