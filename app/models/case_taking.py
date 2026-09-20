"""
Hahnemannian Case-Taking & Semantic Symptom Anatomy Domain Contracts (Aphorisms 83-104).
Defines Location, Sensation, Modality, Concomitant (LSMC) and Bounded Human-in-the-Loop verification gates.
"""
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field
import uuid

class ModalityPolarityEnum(str, Enum):
    AGGRAVATION = "AGGRAVATION"  # < Worsened by
    AMELIORATION = "AMELIORATION"  # > Relieved by

class SymptomCategoryEnum(str, Enum):
    MENTAL_GENERAL = "MENTAL_GENERAL"
    PHYSICAL_GENERAL = "PHYSICAL_GENERAL"
    CHARACTERISTIC_PARTICULAR = "CHARACTERISTIC_PARTICULAR"
    COMMON_PARTICULAR = "COMMON_PARTICULAR"

class VerificationStatusEnum(str, Enum):
    PENDING_REVIEW = "PENDING_REVIEW"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    MODIFIED = "MODIFIED"

class ModalityDetail(BaseModel):
    trigger: str = Field(..., description="e.g. cold air, movement, midnight, warm drinks")
    polarity: ModalityPolarityEnum
    context: Optional[str] = None  # e.g., thermal, temporal, motion, physiological

class CompleteSymptom(BaseModel):
    symptom_id: str = Field(default_factory=lambda: f"SYM-{uuid.uuid4().hex[:8].upper()}")
    raw_source_text: str
    location: str = Field(..., description="Anatomical site, side of body, tissue affinity")
    sensation: str = Field(..., description="Quality: stitching, burning, throbbing, cramping, etc.")
    modalities: List[ModalityDetail] = Field(default_factory=list)
    concomitants: List[str] = Field(default_factory=list)
    category: SymptomCategoryEnum
    is_srp: bool = Field(default=False, description="Strange, Rare, and Peculiar (Aphorism 153)")

class CandidateRubricMatch(BaseModel):
    candidate_id: str = Field(default_factory=lambda: f"CAN-{uuid.uuid4().hex[:8].upper()}")
    symptom_id: str
    source_phrase: str
    proposed_rubric_path: str = Field(..., description="Standardized Repertorial Path e.g. HEAD - PAIN - right")
    repertory_source: str = Field(default="KENT", description="KENT, BTPB, BBCR")
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    hierarchical_weight: float = Field(default=1.0, ge=0.5, le=5.0)
    status: VerificationStatusEnum = Field(default=VerificationStatusEnum.PENDING_REVIEW)
    clinician_notes: Optional[str] = None

class CaseTakingNarrativeInput(BaseModel):
    encounter_id: str
    patient_id: str
    narrative_text: str = Field(..., min_length=10, max_length=10000, description="Full patient narrative")
    caregiver_account: Optional[str] = None
    physician_observations: Optional[str] = None

class CaseTakingExtractionResult(BaseModel):
    encounter_id: str
    patient_id: str
    complete_symptoms: List[CompleteSymptom]
    candidate_rubrics: List[CandidateRubricMatch]
    total_extracted: int
    pending_verification_count: int

class RubricVerificationDecision(BaseModel):
    candidate_id: str
    decision: VerificationStatusEnum  # ACCEPTED, REJECTED, MODIFIED
    modified_rubric_path: Optional[str] = None
    clinician_id: str
    rejection_reason: Optional[str] = None

class BatchVerificationRequest(BaseModel):
    encounter_id: str
    decisions: List[RubricVerificationDecision]
