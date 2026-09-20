"""
Unit Tests for Phase 44: NABH Homoeopathy 2nd Edition Digital Audit Log System.
"""
from app.governance.nabh_audit import NABHAuditLedger

def setup_function():
    NABHAuditLedger.reset_chain()

def test_nabh_audit_chain_append_and_verify():
    """Verify append-only hash-linked audit logging and validation."""
    e1 = NABHAuditLedger.append_log(
        log_id="LOG-001",
        timestamp="2026-09-20T10:00:00Z",
        actor_id="DR-101",
        action_type="PRESCRIPTION_ISSUED",
        details={"remedy": "Sulphur", "potency": "200C"},
        patient_id="PT-001"
    )
    e2 = NABHAuditLedger.append_log(
        log_id="LOG-002",
        timestamp="2026-09-20T10:05:00Z",
        actor_id="DR-101",
        action_type="INIMICAL_OVERRIDE",
        details={"reason": "Acute emergency override exception invoked"},
        patient_id="PT-001"
    )

    assert e2.previous_hash == e1.current_hash
    assert NABHAuditLedger.verify_chain_integrity() is True

def test_nabh_audit_tamper_detection():
    """Verify that tampering with any historical log invalidates the cryptographic chain."""
    NABHAuditLedger.append_log(
        log_id="LOG-01",
        timestamp="2026-09-20T10:00:00Z",
        actor_id="DR-101",
        action_type="PATIENT_RECORD_ACCESSED",
        details={"module": "case_taking"},
        patient_id="PT-100"
    )
    NABHAuditLedger.append_log(
        log_id="LOG-02",
        timestamp="2026-09-20T10:10:00Z",
        actor_id="DR-101",
        action_type="EMERGENCY_LOCKOUT",
        details={"status": "Code Red activated"},
        patient_id="PT-100"
    )

    assert NABHAuditLedger.verify_chain_integrity() is True

    # Maliciously tamper with the details of the first log entry
    NABHAuditLedger._CHAIN[0].details["module"] = "tampered_module"
    assert NABHAuditLedger.verify_chain_integrity() is False

def test_nabh_audit_filter_by_patient():
    """Verify retrieval of patient-specific audit trails."""
    NABHAuditLedger.append_log(
        log_id="LOG-A",
        timestamp="2026-09-20T11:00:00Z",
        actor_id="DR-101",
        action_type="ACCESS",
        details={"note": "Routine visit"},
        patient_id="PT-AAA"
    )
    NABHAuditLedger.append_log(
        log_id="LOG-B",
        timestamp="2026-09-20T11:05:00Z",
        actor_id="DR-102",
        action_type="ACCESS",
        details={"note": "Routine visit"},
        patient_id="PT-BBB"
    )

    logs_aaa = NABHAuditLedger.get_logs_for_patient("PT-AAA")
    assert len(logs_aaa) == 1
    assert logs_aaa[0].log_id == "LOG-A"
