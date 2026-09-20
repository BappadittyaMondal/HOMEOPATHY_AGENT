"""
Dispensary Management & 50-Millesimal (LM) Preparation Engine (Phase 46).
Implements active stock bottle tracking, Encounter Dispensing Unit (EDU) deduction,
a 10% gravimetric meniscus/evaporation loss tolerance model, and Organon Aphorism 270 LM liquid preparation protocols.
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class StockBottle(BaseModel):
    bottle_id: str
    remedy_name: str
    potency: str
    initial_volume_ml: float
    current_volume_ml: float
    reorder_threshold_ml: float = 15.0
    evaporation_tolerance_pct: float = 10.0  # 10% gravimetric tolerance

class DispenseTransaction(BaseModel):
    transaction_id: str
    bottle_id: str
    patient_id: str
    edu_units_dispensed: int = 1  # 1 EDU = 0.5 mL
    volume_per_edu_ml: float = 0.5
    is_lm_dilution_bottle: bool = False

class LMPreparationInstruction(BaseModel):
    remedy_name: str
    lm_degree: str  # e.g., "LM 0/1"
    solvent_water_ml: float = 100.0
    preservative_alcohol_ml: float = 5.0
    medicinal_globule_size: str = "Size No. 10 (Poppy-seed size, 1 globule)"
    succussion_directive: str = "10 forceful downward succussions against an elastic body before each tablespoonful dose"
    aphorism_basis: str = "Organon Aphorism 270: The 50-Millesimal (LM/Q) Potency Scale Preparation"

class DispensaryLedgerEngine:
    """
    Manages stock bottle inventory, gravimetric evaporation modeling, and LM preparation protocols.
    """

    _INVENTORY: Dict[str, StockBottle] = {}

    @classmethod
    def register_bottle(cls, bottle: StockBottle) -> None:
        """Registers a new stock bottle into active inventory."""
        cls._INVENTORY[bottle.bottle_id] = bottle

    @classmethod
    def dispense_edu(
        cls,
        transaction: DispenseTransaction
    ) -> Dict:
        """
        Deducts dispensing volume and accounts for gravimetric evaporation.
        """
        bottle = cls._INVENTORY.get(transaction.bottle_id)
        if not bottle:
            raise ValueError(f"Stock bottle {transaction.bottle_id} not found in dispensary inventory.")

        deducted_ml = transaction.edu_units_dispensed * transaction.volume_per_edu_ml
        
        # Check stock sufficiency
        if bottle.current_volume_ml < deducted_ml:
            raise ValueError(
                f"STOCK OUT ERROR: Bottle {bottle.remedy_name} {bottle.potency} has only "
                f"{bottle.current_volume_ml:.1f} mL remaining; cannot dispense {deducted_ml:.1f} mL."
            )

        bottle.current_volume_ml = round(bottle.current_volume_ml - deducted_ml, 2)
        needs_reorder = bottle.current_volume_ml <= bottle.reorder_threshold_ml

        return {
            "transaction_id": transaction.transaction_id,
            "bottle_id": bottle.bottle_id,
            "remedy": bottle.remedy_name,
            "potency": bottle.potency,
            "volume_deducted_ml": deducted_ml,
            "remaining_volume_ml": bottle.current_volume_ml,
            "needs_reorder": needs_reorder
        }

    @classmethod
    def verify_tare_weight(
        cls,
        bottle_id: str,
        actual_measured_volume_ml: float
    ) -> Dict:
        """
        Reconciles measured tare volume against ledger volume within the 10% gravimetric tolerance window.
        """
        bottle = cls._INVENTORY.get(bottle_id)
        if not bottle:
            raise ValueError(f"Bottle {bottle_id} not found.")

        expected = bottle.current_volume_ml
        delta = abs(expected - actual_measured_volume_ml)
        tolerance_ml = (bottle.evaporation_tolerance_pct / 100.0) * bottle.initial_volume_ml

        within_tolerance = delta <= tolerance_ml

        # Update ledger to actual measured volume
        bottle.current_volume_ml = actual_measured_volume_ml

        return {
            "bottle_id": bottle_id,
            "ledger_volume_ml": expected,
            "actual_measured_ml": actual_measured_volume_ml,
            "delta_ml": round(delta, 2),
            "tolerance_limit_ml": round(tolerance_ml, 2),
            "is_gravimetrically_valid": within_tolerance
        }

    @classmethod
    def generate_lm_bottle_protocol(
        cls,
        remedy_name: str,
        lm_degree: str
    ) -> LMPreparationInstruction:
        """
        Generates strict Organon Aphorism 270 preparation directive for 50-Millesimal liquid dose.
        """
        return LMPreparationInstruction(
            remedy_name=remedy_name,
            lm_degree=lm_degree
        )

    @classmethod
    def reset_inventory(cls) -> None:
        """Clears inventory for testing fixtures."""
        cls._INVENTORY.clear()
