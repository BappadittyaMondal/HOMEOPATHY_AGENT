"""
Unit Tests for Phase 48: Tele-Homoeopathy & DPDP Consent Engine.
"""
from app.governance.tele_homoeopathy import (
    TeleHomoeopathyGateway,
    DPDPPatientConsent,
    TeleTriageAssessment
)

def test_tele_homoeopathy_approved_consultation():
    """Verify approval of remote consultation with valid DPDP consent and no red flags."""
    consent = DPDPPatientConsent(
        consent_id="CNS-001",
        patient_id="PT-50",
        consultation_mode="VIDEO",
        consent_timestamp="2026-09-20T11:00:00Z",
        has_agreed_to_telemedicine_limitations=True,
        right_to_withdraw_acknowledged=True
    )
    assessment = TeleTriageAssessment(
        consultation_id="TEL-101",
        patient_id="PT-50",
        chief_complaint="Chronic recurrent allergic rhinitis",
        has_emergency_red_flags=False,
        consent=consent
    )
    clearance = TeleHomoeopathyGateway.evaluate_tele_triage(assessment)
    assert clearance.is_telemedicine_permitted is True
    assert clearance.status == "APPROVED_FOR_TELE_CONSULTATION"
    assert "VIDEO" in clearance.clinical_guidance

def test_tele_homoeopathy_emergency_red_flag_rejected():
    """Verify rejection when patient reports acute emergency red flags."""
    consent = DPDPPatientConsent(
        consent_id="CNS-002",
        patient_id="PT-51",
        consultation_mode="AUDIO",
        consent_timestamp="2026-09-20T11:05:00Z",
        has_agreed_to_telemedicine_limitations=True,
        right_to_withdraw_acknowledged=True
    )
    assessment = TeleTriageAssessment(
        consultation_id="TEL-102",
        patient_id="PT-51",
        chief_complaint="Severe chest pain and sudden dyspnea",
        has_emergency_red_flags=True,
        consent=consent
    )
    clearance = TeleHomoeopathyGateway.evaluate_tele_triage(assessment)
    assert clearance.is_telemedicine_permitted is False
    assert clearance.status == "REJECTED_EMERGENCY_RED_FLAG"
    assert "TELEMEDICINE CONTRAINDICATION" in clearance.clinical_guidance

def test_tele_homoeopathy_invalid_dpdp_consent():
    """Verify rejection when patient has not consented to statutory limitations."""
    consent = DPDPPatientConsent(
        consent_id="CNS-003",
        patient_id="PT-52",
        consultation_mode="TEXT_CHAT",
        consent_timestamp="2026-09-20T11:10:00Z",
        has_agreed_to_telemedicine_limitations=False,  # Did not agree
        right_to_withdraw_acknowledged=True
    )
    assessment = TeleTriageAssessment(
        consultation_id="TEL-103",
        patient_id="PT-52",
        chief_complaint="Mild insomnia",
        has_emergency_red_flags=False,
        consent=consent
    )
    clearance = TeleHomoeopathyGateway.evaluate_tele_triage(assessment)
    assert clearance.is_telemedicine_permitted is False
    assert clearance.status == "CONSENT_INVALID"
