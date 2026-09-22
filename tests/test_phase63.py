"""
Phase 63 Unit Tests: Heavy Metal & Environmental Trace Element Toxicology Gateway (INV-14 Extended).
Validates critical lab panic thresholds for Arsenic (urine, hair, nails), Lead, Mercury, and Fluoride.
"""
import pytest
from app.clinical.lab_gateway import (
    LaboratoryPanicGateway,
    LabPanelObservation,
    LabObservation,
    LaboratoryPanicException,
    LabEvaluationResult
)


def test_inv_14_elevated_urine_arsenic_triggers_panic_lockout():
    """Verify INV-14: Urine Arsenic >= 50 ug/L raises LaboratoryPanicException."""
    panel = LabPanelObservation(
        patient_id="PT-TOX-001",
        panel_name="HEAVY_METAL_SCREEN",
        timestamp="2026-09-22T08:00:00Z",
        observations=[
            LabObservation(analyte="urine_arsenic", value=85.0, unit="ug/L")
        ]
    )
    with pytest.raises(LaboratoryPanicException) as exc_info:
        LaboratoryPanicGateway.evaluate_lab_panel(panel, raise_on_panic=True)
    assert "INV-14" in str(exc_info.value)
    assert exc_info.value.analyte_name == "urine_arsenic"
    assert exc_info.value.observed_value == 85.0


def test_inv_14_elevated_hair_arsenic_triggers_panic_lockout():
    """Verify INV-14: Hair Arsenic >= 1.0 ug/g raises LaboratoryPanicException."""
    panel = LabPanelObservation(
        patient_id="PT-TOX-002",
        panel_name="TRACE_ELEMENT_ASSAY",
        timestamp="2026-09-22T08:05:00Z",
        observations=[
            LabObservation(analyte="hair_arsenic", value=3.2, unit="ug/g")
        ]
    )
    with pytest.raises(LaboratoryPanicException) as exc_info:
        LaboratoryPanicGateway.evaluate_lab_panel(panel, raise_on_panic=True)
    assert "INV-14" in str(exc_info.value)
    assert "chronic tissue arsenic bioaccumulation" in str(exc_info.value).lower()


def test_inv_14_elevated_nail_arsenic_triggers_panic_lockout():
    """Verify INV-14: Nail Arsenic >= 1.0 ug/g raises LaboratoryPanicException."""
    panel = LabPanelObservation(
        patient_id="PT-TOX-003",
        panel_name="NAIL_ICPMS_ASSAY",
        timestamp="2026-09-22T08:10:00Z",
        observations=[
            LabObservation(analyte="nail_arsenic", value=2.4, unit="ug/g")
        ]
    )
    with pytest.raises(LaboratoryPanicException) as exc_info:
        LaboratoryPanicGateway.evaluate_lab_panel(panel, raise_on_panic=True)
    assert "INV-14" in str(exc_info.value)
    assert exc_info.value.analyte_name == "nail_arsenic"


def test_inv_14_blood_lead_plumbism_triggers_panic_lockout():
    """Verify INV-14: Blood Lead >= 5.0 ug/dL raises LaboratoryPanicException."""
    panel = LabPanelObservation(
        patient_id="PT-TOX-004",
        panel_name="BLOOD_LEAD_LEVEL",
        timestamp="2026-09-22T08:15:00Z",
        observations=[
            LabObservation(analyte="blood_lead", value=14.5, unit="ug/dL")
        ]
    )
    with pytest.raises(LaboratoryPanicException) as exc_info:
        LaboratoryPanicGateway.evaluate_lab_panel(panel, raise_on_panic=True)
    assert "INV-14" in str(exc_info.value)
    assert "plumbism" in str(exc_info.value).lower()


def test_inv_14_toxic_fluoride_elevation_triggers_panic_lockout():
    """Verify INV-14: Serum Fluoride >= 0.2 mg/L raises LaboratoryPanicException."""
    panel = LabPanelObservation(
        patient_id="PT-TOX-005",
        panel_name="ENDEMIC_FLUORIDE_SCREEN",
        timestamp="2026-09-22T08:20:00Z",
        observations=[
            LabObservation(analyte="serum_fluoride", value=0.45, unit="mg/L")
        ]
    )
    with pytest.raises(LaboratoryPanicException) as exc_info:
        LaboratoryPanicGateway.evaluate_lab_panel(panel, raise_on_panic=True)
    assert "INV-14" in str(exc_info.value)
    assert "fluorosis" in str(exc_info.value).lower()


def test_normal_trace_element_panel_passes_safely():
    """Verify safe normal trace element levels pass without triggering panic exceptions."""
    panel = LabPanelObservation(
        patient_id="PT-NORMAL-006",
        panel_name="OCCUPATIONAL_MONITORING",
        timestamp="2026-09-22T08:25:00Z",
        observations=[
            LabObservation(analyte="urine_arsenic", value=12.0, unit="ug/L"),  # < 50
            LabObservation(analyte="hair_arsenic", value=0.4, unit="ug/g"),    # < 1.0
            LabObservation(analyte="blood_lead", value=1.8, unit="ug/dL"),     # < 5.0
            LabObservation(analyte="serum_fluoride", value=0.05, unit="mg/L")  # < 0.2
        ]
    )
    result = LaboratoryPanicGateway.evaluate_lab_panel(panel, raise_on_panic=True)
    assert result.is_safe_for_outpatient_care is True
    assert result.has_critical_panic_values is False
    assert len(result.panic_findings) == 0
