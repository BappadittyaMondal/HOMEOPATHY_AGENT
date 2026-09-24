"""
Automated Test Suite for Phase 76: Explicit Vitality Mandate & Low-Reserve Safety Engine (INV-20).
"""
import pytest
from app.models.vitality import PatientVitalityAssessment, ConstitutionTemperamentEnum
from app.clinical.vitality_mandate import (
    ExplicitVitalityMandateEngine,
    VitalityUnassessedException,
    KentObservation1HazardException
)


def test_chronic_without_vitality_raises_vitality_unassessed_exception():
    """Verify INV-20: Chronic constitutional prescribing without explicit vitality scoring raises VitalityUnassessedException."""
    with pytest.raises(VitalityUnassessedException) as exc_info:
        ExplicitVitalityMandateEngine.validate_chronic_vitality(
            vitality_assessment=None,
            is_acute=False,
            patient_id="PT-CHRONIC-001"
        )
    assert "VITALITY ASSESSMENT MANDATE (INV-20)" in str(exc_info.value)
    assert exc_info.value.patient_id == "PT-CHRONIC-001"


def test_chronic_with_explicit_vitality_succeeds():
    """Verify that providing an explicit PatientVitalityAssessment passes validation cleanly."""
    vitality = PatientVitalityAssessment(
        susceptibility_score=6.5,
        vital_force_score=7.0,
        pathological_depth=1,
        temperament=ConstitutionTemperamentEnum.NERVOUS_INTELLECTUAL,
        posology_scaling_factor=22.75,
        clinical_recommendation="Good reserve"
    )
    result = ExplicitVitalityMandateEngine.validate_chronic_vitality(
        vitality_assessment=vitality,
        is_acute=False,
        patient_id="PT-CHRONIC-002"
    )
    assert result == vitality
    assert result.vital_force_score == 7.0


def test_acute_prescribing_permits_vitality_omission():
    """Verify that acute prescribing does not fail when vitality assessment is not explicitly provided."""
    result = ExplicitVitalityMandateEngine.validate_chronic_vitality(
        vitality_assessment=None,
        is_acute=True,
        patient_id="PT-ACUTE-001"
    )
    assert result is not None
    assert result.vital_force_score == 5.0
    assert result.pathological_depth == 1


def test_kent_observation_1_high_potency_depleted_patient_blocked():
    """Verify Kent Observation 1: Depleted vital force (V <= 3.5) with deep pathology (depth >= 3) blocks high centesimals."""
    frail_vitality = PatientVitalityAssessment(
        susceptibility_score=2.0,
        vital_force_score=2.5,
        pathological_depth=4,
        temperament=ConstitutionTemperamentEnum.DEBILITATED_EXHAUSTED,
        posology_scaling_factor=1.0,
        clinical_recommendation="Exhausted vitality, deep structural pathology"
    )

    hazardous_potencies = ["200C", "1M", "10M", "50M", "CM", "200 CH"]
    for pot in hazardous_potencies:
        with pytest.raises(KentObservation1HazardException) as exc_info:
            ExplicitVitalityMandateEngine.verify_potency_reserve_safety(frail_vitality, pot)
        assert "KENT OBSERVATION 1 COLLAPSE HAZARD" in str(exc_info.value)
        assert exc_info.value.vitality_score == 2.5
        assert exc_info.value.pathological_depth == 4


def test_kent_observation_1_low_potency_allowed_for_depleted_patient():
    """Verify that low potencies (3X, 6X, 6C, 12C, LM 0/1) are safe for low-reserve patients."""
    frail_vitality = PatientVitalityAssessment(
        susceptibility_score=2.0,
        vital_force_score=2.5,
        pathological_depth=4,
        temperament=ConstitutionTemperamentEnum.DEBILITATED_EXHAUSTED,
        posology_scaling_factor=1.0,
        clinical_recommendation="Exhausted vitality, deep structural pathology"
    )

    safe_potencies = ["3X", "6X", "6C", "12C", "LM 0/1", "Q1", "MT"]
    for pot in safe_potencies:
        # Should not raise any exception
        ExplicitVitalityMandateEngine.verify_potency_reserve_safety(frail_vitality, pot)


def test_robust_vitality_patient_permits_high_potency():
    """Verify that patients with robust vitality (V > 3.5) can safely receive high centesimal potencies."""
    robust_vitality = PatientVitalityAssessment(
        susceptibility_score=8.0,
        vital_force_score=8.5,
        pathological_depth=1,
        temperament=ConstitutionTemperamentEnum.SANGUINE_ACTIVE,
        posology_scaling_factor=34.0,
        clinical_recommendation="Robust vital reaction"
    )

    for pot in ["200C", "1M", "10M", "CM"]:
        ExplicitVitalityMandateEngine.verify_potency_reserve_safety(robust_vitality, pot)
