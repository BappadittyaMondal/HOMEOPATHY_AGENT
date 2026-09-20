"""
Iatrogenic Drug Suppression & Tautopathic Cleansing Engine (Phase 38).
Codifies Samuel Hahnemann's Organon Aphorisms 74-76 on allopathic drug-diseases
and formulates sequential tautopathic/isopathic detoxification and clearing protocols.
"""
from typing import Dict, List, Optional
from pydantic import BaseModel

class TautopathicCleansingRequest(BaseModel):
    suppressing_drug_class: str  # e.g., "CORTICOSTEROID", "ANTIBIOTIC", "NSAID", "VACCINE", "CHEMOTHERAPY"
    drug_name: str
    duration_months: int
    presenting_suppression_symptoms: List[str]

class TautopathicCleansingProtocol(BaseModel):
    drug_name: str
    indicated_constitutional_clearing_remedy: str
    tautopathic_remedy: str
    potency_sequence: List[str]
    detox_instructions: str
    aphorism_basis: str = "Organon Aphorisms 74-76: Healing chronic medicinal diseases induced by allopathic drugs"

class TautopathyEngine:
    """
    Evaluates iatrogenic suppression and formulates layered tautopathic detoxification protocols.
    """

    DRUG_CLASS_MAPPING: Dict[str, Dict[str, str]] = {
        "CORTICOSTEROID": {
            "constitutional": "Thuja occidentalis",
            "tautopathic": "Cortisone",
            "notes": "Reversal of adrenal suppression and cellular water retention; skin eruptions may temporarily return."
        },
        "ANTIBIOTIC": {
            "constitutional": "Sulphur",
            "tautopathic": "Penicillinum",
            "notes": "Restoration of intestinal microbiome vitality and elimination of persistent fungal/mycotic layers."
        },
        "NSAID": {
            "constitutional": "Strychnos nux-vomica",
            "tautopathic": "Acidum acetylsalicylicum",
            "notes": "Gastric mucosal restoration and hepatobiliary clearing following chronic analgesic abuse."
        },
        "VACCINE": {
            "constitutional": "Thuja occidentalis",
            "tautopathic": "Vaccininum",
            "notes": "Post-vaccinal vaccinosis clearing; sycotic dyscrasia elimination."
        },
        "CHEMOTHERAPY": {
            "constitutional": "Cadmium sulphuricum",
            "tautopathic": "Carbo vegetabilis",
            "notes": "Profound post-chemotherapeutic cellular prostration, intractable nausea, and cold breath."
        }
    }

    @classmethod
    def generate_cleansing_protocol(
        cls,
        request: TautopathicCleansingRequest
    ) -> TautopathicCleansingProtocol:
        """
        Synthesizes drug suppression history and generates sequential clearing protocol.
        """
        info = cls.DRUG_CLASS_MAPPING.get(request.suppressing_drug_class.upper())
        if not info:
            constitutional = "Strychnos nux-vomica"
            tautopathic = f"Potentized {request.drug_name}"
            notes = "General medicinal detoxification and hepatobiliary clearing."
        else:
            constitutional = info["constitutional"]
            tautopathic = info["tautopathic"]
            notes = info["notes"]

        if request.duration_months >= 12:
            sequence = ["30C", "200C", "1M"]
            regimen = (
                f"CHRONIC DRUG LAYER DETOXIFICATION (>12 months exposure): Begin with {constitutional} 200C "
                f"(single dose) to stimulate vital reactivity. Follow after 14 days with tautopathic {tautopathic} "
                f"in ascending scale: 30C weekly for 2 weeks, then 200C weekly for 2 weeks, then 1M single dose. {notes}"
            )
        else:
            sequence = ["30C", "200C"]
            regimen = (
                f"ACUTE/SUBACUTE DRUG CLEARING (<12 months exposure): Administer {constitutional} 30C twice daily "
                f"for 3 days, followed by tautopathic {tautopathic} 30C once weekly. {notes}"
            )

        return TautopathicCleansingProtocol(
            drug_name=request.drug_name,
            indicated_constitutional_clearing_remedy=constitutional,
            tautopathic_remedy=tautopathic,
            potency_sequence=sequence,
            detox_instructions=regimen
        )
