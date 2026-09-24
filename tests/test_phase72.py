"""
Automated Test Suite for Phase 72: Interactive Hahnemannian Case-Taking Dialogue Engine.
"""
import pytest
from app.clinical.interactive_case_taking import (
    InteractiveCaseTakingEngine,
    DialogueState,
    ClarificationDimension
)


def test_initial_session_with_incomplete_symptoms():
    """Verify incomplete symptom triggers AWAITING_CLARIFICATION with targeted LSMC queries."""
    narrative = "amar matha betha" # Only 1 symptom (Location)
    session = InteractiveCaseTakingEngine.initialize_session(
        patient_id="PT-INCOMPL-001",
        initial_narrative=narrative,
        language="bn"
    )

    assert session.state == DialogueState.AWAITING_CLARIFICATION
    assert session.can_proceed_to_repertorization is False
    assert session.repertory_rubric_count == 1
    assert len(session.pending_queries) >= 3

    # Check that Bengali prompts are present
    assert any("ব্যথার ধরন" in q.prompt_bengali for q in session.pending_queries)
    assert any("নড়াচড়া" in q.prompt_bengali for q in session.pending_queries)


def test_interactive_clarification_leads_to_complete_case():
    """Verify multi-turn answering completes case and enables repertorization."""
    session = InteractiveCaseTakingEngine.initialize_session(
        patient_id="PT-CLARIF-002",
        initial_narrative="matha betha",
        language="bn"
    )
    assert session.state == DialogueState.AWAITING_CLARIFICATION

    # Find the motion modality query
    motion_q = next(q for q in session.pending_queries if q.dimension == ClarificationDimension.MODALITY_MOTION)
    session = InteractiveCaseTakingEngine.submit_clarification_answer(
        session=session,
        query_id=motion_q.query_id,
        patient_answer="norachora korle bare" # Motion aggravation
    )

    # Find thirst or thermal query
    thirst_q = next(q for q in session.pending_queries if q.dimension == ClarificationDimension.THIRST_DISPOSITION)
    session = InteractiveCaseTakingEngine.submit_clarification_answer(
        session=session,
        query_id=thirst_q.query_id,
        patient_answer="jol pipasha nei" # Thirstlessness
    )

    assert session.repertory_rubric_count >= 3
    assert session.state == DialogueState.COMPLETE
    assert session.can_proceed_to_repertorization is True
    assert len(session.pending_queries) == 0


def test_complete_initial_narrative_bypasses_clarification():
    """Verify rich initial narrative immediately marks session as COMPLETE."""
    rich_narrative = "sir me thak thak dard hai hilne dulne se badhta hai aur pani ki pyas nahi"
    session = InteractiveCaseTakingEngine.initialize_session(
        patient_id="PT-RICH-003",
        initial_narrative=rich_narrative,
        language="hi"
    )

    assert session.state == DialogueState.COMPLETE
    assert session.can_proceed_to_repertorization is True
    assert session.repertory_rubric_count >= 3
    assert len(session.pending_queries) == 0


def test_emergency_sentinel_initial_narrative():
    """Verify catastrophic emergency keywords in initial narrative halt dialogue immediately."""
    emergency_text = "crushing chest pain radiating to left arm and sweating"
    session = InteractiveCaseTakingEngine.initialize_session(
        patient_id="PT-EMERG-004",
        initial_narrative=emergency_text,
        language="en"
    )

    assert session.state == DialogueState.EMERGENCY_HALTED
    assert session.can_proceed_to_repertorization is False
    assert "crushing chest pain" in session.emergency_flag


def test_emergency_sentinel_during_clarification_answer():
    """Verify emergency psychiatric red flag in clarification response halts session."""
    session = InteractiveCaseTakingEngine.initialize_session(
        patient_id="PT-PSYCH-005",
        initial_narrative="matha betha",
        language="bn"
    )
    first_q = session.pending_queries[0]

    session = InteractiveCaseTakingEngine.submit_clarification_answer(
        session=session,
        query_id=first_q.query_id,
        patient_answer="amar ar bachte iccha nei ami atmohotya korte chai"
    )

    assert session.state == DialogueState.EMERGENCY_HALTED
    assert session.can_proceed_to_repertorization is False
    assert "atmohotya" in session.emergency_flag


def test_abstain_insufficient_when_queries_exhausted():
    """Verify session transitions to ABSTAIN_INSUFFICIENT if queries answered with non-clinical noise."""
    session = InteractiveCaseTakingEngine.initialize_session(
        patient_id="PT-NOISE-006",
        initial_narrative="matha betha",
        language="bn"
    )

    # Exhaust all pending queries with unmapped noise
    while session.pending_queries:
        q = session.pending_queries[0]
        session = InteractiveCaseTakingEngine.submit_clarification_answer(
            session=session,
            query_id=q.query_id,
            patient_answer="janina thik moto" # "I don't know properly"
        )

    assert session.state == DialogueState.ABSTAIN_INSUFFICIENT
    assert session.can_proceed_to_repertorization is False
