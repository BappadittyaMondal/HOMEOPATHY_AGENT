"""
Mental-Somatic Dissociation Index - MSDI (Phase 68).

Implements Samuel Hahnemann's Organon of Medicine Aphorism 253 and Kent's
Prognostic Observations:
Distinguishes benign primary homeopathic aggravation from clinical collapse
by evaluating mental disposition delta (ΔM) against physical symptom severity delta (ΔS).
"""
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class ClinicalFollowUpState(str, Enum):
    BENIGN_HOMEOPATHIC_AGGRAVATION = "BENIGN_HOMEOPATHIC_AGGRAVATION"
    TRUE_HOMOEOPATHIC_AMELIORATION = "TRUE_HOMOEOPATHIC_AMELIORATION"
    ORGANIC_COLLAPSE_OR_PROGRESSION = "ORGANIC_COLLAPSE_OR_PROGRESSION"
    REMEDY_PATHOGENESIS_PROVING = "REMEDY_PATHOGENESIS_PROVING"
    STATIC_NO_REACTION = "STATIC_NO_REACTION"


class PrescribingDirective(str, Enum):
    OBSERVE_SAC_LAC_WAIT = "OBSERVE_SAC_LAC_WAIT"
    CONTINUE_WITHOUT_INTERFERENCE = "CONTINUE_WITHOUT_INTERFERENCE"
    IMMEDIATE_CLINICAL_REASSESSMENT = "IMMEDIATE_CLINICAL_REASSESSMENT"
    DISCONTINUE_AND_ANTIDOTE = "DISCONTINUE_AND_ANTIDOTE"
    REPEAT_OR_ASCEND_POTENCY = "REPEAT_OR_ASCEND_POTENCY"


class TelemetrySnapshot(BaseModel):
    patient_id: str
    physical_severity: float = Field(ge=0.0, le=10.0, description="0=None, 10=Intolerable")
    mental_calmness: float = Field(ge=0.0, le=10.0, description="0=Severe anguish/panic, 10=Serene/tranquil")
    days_since_dose: float = Field(ge=0.0)
    reported_new_symptoms: List[str] = Field(default_factory=list)
    vital_signs_stable: bool = True


class DissociationAnalysis(BaseModel):
    patient_id: str
    delta_somatic_severity: float  # +ve means worsened, -ve means improved
    delta_mental_calmness: float   # +ve means improved serenity, -ve means worsened
    state: ClinicalFollowUpState
    directive: PrescribingDirective
    aphorism_reference: str
    clinical_rationale: str
    emergency_referral_mandated: bool = False


class MentalSomaticDissociationEngine:
    """
    Computes Mental-Somatic Dissociation Index (MSDI) per Aphorism 253.
    """

    BENIGN_AGGRAVATION_MENTAL_DELTA_MIN: float = 0.5  # Calmness improved by >= 0.5/10

    def evaluate(
        self,
        baseline: TelemetrySnapshot,
        followup: TelemetrySnapshot,
    ) -> DissociationAnalysis:
        """
        Evaluates longitudinal change between baseline and follow-up.
        """
        if baseline.patient_id != followup.patient_id:
            raise ValueError("Baseline and follow-up patient IDs must match.")

        # Delta somatic: positive means physical symptom severity worsened (flare)
        delta_somatic = round(followup.physical_severity - baseline.physical_severity, 2)
        # Delta mental: positive means calmness/serenity improved
        delta_mental = round(followup.mental_calmness - baseline.mental_calmness, 2)

        # Check for immediate vital signs instability
        if not followup.vital_signs_stable:
            return DissociationAnalysis(
                patient_id=baseline.patient_id,
                delta_somatic_severity=delta_somatic,
                delta_mental_calmness=delta_mental,
                state=ClinicalFollowUpState.ORGANIC_COLLAPSE_OR_PROGRESSION,
                directive=PrescribingDirective.IMMEDIATE_CLINICAL_REASSESSMENT,
                aphorism_reference="Organon §253; Red Flag Physiological Decompensation",
                clinical_rationale="Vital signs unstable. Immediate emergency medical evaluation required.",
                emergency_referral_mandated=True,
            )

        # Check for new uncharacteristic proving symptoms (Pathogenesis)
        if len(followup.reported_new_symptoms) >= 2 and delta_somatic >= 0 and delta_mental <= 0:
            return DissociationAnalysis(
                patient_id=baseline.patient_id,
                delta_somatic_severity=delta_somatic,
                delta_mental_calmness=delta_mental,
                state=ClinicalFollowUpState.REMEDY_PATHOGENESIS_PROVING,
                directive=PrescribingDirective.DISCONTINUE_AND_ANTIDOTE,
                aphorism_reference="Organon §249; Kent Observation 6",
                clinical_rationale="Patient developed new pathogenetic symptoms not part of original natural disease. Discontinue remedy.",
            )

        # Condition 1: Benign Homeopathic Aggravation (Aphorism 253)
        # Physical symptoms flared (delta_somatic > 0), BUT mental calmness/demeanor improved (delta_mental >= threshold)
        if delta_somatic > 0 and delta_mental >= self.BENIGN_AGGRAVATION_MENTAL_DELTA_MIN:
            return DissociationAnalysis(
                patient_id=baseline.patient_id,
                delta_somatic_severity=delta_somatic,
                delta_mental_calmness=delta_mental,
                state=ClinicalFollowUpState.BENIGN_HOMEOPATHIC_AGGRAVATION,
                directive=PrescribingDirective.OBSERVE_SAC_LAC_WAIT,
                aphorism_reference="Organon §253, §280; Kent Observation 3",
                clinical_rationale=(
                    f"Physical symptoms flared (+{delta_somatic}), but patient mental serenity and internal calmness "
                    f"improved (+{delta_mental}). Signifies benign primary action of the simillimum. "
                    "Strictly administer Sacrum Lactis (placebo) and wait. DO NOT repeat or change remedy."
                ),
            )

        # Condition 2: True Homeopathic Amelioration (Organon §253)
        # Physical symptoms improved (delta_somatic < 0) and mental state stable or improved
        if delta_somatic < 0 and delta_mental >= 0:
            return DissociationAnalysis(
                patient_id=baseline.patient_id,
                delta_somatic_severity=delta_somatic,
                delta_mental_calmness=delta_mental,
                state=ClinicalFollowUpState.TRUE_HOMOEOPATHIC_AMELIORATION,
                directive=PrescribingDirective.CONTINUE_WITHOUT_INTERFERENCE,
                aphorism_reference="Organon §253; Hering's Law of Cure",
                clinical_rationale=(
                    f"Physical symptoms improved ({delta_somatic}) with tranquil or improving mental demeanor (+{delta_mental}). "
                    "Curative response underway. Allow dynamic action to unfold without repetition."
                ),
            )

        # Condition 3: Disease Progression or Organic Collapse (Kent Observation 1)
        # Physical symptoms worsened (delta_somatic >= 0) and mental demeanor worsened (delta_mental < 0)
        if delta_somatic > 0 and delta_mental < 0:
            return DissociationAnalysis(
                patient_id=baseline.patient_id,
                delta_somatic_severity=delta_somatic,
                delta_mental_calmness=delta_mental,
                state=ClinicalFollowUpState.ORGANIC_COLLAPSE_OR_PROGRESSION,
                directive=PrescribingDirective.IMMEDIATE_CLINICAL_REASSESSMENT,
                aphorism_reference="Organon §253; Kent Observation 1",
                clinical_rationale=(
                    f"Both physical severity (+{delta_somatic}) and mental tranquility ({delta_mental}) have worsened. "
                    "Indicates disease progression or wrong remedy failing to halt pathological destruction. "
                    "Immediate clinical re-case-taking required."
                ),
                emergency_referral_mandated=(delta_somatic >= 4.0 or delta_mental <= -4.0),
            )

        # Condition 4: Static / No Reaction
        return DissociationAnalysis(
            patient_id=baseline.patient_id,
            delta_somatic_severity=delta_somatic,
            delta_mental_calmness=delta_mental,
            state=ClinicalFollowUpState.STATIC_NO_REACTION,
            directive=PrescribingDirective.REPEAT_OR_ASCEND_POTENCY,
            aphorism_reference="Organon §281",
            clinical_rationale="No perceptible change in somatic or mental sphere. Re-evaluate potency or remedy concordance.",
        )
