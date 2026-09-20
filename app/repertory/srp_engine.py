"""
Strange, Rare, and Peculiar (SRP - Aphorism 153) Symptom Isolation Engine.
Identifies clinical paradoxes running counter to ordinary disease pathology.
"""
from typing import List, Optional
import re
from app.models.srp import SRPParadoxType, SRPEvaluationResult

class SRPEngine:
    """
    Evaluates clinical text and extracted symptoms against verified Hahnemannian SRP paradoxes.
    Assigns top-tier discriminatory weights (4.8 to 5.0) to characteristic anomalies.
    """

    SRP_DATABASE = [
        {
            "id": "SRP-01",
            "type": SRPParadoxType.THERMAL_MODALITY_PARADOX,
            "patterns": [r"burning.*(?:relieved|better|amel).*(?:heat|hot|warm)"],
            "canonical_rubric": "GENERALITIES - HEAT - flushes of - amel. external heat",
            "weight": 5.0,
            "remedies": ["Arsenicum album"],
            "rationale": "Burning sensations are typically aggravated by heat. Burning relieved by hot applications is an unmistakable characteristic key of Arsenicum album."
        },
        {
            "id": "SRP-02",
            "type": SRPParadoxType.THIRST_FEVER_PARADOX,
            "patterns": [r"(?:fever|heat|febrile).*(?:thirstless|no thirst|without thirst|thirst absent)"],
            "canonical_rubric": "CHILL - THIRST - absent",
            "weight": 4.8,
            "remedies": ["Apis mellifica", "Pulsatilla", "Gelsemium"],
            "rationale": "High inflammatory fever usually drives intense thirst due to insensible water loss. Absence of thirst during burning fever is a striking pathogenetic anomaly (Apis, Pulsatilla, Gelsemium)."
        },
        {
            "id": "SRP-03",
            "type": SRPParadoxType.PHYSIOLOGICAL_CONTRADICTION,
            "patterns": [r"throat.*(?:pain|sore).*(?:better|amel|relieved).*(?:solid|eating|food)"],
            "canonical_rubric": "THROAT - PAIN - swallowing - solids amel.",
            "weight": 5.0,
            "remedies": ["Ignatia amara", "Lachesis muta"],
            "rationale": "Inflamed mucosal ulcerations are normally aggravated by solid bolus passage. Pain relieved by swallowing hard solids while aggravated by empty swallowing is characteristic of Ignatia."
        },
        {
            "id": "SRP-04",
            "type": SRPParadoxType.THERMAL_MODALITY_PARADOX,
            "patterns": [r"toothache.*(?:better|amel|relieved).*(?:ice|cold water|cold)"],
            "canonical_rubric": "TEETH - PAIN - cold - water - amel.",
            "weight": 4.8,
            "remedies": ["Coffea cruda", "Bismuthum", "Bryonia"],
            "rationale": "Pulpitis and dental nerve pain are normally violently aggravated by cold drinks. Relief from holding ice water in the mouth is a verified characteristic of Coffea cruda."
        },
        {
            "id": "SRP-05",
            "type": SRPParadoxType.PHYSIOLOGICAL_CONTRADICTION,
            "patterns": [r"(?:nausea|vomiting).*(?:not relieved|no relief|unrelieved|constant).*after vomiting"],
            "canonical_rubric": "STOMACH - NAUSEA - vomiting - does not amel.",
            "weight": 4.9,
            "remedies": ["Ipecacuanha"],
            "rationale": "Vomiting typically provides temporary relief to gastro-duodenal reflex nausea. Persistent intense nausea unaffected by vomiting is the core SRP symptom of Ipecacuanha."
        },
        {
            "id": "SRP-06",
            "type": SRPParadoxType.MOTION_POSTURE_PARADOX,
            "patterns": [r"fear.*(?:downward|descending|downstairs|elevator)"],
            "canonical_rubric": "MIND - FEAR - downward motion, of",
            "weight": 5.0,
            "remedies": ["Borax", "Gelsemium", "Sanicula"],
            "rationale": "Fear of downward motion is not a generic phobia; it is a profound vestibular-proprioceptive SRP characteristic, predominantly indicating Borax."
        },
        {
            "id": "SRP-07",
            "type": SRPParadoxType.METABOLIC_PARADOX,
            "patterns": [r"(?:losing weight|emaciation|thin|wasting).*(?:good appetite|voracious|eating well|hunger)"],
            "canonical_rubric": "GENERALITIES - EMACIATION - ravenous hunger, with",
            "weight": 4.8,
            "remedies": ["Iodium", "Natrum muriaticum", "Tuberculinum", "Abrotanum"],
            "rationale": "Progressive constitutional emaciation despite ravenous nutritional intake indicates profound cellular assimilation failure (Iodium, Natrum mur)."
        },
        {
            "id": "SRP-08",
            "type": SRPParadoxType.EMOTIONAL_PARADOX,
            "patterns": [r"weep.*(?:music|listening to music)"],
            "canonical_rubric": "MIND - WEEPING - music, from",
            "weight": 4.8,
            "remedies": ["Graphites", "Natrum carbonicum", "Natrum sulphuricum", "Thuja"],
            "rationale": "Involuntary weeping triggered specifically by music reveals high emotional/neuro-sensory resonance, characteristic of Graphites and Natrum salts."
        }
    ]

    @classmethod
    def analyze_symptom(cls, text: str) -> SRPEvaluationResult:
        """
        Scans symptom description for known clinical paradoxes and returns Aphorism 153 evaluation.
        """
        clean_text = text.lower().strip()
        for srp in cls.SRP_DATABASE:
            for pattern in srp["patterns"]:
                if re.search(pattern, clean_text):
                    return SRPEvaluationResult(
                        symptom_text=text,
                        is_srp=True,
                        paradox_type=srp["type"],
                        canonical_rubric=srp["canonical_rubric"],
                        aphorism_153_weight=srp["weight"],
                        characteristic_remedies=srp["remedies"],
                        clinical_rationale=srp["rationale"]
                    )

        # Standard non-SRP symptom
        return SRPEvaluationResult(
            symptom_text=text,
            is_srp=False,
            paradox_type=None,
            canonical_rubric=None,
            aphorism_153_weight=1.0,
            characteristic_remedies=[],
            clinical_rationale="Common or non-paradoxical symptom under ordinary disease pathology."
        )
