"""
Dynamic Posology & Potency Selection Calculus (Phase 16).
Calculates exact scale (C, X, LM), potency grade, vehicle, and administration schedule.
"""
from typing import Optional
from app.models.posology import (
    PotencyScaleEnum, 
    PosologyVehicleEnum, 
    PrescribedPosologyProtocol
)
from app.models.vitality import PatientVitalityAssessment

class DynamicPosologyCalculus:
    """
    Computes potency, scale, vehicle, and Hahnemannian repetition schedule.
    Adheres strictly to Aphorisms 246-248 (6th Edition) and Kentian posology.
    """

    @classmethod
    def calculate_protocol(
        cls,
        remedy_name: str,
        vitality: PatientVitalityAssessment,
        is_acute: bool = False
    ) -> PrescribedPosologyProtocol:
        """
        Decision function Phi(S, V, Delta_T, Acute/Chronic).
        """
        s = vitality.susceptibility_score
        v = vitality.vital_force_score
        dt = vitality.pathological_depth
        sigma = vitality.posology_scaling_factor

        # 1. Acute Violent Cases: Split Dose in Water
        if is_acute:
            if sigma >= 35.0:
                potency = "200C"
            else:
                potency = "30C"

            return PrescribedPosologyProtocol(
                remedy_name=remedy_name,
                scale=PotencyScaleEnum.CENTESIMAL,
                potency_grade=potency,
                vehicle=PosologyVehicleEnum.SUCCUSSED_AQUEOUS_SOLUTION,
                administration_schedule=(
                    f"Dissolve 2 globules of {potency} in 100 mL clean water. "
                    "Administer 1 teaspoon every 15 to 30 minutes. Stir vigorously before each dose. "
                    "STOP IMMEDIATELY upon the first clear sign of improvement (Aphorism 246)."
                ),
                placebo_sac_lac_schedule="Follow with Sac Lac No. 30 globules every 2 hours once improvement starts.",
                aphorism_reference="Organon of Medicine, Aphorisms 246, 272",
                rationale="Acute inflammatory flare with rapid progression: split aqueous dose allows gentle repetition until vital reaction begins."
            )

        # 2. Fifty-Millesimal (LM) Scale Trigger:
        # High/moderate susceptibility with structural tissue pathology (Delta_T >= 2 and S >= 5.5 and V >= 4.0)
        # Prevents violent primary aggravations in reactive patients with organic lesions.
        if dt >= 2 and s >= 5.5 and v >= 4.0:
            return PrescribedPosologyProtocol(
                remedy_name=remedy_name,
                scale=PotencyScaleEnum.FIFTY_MILLESIMAL,
                potency_grade="LM 0/1",
                vehicle=PosologyVehicleEnum.SUCCUSSED_AQUEOUS_SOLUTION,
                administration_schedule=(
                    "Dissolve 1 poppy-seed globule of LM 0/1 in 120 mL distilled water + 5 mL alcohol. "
                    "Before each dose, succuss bottle 8-10 times. Take 1 teaspoon (5 mL) into 60 mL water, "
                    "stir thoroughly, and take 1 teaspoon orally once daily in morning on empty stomach."
                ),
                placebo_sac_lac_schedule="Not required during daily LM liquid administration.",
                aphorism_reference="Organon of Medicine (6th Ed), Aphorisms 246-248",
                rationale="High susceptibility with significant structural pathology mandates 50-Millesimal scale to avert violent homeopathic aggravation."
            )

        # 3. Low Vitality / Severe Exhaustion / Low Susceptibility: Low Decimal (3X, 6X, 12X)
        if v <= 3.5 or s <= 4.0 or (dt >= 4 and v <= 4.5):
            return PrescribedPosologyProtocol(
                remedy_name=remedy_name,
                scale=PotencyScaleEnum.DECIMAL,
                potency_grade="6X",
                vehicle=PosologyVehicleEnum.SACCHARUM_LACTIS_POWDER,
                administration_schedule="1 powder of 6X twice daily for 14 days.",
                placebo_sac_lac_schedule="Sac Lac powder as needed.",
                aphorism_reference="Hering's Posology & Boericke's Organotherapy",
                rationale="Severely compromised vital reserves or irreversible structural pathology: low decimal potency supports metabolic function without fatal primary aggravation."
            )

        # 4. High Centesimal Scale (200C, 1M): Robust Chronic Simillimum
        if dt <= 1 and v >= 6.0 and s >= 6.0:
            return PrescribedPosologyProtocol(
                remedy_name=remedy_name,
                scale=PotencyScaleEnum.CENTESIMAL,
                potency_grade="200C",
                vehicle=PosologyVehicleEnum.CANE_SUGAR_GLOBULES_NO_30,
                administration_schedule="Single dose of 4 globules No. 30 dry on tongue at bedtime. Do NOT repeat.",
                placebo_sac_lac_schedule="Sac Lac 1 powder daily at bedtime for 14 to 28 days.",
                aphorism_reference="Organon of Medicine, Aphorism 275-283 & Kent's Philosophy",
                rationale="High vitality with purely functional or dynamic disease: single high-potency dose allows unimpeded vital curative action."
            )

        # 5. Default Standard Chronic: 30C Centesimal
        return PrescribedPosologyProtocol(
            remedy_name=remedy_name,
            scale=PotencyScaleEnum.CENTESIMAL,
            potency_grade="30C",
            vehicle=PosologyVehicleEnum.CANE_SUGAR_GLOBULES_NO_30,
            administration_schedule="Single dose of 4 globules No. 30 dry on tongue. Wait and watch.",
            placebo_sac_lac_schedule="Sac Lac 4 globules daily for 14 days.",
            aphorism_reference="Organon of Medicine, Aphorism 246",
            rationale="Standard moderate vitality chronic presentation: 30C provides safe therapeutic stimulus."
        )
