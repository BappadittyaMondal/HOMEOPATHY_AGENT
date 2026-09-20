"""
Classical Second Prescription Decision Engine (Phase 23).
Codifies Hahnemannian posological and remedial transitions per Organon Aphorisms 245-251
and Kent's Lectures on Second Prescription.
"""
from typing import Optional
from app.models.safety import (
    SecondPrescriptionAction,
    SecondPrescriptionDecision
)

class SecondPrescriptionEngine:
    """
    Automates clinical decision logic for the follow-up second prescription:
    Sac Lac (Placebo), Repetition, Potency Jump, Remedy Change, Antidote, or Intercurrent.
    """

    @classmethod
    def evaluate_next_step(
        cls,
        prior_remedy: str,
        prior_potency: str,
        is_improving: bool,
        symptom_picture_shifted: bool = False,
        suppression_or_aggravation: bool = False,
        miasmatic_block: bool = False,
        antidote_candidate: Optional[str] = None
    ) -> SecondPrescriptionDecision:
        """
        Determines the exact second prescription action adhering to pure Hahnemannian methodology.
        """
        # 1. Antidote required for suppression or violent toxic aggravation
        if suppression_or_aggravation:
            antidote = antidote_candidate or "Indicated Classical Antidote / Camphora"
            return SecondPrescriptionDecision(
                action=SecondPrescriptionAction.ADMINISTER_ANTIDOTE,
                recommended_potency="30C",
                recommended_remedy=antidote,
                rationale=(
                    f"Violent medicinal aggravation or centripetal suppression observed. "
                    f"Remedy action must be neutralized immediately using {antidote}."
                ),
                aphorism_basis="Organon Aphorism 249: Prompt antidoting of inappropriate or overly violent medicinal disturbance."
            )

        # 2. Patient is currently improving: Strict prohibition against repeating or changing
        if is_improving:
            return SecondPrescriptionDecision(
                action=SecondPrescriptionAction.SAC_LAC_PLACEBO,
                recommended_potency="Placebo (Saccharum Lactis)",
                recommended_remedy="Sac Lac",
                rationale=(
                    f"Patient is currently improving under the dynamic action of {prior_remedy} {prior_potency}. "
                    f"Organon and Kent strictly forbid repeating or changing medicine while improvement progresses."
                ),
                aphorism_basis="Organon Aphorisms 245 & 246: Never interrupt progressive amelioration with active medicine."
            )

        # 3. Miasmatic Block / Obstacle to Cure
        if miasmatic_block:
            return SecondPrescriptionDecision(
                action=SecondPrescriptionAction.INTERCURRENT_NOSODE,
                recommended_potency="200C",
                recommended_remedy="Psorinum / Tuberculinum / Medorrhinum",
                rationale=(
                    f"Progress has halted due to latent miasmatic dyscrasia despite well-chosen {prior_remedy}. "
                    f"A single intercurrent dose of indicated chronic nosode is required to unlock vital susceptibility."
                ),
                aphorism_basis="Organon Aphorisms 204-206 & The Chronic Diseases: Overcoming dormant psoric/syphilitic barriers."
            )

        # 4. Symptoms have completely changed / shifted picture
        if symptom_picture_shifted:
            return SecondPrescriptionDecision(
                action=SecondPrescriptionAction.CHANGE_OF_REMEDY,
                recommended_potency="200C",
                recommended_remedy="New Simillimum to be selected from fresh case totality",
                rationale=(
                    f"The symptom totality has fundamentally altered. Prior remedy ({prior_remedy}) has exhausted its sphere. "
                    f"Case must be retaken from the current symptom presentation to identify the complementary remedy."
                ),
                aphorism_basis="Organon Aphorism 248: When the remaining symptoms present an altered totality, select new simillimum."
            )

        # 5. Improvement halted, but exact original symptom picture remains unchanged
        # Advance potency along the centesimal or LM scale
        next_potency = cls._calculate_potency_advance(prior_potency)
        if next_potency != prior_potency:
            return SecondPrescriptionDecision(
                action=SecondPrescriptionAction.POTENCY_JUMP,
                recommended_potency=next_potency,
                recommended_remedy=prior_remedy,
                rationale=(
                    f"Prior remedy {prior_remedy} produced clear benefit, but improvement has fully stalled and the same "
                    f"totality persists. Advance potency to {next_potency} to engage higher dynamic vitality."
                ),
                aphorism_basis="Organon Aphorisms 246-248: Graduated potency escalation when identical picture returns."
            )
        else:
            return SecondPrescriptionDecision(
                action=SecondPrescriptionAction.REPEAT_SAME_POTENCY,
                recommended_potency=prior_potency,
                recommended_remedy=prior_remedy,
                rationale=(
                    f"Repeat {prior_remedy} {prior_potency} in modified/succussed form as the symptom picture remains identical."
                ),
                aphorism_basis="Organon Aphorism 247: Repetition in modified form with successive succussions."
            )

    @classmethod
    def _calculate_potency_advance(cls, current_potency: str) -> str:
        """
        Computes the next logical potency step.
        30C -> 200C -> 1M -> 10M -> 50M -> CM
        LM 0/1 -> LM 0/2 -> LM 0/3 -> ... -> LM 0/30
        6X -> 12X -> 30X
        """
        p = current_potency.strip().upper()
        centesimal_ladder = ["30C", "200C", "1M", "10M", "50M", "CM"]
        for i, level in enumerate(centesimal_ladder[:-1]):
            if p == level:
                return centesimal_ladder[i + 1]

        if "LM" in p or "0/" in p:
            import re
            m = re.search(r"0/(\d+)", p)
            if m:
                curr_deg = int(m.group(1))
                if curr_deg < 30:
                    return f"LM 0/{curr_deg + 1}"

        decimal_ladder = ["6X", "12X", "30X", "200X"]
        for i, level in enumerate(decimal_ladder[:-1]):
            if p == level:
                return decimal_ladder[i + 1]

        return current_potency
