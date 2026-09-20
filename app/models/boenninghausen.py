"""
Boenninghausen Complete Symptom & Grand Generalization Domain Contracts.
Codifies the 4-part symptom anatomy: Location, Sensation, Modality, and Concomitant (LSMC).
"""
from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional

class PolarAxisEnum(str, Enum):
    THERMAL = "THERMAL"       # Heat vs Cold
    MOTION = "MOTION"         # Motion vs Rest
    PRESSURE = "PRESSURE"     # Hard Pressure vs Light Touch
    TEMPORAL = "TEMPORAL"     # Day vs Night, Specific hours
    POSITION = "POSITION"     # Lying vs Standing vs Sitting
    WEATHER = "WEATHER"       # Dry vs Wet / Stormy

class BoenninghausenModality(BaseModel):
    trigger: str
    is_aggravation: bool     # True = < (agg.), False = > (amel.)
    polar_axis: PolarAxisEnum
    intensity_grade: int = Field(default=3, ge=1, le=4)

class BoenninghausenParsedSymptom(BaseModel):
    symptom_id: str
    original_text: str
    location: Optional[str] = None
    sensation: Optional[str] = None
    modalities: List[BoenninghausenModality] = Field(default_factory=list)
    concomitants: List[str] = Field(default_factory=list)
    completeness_score: float = Field(..., ge=0.0, le=1.0, description="1.0 = All 4 elements present")
    is_fully_qualified: bool
    grand_generalization_eligible: bool = Field(default=False)
