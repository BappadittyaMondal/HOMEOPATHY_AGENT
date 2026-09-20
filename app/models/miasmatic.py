"""
Four-Dimensional Miasmatic Simplex Domain Contracts (Phase 14).
Codifies Psora, Sycosis, Syphilis, and Tubercular miasmatic dynamics.
"""
from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class MiasmTypeEnum(str, Enum):
    PSORA = "PSORA"
    SYCOSIS = "SYCOSIS"
    SYPHILIS = "SYPHILIS"
    TUBERCULAR = "TUBERCULAR"

class MiasmaticSimplexVector(BaseModel):
    psora: float = Field(..., ge=0.0, le=1.0)
    sycosis: float = Field(..., ge=0.0, le=1.0)
    syphilis: float = Field(..., ge=0.0, le=1.0)
    tubercular: float = Field(..., ge=0.0, le=1.0)
    dominant_miasm: MiasmTypeEnum
    is_normalized: bool = True

class RemedyMiasmaticProfile(BaseModel):
    remedy_name: str
    miasm_vector: MiasmaticSimplexVector
    primary_affinity: MiasmTypeEnum
