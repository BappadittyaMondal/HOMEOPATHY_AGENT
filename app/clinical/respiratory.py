"""
Respiratory, Allergic Rhinitis & Chronic Bronchial Asthma Engine (Phase 32).
Codifies chronobiological respiratory modalities (1-2 AM, 2-5 AM), postural constraints,
and humid vs dry catarrhal affinities per Kent, Allen, and Boericke.
"""
from typing import Optional
from app.models.clinical import RespiratoryProfile, RespiratoryPrescription

class RespiratoryEngine:
    """
    Evaluates asthma, allergic rhinitis, and pulmonary presentations
    by matching chronobiology, posture, and climatic modalities.
    """

    @classmethod
    def evaluate_respiratory_case(cls, profile: RespiratoryProfile) -> RespiratoryPrescription:
        """
        Determines indicated respiratory simillimum.
        """
        # 1. Arsenicum Album: 1:00 AM - 2:00 AM, cannot lie down, must sit bent forward
        if profile.time_aggravation == "1_AM_TO_2_AM" or (
            profile.condition_category == "BRONCHIAL_ASTHMA" and profile.postural_modality == "MUST_SIT_BENT_FORWARD" and profile.weather_modality == "DRY_COLD_WIND"
        ):
            return RespiratoryPrescription(
                indicated_remedy="Arsenicum album",
                recommended_potency="200C",
                clinical_sphere=(
                    "Nocturnal suffocative asthma past midnight (1-2 AM), extreme anguish and prostration, "
                    "cannot lie down, burning in chest relieved by warm drinks."
                )
            )

        # 2. Kali Carbonicum: 2:00 AM - 5:00 AM (3 AM), must sit upright with elbows on knees
        if profile.time_aggravation == "2_AM_TO_5_AM" or profile.postural_modality == "MUST_SIT_BENT_FORWARD":
            return RespiratoryPrescription(
                indicated_remedy="Kali carbonicum",
                recommended_potency="200C",
                clinical_sphere=(
                    "Asthmatic paroxysms strictly between 2:00 AM and 5:00 AM (peaking at 3:00 AM). "
                    "Must sit bent forward with elbows on knees; bag-like puffiness of upper eyelids."
                )
            )

        # 3. Natrum Sulphuricum: Humid asthma in damp weather, holds chest
        if profile.weather_modality == "COLD_DAMP_FOGGY" or "humid" in profile.condition_category.lower():
            return RespiratoryPrescription(
                indicated_remedy="Natrum sulphuricum",
                recommended_potency="200C",
                clinical_sphere=(
                    "Hydrogenoid sycotic asthma aggravated by damp rainy weather or living in basements. "
                    "Loose morning rattling cough; must hold chest firmly with hands while coughing."
                )
            )

        # 4. Bryonia: Worse least motion, holding chest, better lying on painful side
        if profile.postural_modality == "BETTER_LYING_ON_AFFECTED_SIDE" or profile.time_aggravation == "SLIGHTEST_MOTION":
            return RespiratoryPrescription(
                indicated_remedy="Bryonia alba",
                recommended_potency="200C",
                clinical_sphere=(
                    "Sharp stitching pleuritic chest pains; aggravated by the least respiration or motion; "
                    "ameliorated by absolute rest and pressure (lying on painful side)."
                )
            )

        # Default fallback
        return RespiratoryPrescription(
            indicated_remedy="Arsenicum album",
            recommended_potency="30C",
            clinical_sphere="General respiratory constitutional support."
        )
