"""
Tele-Homoeopathy Secure Consultation, DPDP Consent & Triage Architecture (Phase 48).
Enforces Ministry of Ayush / NCH Telemedicine Practice Guidelines 2022
and Digital Personal Data Protection (DPDP) Act 2023 consent artefacts.
"""
from typing import List, Optional
from pydantic import BaseModel

class DPDPPatientConsent(BaseModel):
    consent_id: str
    patient_id: str
    consultation_mode: str  # "VIDEO", "AUDIO", "TEXT_CHAT"
    purpose_description: str = "Homeopathic clinical assessment, case-taking, and prescription"
    data_fiduciary_name: str = "Hospital Enterprise HHIS"
    consent_timestamp: str
    has_agreed_to_telemedicine_limitations: bool
    right_to_withdraw_acknowledged: bool

class TeleTriageAssessment(BaseModel):
    consultation_id: str
    patient_id: str
    chief_complaint: str
    has_emergency_red_flags: bool  # e.g., severe dyspnea, crushing chest pain, trauma
    consent: DPDPPatientConsent

class TeleConsultationClearance(BaseModel):
    is_telemedicine_permitted: bool
    status: str  # "APPROVED_FOR_TELE_CONSULTATION", "REJECTED_EMERGENCY_RED_FLAG", "CONSENT_INVALID"
    clinical_guidance: str
    statutory_standard: str = "Telemedicine Practice Guidelines for Homoeopathy 2022 & DPDP Act 2023"

class TeleHomoeopathyGateway:
    """
    Validates DPDP Act 2023 consent and filters emergency red flags before tele-consultations.
    """

    @classmethod
    def evaluate_tele_triage(
        cls,
        assessment: TeleTriageAssessment
    ) -> TeleConsultationClearance:
        """
        Validates consent integrity and enforces tele-homoeopathy triage safety boundaries.
        """
        # 1. Validate DPDP Consent
        if (
            not assessment.consent.has_agreed_to_telemedicine_limitations
            or not assessment.consent.right_to_withdraw_acknowledged
        ):
            return TeleConsultationClearance(
                is_telemedicine_permitted=False,
                status="CONSENT_INVALID",
                clinical_guidance="DPDP Act 2023 non-compliance: Valid patient informed consent is mandatory prior to tele-consultation."
            )

        # 2. Check for Emergency Red Flags
        if assessment.has_emergency_red_flags:
            return TeleConsultationClearance(
                is_telemedicine_permitted=False,
                status="REJECTED_EMERGENCY_RED_FLAG",
                clinical_guidance=(
                    "TELEMEDICINE CONTRAINDICATION: Patient reports acute emergency red flags. "
                    "Per NCH Guidelines Section 4.2, telemedicine is strictly barred for acute critical emergencies. "
                    "Instruct patient to report immediately to the nearest hospital casualty / emergency department."
                )
            )

        # 3. Approved for Remote Clinical Case-Taking
        return TeleConsultationClearance(
            is_telemedicine_permitted=True,
            status="APPROVED_FOR_TELE_CONSULTATION",
            clinical_guidance=f"Patient cleared for {assessment.consent.consultation_mode} tele-consultation under NCH 2022 guidelines."
        )
