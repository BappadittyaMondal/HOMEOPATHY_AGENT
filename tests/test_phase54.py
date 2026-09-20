"""
Tests for Phase 54: Dispensary Physical Verification, Batch/Expiry Tracking & ADR Severity Re-ordering.
Validates INV-07 (Dispensary Physical Match) and INV-08 (ADR Severity-First Ordering).
"""
import pytest
from app.dispensary.stock_ledger import (
    DispensaryLedgerEngine,
    StockBottle,
    DispenseTransaction,
    DispensingMismatchException,
    BottleQuarantinedException
)
from app.governance.pharmacovigilance import (
    PharmacovigilanceEngine,
    ADRReport,
    ADRSurveillanceResult
)


def setup_function():
    DispensaryLedgerEngine.reset_inventory()
    PharmacovigilanceEngine.reset_surveillance()


def test_inv_07_dispensary_remedy_mismatch_raises_exception():
    """
    INV-07: Attempting to dispense Sulphur from a Rhus tox bottle
    must raise DispensingMismatchException and prevent stock deduction.
    """
    bottle = StockBottle(
        bottle_id="BOT-RHUS-200C",
        remedy_name="Rhus toxicodendron",
        potency="200C",
        initial_volume_ml=100.0,
        current_volume_ml=50.0,
        batch_number="BATCH-RHUS-01"
    )
    DispensaryLedgerEngine.register_bottle(bottle)

    tx = DispenseTransaction(
        transaction_id="TX-MISMATCH-01",
        bottle_id="BOT-RHUS-200C",
        patient_id="PAT-001",
        expected_remedy_name="Sulphur",  # Mismatch! Prescribed Sulphur, bottle is Rhus tox
        expected_potency="200C"
    )

    with pytest.raises(DispensingMismatchException) as exc_info:
        DispensaryLedgerEngine.dispense_edu(tx)
    assert "DISPENSARY MISMATCH" in str(exc_info.value)
    assert bottle.current_volume_ml == 50.0  # Volume unchanged


def test_inv_07_dispensary_potency_mismatch_raises_exception():
    """
    INV-07: Attempting to dispense 30C from a 1M bottle of the same remedy
    must raise DispensingMismatchException.
    """
    bottle = StockBottle(
        bottle_id="BOT-ARN-1M",
        remedy_name="Arnica montana",
        potency="1M",
        initial_volume_ml=100.0,
        current_volume_ml=50.0,
        batch_number="BATCH-ARN-01"
    )
    DispensaryLedgerEngine.register_bottle(bottle)

    tx = DispenseTransaction(
        transaction_id="TX-MISMATCH-02",
        bottle_id="BOT-ARN-1M",
        patient_id="PAT-002",
        expected_remedy_name="Arnica montana",
        expected_potency="30C"  # Mismatch! Prescribed 30C, bottle is 1M
    )

    with pytest.raises(DispensingMismatchException) as exc_info:
        DispensaryLedgerEngine.dispense_edu(tx)
    assert "potency" in str(exc_info.value).lower()
    assert bottle.current_volume_ml == 50.0


def test_inv_07_quarantined_bottle_raises_exception():
    """
    INV-07: Attempting to dispense from a quarantined stock bottle
    must raise BottleQuarantinedException.
    """
    bottle = StockBottle(
        bottle_id="BOT-CONTAM-01",
        remedy_name="Belladonna",
        potency="30C",
        initial_volume_ml=100.0,
        current_volume_ml=50.0,
        batch_number="BATCH-CONTAM-99",
        status="QUARANTINED",
        is_quarantined=True
    )
    DispensaryLedgerEngine.register_bottle(bottle)

    tx = DispenseTransaction(
        transaction_id="TX-QUAR-01",
        bottle_id="BOT-CONTAM-01",
        patient_id="PAT-003",
        expected_remedy_name="Belladonna",
        expected_potency="30C"
    )

    with pytest.raises(BottleQuarantinedException) as exc_info:
        DispensaryLedgerEngine.dispense_edu(tx)
    assert "QUARANTINE" in str(exc_info.value)


def test_inv_08_adr_severity_first_ordering():
    """
    INV-08: Grade 4 life-threatening reaction with reported vitality improvement
    must NOT be classified as curative aggravation. It MUST trigger confirmed ADR and quarantine.
    """
    report = ADRReport(
        report_id="ADR-INV08-01",
        patient_id="PAT-TOXIC-01",
        remedy_name="Arsenicum album",
        potency="30C",
        batch_number="BATCH-ARS-HAZARD-01",
        manufacturer="Ayush Pharma",
        reaction_symptoms=["severe tachycardia", "cardiac arrhythmia", "acute mucosal ulceration"],
        is_general_vitality_improved=True,  # Flawed subjective observation
        are_symptoms_new=False,             # Existing symptom worsened catastrophically
        severity_grade=4                    # Severe Grade 4 event
    )
    res = PharmacovigilanceEngine.process_adr_report(report)
    assert res.classification == "ADVERSE_DRUG_REACTION_CONFIRMED"
    assert res.action_required == "ISOLATE_AND_QUARANTINE_BATCH"
    assert res.requires_batch_quarantine is True
    assert PharmacovigilanceEngine.is_batch_quarantined("BATCH-ARS-HAZARD-01") is True


def test_matching_dispense_succeeds():
    """Valid transaction with matching remedy and potency dispenses smoothly."""
    bottle = StockBottle(
        bottle_id="BOT-NUX-30C",
        remedy_name="Nux vomica",
        potency="30C",
        initial_volume_ml=100.0,
        current_volume_ml=50.0,
        batch_number="BATCH-NUX-01"
    )
    DispensaryLedgerEngine.register_bottle(bottle)

    tx = DispenseTransaction(
        transaction_id="TX-VALID-01",
        bottle_id="BOT-NUX-30C",
        patient_id="PAT-004",
        expected_remedy_name="Nux vomica",
        expected_potency="30C",
        edu_units_dispensed=1,
        volume_per_edu_ml=0.5
    )
    res = DispensaryLedgerEngine.dispense_edu(tx)
    assert res["volume_deducted_ml"] == 0.5
    assert res["remaining_volume_ml"] == 49.5
