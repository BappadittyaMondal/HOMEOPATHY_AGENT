"""
Boenninghausen Polarity Analysis Domain Contracts (Phase 13).
Codifies Polar Opposites, Polarity Difference (ΔP), and Contraindication Index (CI).
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class PolarPairDefinition(BaseModel):
    pair_id: str
    axis_name: str
    positive_rubric: str   # e.g., GENERALITIES - COLD - agg.
    negative_rubric: str   # e.g., GENERALITIES - WARMTH - agg.

class RemedyPolarityEvaluation(BaseModel):
    remedy_name: str
    polarity_difference: int = Field(..., description="ΔP = sum(P+) - sum(P-)")
    contraindication_index: int = Field(..., description="CI = sum of opposite grades >= 3")
    is_contraindicated: bool
    contraindicated_rubrics: List[str] = Field(default_factory=list)
    adjusted_penalty_factor: float = Field(..., ge=0.0, le=1.0)
