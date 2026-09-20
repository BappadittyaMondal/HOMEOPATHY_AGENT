"""
Susceptibility, Vital Force & Constitutional Tone Assessment Engine (Phase 15).
Calculates objective Posology Scaling Factor sigma = (S * V) / (Delta_T + 1.0).
"""
from typing import Optional
from app.models.vitality import ConstitutionTemperamentEnum, PatientVitalityAssessment

class VitalityAssessmentEngine:
    """
    Evaluates patient dynamic susceptibility, vital reserve, and structural pathology depth.
    Protects frail patients with deep tissue pathology from destructive high-potency aggravations.
    """

    @classmethod
    def assess_patient(
        cls,
        age_years: int,
        temperament: ConstitutionTemperamentEnum,
        has_active_inflammation: bool = False,
        pathological_depth: int = 0,
        chronic_disease_duration_months: int = 0,
        is_on_corticosteroids: bool = False
    ) -> PatientVitalityAssessment:
        """
        Calculates S (1..10), V (1..10), Delta_T (0..5), and sigma.
        """
        # 1. Calculate Susceptibility S
        s = 5.0
        if age_years < 16:
            s += 2.5  # Children have high susceptibility
        elif age_years > 70:
            s -= 1.5  # Senile torpor

        if temperament in (ConstitutionTemperamentEnum.NERVOUS_INTELLECTUAL, ConstitutionTemperamentEnum.SANGUINE_ACTIVE):
            s += 1.5
        elif temperament in (ConstitutionTemperamentEnum.PHLEGMATIC_TORPID, ConstitutionTemperamentEnum.DEBILITATED_EXHAUSTED):
            s -= 1.5

        if has_active_inflammation:
            s += 1.0

        s = max(1.0, min(10.0, s))

        # 2. Calculate Vital Force V
        v = 7.0
        if age_years > 75:
            v -= 2.0
        if chronic_disease_duration_months > 60:
            v -= 2.0  # Prolonged exhaustion of vital force
        if is_on_corticosteroids:
            v -= 2.0  # Dynamic suppression

        if temperament == ConstitutionTemperamentEnum.DEBILITATED_EXHAUSTED:
            v -= 2.0

        v = max(1.0, min(10.0, v))
        dt = max(0, min(5, pathological_depth))

        # 3. Calculate Posology Scaling Factor (sigma)
        sigma = (s * v) / (float(dt) + 1.0)
        sigma = round(sigma, 2)

        # 4. Formulate Clinical Recommendation
        if dt >= 3 and s >= 6.0:
            rec = "High susceptibility with deep structural pathology: Strict indication for 50-Millesimal (LM) scale to avert destructive aggravations."
        elif sigma >= 40.0:
            rec = "Robust vitality and high susceptibility: Ideal for High Centesimals (200C, 1M) in single infrequent doses."
        elif sigma <= 15.0:
            rec = "Low vitality or severe organic structural change: Low Decimal/Centesimal potencies (3X, 6X, 6C) or organ-supportive mother tinctures."
        else:
            rec = "Moderate vitality: Medium Centesimals (30C, 200C) indicated."

        return PatientVitalityAssessment(
            susceptibility_score=round(s, 1),
            vital_force_score=round(v, 1),
            pathological_depth=dt,
            temperament=temperament,
            is_suppressed_by_allopathy=is_on_corticosteroids,
            posology_scaling_factor=sigma,
            clinical_recommendation=rec
        )
