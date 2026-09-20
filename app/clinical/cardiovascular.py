"""
Cardiovascular & Peripheral Vascular Decision Support Engine (Phase 35).
Codifies precordial constriction modalities (Cactus iron band), bradycardia (Digitalis),
senile myocardial insufficiency (Crataegus), and vascular engorgement per Kent and Clarke.
"""
from typing import List, Optional
from app.models.clinical import CardiovascularProfile, CardiovascularPrescription

class CardiovascularEngine:
    """
    Evaluates cardiac and vascular syndromes, integrating statutory safety firewalls
    for toxic cardiac glycosides (Digitalis).
    """

    @classmethod
    def evaluate_cardiovascular_case(cls, profile: CardiovascularProfile) -> CardiovascularPrescription:
        """
        Synthesizes cardiovascular modalities and returns indicated simillimum.
        """
        chest_str = " ".join(profile.chest_concomitants).lower()

        # 1. Cactus Grandiflorus: Constriction as of an iron band
        if profile.symptom_syndrome == "CONSTRICTION_IRON_BAND" or "iron band" in chest_str or "clutched" in chest_str:
            return CardiovascularPrescription(
                indicated_remedy="Cactus grandiflorus",
                recommended_potency="30C",
                statutory_safety_caution=(
                    "Sensation of violent constriction as if heart were grasped and squeezed by an iron hand. "
                    "Angina pectoris radiating down left arm to fingers with dyspnea."
                )
            )

        # 2. Digitalis Purpurea: Severe bradycardia, heart stops on motion
        if profile.pulse_character == "SLOW_IRREGULAR" or profile.symptom_syndrome == "ARRHYTHMIC_BRADYCARDIA" or "stops on motion" in chest_str:
            return CardiovascularPrescription(
                indicated_remedy="Digitalis purpurea",
                recommended_potency="30C",
                statutory_safety_caution=(
                    "STATUTORY SAFETY MANDATE: Digitalis cardiac glycoside. Banned below 3X under HPI Schedule E(1). "
                    "Indicated only in dynamic dilutions (30C). Sensation heart would cease beating if moved; extreme bradycardia."
                )
            )

        # 3. Crataegus Oxyacantha: Heart failure, dyspnea on exertion, arteriosclerosis
        if profile.symptom_syndrome == "CARDIAC_HYPERTROPHY_DEBILITY" or "dyspnea on exertion" in chest_str:
            return CardiovascularPrescription(
                indicated_remedy="Crataegus oxyacantha",
                recommended_potency="Q",
                statutory_safety_caution=(
                    "Non-toxic physiological myocardial tonic. Supports myocardial contractility and coronary perfusion. "
                    "Prescribe 10 drops in water twice daily."
                )
            )

        # 4. Lachesis: Intolerance of neck constriction, wakes suffocating
        if "collar" in chest_str or "wakes suffocating" in chest_str:
            return CardiovascularPrescription(
                indicated_remedy="Lachesis muta",
                recommended_potency="200C",
                statutory_safety_caution=(
                    "Crotalid venom. Banned below 6C. Cannot tolerate collar, tie, or constriction at neck. "
                    "Suffocative nocturnal awakening from cardiac distress."
                )
            )

        # Default fallback
        return CardiovascularPrescription(
            indicated_remedy="Crataegus oxyacantha",
            recommended_potency="30C",
            statutory_safety_caution="Cardiovascular circulatory tonic and venous support."
        )
