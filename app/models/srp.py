"""
Strange, Rare, and Peculiar (SRP - Aphorism 153) Domain Contracts.
Codifies pathognomonic paradoxes and characteristic clinical indicators.
"""
from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional

class SRPParadoxType(str, Enum):
    THERMAL_MODALITY_PARADOX = "THERMAL_MODALITY_PARADOX"       # e.g. Burning pain relieved by heat (Ars)
    THIRST_FEVER_PARADOX = "THIRST_FEVER_PARADOX"               # e.g. High fever with no thirst (Apis, Puls)
    PHYSIOLOGICAL_CONTRADICTION = "PHYSIOLOGICAL_CONTRADICTION" # e.g. Throat pain amel swallowing solids (Ign)
    METABOLIC_PARADOX = "METABOLIC_PARADOX"                     # e.g. Emaciation despite canine hunger (Iod, Nat-m)
    MOTION_POSTURE_PARADOX = "MOTION_POSTURE_PARADOX"           # e.g. Fear of downward motion (Borax)
    EMOTIONAL_PARADOX = "EMOTIONAL_PARADOX"                     # e.g. Weeping from music (Graphites, Nat-c)

class SRPEvaluationResult(BaseModel):
    symptom_text: str
    is_srp: bool
    paradox_type: Optional[SRPParadoxType] = None
    canonical_rubric: Optional[str] = None
    aphorism_153_weight: float = Field(default=1.0, ge=1.0, le=5.0)
    characteristic_remedies: List[str] = Field(default_factory=list)
    clinical_rationale: str
