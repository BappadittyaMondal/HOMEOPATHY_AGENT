"""
Phase 62 Unit Tests: Oncological Pre-Malignancy Surveillance Gate (INV-17).
Validates mandatory biopsy lockouts on chronic keratoses, Bowenoid transformations, and suspicious indurations.
"""
import pytest
from app.clinical.cpde import (
    ClinicalPathologyDiagnosticEngine,
    ClinicalPresentationInput,
    ClinicalDomainCategory,
    OncologicalBiopsyRequiredException,
    SurgicalInterventionRequiredException
)


def test_inv_17_arsenical_keratosis_with_induration_raises_exception():
    """Verify INV-17: Chronic arsenical keratosis with focal induration triggers mandatory biopsy lockout."""
    presentation = ClinicalPresentationInput(
        patient_id="PT-ARS-KERA-001",
        patient_age_years=48,
        chief_complaint="Rough thickened palms and soles since 15 years",
        duration_days=5475,  # 15 years
        physical_signs=["punctate keratosis on both palms", "indurated keratosis on right hypothenar", "dark rough skin"],
        known_diagnoses=["Groundwater arsenic exposure in childhood"]
    )
    with pytest.raises(OncologicalBiopsyRequiredException) as exc_info:
        ClinicalPathologyDiagnosticEngine.evaluate_presentation(presentation, raise_on_oncological=True)
    assert "INV-17" in str(exc_info.value)
    assert "Dermatopathology Punch Biopsy" in exc_info.value.recommended_investigation


def test_inv_17_bowen_disease_in_situ_carcinoma_raises_exception():
    """Verify INV-17: Bowen's disease triggers full-thickness punch biopsy mandate."""
    presentation = ClinicalPresentationInput(
        patient_id="PT-BOWEN-002",
        patient_age_years=62,
        chief_complaint="Crusted erythematous plaque on dorsum of hand",
        duration_days=730,
        physical_signs=["scaling plaque", "suspected bowen disease", "irregular border"]
    )
    with pytest.raises(OncologicalBiopsyRequiredException) as exc_info:
        ClinicalPathologyDiagnosticEngine.evaluate_presentation(presentation)
    assert "INV-17" in str(exc_info.value)
    assert "Bowen" in exc_info.value.suspected_lesion


def test_inv_17_marjolin_ulcer_raises_exception():
    """Verify INV-17: Chronic burn scar with non-healing indurated ulcer edge raises exception."""
    presentation = ClinicalPresentationInput(
        patient_id="PT-MARJOLIN-003",
        patient_age_years=55,
        chief_complaint="Non-healing ulcer over old scar tissue",
        duration_days=400,
        physical_signs=["non-healing chronic ulcer with everted edges", "indurated ulcer edge"]
    )
    with pytest.raises(OncologicalBiopsyRequiredException) as exc_info:
        ClinicalPathologyDiagnosticEngine.evaluate_presentation(presentation)
    assert "INV-17" in str(exc_info.value)
    assert "Marjolin" in exc_info.value.suspected_lesion


def test_inv_17_multi_decade_keratosis_with_ulceration_heuristic():
    """Verify INV-17: >10y chronic keratosis presenting spontaneous bleeding/ulceration triggers biopsy."""
    presentation = ClinicalPresentationInput(
        patient_id="PT-CHRONIC-004",
        patient_age_years=50,
        chief_complaint="Thick skin on palms and soles since 20 years",
        duration_days=7300,  # 20 years
        physical_signs=["palmar keratosis", "deep bleeding crack", "ulceration on heel"],
        known_diagnoses=[]
    )
    with pytest.raises(OncologicalBiopsyRequiredException) as exc_info:
        ClinicalPathologyDiagnosticEngine.evaluate_presentation(presentation)
    assert "INV-17" in str(exc_info.value)
    assert "High-Risk Bowenoid Degeneration" in exc_info.value.suspected_lesion


def test_inv_17_non_raising_mode_returns_report_with_biopsy_mandate():
    """Verify that when raise_on_oncological=False, report correctly reflects ONCOLOGICAL_BIOPSY_MANDATED."""
    presentation = ClinicalPresentationInput(
        patient_id="PT-REPORT-005",
        patient_age_years=45,
        chief_complaint="Keratosis with induration on sole",
        duration_days=4000,
        physical_signs=["indurated keratosis"]
    )
    report = ClinicalPathologyDiagnosticEngine.evaluate_presentation(
        presentation, raise_on_oncological=False
    )
    assert report.category == ClinicalDomainCategory.ONCOLOGICAL_BIOPSY_MANDATED
    assert report.is_homeopathy_permitted_as_monotherapy is False
    assert report.biopsy_mandated is True
    assert "INV-17" in report.clinical_rationale


def test_benign_skin_complaint_permitted_without_biopsy():
    """Verify standard benign chronic dermatosis passes without triggering INV-17 or INV-15."""
    presentation = ClinicalPresentationInput(
        patient_id="PT-BENIGN-006",
        patient_age_years=35,
        chief_complaint="Dry itchy eczema on elbows and knees",
        duration_days=180,
        physical_signs=["erythema", "dry scaling", "mild itching"],
        known_diagnoses=[]
    )
    report = ClinicalPathologyDiagnosticEngine.evaluate_presentation(presentation)
    assert report.category == ClinicalDomainCategory.MEDICAL_OUTPATIENT_HOMOEOPATHY
    assert report.is_homeopathy_permitted_as_monotherapy is True
    assert report.biopsy_mandated is False
    assert report.surgical_referral_mandated is False
