"""
Susceptibility, Vital Force & Constitutional Tone Domain Contracts (Phase 15).
Calculates posology scaling factor (sigma) for dynamic potency assignment.
"""
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional

class ConstitutionTemperamentEnum(str, Enum):
    NERVOUS_INTELLECTUAL = "NERVOUS_INTELLECTUAL"
    SANGUINE_ACTIVE = "SANGUINE_ACTIVE"
    BILIOUS_CHOLERIC = "BILIOUS_CHOLERIC"
    PHLEGMATIC_TORPID = "PHLEGMATIC_TORPID"
    DEBILITATED_EXHAUSTED = "DEBILITATED_EXHAUSTED"

class PatientVitalityAssessment(BaseModel):
    susceptibility_score: float = Field(..., ge=1.0, le=10.0, description="1=Torpid, 10=Extreme Hypersensitive")
    vital_force_score: float = Field(..., ge=1.0, le=10.0, description="1=Exhausted, 10=Robust Vitality")
    pathological_depth: int = Field(..., ge=0, le=5, description="0=Dynamic/Functional, 5=Irreversible Necrosis")
    temperament: ConstitutionTemperamentEnum
    is_suppressed_by_allopathy: bool = False
    posology_scaling_factor: float = Field(..., description="sigma = (S * V) / (Delta_T + 1.0)")
    clinical_recommendation: str
