"""
Gastrointestinal, Hepatobiliary & Dyspeptic Repertory Engine (Phase 33).
Codifies postprandial dyspepsia patterns, ineffectual urging, hepatic scapular reflex pain,
and chronobiological gastric modalities per Kent, Boericke, and Nash.
"""
from typing import List, Optional
from app.models.clinical import GastrointestinalProfile, GastrointestinalPrescription

class GastrointestinalEngine:
    """
    Evaluates dyspeptic, hepatic, and intestinal syndromes based on distinct clinical modalities.
    """

    @classmethod
    def evaluate_gastrointestinal_case(cls, profile: GastrointestinalProfile) -> GastrointestinalPrescription:
        """
        Synthesizes gastrointestinal modalities and returns indicated simillimum.
        """
        foods_str = " ".join(profile.food_modalities).lower()

        # 1. Chelidonium: Constant pain under inferior angle of right scapula, hepatic jaundice
        if "right scapula" in foods_str or "jaundice" in profile.dyspepsia_type.lower() or "scapula" in profile.dyspepsia_type.lower():
            return GastrointestinalPrescription(
                indicated_remedy="Chelidonium majus",
                recommended_potency="30C",
                clinical_focus=(
                    "Hepatobiliary congestion, sluggish portal system, jaundice. "
                    "Characteristic fixed pain under lower inner angle of right scapula; desires hot drinks."
                )
            )

        # 2. Lycopodium: 4:00 PM - 8:00 PM, bloating immediately after eating a little
        if profile.time_modality == "4_PM_TO_8_PM" or profile.dyspepsia_type == "POSTPRANDIAL_BLOATING_IMMEDIATE":
            return GastrointestinalPrescription(
                indicated_remedy="Lycopodium clavatum",
                recommended_potency="200C",
                clinical_focus=(
                    "Flatulent dyspepsia; sensation of full satiety after a few mouthfuls; "
                    "marked aggravation 4:00 PM to 8:00 PM; desires warm drinks and sweets."
                )
            )

        # 3. Nux Vomica: Ineffectual urging, morning hangover dyspepsia, spicy foods/alcohol
        if profile.stool_character == "INEFFECTUAL_CONSTANT_URGING" or profile.time_modality == "MORNING_AFTER_STIMULANTS":
            return GastrointestinalPrescription(
                indicated_remedy="Strychnos nux-vomica",
                recommended_potency="200C",
                clinical_focus=(
                    "Gastric derangement from sedentary lifestyle, alcohol, coffee, and stress. "
                    "Ineffectual frequent urging to stool; sour bitter eructations; irritable disposition."
                )
            )

        # 4. Sulphur: 11:00 AM sinking sensation, 5:00 AM diarrhea driving out of bed
        if profile.stool_character == "DIARRHEA_DRIVES_OUT_OF_BED_5AM" or "11 am" in foods_str:
            return GastrointestinalPrescription(
                indicated_remedy="Sulphur",
                recommended_potency="200C",
                clinical_focus=(
                    "All-gone, sinking feeling at epigastrium at 11:00 AM; early morning painless diarrhea "
                    "forcing patient precipitately out of bed; red burning anal orifice."
                )
            )

        # 5. Carbo Veg: Upper abdominal tympanites, air hunger, relieved by eructation
        if "air hunger" in foods_str or "fanning" in foods_str:
            return GastrointestinalPrescription(
                indicated_remedy="Carbo vegetabilis",
                recommended_potency="200C",
                clinical_focus=(
                    "Excessive gastrointestinal tympanitic distension; patient desires to be fanned rapidly; "
                    "cold breath and extremities; temporary relief from belching."
                )
            )

        # Default fallback
        return GastrointestinalPrescription(
            indicated_remedy="Strychnos nux-vomica",
            recommended_potency="30C",
            clinical_focus="General hepatic and digestive harmonization."
        )
