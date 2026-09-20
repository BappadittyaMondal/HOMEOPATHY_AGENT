"""
Unit Tests for Phase 39: Western Emergency Break-Glass & Acute Care Transfer Gateway.
"""
from app.clinical.break_glass import EmergencyBreakGlassGateway, EmergencyVitals

def test_break_glass_qsofa_septic_shock_lockout():
    """Verify emergency lockout triggered by qSOFA score >= 2."""
    vitals = EmergencyVitals(
        systolic_bp=85,
        diastolic_bp=55,
        respiratory_rate=26,
        heart_rate=118,
        gcs_score=13,
        spo2_percentage=89
    )
    packet = EmergencyBreakGlassGateway.evaluate_emergency_status(vitals)
    assert packet.is_emergency_lockout_active is True
    assert packet.emergency_level == "CODE_RED_CRITICAL"
    assert packet.qsofa_score >= 2
    assert any("qSOFA" in c for c in packet.triggered_conditions)
    assert any("ACTIVATE CODE RED" in a for a in packet.immediate_actions_required)

def test_break_glass_acute_mi_shock():
    """Verify emergency lockout triggered by acute MI with cardiogenic shock."""
    vitals = EmergencyVitals(
        systolic_bp=80,
        diastolic_bp=50,
        respiratory_rate=20,
        heart_rate=125,
        gcs_score=15,
        spo2_percentage=94,
        has_crushing_chest_pain=True
    )
    packet = EmergencyBreakGlassGateway.evaluate_emergency_status(vitals)
    assert packet.is_emergency_lockout_active is True
    assert packet.emergency_level == "CODE_RED_CRITICAL"
    assert any("Myocardial Infarction" in c for c in packet.triggered_conditions)

def test_break_glass_surgical_abdomen():
    """Verify emergency lockout triggered by board-like abdominal rigidity."""
    vitals = EmergencyVitals(
        systolic_bp=110,
        diastolic_bp=70,
        respiratory_rate=18,
        heart_rate=95,
        gcs_score=15,
        spo2_percentage=98,
        has_board_like_abdomen=True
    )
    packet = EmergencyBreakGlassGateway.evaluate_emergency_status(vitals)
    assert packet.is_emergency_lockout_active is True
    assert any("Surgical Abdomen" in c for c in packet.triggered_conditions)

def test_break_glass_stable_opd_vitals():
    """Verify normal outpatient vitals do not trigger lockout."""
    vitals = EmergencyVitals(
        systolic_bp=120,
        diastolic_bp=80,
        respiratory_rate=16,
        heart_rate=72,
        gcs_score=15,
        spo2_percentage=98
    )
    packet = EmergencyBreakGlassGateway.evaluate_emergency_status(vitals)
    assert packet.is_emergency_lockout_active is False
    assert packet.emergency_level == "STABLE_OPD"
    assert packet.qsofa_score == 0
