"""
Phase 82 Verification Runner: Forensic Structured Markdown Report Builder.
"""
import sys
import pytest

def run_phase82_verification() -> int:
    print("=" * 80)
    print("   HOMEOPATHY_AGENT VERIFICATION RUNNER: PHASE 82 (MARKDOWN REPORT BUILDER)  ")
    print("=" * 80)
    exit_code = pytest.main(["-v", "tests/test_phase82.py"])
    if exit_code == 0:
        print("\n>>> PHASE 82 VERIFICATION PASSED: FORENSIC MARKDOWN DOSSIER CERTIFIED <<<\n")
    else:
        print("\n>>> PHASE 82 VERIFICATION FAILED: REGRESSIONS DETECTED <<<\n")
    return exit_code

if __name__ == "__main__":
    sys.exit(run_phase82_verification())
