"""
Automated Test Suite for Phase 73: Multi-Parameter Laboratory Diagnostic Report Parser.
"""
import pytest
from app.clinical.lab_report_parser import (
    LabReportParserEngine,
    ParsedLabReport
)
from app.clinical.lab_gateway import (
    LaboratoryPanicGateway,
    LaboratoryPanicException
)


def test_normal_routine_lab_panel_extraction():
    """Verify normal lab panel parameters are parsed with zero panic triggers."""
    sample_text = """
    CENTRAL CLINICAL DIAGNOSTICS
    Patient ID: PT-NORM-101
    Date: 2026-09-24
    Hemoglobin: 14.2 g/dL
    Total WBC: 6500 /uL
    Platelet Count: 250000 /uL
    Serum Creatinine: 0.9 mg/dL
    Potassium: 4.3 mEq/L
    Fasting Blood Sugar: 92 mg/dL
    """
    report = LabReportParserEngine.parse_lab_text("PT-NORM-101", sample_text)

    assert report.has_panic_values is False
    assert report.statutory_action_mandated == "PROCEED_WITH_STANDARD_CARE"
    assert len(report.items) == 6

    # Verify values
    k_item = next(i for i in report.items if i.analyte_canonical_name == "potassium")
    assert k_item.value == 4.3
    assert k_item.is_panic is False
    assert k_item.is_abnormal is False


def test_cardiac_troponin_panic_detection():
    """Verify Troponin-I elevation immediately flags panic and emergency transfer mandate."""
    sample_text = """
    EMERGENCY BIOCHEMISTRY REPORT
    Patient: PT-CARDIAC-999
    Cardiac Troponin I: 0.28 ng/mL
    Total WBC: 12400 /uL
    Potassium: 4.1 mEq/L
    """
    report = LabReportParserEngine.parse_lab_text("PT-CARDIAC-999", sample_text)

    assert report.has_panic_values is True
    assert report.statutory_action_mandated == "EMERGENCY_LOCKOUT_TRANSFER_MANDATED"
    assert any("TROPONIN_I" in f for f in report.panic_findings)

    # Convert to gateway panel and verify gateway evaluates it as unsafe
    panel = LabReportParserEngine.convert_to_gateway_panel(report)
    with pytest.raises(LaboratoryPanicException):
        LaboratoryPanicGateway.evaluate_lab_panel(panel)


def test_severe_thrombocytopenia_panic():
    """Verify platelet count below 20,000 /uL triggers critical visceral hemorrhage panic."""
    sample_text = """
    CBC REPORT
    Hb: 10.5 g/dL
    Platelets: 14000 /uL
    TLC: 4500 /uL
    """
    report = LabReportParserEngine.parse_lab_text("PT-THROMB-303", sample_text)

    assert report.has_panic_values is True
    plt_item = next(i for i in report.items if i.analyte_canonical_name == "platelets")
    assert plt_item.value == 14000.0
    assert plt_item.is_panic is True
    assert "intracranial / visceral hemorrhage" in plt_item.clinical_risk


def test_hypokalemic_cardiac_arrest_panic():
    """Verify severe hypokalemia (< 2.5 mEq/L) triggers lethal arrhythmia panic."""
    sample_text = """
    SERUM ELECTROLYTES
    Sodium: 138 mEq/L
    Potassium: 2.2 mEq/L
    """
    report = LabReportParserEngine.parse_lab_text("PT-K-505", sample_text)

    assert report.has_panic_values is True
    k_item = next(i for i in report.items if i.analyte_canonical_name == "potassium")
    assert k_item.value == 2.2
    assert k_item.is_panic is True


def test_heavy_metal_toxicology_panic():
    """Verify Urine Arsenic elevation (>= 50 ug/L) triggers INV-14 toxicological panic."""
    sample_text = """
    ENVIRONMENTAL TRACE ELEMENT ASSAY
    Patient ID: PT-GEO-707
    Urine Arsenic: 84.5 ug/L
    Blood Lead: 2.1 ug/dL
    """
    report = LabReportParserEngine.parse_lab_text("PT-GEO-707", sample_text)

    assert report.has_panic_values is True
    as_item = next(i for i in report.items if i.analyte_canonical_name == "urine_arsenic")
    assert as_item.value == 84.5
    assert as_item.is_panic is True
    assert "arsenic toxicity" in as_item.clinical_risk


def test_platelet_lakh_unit_normalization():
    """Verify Indian laboratory platelet representation in lakhs is correctly converted to /uL."""
    sample_text = """
    ROUTINE BLOOD REPORT
    Platelet Count: 1.8 lakh / cumm
    Serum Creatinine: 1.1 mg/dL
    """
    report = LabReportParserEngine.parse_lab_text("PT-LAKH-808", sample_text)

    plt_item = next(i for i in report.items if i.analyte_canonical_name == "platelets")
    assert plt_item.value == 180000.0
    assert plt_item.is_panic is False
