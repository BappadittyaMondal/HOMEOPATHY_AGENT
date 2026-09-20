"""
Unit Tests for Phase 21: Kent's 12 Observations Decision Automaton.
"""
from app.safety.kent_observations import KentObservationEngine
from app.models.safety import FollowUpObservationTelemetry, KentObservationIndex

def test_observation_3_ideal_simillimum():
    """Verify Observation 3: Short sharp aggravation followed by rapid cure."""
    telemetry = FollowUpObservationTelemetry(
        aggravation_occurred=True,
        aggravation_duration_days=2,
        aggravation_severity="MILD",
        general_vitality_improved=True,
        chief_complaint_ameliorated=True,
        new_symptoms_appeared=False,
        old_symptoms_returned=False,
        days_since_prescription=7
    )
    eval_res = KentObservationEngine.evaluate_followup(telemetry)
    assert eval_res.observation_number == KentObservationIndex.OBSERVATION_3
    assert eval_res.action_required == "SAC_LAC_WAIT"
    assert "ideal simillimum" in eval_res.prognosis.lower()

def test_observation_1_prolonged_decline():
    """Verify Observation 1: Prolonged aggravation and decline in exhausted vitality."""
    telemetry = FollowUpObservationTelemetry(
        aggravation_occurred=True,
        aggravation_duration_days=18,
        aggravation_severity="SEVERE_VIOLENT",
        general_vitality_improved=False,
        chief_complaint_ameliorated=False,
        new_symptoms_appeared=False,
        old_symptoms_returned=False,
        days_since_prescription=21
    )
    eval_res = KentObservationEngine.evaluate_followup(telemetry)
    assert eval_res.observation_number == KentObservationIndex.OBSERVATION_1
    assert "ANTIDOTE" in eval_res.action_required

def test_observation_10_wrong_remedy():
    """Verify Observation 10: New symptoms appear signaling wrong remedy."""
    telemetry = FollowUpObservationTelemetry(
        aggravation_occurred=False,
        aggravation_duration_days=0,
        aggravation_severity="MILD",
        general_vitality_improved=False,
        chief_complaint_ameliorated=False,
        new_symptoms_appeared=True,
        old_symptoms_returned=False,
        days_since_prescription=10
    )
    eval_res = KentObservationEngine.evaluate_followup(telemetry)
    assert eval_res.observation_number == KentObservationIndex.OBSERVATION_10
    assert eval_res.action_required == "RE_CASE_TAKE_AND_REMEDY_CHANGE"

def test_observation_11_herings_law():
    """Verify Observation 11: Reappearance of old symptoms confirms curative progression."""
    telemetry = FollowUpObservationTelemetry(
        aggravation_occurred=False,
        aggravation_duration_days=0,
        aggravation_severity="MILD",
        general_vitality_improved=True,
        chief_complaint_ameliorated=True,
        new_symptoms_appeared=False,
        old_symptoms_returned=True,
        days_since_prescription=14
    )
    eval_res = KentObservationEngine.evaluate_followup(telemetry)
    assert eval_res.observation_number == KentObservationIndex.OBSERVATION_11
    assert eval_res.action_required == "SAC_LAC_WAIT"
    assert "reverse chronological order" in eval_res.prognosis.lower()

def test_observation_12_suppression():
    """Verify Observation 12: Direction towards vital interior signals suppression."""
    telemetry = FollowUpObservationTelemetry(
        aggravation_occurred=False,
        aggravation_duration_days=0,
        aggravation_severity="MILD",
        general_vitality_improved=False,
        chief_complaint_ameliorated=False,
        new_symptoms_appeared=False,
        old_symptoms_returned=False,
        days_since_prescription=5,
        symptoms_take_wrong_direction=True
    )
    eval_res = KentObservationEngine.evaluate_followup(telemetry)
    assert eval_res.observation_number == KentObservationIndex.OBSERVATION_12
    assert eval_res.action_required == "ANTIDOTE_IMMEDIATELY"

def test_observation_4_cure_without_aggravation():
    """Verify Observation 4: Recovery without aggravation in functional cases."""
    telemetry = FollowUpObservationTelemetry(
        aggravation_occurred=False,
        aggravation_duration_days=0,
        aggravation_severity="MILD",
        general_vitality_improved=True,
        chief_complaint_ameliorated=True,
        new_symptoms_appeared=False,
        old_symptoms_returned=False,
        days_since_prescription=14
    )
    eval_res = KentObservationEngine.evaluate_followup(telemetry)
    assert eval_res.observation_number == KentObservationIndex.OBSERVATION_4
    assert eval_res.action_required == "SAC_LAC_WAIT"
