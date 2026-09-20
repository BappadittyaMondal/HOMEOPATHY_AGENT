"""
Tests for Phase 58: Clinical Pathology Diagnostic Engine (CPDE) & Laboratory Panic Gateway.
Validates INV-14 (Critical Laboratory Panic Value Gateway) and INV-15 (Aphorism 186 Operative Boundaries).
"""
import pytest
from app.clinical.cpde import (
    ClinicalPathologyDiagnosticEngine,
    ClinicalPresentationInput,
    ClinicalDomainCategory,
    SurgicalInterventionRequiredException
)
from app.clinical.lab_gateway import (
    LaboratoryPanicGateway,
    LabPanelObservation,
    LabObservation,
    LaboratoryPanicException
)


def test_inv_14_troponin_panic_value_raises_exception():
    """
    INV-14: Cardiac Troponin-I of 0.25 ng/mL (well above 0.04 ng/mL panic threshold)
    signaling acute myocardial infarction must raise LaboratoryPanicException and lock prescribing.
    """
    panel = LabPanelObservation(
        patient_id="PT-CARD-01",
        panel_name="CARDIAC_BIOMARKERS",
        timestamp="2026-09-20T12:00:00Z",
        observations=[
            LabObservation(analyte="troponin_i", value=0.25, unit="ng/mL")
        ]
    )
    with pytest.raises(LaboratoryPanicException) as exc_info:
        LaboratoryPanicGateway.evaluate_lab_panel(panel)
    assert "CRITICAL LAB PANIC" in str(exc_info.value)
    assert "TROPONIN_I" in str(exc_info.value)
    assert "myocardial infarction" in str(exc_info.value).lower()


def test_inv_14_potassium_lethal_hypokalemia_raises_exception():
    """INV-14: Severe hypokalemia (Potassium = 2.1 mEq/L < 2.5) must raise LaboratoryPanicException."""
    panel = LabPanelObservation(
        patient_id="PT-ELECTRO-01",
        panel_name="SERUM_ELECTROLYTES",
        timestamp="2026-09-20T12:00:00Z",
        observations=[
            LabObservation(analyte="potassium", value=2.1, unit="mEq/L")
        ]
    )
    with pytest.raises(LaboratoryPanicException) as exc_info:
        LaboratoryPanicGateway.evaluate_lab_panel(panel)
    assert "POTASSIUM" in str(exc_info.value)
    assert "arrhythmia" in str(exc_info.value).lower()


def test_inv_14_thrombocytopenia_spontaneous_hemorrhage_risk():
    """INV-14: Platelets 12,000 /uL (< 20,000 panic threshold) must raise LaboratoryPanicException."""
    panel = LabPanelObservation(
        patient_id="PT-CBC-01",
        panel_name="COMPLETE_BLOOD_COUNT",
        timestamp="2026-09-20T12:00:00Z",
        observations=[
            LabObservation(analyte="platelets", value=12000.0, unit="/uL")
        ]
    )
    with pytest.raises(LaboratoryPanicException) as exc_info:
        LaboratoryPanicGateway.evaluate_lab_panel(panel)
    assert "PLATELETS" in str(exc_info.value)


def test_normal_lab_panel_passes_safely():
    """Normal lab values allow routine outpatient homeopathic care."""
    panel = LabPanelObservation(
        patient_id="PT-NORMAL-01",
        panel_name="BASIC_METABOLIC",
        timestamp="2026-09-20T12:00:00Z",
        observations=[
            LabObservation(analyte="potassium", value=4.2, unit="mEq/L"),
            LabObservation(analyte="glucose", value=95.0, unit="mg/dL"),
            LabObservation(analyte="creatinine", value=0.9, unit="mg/dL")
        ]
    )
    res = LaboratoryPanicGateway.evaluate_lab_panel(panel, raise_on_panic=True)
    assert res.is_safe_for_outpatient_care is True
    assert res.has_critical_panic_values is False
    assert len(res.panic_findings) == 0


def test_inv_15_acute_appendicitis_surgical_boundary_raises_exception():
    """
    INV-15: Acute Appendicitis with McBurney point tenderness and rebound guarding
    must raise SurgicalInterventionRequiredException per Aphorism 186.
    """
    presentation = ClinicalPresentationInput(
        patient_id="PT-SURG-01",
        patient_age_years=22,
        chief_complaint="Severe right lower quadrant abdominal pain with nausea",
        duration_days=1,
        physical_signs=["McBurney point tenderness", "rebound tenderness", "guarding in right iliac fossa"],
        temperature_c=38.5
    )
    with pytest.raises(SurgicalInterventionRequiredException) as exc_info:
        ClinicalPathologyDiagnosticEngine.evaluate_presentation(presentation)
    assert "APHORISM 186 OPERATIVE BOUNDARY" in str(exc_info.value)
    assert "Acute Appendicitis" in exc_info.value.suspected_surgical_condition
    assert exc_info.value.recommended_surgical_specialty == "General Surgery"


def test_inv_15_bowel_obstruction_surgical_boundary():
    """INV-15: Acute mechanical bowel obstruction must be blocked from medical repertorization."""
    presentation = ClinicalPresentationInput(
        patient_id="PT-SURG-02",
        patient_age_years=68,
        chief_complaint="Abdominal distension with absolute constipation and feculent vomiting",
        duration_days=2,
        physical_signs=["feculent vomiting", "absent bowel sounds"]
    )
    with pytest.raises(SurgicalInterventionRequiredException) as exc_info:
        ClinicalPathologyDiagnosticEngine.evaluate_presentation(presentation)
    assert "Mechanical Bowel Obstruction" in exc_info.value.suspected_surgical_condition


def test_integrated_co_management_for_t1dm():
    """Type 1 Diabetes Mellitus requires integrated co-management without withdrawal of insulin."""
    presentation = ClinicalPresentationInput(
        patient_id="PT-T1D-01",
        patient_age_years=14,
        chief_complaint="Fatigue and polyuria with known Type 1 Diabetes",
        duration_days=30,
        known_diagnoses=["Type 1 Diabetes Mellitus", "T1DM"]
    )
    report = ClinicalPathologyDiagnosticEngine.evaluate_presentation(presentation, raise_on_surgical=True)
    assert report.category == ClinicalDomainCategory.INTEGRATED_CO_MANAGEMENT
    assert report.is_homeopathy_permitted_as_monotherapy is False
    assert report.requires_integrated_allopathic_co_management is True


def test_standard_outpatient_complaint_permitted():
    """Standard dynamic complaints (e.g. chronic allergic rhinitis) permit outpatient homeopathy."""
    presentation = ClinicalPresentationInput(
        patient_id="PT-OPD-01",
        patient_age_years=35,
        chief_complaint="Seasonal allergic rhinitis with sneezing and watery eyes",
        duration_days=14,
        physical_signs=["mild nasal mucosal edema"]
    )
    report = ClinicalPathologyDiagnosticEngine.evaluate_presentation(presentation, raise_on_surgical=True)
    assert report.category == ClinicalDomainCategory.MEDICAL_OUTPATIENT_HOMOEOPATHY
    assert report.is_homeopathy_permitted_as_monotherapy is True
    assert report.surgical_referral_mandated is False
