"""
Dynamic Posology & Potency Selection Calculus Domain Contracts (Phase 16).
Codifies Centesimal (C), Decimal (X), and 50-Millesimal (LM/Q) posology schedules.
"""
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional

class PotencyScaleEnum(str, Enum):
    CENTESIMAL = "CENTESIMAL"       # 30C, 200C, 1M, 10M
    FIFTY_MILLESIMAL = "50_MILLESIMAL" # LM 0/1 to LM 0/30 (Aphorisms 246-248)
    DECIMAL = "DECIMAL"             # 3X, 6X, 12X
    MOTHER_TINCTURE = "MOTHER_TINCTURE" # Q

class PosologyVehicleEnum(str, Enum):
    SUCCUSSED_AQUEOUS_SOLUTION = "SUCCUSSED_AQUEOUS_SOLUTION"
    CANE_SUGAR_GLOBULES_NO_30 = "CANE_SUGAR_GLOBULES_NO_30"
    CANE_SUGAR_GLOBULES_NO_20 = "CANE_SUGAR_GLOBULES_NO_20"
    SACCHARUM_LACTIS_POWDER = "SACCHARUM_LACTIS_POWDER"
    DISTILLED_WATER_DROPS = "DISTILLED_WATER_DROPS"

class PrescribedPosologyProtocol(BaseModel):
    remedy_name: str
    scale: PotencyScaleEnum
    potency_grade: str              # e.g. "LM 0/1", "200C", "30C", "6X"
    vehicle: PosologyVehicleEnum
    administration_schedule: str    # Exact dosing instructions
    placebo_sac_lac_schedule: str   # Placebo instructions
    aphorism_reference: str
    rationale: str
