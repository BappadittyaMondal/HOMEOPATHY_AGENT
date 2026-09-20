"""
Unit Tests for Phase 47: Pharmacovigilance & ADR Surveillance System.
"""
from app.governance.pharmacovigilance import PharmacovigilanceEngine, ADRReport

def setup_function():
    PharmacovigilanceEngine.reset_surveillance()

def test_pharmacovigilance_curative_aggravation():
    """Verify classification of expected curative homeopathic aggravation."""
    report = ADRReport(
        report_id="ADR-001",
        patient_id="PT-10",
        remedy_name="Sulphur",
        potency="200C",
        batch_number="BATCH-SULPH-2026",
        manufacturer="HPI Certified Lab",
        reaction_symptoms=["skin itching slightly intensified for 24 hours"],
        is_general_vitality_improved=True,
        are_symptoms_new=False,
        severity_grade=1
    )
    res = PharmacovigilanceEngine.process_adr_report(report)
    assert res.classification == "CURATIVE_HOMEOPATHIC_AGGRAVATION"
    assert res.action_required == "SAC_LAC_WAIT"
    assert PharmacovigilanceEngine.is_batch_quarantined("BATCH-SULPH-2026") is False

def test_pharmacovigilance_confirmed_adr_quarantine():
    """Verify batch quarantine when true adverse reaction or toxic contamination occurs."""
    report = ADRReport(
        report_id="ADR-002",
        patient_id="PT-20",
        remedy_name="Aconitum napellus Q",
        potency="Q",
        batch_number="BATCH-TOXIC-ACON-99",
        manufacturer="Dubious Supplier",
        reaction_symptoms=["acute cardiac arrhythmia", "numbness of tongue", "vomiting"],
        is_general_vitality_improved=False,
        are_symptoms_new=True,
        severity_grade=4
    )
    res = PharmacovigilanceEngine.process_adr_report(report)
    assert res.classification == "ADVERSE_DRUG_REACTION_CONFIRMED"
    assert res.action_required == "ISOLATE_AND_QUARANTINE_BATCH"
    assert "IMMEDIATE QUARANTINE" in res.regulatory_notice
    assert PharmacovigilanceEngine.is_batch_quarantined("BATCH-TOXIC-ACON-99") is True
