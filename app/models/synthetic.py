"""
Modern Synthetic Repertory & Pluggable Dataset Domain Contracts (Phase 10).
Enforces clean-room IP licensing and standardized ingestion schemas.
"""
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class ExternalRubricPayload(BaseModel):
    rubric_path: str = Field(..., description="e.g. CLINICAL - FIBROMYALGIA - general")
    chapter: str
    remedies_with_grades: Dict[str, int] = Field(..., description="Remedy abbreviation -> Grade 1..4")
    author_source: str = Field(..., description="e.g. Synthesis, Murphy, Complete, or Academic Proving")
    cross_references: List[str] = Field(default_factory=list)

class SyntheticDatasetManifest(BaseModel):
    dataset_name: str
    version: str
    license_key: str
    authorized_institution: str
    total_rubrics: int
    rubrics: List[ExternalRubricPayload]

class IngestionResult(BaseModel):
    status: str
    dataset_name: str
    rubrics_imported: int
    new_remedies_added: int
    errors: List[str] = Field(default_factory=list)
