"""
Geriatric Degenerative Disease & Low-Potency Organic Support Engine (Phase 28).
Prevents catastrophic high-potency aggravations in elderly patients with exhausted vitality
and deep structural pathology, enforcing organopathic support and gentle LM/decimal scales.
"""
from app.models.clinical import GeriatricAssessment, GeriatricPrescriptionPlan

class GeriatricEngine:
    """
    Evaluates geriatric patients with low susceptibility and deep tissue pathology,
    enforcing safe posological thresholds to preserve vital tone.
    """

    @classmethod
    def evaluate_geriatric_case(cls, assessment: GeriatricAssessment) -> GeriatricPrescriptionPlan:
        """
        Determines appropriate gentle geriatric remedy and guards against high-potency trauma.
        """
        # 1. Rule out high potencies if vitality is low or deep structural pathology exists
        is_fragile = assessment.vitality_score <= 4.0 or assessment.organ_pathology_depth >= 3

        # 2. Match Geriatric Therapeutic Syndrome
        if assessment.cardiorenal_compromise:
            remedy = "Crataegus oxyacantha"
            sphere = "Senile myocardial insufficiency, arteriosclerotic hypertension, cardiorenal strain."
        elif assessment.arteriosclerotic_degeneration:
            remedy = "Baryta carbonica"
            sphere = "Cerebral arteriosclerosis, senile cognitive decline, prostatic induration."
        elif assessment.vitality_score <= 2.5:
            remedy = "Kali phosphoricum"
            sphere = "Profound nervous exhaustion, senile neurasthenia, sinking vital force."
        else:
            remedy = "Conium maculatum"
            sphere = "Senile debility, ascending motor paresis, glandular indurations."

        # 3. Formulate Posology Strategy
        if is_fragile:
            if assessment.cardiorenal_compromise:
                strategy = "LOW_DECIMAL_ORGAN_SUPPORT"
                potency = "3X"
                warning = (
                    "CRITICAL GERIATRIC GUARD: High Centesimal potencies (200C, 1M) strictly contraindicated "
                    "due to exhausted vital reserve and organic damage (Kent Observation 1 risk). "
                    "Prescribe low decimal (3X/6X) organ support twice daily in water."
                )
            else:
                strategy = "50_MILLESIMAL_MINIMAL"
                potency = "LM 0/1"
                warning = (
                    "Prescribe 50-Millesimal (LM 0/1) aqueous dose with 2 gentle succussions. "
                    "Provides dynamic cure without danger of violent medicinal aggravation."
                )
        else:
            strategy = "LOW_DECIMAL_ORGAN_SUPPORT"
            potency = "6X"
            warning = "Gradual physiological organ support. Monitor vitality weekly."

        return GeriatricPrescriptionPlan(
            indicated_remedy=remedy,
            recommended_potency=potency,
            posology_strategy=strategy,
            safety_warning=warning
        )
