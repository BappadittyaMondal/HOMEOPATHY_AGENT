"""
Dermatological Rubric Analysis & Anti-Suppression Warning Engine (Phase 31).
Enforces Hahnemannian anti-suppression firewalls against topical corticosteroid repression
and codifies characteristic dermatological phenotypes per The Chronic Diseases.
"""
from typing import Optional
from app.models.clinical import DermatologicalLesion, SkinSuppressionEvaluation

class DermatologyEngine:
    """
    Evaluates skin pathologies, discharge viscosities, and thermal modalities,
    while monitoring and preventing dangerous suppressive interventions.
    """

    @classmethod
    def evaluate_dermatological_case(cls, lesion: DermatologicalLesion) -> SkinSuppressionEvaluation:
        """
        Synthesizes skin eruption characteristics and generates anti-suppression alerts.
        """
        # 1. Match Dermatological Simillimum
        if lesion.discharge_nature == "HONEY_LIKE_STICKY" or "flexures" in lesion.lesion_type.lower():
            remedy = "Graphites"
            potency = "200C"
            sphere = "Moist eczema in skin folds, groins, behind ears, with sticky honey-like discharge."
        elif lesion.thermal_modality == "WORSE_HEAT_OF_BED" and lesion.lesion_type == "PRURITIC_BURNING":
            remedy = "Sulphur"
            potency = "200C"
            sphere = "Voluptuous burning itching worse warmth of bed and washing; scratching causes burning."
        elif lesion.lesion_type == "DRY_SCALY_CRACKED" and "winter" in lesion.thermal_modality.lower() or "cracked" in lesion.lesion_type.lower():
            remedy = "Petroleum"
            potency = "30C"
            sphere = "Deep bleeding rhagades, hands rough and cracked, severe winter aggravation."
        elif lesion.discharge_nature == "PUSTULAR_CRUSTED" or "crusts" in lesion.lesion_type.lower():
            remedy = "Mezereum"
            potency = "200C"
            sphere = "Thick hard crusts under which thick yellow-white pus collects; burning neuralgias."
        elif lesion.thermal_modality == "WORSE_COLD_AIR" and lesion.lesion_type == "DRY_SCALY_CRACKED":
            remedy = "Arsenicum album"
            potency = "200C"
            sphere = "Dry scaly bran-like eruptions with intense burning ameliorated by hot applications."
        else:
            remedy = "Sulphur"
            potency = "30C"
            sphere = "Fundamental psoric skin diathesis."

        # 2. Anti-Suppression Alert Mechanism
        if lesion.topical_suppression_history:
            danger = True
            warning = (
                "ANTI-SUPPRESSION CLINICAL WARNING: Patient has a history of topical suppression "
                "(corticosteroids/astringents). Centripetal internalization of psora is imminent. "
                "Prescribe indicated internal dynamic simillimum without external ointments. "
                "Warn patient that external rash may flare temporarily before internal healing completes (Hering's Law)."
            )
        else:
            danger = False
            warning = "No history of topical suppression. Proceed with constitutional internal dynamic treatment."

        return SkinSuppressionEvaluation(
            indicated_remedy=remedy,
            recommended_potency=potency,
            is_suppression_danger=danger,
            warning=warning
        )
