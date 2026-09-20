"""
Pediatric Constitutional Types & Infant Posology Calculation Engine (Phase 27).
Codifies pediatric constitutional profiling (Calc-c, Calc-p, Silicea, Chamomilla, Baryta-c)
and liquid aqueous droplet posology protocols to eliminate pediatric choking hazards.
"""
from typing import Optional
from app.models.clinical import PediatricConstitution, PediatricDoseAdvice

class PediatricEngine:
    """
    Evaluates infant and child clinical presentations, matches classical pediatric constitutions,
    and calculates safe pediatric posological administration modes.
    """

    @classmethod
    def evaluate_pediatric_case(cls, profile: PediatricConstitution) -> PediatricDoseAdvice:
        """
        Synthesizes pediatric constitution and returns indicated remedy and safe administration route.
        """
        # 1. Evaluate Constitutional Remedy
        if profile.dentition_delayed and profile.sweat_pattern == "HEAD_DURING_SLEEP" and profile.thermals == "CHILLY":
            indicated = "Calcarea carbonica"
            rationale = "Fat, flabby, large open fontanelles with profuse nocturnal head sweat and slow dentition."
        elif "IRRITABLE" in profile.temperament and "CARRIED" in profile.temperament:
            indicated = "Chamomilla"
            rationale = "Extreme petulance during dentition; quiet only when constantly carried."
        elif not profile.fontanelles_closed and profile.temperament == "OBSTINATE_TIRED":
            indicated = "Calcarea phosphorica"
            rationale = "Rachitic slow bone development, delayed fontanelle closure, growing pains."
        elif profile.temperament == "TIMID_FEARFUL" and profile.dentition_delayed:
            indicated = "Baryta carbonica"
            rationale = "Delayed developmental milestones, glandular enlargement, extreme shyness."
        elif profile.sweat_pattern == "SOUR_SMELL":
            indicated = "Rheum officinale"
            rationale = "Whole child smells sour despite washing; colic and dentition diarrhea."
        else:
            indicated = "Silicea terra"
            rationale = "Defective assimilation, rachitic diathesis, profuse head/foot sweat."

        # 2. Compute Safe Posology & Route Based on Age
        if profile.age_months < 12:
            # Infant under 1 year: Strict choking hazard prevention
            potency = "30C"
            vehicle = "AQUEOUS_DROPLET"
            instructions = (
                "INFANT SAFETY DIRECTIVE: Strictly avoid dry sugar globules due to aspiration risk. "
                "Dissolve 1 globule in 10 mL of boiled, cooled water. Administer 1 teaspoonful (5 mL) "
                "or 5 droplets by sterile pipette once. Placebo (Sac Lac in water) for subsequent doses."
            )
        elif profile.age_months <= 36:
            # Toddler 1 to 3 years
            potency = "200C"
            vehicle = "SUGAR_GLOBULE_DISSOLVED"
            instructions = (
                "Dissolve 2 No. 20 globules in 10 mL water or administer dissolved on spoon. Single dose."
            )
        else:
            # Child over 3 years
            potency = "200C"
            vehicle = "SUGAR_GLOBULE_DISSOLVED"
            instructions = "Single dose of 2 No. 30 globules allowed to dissolve on tongue under adult supervision."

        return PediatricDoseAdvice(
            indicated_remedy=indicated,
            recommended_potency=potency,
            administration_vehicle=vehicle,
            posology_instructions=instructions
        )
