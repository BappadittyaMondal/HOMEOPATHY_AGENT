"""
Tests for Phase 51: Unified Hard Control-Flow Safety Gating Architecture.
Validates INV-01, INV-02, and ApprovedDraft cryptographic sealing.
"""
import pytest
from app.safety.gates import (
    SafetyGatePipeline,
    SafetyBlockException,
    ApprovedDraft,
    GateVerdict
)


def test_approved_draft_generation_and_verification():
    """Verify that a safe, compatible remedy produces a valid, verified ApprovedDraft."""
    draft = SafetyGatePipeline.run_gates(
        prescription_id="RX-TEST-001",
        patient_id="PAT-TEST-001",
        candidate_remedy="Arnica montana",
        potency="30C",
        dosage_instructions="4 globules twice daily for 3 days",
        previous_remedy="Belladonna",
        days_since_previous=30,
        is_acute_override=False
    )
    assert isinstance(draft, ApprovedDraft)
    assert draft.remedy_name == "Arnica montana"
    assert draft.potency == "30C"
    assert SafetyGatePipeline.verify_approved_draft(draft) is True
    assert all(gr.verdict in [GateVerdict.ALLOW, GateVerdict.WARN_OVERRIDABLE] for gr in draft.gate_results)


def test_inv_01_inimical_hard_block_raises_exception():
    """
    INV-01: Causticum immediately following Phosphorus within 60-day washout
    must throw SafetyBlockException and NEVER issue an ApprovedDraft.
    """
    with pytest.raises(SafetyBlockException) as exc_info:
        SafetyGatePipeline.run_gates(
            prescription_id="RX-TEST-002",
            patient_id="PAT-TEST-002",
            candidate_remedy="Causticum",
            potency="200C",
            dosage_instructions="Single dose",
            previous_remedy="Phosphorus",
            days_since_previous=10,  # Required: 60 days
            is_acute_override=False
        )
    assert exc_info.value.gate_name == "INIMICAL_SEQUENCE_GATE"
    assert "inimical" in exc_info.value.message.lower()


def test_inimical_acute_override_allows_approved_draft():
    """Verify that a bona fide acute emergency override permits dispensing with warning."""
    draft = SafetyGatePipeline.run_gates(
        prescription_id="RX-TEST-003",
        patient_id="PAT-TEST-003",
        candidate_remedy="Causticum",
        potency="30C",
        dosage_instructions="Acute emergency split dose",
        previous_remedy="Phosphorus",
        days_since_previous=10,
        is_acute_override=True  # Doctor overrides for acute state
    )
    assert isinstance(draft, ApprovedDraft)
    assert any(gr.verdict == GateVerdict.WARN_OVERRIDABLE for gr in draft.gate_results)
    assert SafetyGatePipeline.verify_approved_draft(draft) is True


def test_inv_02_statutory_toxicology_subpotent_e1_raises_exception():
    """
    INV-02: Aconitum napellus requested as Mother Tincture (Q) or 1X (banned below 3X)
    violates Drugs & Cosmetics Act Schedule E(1) and must throw SafetyBlockException.
    """
    with pytest.raises(SafetyBlockException) as exc_info:
        SafetyGatePipeline.run_gates(
            prescription_id="RX-TEST-004",
            patient_id="PAT-TEST-004",
            candidate_remedy="Aconitum napellus",
            potency="Q",  # Hazardous mother tincture containing lethal aconitine
            dosage_instructions="5 drops in water"
        )
    assert exc_info.value.gate_name == "STATUTORY_TOXICOLOGY_GATE"
    assert "toxicology violation" in exc_info.value.message.lower()


def test_obstetric_abortifacient_hard_block():
    """INV-12 preliminary: Sabina prescribed during pregnancy trimester 1 must be blocked."""
    with pytest.raises(SafetyBlockException) as exc_info:
        SafetyGatePipeline.run_gates(
            prescription_id="RX-TEST-005",
            patient_id="PAT-TEST-005",
            candidate_remedy="Sabina",
            potency="30C",
            dosage_instructions="Daily dose",
            is_pregnant=True,
            gestational_trimester=1
        )
    assert exc_info.value.gate_name == "OBSTETRIC_SAFETY_GATE"
    assert "abortifacient" in exc_info.value.message.lower()
