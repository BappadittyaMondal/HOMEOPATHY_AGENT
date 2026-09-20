"""
Longitudinal Homeopathic EHR & Multi-Tenant Timeline Domain Contracts (Phase 41).
"""
from typing import List, Optional
from pydantic import BaseModel, Field

class EHRClinicalEncounter(BaseModel):
    encounter_id: str
    patient_id: str
    tenant_id: str
    encounter_date: str
    chief_complaint: str
    rubrics_selected: List[str]
    remedy_prescribed: str
    potency: str
    kent_observation_num: Optional[int] = None
    vitality_score: float = Field(..., ge=1.0, le=10.0)
    dominant_miasm: str  # "PSORA", "SYCOSIS", "SYPHILIS", "TUBERCULAR"

class LongitudinalPatientTrajectory(BaseModel):
    patient_id: str
    tenant_id: str
    total_encounters: int
    encounters: List[EHRClinicalEncounter]
    vitality_trend: List[float]
    remedy_history: List[str]
    is_vitality_improving: bool
    summary_verdict: str
