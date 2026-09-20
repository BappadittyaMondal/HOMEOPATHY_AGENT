"""
Unit Tests for Phase 46: Dispensary Management & LM Preparation Engine.
"""
from app.dispensary.stock_ledger import (
    DispensaryLedgerEngine,
    StockBottle,
    DispenseTransaction
)

def setup_function():
    DispensaryLedgerEngine.reset_inventory()

def test_dispense_edu_and_reorder_threshold():
    """Verify stock deduction by Encounter Dispensing Unit (EDU) and reorder alerts."""
    bottle = StockBottle(
        bottle_id="BOT-SULPH-200C",
        remedy_name="Sulphur",
        potency="200C",
        initial_volume_ml=100.0,
        current_volume_ml=16.0,
        reorder_threshold_ml=15.0
    )
    DispensaryLedgerEngine.register_bottle(bottle)

    # Dispense 2 EDUs (2 * 0.5 mL = 1.0 mL) -> 16.0 - 1.0 = 15.0 mL
    tx = DispenseTransaction(
        transaction_id="TX-001",
        bottle_id="BOT-SULPH-200C",
        patient_id="PT-001",
        edu_units_dispensed=2,
        volume_per_edu_ml=0.5
    )
    res = DispensaryLedgerEngine.dispense_edu(tx)
    assert res["volume_deducted_ml"] == 1.0
    assert res["remaining_volume_ml"] == 15.0
    assert res["needs_reorder"] is True  # Exactly at threshold

def test_gravimetric_tare_weight_reconciliation():
    """Verify 10% gravimetric meniscus/evaporation tolerance model."""
    bottle = StockBottle(
        bottle_id="BOT-ACON-30C",
        remedy_name="Aconitum napellus",
        potency="30C",
        initial_volume_ml=100.0,
        current_volume_ml=80.0,
        evaporation_tolerance_pct=10.0  # 10 mL tolerance
    )
    DispensaryLedgerEngine.register_bottle(bottle)

    # Actual measured 75.0 mL (delta 5.0 mL, within 10.0 mL tolerance)
    res = DispensaryLedgerEngine.verify_tare_weight("BOT-ACON-30C", actual_measured_volume_ml=75.0)
    assert res["is_gravimetrically_valid"] is True
    assert res["delta_ml"] == 5.0

    # Actual measured 60.0 mL (delta 15.0 mL, exceeds 10.0 mL tolerance)
    res_exceed = DispensaryLedgerEngine.verify_tare_weight("BOT-ACON-30C", actual_measured_volume_ml=60.0)
    assert res_exceed["is_gravimetrically_valid"] is False

def test_lm_preparation_instruction():
    """Verify Aphorism 270 50-Millesimal preparation directive."""
    proto = DispensaryLedgerEngine.generate_lm_bottle_protocol(
        remedy_name="Lycopodium clavatum",
        lm_degree="LM 0/1"
    )
    assert proto.remedy_name == "Lycopodium clavatum"
    assert proto.lm_degree == "LM 0/1"
    assert proto.solvent_water_ml == 100.0
    assert "Aphorism 270" in proto.aphorism_basis
