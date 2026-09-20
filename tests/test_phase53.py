"""
Tests for Phase 53: Comprehensive Emergency Break-Glass & Psychiatric Crisis Firewall.
Validates INV-05 (Suicidality / Psychosis Lockout) and INV-06 (NEWS2 / PEWS Physiological Scoring).
"""
import pytest
from app.clinical.break_glass import (
    EmergencyVitals,
    EmergencyBreakGlassGateway,
    EmergencyTransferPacket
)


def test_inv_05_suicidal_ideation_triggers_code_red_psychiatric_lockout():
    """
    INV-05: Patient expressing active suicidal ideation must trigger an immutable
    CODE_RED_PSYCHIATRIC lockout, locking outpatient prescribing.
    """
    vitals = EmergencyVitals(
        systolic_bp=120,
        diastolic_bp=80,
        respiratory_rate=16,
        heart_rate=72,
        has_suicidal_ideation=True,
        patient_age_years=28
    )
    packet = EmergencyBreakGlassGateway.evaluate_emergency_status(vitals)
    assert packet.is_emergency_lockout_active is True
    assert packet.emergency_level == "CODE_RED_PSYCHIATRIC"
    assert packet.is_psychiatric_lockout is True
    assert any("suicidal" in c.lower() for c in packet.triggered_conditions)
    assert any("halt and lock" in a.lower() for a in packet.immediate_actions_required)


def test_inv_05_acute_psychosis_triggers_psychiatric_lockout():
    """INV-05: Acute psychotic excitation must trigger psychiatric lockout."""
    vitals = EmergencyVitals(
        systolic_bp=130,
        diastolic_bp=85,
        respiratory_rate=20,
        heart_rate=95,
        has_acute_psychosis=True,
        patient_age_years=35
    )
    packet = EmergencyBreakGlassGateway.evaluate_emergency_status(vitals)
    assert packet.is_emergency_lockout_active is True
    assert packet.emergency_level == "CODE_RED_PSYCHIATRIC"
    assert packet.is_psychiatric_lockout is True


def test_inv_06_adult_news2_high_risk_triggers_code_red():
    """
    INV-06: Adult patient with severe physiological deterioration (NEWS2 >= 7)
    must trigger fail-closed CODE_RED_CRITICAL transfer.
    """
    # RR=26 (3), SpO2=90% (3), Pulse=135 (3) -> Total NEWS2 >= 9
    vitals = EmergencyVitals(
        systolic_bp=115,
        diastolic_bp=75,
        respiratory_rate=26,
        heart_rate=135,
        spo2_percentage=90,
        patient_age_years=55
    )
    packet = EmergencyBreakGlassGateway.evaluate_emergency_status(vitals)
    assert packet.is_emergency_lockout_active is True
    assert packet.emergency_level == "CODE_RED_CRITICAL"
    assert packet.news2_score is not None
    assert packet.news2_score >= 7
    assert any("news2 score" in c.lower() for c in packet.triggered_conditions)


def test_inv_06_pediatric_pews_high_risk_triggers_code_red():
    """
    INV-06: Pediatric patient (age < 18) with PEWS >= 5 must trigger
    fail-closed pediatric emergency transfer.
    """
    # Child aged 4: RR=52 (3), HR=165 (3) -> PEWS >= 6
    vitals = EmergencyVitals(
        systolic_bp=90,
        diastolic_bp=60,
        respiratory_rate=52,
        heart_rate=165,
        patient_age_years=4
    )
    packet = EmergencyBreakGlassGateway.evaluate_emergency_status(vitals)
    assert packet.is_emergency_lockout_active is True
    assert packet.emergency_level == "CODE_RED_CRITICAL"
    assert packet.pews_score is not None
    assert packet.pews_score >= 5
    assert any("pediatric pews" in c.lower() for c in packet.triggered_conditions)


def test_stable_opd_patient_permits_consultation():
    """Normal vitals without red flags must return STABLE_OPD with lockout inactive."""
    vitals = EmergencyVitals(
        systolic_bp=120,
        diastolic_bp=80,
        respiratory_rate=16,
        heart_rate=72,
        spo2_percentage=98,
        patient_age_years=30
    )
    packet = EmergencyBreakGlassGateway.evaluate_emergency_status(vitals)
    assert packet.is_emergency_lockout_active is False
    assert packet.emergency_level == "STABLE_OPD"
    assert len(packet.triggered_conditions) == 0
