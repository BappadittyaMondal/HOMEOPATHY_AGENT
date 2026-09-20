"""
Kent's 12 Observations Decision Automaton (Phase 21).
Codifies James Tyler Kent's Twelve Post-Prescription Prognostic Observations
into a deterministic clinical follow-up state machine per Lectures on Homeopathic Philosophy.
"""
from app.models.safety import (
    FollowUpObservationTelemetry,
    KentObservationEvaluation,
    KentObservationIndex
)

class KentObservationEngine:
    """
    Evaluates follow-up clinical telemetry and maps to Kent's Twelve Observations,
    providing deterministic prognosis and second prescription guidance.
    """

    @classmethod
    def evaluate_followup(cls, telemetry: FollowUpObservationTelemetry) -> KentObservationEvaluation:
        """
        Processes follow-up observation metrics and returns Kentian clinical verdict.
        """
        # 1. Scientific Proving Mode
        if telemetry.proving_trial_mode:
            return KentObservationEvaluation(
                observation_number=KentObservationIndex.OBSERVATION_9,
                title="Observation IX: Action of the Medicine Upon Provers",
                prognosis="Healthy prover state; scientific pathogenetic observation.",
                underlying_pathophysiology="Artificial disease produced on a healthy vital organism.",
                action_required="RECORD_SYMPTOMS_CAREFULLY"
            )

        # 2. Oversensitive / Idiosyncratic Prover
        if telemetry.proves_every_remedy:
            return KentObservationEvaluation(
                observation_number=KentObservationIndex.OBSERVATION_8,
                title="Observation VIII: Patient Proves Every Remedy",
                prognosis="Hypersensitive idiosyncrasy; delicate vital equilibrium.",
                underlying_pathophysiology="Susceptibility exaggerated; vital force responds pathogenetically to remedies.",
                action_required="MINIMAL_LM_POTENCY_OR_OLFACTION"
            )

        # 3. Wrong Direction / Dangerous Suppression (External to Internal)
        if telemetry.symptoms_take_wrong_direction:
            return KentObservationEvaluation(
                observation_number=KentObservationIndex.OBSERVATION_12,
                title="Observation XII: Symptoms Take the Wrong Direction",
                prognosis="Grave hazard; disease driven into more vital centers (Iatrogenic Suppression).",
                underlying_pathophysiology="Medicinal force acted centripetally, repressing peripheral signs to internal organs.",
                action_required="ANTIDOTE_IMMEDIATELY"
            )

        # 4. New Symptoms Appear (Wrong Remedy / Metastasized symptom picture)
        if telemetry.new_symptoms_appeared:
            return KentObservationEvaluation(
                observation_number=KentObservationIndex.OBSERVATION_10,
                title="Observation X: New Symptoms Appear After the Remedy",
                prognosis="Unfavorable; the remedy was an erroneous prescription (simulacrum).",
                underlying_pathophysiology="The remedy was not homeomorphic to the case; excited medicinal symptoms.",
                action_required="RE_CASE_TAKE_AND_REMEDY_CHANGE"
            )

        # 5. Old Symptoms Reappear (Hering's Law Confirmation)
        if telemetry.old_symptoms_returned and telemetry.general_vitality_improved:
            return KentObservationEvaluation(
                observation_number=KentObservationIndex.OBSERVATION_11,
                title="Observation XI: Old Symptoms Observed to Reappear",
                prognosis="Most favorable; disease unraveling in reverse chronological order.",
                underlying_pathophysiology="Vital force throwing off disease layers per Hering's Law of Cure.",
                action_required="SAC_LAC_WAIT"
            )

        # 6. Full symptom relief without general systemic relief
        if telemetry.chief_complaint_ameliorated and not telemetry.general_vitality_improved:
            return KentObservationEvaluation(
                observation_number=KentObservationIndex.OBSERVATION_7,
                title="Observation VII: Full Amelioration Yet No Special Relief to Patient",
                prognosis="Unfavorable; advanced organic destruction or latent malignancy.",
                underlying_pathophysiology="Structural organic changes too profound for restorative vital reaction.",
                action_required="PALLIATIVE_SAC_LAC"
            )

        # 7. Amelioration first, then aggravation
        if telemetry.amelioration_preceded_aggravation:
            return KentObservationEvaluation(
                observation_number=KentObservationIndex.OBSERVATION_5,
                title="Observation V: The Amelioration Comes First, Aggravation Afterwards",
                prognosis="Unfavorable; superficial palliation or incurable organic state.",
                underlying_pathophysiology="Remedy acted only on surface symptoms without touching root miasm.",
                action_required="RE_CASE_TAKE_FOR_CONSTITUTIONAL_SIMILLIMUM"
            )

        # 8. Too short relief
        if (
            telemetry.relief_duration_days is not None
            and telemetry.relief_duration_days <= 3
            and not telemetry.chief_complaint_ameliorated
        ):
            return KentObservationEvaluation(
                observation_number=KentObservationIndex.OBSERVATION_6,
                title="Observation VI: Too Short Relief of Symptoms",
                prognosis="Guarded; structural obstacle, miasmatic obstruction, or mechanical barrier.",
                underlying_pathophysiology="Remedy consumed rapidly by active pathology or blocked by miasmatic dyscrasia.",
                action_required="INTERCURRENT_NOSODE_OR_HIGHER_POTENCY"
            )

        # 9. Aggravation Cases
        if telemetry.aggravation_occurred:
            if not telemetry.general_vitality_improved and telemetry.aggravation_duration_days >= 14:
                return KentObservationEvaluation(
                    observation_number=KentObservationIndex.OBSERVATION_1,
                    title="Observation I: Prolonged Aggravation and Final Decline",
                    prognosis="Unfavorable / Terminal decline; vital force exhausted.",
                    underlying_pathophysiology="Deep antipsoric remedy was too high for exhausted vitality with organic destruction.",
                    action_required="ANTIDOTE_AND_SOOTHE"
                )
            elif telemetry.general_vitality_improved and telemetry.aggravation_duration_days >= 7:
                return KentObservationEvaluation(
                    observation_number=KentObservationIndex.OBSERVATION_2,
                    title="Observation II: Long Aggravation, Slow Gradual Recovery",
                    prognosis="Favorable; structural tissue turnaround after prolonged reaction.",
                    underlying_pathophysiology="Borderland organic changes requiring severe vital turmoil before cure ensues.",
                    action_required="SAC_LAC_WAIT"
                )
            elif telemetry.general_vitality_improved and telemetry.aggravation_duration_days <= 3:
                return KentObservationEvaluation(
                    observation_number=KentObservationIndex.OBSERVATION_3,
                    title="Observation III: Aggravation Quick, Short, Strong with Rapid Cure",
                    prognosis="Highest excellence; ideal simillimum match.",
                    underlying_pathophysiology="Dynamic functional illness; high vital reactivity throwing off morbid state immediately.",
                    action_required="SAC_LAC_WAIT"
                )

        # 10. Recovery without aggravation (Observation 4)
        if not telemetry.aggravation_occurred and telemetry.chief_complaint_ameliorated:
            return KentObservationEvaluation(
                observation_number=KentObservationIndex.OBSERVATION_4,
                title="Observation IV: Recovery Without Any Aggravation",
                prognosis="Excellent; gentle cure without physiological disturbance.",
                underlying_pathophysiology="Exact match in potency and susceptibility without gross structural pathology.",
                action_required="SAC_LAC_WAIT"
            )

        # Fallback default
        return KentObservationEvaluation(
            observation_number=KentObservationIndex.OBSERVATION_4,
            title="Observation IV: Recovery Without Aggravation",
            prognosis="Stable clinical state.",
            underlying_pathophysiology="Gradual restoration of health under dynamic medicinal influence.",
            action_required="SAC_LAC_WAIT"
        )
