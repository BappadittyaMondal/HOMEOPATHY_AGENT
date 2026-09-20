"""
Master Hardened Test Runner (Milestone 6: Phases 51 to 60).
Executes all 10 dedicated phase test suites and the consolidated 16-invariant master suite.
Verifies zero regression, zero circular oscillation, and 100% operational integrity.
"""
import sys
import time
import pytest


HARDENED_SUITES = [
    ("Phase 51: Unified Control-Flow Safety Gating (INV-01, INV-02)", "tests/test_phase51.py"),
    ("Phase 52: Repertory Boundary & ABSTAIN Engine (INV-03, INV-04)", "tests/test_phase52.py"),
    ("Phase 53: Emergency Break-Glass & Psychiatric Crisis (INV-05, INV-06)", "tests/test_phase53.py"),
    ("Phase 54: Dispensary Verification & ADR Priority Triage (INV-07, INV-08)", "tests/test_phase54.py"),
    ("Phase 55: SQLite WAL True Persistence Hardening (INV-09)", "tests/test_phase55.py"),
    ("Phase 56: Server-Side RBAC & Anti-Spoofing Signatures (INV-10, INV-11)", "tests/test_phase56.py"),
    ("Phase 57: Obstetric Gestational Firewall & Pediatric Consent (INV-12, INV-13)", "tests/test_phase57.py"),
    ("Phase 58: Clinical Pathology & Lab Panic Gateway (INV-14, INV-15)", "tests/test_phase58.py"),
    ("Phase 59: Canonical Remedy Registry & Normalization (INV-16)", "tests/test_phase59.py"),
    ("Phase 60: Master Operational Invariant Suite (INV-01 to INV-16)", "tests/test_invariants.py"),
]


def main():
    print("=" * 80)
    print("HOMEOPATHY HOSPITAL INFORMATION SYSTEM (HHIS v3.0.0-ENTERPRISE-CLINICAL)")
    print("RUNNING MILESTONE 6 MASTER HARDENED TEST SUITE (PHASES 51 - 60)")
    print("=" * 80)

    total_start = time.time()
    passed_phases = 0
    failed_phases = []

    for name, test_path in HARDENED_SUITES:
        print(f"\n>>> Running {name} ({test_path})...")
        phase_start = time.time()
        exit_code = pytest.main([test_path, "-v", "--tb=short"])
        phase_duration = time.time() - phase_start

        if exit_code == 0:
            print(f"PASS: {name} completed successfully in {phase_duration:.3f}s.")
            passed_phases += 1
        else:
            print(f"FAIL: {name} FAILED with exit code {exit_code} in {phase_duration:.3f}s.")
            failed_phases.append(name)

    total_duration = time.time() - total_start
    print("\n" + "=" * 80)
    print("MILESTONE 6 HARDENED SUITE SUMMARY")
    print(f"Total Suites Executed: {len(HARDENED_SUITES)}")
    print(f"Passed: {passed_phases}/{len(HARDENED_SUITES)}")
    print(f"Failed: {len(failed_phases)}/{len(HARDENED_SUITES)}")
    print(f"Total Time: {total_duration:.3f}s")
    print("=" * 80)

    if failed_phases:
        print("FAILED SUITES:")
        for f in failed_phases:
            print(f" - {f}")
        return 1

    print("\nALL 10 HARDENED PHASES (PHASES 51 TO 60) AND ALL 16 INVARIANTS PASSED WITH 100% SUCCESS.")
    print("QUALITY GATE: 100% OPERATIONAL & VERIFIED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
