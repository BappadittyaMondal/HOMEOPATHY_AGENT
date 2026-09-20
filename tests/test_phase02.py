"""
Unit & Integration Tests for Phase 02: Hahnemannian Case-Taking & Human-in-the-Loop Rubric Verification.
"""
import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.repertory.case_parser import HahnemannCaseParser
from app.models.case_taking import ModalityPolarityEnum, SymptomCategoryEnum, VerificationStatusEnum

def test_hahnemann_parser_mental_and_lsmc():
    """Verify parsing of mental generals and complete LSMC particular symptoms."""
    narrative = """
    Patient reports severe anxiety about health and weeping mood since the loss of a parent.
    Complains of throbbing headache in forehead, worse from light, better from tight bandage.
    Also has burning pain in stomach, aggravated by cold drinks.
    """
    result = HahnemannCaseParser.parse_narrative(
        encounter_id="ENC-TEST-001",
        patient_id="PAT-TEST-001",
        text=narrative
    )

    assert result.total_extracted > 0
    assert result.pending_verification_count == result.total_extracted
    
    # 1. Verify Mental Generals were extracted and prioritized
    mental_candidates = [
        c for c in result.candidate_rubrics 
        if c.proposed_rubric_path.startswith("MIND")
    ]
    assert len(mental_candidates) >= 2, "Expected anxiety and weeping to be captured in MIND chapter"
    for mc in mental_candidates:
        assert mc.hierarchical_weight >= 4.0
        assert mc.status == VerificationStatusEnum.PENDING_REVIEW

    # 2. Verify Particular LSMC symptom
    head_candidates = [
        c for c in result.candidate_rubrics 
        if "HEAD" in c.proposed_rubric_path
    ]
    assert len(head_candidates) >= 1
    
    # Check for SRP flag on tight bandage relief
    srp_symptoms = [s for s in result.complete_symptoms if s.is_srp]
    assert len(srp_symptoms) >= 1, "Expected relief from tight bandage to be flagged as SRP (Aphorism 153)"

def test_api_case_taking_extraction_and_verification_pipeline():
    """Verify the end-to-end API pipeline from narrative ingestion to clinician verification."""
    async def _test():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            payload = {
                "encounter_id": "ENC-API-002",
                "patient_id": "PAT-API-002",
                "narrative_text": "I feel very restless at night. My right knee has stitching pain, worse from initial movement, better continuing to walk.",
                "caregiver_account": "Patient cannot sleep peacefully, tossing and turning.",
                "physician_observations": "Patient looks anxious, frequently shifting posture."
            }

            # 1. Ingest narrative
            res_extract = await ac.post("/api/v1/case-taking/extract", json=payload)
            assert res_extract.status_code == 200
            data_extract = res_extract.json()
            assert data_extract["encounter_id"] == "ENC-API-002"
            candidates = data_extract["candidate_rubrics"]
            assert len(candidates) > 0

            # 2. Retrieve candidates from endpoint
            res_cand = await ac.get(f"/api/v1/case-taking/candidates/ENC-API-002")
            assert res_cand.status_code == 200
            assert len(res_cand.json()) == len(candidates)

            # 3. Clinician executes bounded Human-in-the-Loop review:
            # Accept first, Reject second (if present), Modify third (if present)
            c1_id = candidates[0]["candidate_id"]
            decisions = [
                {
                    "candidate_id": c1_id,
                    "decision": "ACCEPTED",
                    "clinician_id": "DOC-KOLKATA-01"
                }
            ]
            if len(candidates) > 1:
                decisions.append({
                    "candidate_id": candidates[1]["candidate_id"],
                    "decision": "REJECTED",
                    "clinician_id": "DOC-KOLKATA-01",
                    "rejection_reason": "Non-characteristic common symptom"
                })

            verify_payload = {
                "encounter_id": "ENC-API-002",
                "decisions": decisions
            }
            res_verify = await ac.post("/api/v1/case-taking/verify", json=verify_payload)
            assert res_verify.status_code == 200
            verify_data = res_verify.json()
            assert verify_data["accepted_count"] >= 1
            assert len(verify_data["verified_rubrics_for_repertorization"]) >= 1
            assert verify_data["verified_rubrics_for_repertorization"][0]["candidate_id"] == c1_id

    asyncio.run(_test())
