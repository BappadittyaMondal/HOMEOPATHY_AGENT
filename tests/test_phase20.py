"""
Unit Tests for Phase 20: Classical 26-Point Inimical Matrix & Antidotal Engine.
"""
from app.safety.inimical_matrix import InimicalSafetyMatrix
from app.models.safety import ToxicitySafetyStatus

def test_inimical_pair_hard_blocked_within_washout():
    """Verify that prescribing an inimical remedy within the washout window is HARD_BLOCKED."""
    # Apis mellifica and Rhus tox have 14 days washout
    eval_apis_rhus = InimicalSafetyMatrix.evaluate_sequence(
        candidate_remedy="Rhus toxicodendron",
        prior_remedy="Apis mellifica",
        days_since_prior=5,
        is_acute_override=False
    )
    assert eval_apis_rhus.status == ToxicitySafetyStatus.HARD_BLOCKED
    assert "HARD CLINICAL SAFETY BLOCK" in eval_apis_rhus.clinical_advice
    assert "Apis mellifica" in eval_apis_rhus.clinical_advice

    # Causticum and Phosphorus have 60 days washout
    eval_caust_phos = InimicalSafetyMatrix.evaluate_sequence(
        candidate_remedy="Phosphorus",
        prior_remedy="Causticum",
        days_since_prior=25,
        is_acute_override=False
    )
    assert eval_caust_phos.status == ToxicitySafetyStatus.HARD_BLOCKED
    assert "paralytic weakness" in eval_caust_phos.hazard_description

def test_acute_intercurrent_override_exception():
    """Verify that an acute override changes HARD_BLOCKED to WARNING_OVERRIDABLE."""
    eval_override = InimicalSafetyMatrix.evaluate_sequence(
        candidate_remedy="Rhus toxicodendron",
        prior_remedy="Apis mellifica",
        days_since_prior=3,
        is_acute_override=True
    )
    assert eval_override.status == ToxicitySafetyStatus.WARNING_OVERRIDABLE
    assert eval_override.is_acute_override is True
    assert "ACUTE INTERCURRENT OVERRIDE ACTIVATED" in eval_override.clinical_advice

def test_inimical_approved_after_washout_elapsed():
    """Verify that once the classical washout period elapses, the sequence is APPROVED."""
    eval_post_washout = InimicalSafetyMatrix.evaluate_sequence(
        candidate_remedy="Causticum",
        prior_remedy="Phosphorus",
        days_since_prior=65,
        is_acute_override=False
    )
    assert eval_post_washout.status == ToxicitySafetyStatus.APPROVED
    assert "minimum washout of 60 days has elapsed" in eval_post_washout.hazard_description

def test_compatible_remedy_sequence():
    """Verify that remedies with non-inimical relationships pass cleanly."""
    eval_comp = InimicalSafetyMatrix.evaluate_sequence(
        candidate_remedy="Bryonia alba",
        prior_remedy="Aconitum napellus",
        days_since_prior=2
    )
    assert eval_comp.status == ToxicitySafetyStatus.APPROVED
    assert "No known classical inimical" in eval_comp.hazard_description

def test_antidote_lookup():
    """Verify retrieval of verified classical antidotes."""
    antidotes_acon = InimicalSafetyMatrix.get_antidotes("Aconitum napellus")
    assert "Coffea cruda" in antidotes_acon
    assert "Strychnos nux-vomica" in antidotes_acon

    antidotes_phos = InimicalSafetyMatrix.get_antidotes("Phosphorus")
    assert "Camphora" in antidotes_phos
