"""
Case Taking and Bounded Human-in-the-Loop Rubric Verification Endpoints.
Prevents probabilistic hallucination by enforcing mandatory clinician review of all extracted rubrics.
"""
from fastapi import APIRouter, HTTPException, status
from app.models.case_taking import (
    CaseTakingNarrativeInput,
    CaseTakingExtractionResult,
    BatchVerificationRequest,
    CandidateRubricMatch,
    VerificationStatusEnum
)
from app.repertory.case_parser import HahnemannCaseParser
from typing import Dict, List

router = APIRouter(prefix="/case-taking", tags=["Case Taking & Rubric Verification (Aphorisms 83-104)"])

# In-memory transient candidate store (persisted to SQLite once verified)
_ENCOUNTER_CANDIDATES_CACHE: Dict[str, List[CandidateRubricMatch]] = {}

@router.post("/extract", response_model=CaseTakingExtractionResult, status_code=status.HTTP_200_OK)
async def extract_symptoms_from_narrative(payload: CaseTakingNarrativeInput):
    """
    Parses unstructured patient and caregiver narratives into LSMC symptom structures.
    Every rubric is returned with status 'PENDING_REVIEW'.
    """
    combined_text = payload.narrative_text
    if payload.caregiver_account:
        combined_text += f"\nCaregiver Observations: {payload.caregiver_account}"
    if payload.physician_observations:
        combined_text += f"\nPhysician Observations: {payload.physician_observations}"

    result = HahnemannCaseParser.parse_narrative(
        encounter_id=payload.encounter_id,
        patient_id=payload.patient_id,
        text=combined_text
    )
    
    # Store candidates in cache pending clinician confirmation
    _ENCOUNTER_CANDIDATES_CACHE[payload.encounter_id] = result.candidate_rubrics
    return result

@router.post("/verify", status_code=status.HTTP_200_OK)
async def verify_candidate_rubrics(payload: BatchVerificationRequest):
    """
    Bounded Human-in-the-Loop Gate.
    The Registered Medical Practitioner (RMP) explicitly accepts, rejects, or modifies each rubric.
    Only ACCEPTED rubrics are authorized to enter the mathematical repertorization engine.
    """
    candidates = _ENCOUNTER_CANDIDATES_CACHE.get(payload.encounter_id)
    if not candidates:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No pending candidate rubrics found for encounter {payload.encounter_id}. Submit narrative extraction first."
        )

    decision_map = {d.candidate_id: d for d in payload.decisions}
    verified_rubrics = []
    
    for candidate in candidates:
        if candidate.candidate_id in decision_map:
            dec = decision_map[candidate.candidate_id]
            candidate.status = dec.decision
            if dec.decision == VerificationStatusEnum.MODIFIED and dec.modified_rubric_path:
                candidate.proposed_rubric_path = dec.modified_rubric_path
            if dec.rejection_reason:
                candidate.clinician_notes = dec.rejection_reason
            
            if candidate.status in (VerificationStatusEnum.ACCEPTED, VerificationStatusEnum.MODIFIED):
                verified_rubrics.append(candidate)

    return {
        "encounter_id": payload.encounter_id,
        "total_processed": len(payload.decisions),
        "accepted_count": len(verified_rubrics),
        "rejected_count": len([c for c in candidates if c.status == VerificationStatusEnum.REJECTED]),
        "verified_rubrics_for_repertorization": verified_rubrics
    }

@router.get("/candidates/{encounter_id}", response_model=List[CandidateRubricMatch])
async def get_encounter_candidates(encounter_id: str):
    """Retrieves current rubric candidates and their verification state."""
    candidates = _ENCOUNTER_CANDIDATES_CACHE.get(encounter_id)
    if candidates is None:
        raise HTTPException(status_code=404, detail="Encounter not found or no extraction performed.")
    return candidates
