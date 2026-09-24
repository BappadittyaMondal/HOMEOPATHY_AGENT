"""
Automated Test Suite for Phase 77: Objective Physiological Vitals Gate Engine (INV-21).
"""
import pytest
from app.clinical.vitals_gate import (
    ObjectivePhysiologicalVitals,
    ObjectiveVitalsGateEngine,
    MissingVitalsException,
    CriticalVitalsDecompensationException
)


def test_acute_missing_vitals_raises_missing_vitals_exception():
    """Verify INV-21: Acute tele-triage without verified vitals raises MissingVitalsException."""
    with pytest.raises(MissingVitalsException) as exc_info:
        ObjectiveVitalsGateEngine.evaluate_vitals(
            vitals=None,
            is_acute=True,
            patient_id="PT-ACUTE-101"
        )
    assert "OBJECTIVE VITALS GATE MANDATE (INV-21)" in str(exc_info.value)
    assert exc_info.value.patient_id == "PT-ACUTE-101"
    assert "pulse_bpm" in exc_info.value.missing_fields


def test_stable_acute_vitals_cleared():
    """Verify stable vitals pass the gate cleanly with LOW risk and NEWS2 = 0."""
    vitals = ObjectivePhysiologicalVitals(
        pulse_bpm=72,
        systolic_bp=120,
        diastolic_bp=80,
        respiratory_rate=16,
        temperature_celsius=37.0,
        spo2_percent=98,
        blood_glucose_mg_dl=110.0,
        consciousness_avpu="ALERT"
    )

    assessment = ObjectiveVitalsGateEngine.evaluate_vitals(
        vitals=vitals,
        is_acute=True,
        patient_id="PT-STABLE-102"
    )
    assert assessment.is_cleared is True
    assert assessment.news2_score == 0
    assert assessment.clinical_risk_tier == "LOW"
    assert "Physiological vitals stable" in assessment.clinical_summary


def test_critical_hypoxia_triggers_decompensation_exception():
    """Verify severe hypoxemia (SpO2 88%) triggers CriticalVitalsDecompensationException."""
    vitals = ObjectivePhysiologicalVitals(
        pulse_bpm=95,
        systolic_bp=125,
        diastolic_bp=82,
        respiratory_rate=22,
        temperature_celsius=37.8,
        spo2_percent=88,  # Critical hypoxemia
        consciousness_avpu="ALERT"
    )

    with pytest.raises(CriticalVitalsDecompensationException) as exc_info:
        ObjectiveVitalsGateEngine.evaluate_vitals(
            vitals=vitals,
            is_acute=True,
            patient_id="PT-HYPOXIA-103"
        )
    assert "CRITICAL CARE DECOMPENSATION LOCKOUT" in str(exc_info.value)
    assert any("Severe Hypoxemia" in flag for flag in exc_info.value.critical_flags)
    assert exc_info.value.transfer_packet is not None
    assert exc_info.value.transfer_packet.is_emergency_lockout_active is True


def test_cardiovascular_shock_hypotension_blocked():
    """Verify cardiogenic or septic shock (BP 80/50, pulse 135) triggers critical care lockout."""
    vitals = ObjectivePhysiologicalVitals(
        pulse_bpm=135,       # Extreme tachycardia
        systolic_bp=80,      # Severe hypotension
        diastolic_bp=50,
        respiratory_rate=26, # Tachypnea
        temperature_celsius=39.2,
        spo2_percent=93,
        consciousness_avpu="VOICE"
    )

    with pytest.raises(CriticalVitalsDecompensationException) as exc_info:
        ObjectiveVitalsGateEngine.evaluate_vitals(
            vitals=vitals,
            is_acute=True,
            patient_id="PT-SHOCK-104"
        )
    assert exc_info.value.news2_score >= 7
    assert exc_info.value.transfer_packet.emergency_level == "CODE_RED_CRITICAL"


def test_critical_glucose_derangement_blocked():
    """Verify extreme hyperglycemic crisis (Blood Glucose 480 mg/dL) triggers critical lockout."""
    vitals = ObjectivePhysiologicalVitals(
        pulse_bpm=102,
        systolic_bp=118,
        diastolic_bp=76,
        respiratory_rate=18,
        temperature_celsius=37.1,
        spo2_percent=97,
        blood_glucose_mg_dl=480.0,  # DKA / HHS alert
        consciousness_avpu="ALERT"
    )

    with pytest.raises(CriticalVitalsDecompensationException) as exc_info:
        ObjectiveVitalsGateEngine.evaluate_vitals(
            vitals=vitals,
            is_acute=True,
            patient_id="PT-DKA-105"
        )
    assert any("DKA Risk" in flag for flag in exc_info.value.critical_flags)


def test_chronic_case_without_vitals_defaults_safely():
    """Verify non-acute (chronic) cases do not fail when vitals are not provided."""
    assessment = ObjectiveVitalsGateEngine.evaluate_vitals(
        vitals=None,
        is_acute=False,
        patient_id="PT-CHRONIC-106"
    )
    assert assessment.is_cleared is True
    assert assessment.news2_score == 0
    assert assessment.clinical_risk_tier == "LOW"
