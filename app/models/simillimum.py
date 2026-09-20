"""
Simillimum Ranking & Differential Matrix Domain Contracts (Phase 12).
Codifies the Composite Repertorial Rank (CRR) and multi-column differential output.
"""
from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional

class RemedySimillimumStatus(str, Enum):
    PRIMARY_SIMILLIMUM = "PRIMARY_SIMILLIMUM"
    SECONDARY_DIFFERENTIAL = "SECONDARY_DIFFERENTIAL"
    CONSIDERATION = "CONSIDERATION"
    RULED_OUT = "RULED_OUT"

class RankedRemedyCandidate(BaseModel):
    rank: int
    remedy_name: str
    composite_score: float = Field(..., ge=0.0, le=100.0)
    density_score: float = Field(..., ge=0.0, le=100.0)
    breadth_score: float = Field(..., ge=0.0, le=100.0)
    mental_coverage_percent: float = Field(..., ge=0.0, le=100.0)
    total_rubrics_covered: int
    patient_rubrics_total: int
    status: RemedySimillimumStatus
    clinical_notes: Optional[str] = None

class SimillimumEvaluationReport(BaseModel):
    encounter_id: str
    patient_id: str
    primary_simillimum: str
    top_candidates: List[RankedRemedyCandidate]
    total_evaluated: int
    execution_latency_ms: float
