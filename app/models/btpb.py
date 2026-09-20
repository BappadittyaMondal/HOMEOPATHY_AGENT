"""
Boenninghausen's Therapeutic Pocket Book (BTPB 1846) Domain Contracts.
Codifies the 7 BTPB sections and Remedy Concordance Index.
"""
from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class BTPBSectionEnum(str, Enum):
    MIND_INTELLECT = "MIND_INTELLECT"
    PARTS_OF_BODY = "PARTS_OF_BODY"
    SENSATIONS = "SENSATIONS"
    SLEEP_DREAMS = "SLEEP_DREAMS"
    FEVER_CHILL = "FEVER_CHILL"
    MODALITIES = "MODALITIES"
    CONCORDANCES = "CONCORDANCES"

class ConcordanceRelationship(BaseModel):
    primary_remedy: str
    related_remedy: str
    total_concordance_score: int = Field(..., ge=0, le=100)
    mind_concordance: int = Field(default=0, ge=0, le=20)
    localities_concordance: int = Field(default=0, ge=0, le=20)
    sensations_concordance: int = Field(default=0, ge=0, le=20)
    modalities_concordance: int = Field(default=0, ge=0, le=20)
    relationship_type: str = Field(default="COMPLEMENTARY") # COMPLEMENTARY, CHRONIC_FOLLOWER, CONCORDANT
