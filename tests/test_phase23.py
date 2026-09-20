"""
Unit Tests for Phase 23: Classical Second Prescription Decision Engine.
"""
from app.safety.second_prescription import SecondPrescriptionEngine
from app.models.safety import SecondPrescriptionAction

def test_patient_improving_receives_sac_lac():
    """Verify cardinal rule: Do not interfere while patient is improving."""
    decision = SecondPrescriptionEngine.evaluate_next_step(
        prior_remedy="Sulphur",
        prior_potency="200C",
        is_improving=True
    )
    assert decision.action == SecondPrescriptionAction.SAC_LAC_PLACEBO
    assert decision.recommended_remedy == "Sac Lac"
    assert "Aphorisms 245 & 246" in decision.aphorism_basis

def test_suppression_requires_immediate_antidote():
    """Verify that suppression or violent aggravation triggers immediate antidoting."""
    decision = SecondPrescriptionEngine.evaluate_next_step(
        prior_remedy="Lachesis muta",
        prior_potency="1M",
        is_improving=False,
        suppression_or_aggravation=True,
        antidote_candidate="Camphora"
    )
    assert decision.action == SecondPrescriptionAction.ADMINISTER_ANTIDOTE
    assert decision.recommended_remedy == "Camphora"
    assert "Aphorism 249" in decision.aphorism_basis

def test_miasmatic_block_triggers_intercurrent_nosode():
    """Verify that a miasmatic block prompts an intercurrent nosode prescription."""
    decision = SecondPrescriptionEngine.evaluate_next_step(
        prior_remedy="Calcarea carbonica",
        prior_potency="200C",
        is_improving=False,
        miasmatic_block=True
    )
    assert decision.action == SecondPrescriptionAction.INTERCURRENT_NOSODE
    assert "Psorinum" in decision.recommended_remedy
    assert "Aphorisms 204-206" in decision.aphorism_basis

def test_altered_symptom_picture_requires_remedy_change():
    """Verify that when symptoms fundamentally shift, a new remedy is required."""
    decision = SecondPrescriptionEngine.evaluate_next_step(
        prior_remedy="Aconitum napellus",
        prior_potency="30C",
        is_improving=False,
        symptom_picture_shifted=True
    )
    assert decision.action == SecondPrescriptionAction.CHANGE_OF_REMEDY
    assert "Aphorism 248" in decision.aphorism_basis

def test_potency_jump_when_progress_stalls_on_same_picture():
    """Verify potency jump along Centesimal and LM scales when identical picture persists."""
    # 30C -> 200C
    dec_c = SecondPrescriptionEngine.evaluate_next_step(
        prior_remedy="Lycopodium clavatum",
        prior_potency="30C",
        is_improving=False
    )
    assert dec_c.action == SecondPrescriptionAction.POTENCY_JUMP
    assert dec_c.recommended_potency == "200C"

    # LM 0/1 -> LM 0/2
    dec_lm = SecondPrescriptionEngine.evaluate_next_step(
        prior_remedy="Natrum muriaticum",
        prior_potency="LM 0/1",
        is_improving=False
    )
    assert dec_lm.action == SecondPrescriptionAction.POTENCY_JUMP
    assert dec_lm.recommended_potency == "LM 0/2"
