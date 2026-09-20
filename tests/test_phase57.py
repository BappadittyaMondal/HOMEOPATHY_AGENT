"""
Tests for Phase 57: Obstetric Gestational Trimester Contraindication Firewall & Pediatric Consent.
Validates INV-12 (Obstetric Abortifacient / Emmenagogue Firewall) and INV-13 (DPDP Act Pediatric Consent).
"""
import pytest
from app.safety.obstetric_firewall import (
    ObstetricSafetyFirewall,
    PatientObstetricProfile,
    PregnancyStatus,
    PediatricGuardianConsent,
    ObstetricBlockException,
    PediatricConsentRequiredException
)


def test_inv_12_sabina_in_first_trimester_raises_exception():
    """
    INV-12: Prescribing Sabina during Trimester 1 must raise ObstetricBlockException
    due to violent pelvic congestion and abortion risk.
    """
    profile = PatientObstetricProfile(
        pregnancy_status=PregnancyStatus.TRIMESTER_1,
        gestational_weeks=8
    )
    with pytest.raises(ObstetricBlockException) as exc_info:
        ObstetricSafetyFirewall.evaluate_obstetric_safety(
            remedy_name="Sabina",
            potency="30C",
            profile=profile
        )
    assert "OBSTETRIC CONTRAINDICATION" in str(exc_info.value)
    assert "Sabina" in str(exc_info.value)


def test_inv_12_secale_in_third_trimester_raises_exception():
    """INV-12: Prescribing Secale cornutum during Trimester 3 must be blocked."""
    profile = PatientObstetricProfile(
        pregnancy_status=PregnancyStatus.TRIMESTER_3,
        gestational_weeks=32
    )
    with pytest.raises(ObstetricBlockException) as exc_info:
        ObstetricSafetyFirewall.evaluate_obstetric_safety(
            remedy_name="Secale cornutum",
            potency="200C",
            profile=profile
        )
    assert "OBSTETRIC CONTRAINDICATION" in str(exc_info.value)


def test_inv_12_caulophyllum_in_first_trimester_raises_exception():
    """INV-12: Caulophyllum in early pregnancy (Trimester 1) must be blocked."""
    profile = PatientObstetricProfile(
        pregnancy_status=PregnancyStatus.TRIMESTER_1,
        gestational_weeks=6
    )
    with pytest.raises(ObstetricBlockException) as exc_info:
        ObstetricSafetyFirewall.evaluate_obstetric_safety(
            remedy_name="Caulophyllum thalictroides",
            potency="30C",
            profile=profile
        )
    assert "Caulophyllum" in str(exc_info.value)


def test_safe_remedy_during_pregnancy_passes():
    """Safe constitutional remedy like Arnica montana during Trimester 2 passes."""
    profile = PatientObstetricProfile(
        pregnancy_status=PregnancyStatus.TRIMESTER_2,
        gestational_weeks=20
    )
    res = ObstetricSafetyFirewall.evaluate_obstetric_safety(
        remedy_name="Arnica montana",
        potency="30C",
        profile=profile,
        raise_on_block=True
    )
    assert res.is_permitted is True
    assert res.contraindication_level == "SAFE"


def test_inv_13_pediatric_minor_without_guardian_consent_raises_exception():
    """
    INV-13: Prescribing for a 7-year-old child without verified guardian consent
    must raise PediatricConsentRequiredException under DPDP Act 2023 Section 9.
    """
    with pytest.raises(PediatricConsentRequiredException) as exc_info:
        ObstetricSafetyFirewall.evaluate_pediatric_consent(
            patient_age_years=7,
            consent=None
        )
    assert "DPDP ACT 2023 SECTION 9 VIOLATION" in str(exc_info.value)
    assert exc_info.value.patient_age == 7


def test_inv_13_pediatric_with_verified_consent_succeeds():
    """Pediatric patient with verified guardian consent succeeds."""
    consent = PediatricGuardianConsent(
        guardian_name="Anita Mukherjee",
        guardian_relationship="Mother",
        consent_timestamp="2026-09-20T10:00:00Z",
        is_verified=True,
        national_id_last4="4321"
    )
    assert ObstetricSafetyFirewall.evaluate_pediatric_consent(patient_age_years=5, consent=consent) is True


def test_adult_patient_does_not_require_guardian_consent():
    """Adult patient (age >= 18) does not require guardian consent."""
    assert ObstetricSafetyFirewall.evaluate_pediatric_consent(patient_age_years=25, consent=None) is True
