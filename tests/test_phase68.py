"""
Test Suite for Phase 68: Mental-Somatic Dissociation Index - MSDI (Aphorism 253).
"""
import pytest
from app.safety.mental_somatic_index import (
    MentalSomaticDissociationEngine,
    TelemetrySnapshot,
    ClinicalFollowUpState,
    PrescribingDirective,
)


def test_benign_homeopathic_aggravation_aphorism_253():
    """Physical symptoms flare (+2.0) but mental calmness improves (+2.0) -> Sac Lac Wait."""
    engine = MentalSomaticDissociationEngine()
    baseline = TelemetrySnapshot(
        patient_id="PAT_MSDI_01",
        physical_severity=4.0,
        mental_calmness=3.0,
        days_since_dose=0.0,
    )
    followup = TelemetrySnapshot(
        patient_id="PAT_MSDI_01",
        physical_severity=6.0,  # +2.0 flare
        mental_calmness=5.5,   # +2.5 improved demeanor
        days_since_dose=2.0,
    )
    res = engine.evaluate(baseline, followup)
    assert res.state == ClinicalFollowUpState.BENIGN_HOMEOPATHIC_AGGRAVATION
    assert res.directive == PrescribingDirective.OBSERVE_SAC_LAC_WAIT
    assert res.delta_somatic_severity == 2.0
    assert res.delta_mental_calmness == 2.5
    assert "Sacrum Lactis" in res.clinical_rationale
    assert "253" in res.aphorism_reference


def test_true_curative_amelioration():
    """Physical severity decreases (-4.0) and mental calmness improves (+3.0) -> Continue."""
    engine = MentalSomaticDissociationEngine()
    baseline = TelemetrySnapshot(
        patient_id="PAT_MSDI_02",
        physical_severity=7.5,
        mental_calmness=4.0,
        days_since_dose=0.0,
    )
    followup = TelemetrySnapshot(
        patient_id="PAT_MSDI_02",
        physical_severity=3.5,  # -4.0 improvement
        mental_calmness=7.0,   # +3.0 calmness
        days_since_dose=14.0,
    )
    res = engine.evaluate(baseline, followup)
    assert res.state == ClinicalFollowUpState.TRUE_HOMOEOPATHIC_AMELIORATION
    assert res.directive == PrescribingDirective.CONTINUE_WITHOUT_INTERFERENCE
    assert res.delta_somatic_severity == -4.0
    assert res.delta_mental_calmness == 3.0


def test_organic_collapse_kent_observation_1():
    """Physical worsens (+3.0) and mental plunges (-4.0) -> Immediate clinical reassessment."""
    engine = MentalSomaticDissociationEngine()
    baseline = TelemetrySnapshot(
        patient_id="PAT_MSDI_03",
        physical_severity=4.0,
        mental_calmness=6.0,
        days_since_dose=0.0,
    )
    followup = TelemetrySnapshot(
        patient_id="PAT_MSDI_03",
        physical_severity=7.5,  # +3.5 worse
        mental_calmness=1.5,   # -4.5 collapsed tranquility
        days_since_dose=5.0,
    )
    res = engine.evaluate(baseline, followup)
    assert res.state == ClinicalFollowUpState.ORGANIC_COLLAPSE_OR_PROGRESSION
    assert res.directive == PrescribingDirective.IMMEDIATE_CLINICAL_REASSESSMENT
    assert res.emergency_referral_mandated is True


def test_vital_signs_unstable_emergency():
    """Unstable vitals immediately trigger emergency referral."""
    engine = MentalSomaticDissociationEngine()
    baseline = TelemetrySnapshot(
        patient_id="PAT_MSDI_04",
        physical_severity=3.0,
        mental_calmness=5.0,
        days_since_dose=0.0,
    )
    followup = TelemetrySnapshot(
        patient_id="PAT_MSDI_04",
        physical_severity=5.0,
        mental_calmness=5.0,
        days_since_dose=1.0,
        vital_signs_stable=False,
    )
    res = engine.evaluate(baseline, followup)
    assert res.emergency_referral_mandated is True
    assert res.state == ClinicalFollowUpState.ORGANIC_COLLAPSE_OR_PROGRESSION


def test_remedy_pathogenesis_proving():
    """Appearance of 2+ new uncharacteristic symptoms indicates iatrogenic proving."""
    engine = MentalSomaticDissociationEngine()
    baseline = TelemetrySnapshot(
        patient_id="PAT_MSDI_05",
        physical_severity=4.0,
        mental_calmness=5.0,
        days_since_dose=0.0,
    )
    followup = TelemetrySnapshot(
        patient_id="PAT_MSDI_05",
        physical_severity=4.5,
        mental_calmness=4.5,
        days_since_dose=7.0,
        reported_new_symptoms=["Violent throbbing headache on right temple", "Sudden ravenous canine hunger at 3 AM"],
    )
    res = engine.evaluate(baseline, followup)
    assert res.state == ClinicalFollowUpState.REMEDY_PATHOGENESIS_PROVING
    assert res.directive == PrescribingDirective.DISCONTINUE_AND_ANTIDOTE
    assert "249" in res.aphorism_reference


def test_static_no_reaction():
    """No change in somatic or mental sphere -> Static / ascend potency."""
    engine = MentalSomaticDissociationEngine()
    baseline = TelemetrySnapshot(
        patient_id="PAT_MSDI_06",
        physical_severity=5.0,
        mental_calmness=5.0,
        days_since_dose=0.0,
    )
    followup = TelemetrySnapshot(
        patient_id="PAT_MSDI_06",
        physical_severity=5.0,
        mental_calmness=5.0,
        days_since_dose=21.0,
    )
    res = engine.evaluate(baseline, followup)
    assert res.state == ClinicalFollowUpState.STATIC_NO_REACTION
    assert res.directive == PrescribingDirective.REPEAT_OR_ASCEND_POTENCY
