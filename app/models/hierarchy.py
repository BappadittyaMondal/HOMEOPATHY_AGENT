"""
Kentian Symptom Hierarchy Models & Multiplier Constants.
Reflects Kent's philosophy on the evaluation of symptoms for Simillimum determination.
"""
from enum import Enum
from pydantic import BaseModel, Field

class KentHierarchyTier(str, Enum):
    MENTAL_WILL_AFFECTIONS = "MENTAL_WILL_AFFECTIONS"      # 5.0 - Will, Loved/Hated, Delusions, Suicidal/Fears
    MENTAL_INTELLECT = "MENTAL_INTELLECT"                  # 4.0 - Understanding, Memory, Speech
    PHYSICAL_GENERAL_THERMAL = "PHYSICAL_GENERAL_THERMAL"  # 3.5 - Chilly vs Hot patient, Weather modalities
    PHYSICAL_GENERAL_CRAVING = "PHYSICAL_GENERAL_CRAVING"  # 3.0 - Cravings, Aversions, Thirst, Sleep, Sex
    CHARACTERISTIC_PARTICULAR = "CHARACTERISTIC_PARTICULAR"# 2.5 - Complete with Location + Sensation + Modality
    COMMON_PARTICULAR = "COMMON_PARTICULAR"                # 1.0 - Unqualified local pain without modalities

class SymptomHierarchyEvaluation(BaseModel):
    rubric_path: str
    tier: KentHierarchyTier
    canonical_weight: float = Field(..., ge=0.5, le=5.0)
    chapter: str
    justification: str
