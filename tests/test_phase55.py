"""
Tests for Phase 55: True Database Persistence for Milestone 5 Stores (SQLite WAL Hardening).
Validates INV-09 (Durability of Audit Ledger, Dispensary Inventory, and EHR Encounters).
"""
import pytest
from app.governance.nabh_audit import NABHAuditLedger, NABHAuditEntry
from app.dispensary.stock_ledger import DispensaryLedgerEngine, StockBottle, DispenseTransaction
from app.clinical.longitudinal_ehr import LongitudinalEHREngine, EHRClinicalEncounter
from app.core.database import db


def setup_function():
    NABHAuditLedger.reset_chain()
    DispensaryLedgerEngine.reset_inventory()
    LongitudinalEHREngine.reset_store()


def test_inv_09_audit_ledger_persists_across_memory_resets():
    """
    INV-09: Append log entries to NABHAuditLedger, wipe class memory (_CHAIN),
    reload from SQLite database, and assert chain integrity and hashes match.
    """
    e1 = NABHAuditLedger.append_log(
        log_id="LOG-PERSIST-01",
        timestamp="2026-09-20T12:00:00Z",
        actor_id="DR-PERSIST-101",
        action_type="PRESCRIPTION_ISSUED",
        details={"remedy": "Lycopodium", "potency": "LM 0/1"},
        patient_id="PT-PERSIST-001"
    )
    e2 = NABHAuditLedger.append_log(
        log_id="LOG-PERSIST-02",
        timestamp="2026-09-20T12:05:00Z",
        actor_id="DR-PERSIST-101",
        action_type="DISPENSED",
        details={"volume_ml": "0.5"},
        patient_id="PT-PERSIST-001"
    )

    # Wipe in-memory list ONLY (simulating server restart)
    NABHAuditLedger._CHAIN.clear()
    assert len(NABHAuditLedger.get_chain()) == 0

    # Reload from SQLite database
    reloaded = NABHAuditLedger.reload_from_database()
    assert len(reloaded) == 2
    assert reloaded[0].log_id == "LOG-PERSIST-01"
    assert reloaded[1].log_id == "LOG-PERSIST-02"
    assert reloaded[1].previous_hash == reloaded[0].current_hash
    assert NABHAuditLedger.verify_chain_integrity() is True


def test_inv_09_dispensary_stock_persists_across_memory_resets():
    """
    INV-09: Register a bottle and dispense volume, wipe class memory (_INVENTORY),
    reload from SQLite database, and assert updated volume is preserved.
    """
    bottle = StockBottle(
        bottle_id="BOT-PERSIST-SULPH-30C",
        remedy_name="Sulphur",
        potency="30C",
        initial_volume_ml=100.0,
        current_volume_ml=100.0,
        batch_number="BATCH-WAL-01"
    )
    DispensaryLedgerEngine.register_bottle(bottle)

    # Dispense 2 EDUs (1.0 mL) -> 99.0 mL remaining
    tx = DispenseTransaction(
        transaction_id="TX-PERSIST-01",
        bottle_id="BOT-PERSIST-SULPH-30C",
        patient_id="PT-PERSIST-002",
        edu_units_dispensed=2,
        volume_per_edu_ml=0.5,
        expected_remedy_name="Sulphur",
        expected_potency="30C"
    )
    DispensaryLedgerEngine.dispense_edu(tx)

    # Wipe in-memory dictionary
    DispensaryLedgerEngine._INVENTORY.clear()
    assert len(DispensaryLedgerEngine._INVENTORY) == 0

    # Reload from SQLite database
    reloaded = DispensaryLedgerEngine.reload_from_database()
    assert "BOT-PERSIST-SULPH-30C" in reloaded
    restored_bottle = reloaded["BOT-PERSIST-SULPH-30C"]
    assert restored_bottle.current_volume_ml == 99.0
    assert restored_bottle.batch_number == "BATCH-WAL-01"


def test_inv_09_ehr_encounter_persists_across_memory_resets():
    """
    INV-09: Record clinical encounter, wipe class memory (_TENANT_STORES),
    reload from SQLite database, and assert trajectory recalculation succeeds.
    """
    enc = EHRClinicalEncounter(
        encounter_id="ENC-PERSIST-01",
        patient_id="PT-PERSIST-003",
        tenant_id="TENANT-MUMBAI",
        encounter_date="2026-09-20",
        chief_complaint="Allergic Rhinitis",
        rubrics_selected=["Nose - Coryza - fluent"],
        remedy_prescribed="Allium cepa",
        potency="30C",
        vitality_score=7.5,
        dominant_miasm="PSORA"
    )
    LongitudinalEHREngine.record_encounter(enc)

    # Wipe in-memory dictionary
    LongitudinalEHREngine._TENANT_STORES.clear()
    assert LongitudinalEHREngine.get_patient_trajectory("TENANT-MUMBAI", "PT-PERSIST-003") is None

    # Reload from SQLite database
    restored = LongitudinalEHREngine.reload_from_database("TENANT-MUMBAI", "PT-PERSIST-003")
    assert len(restored) == 1
    assert restored[0].encounter_id == "ENC-PERSIST-01"
    assert restored[0].remedy_prescribed == "Allium cepa"

    traj = LongitudinalEHREngine.get_patient_trajectory("TENANT-MUMBAI", "PT-PERSIST-003")
    assert traj is not None
    assert traj.total_encounters == 1
