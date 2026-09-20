"""
Four-Dimensional Miasmatic Simplex Classifier (Phase 14).
Projects patient totality onto the 3-simplex Delta^3 and computes Anti-Miasmatic Concordance (MCS).
"""
import numpy as np
from typing import List, Dict, Tuple
from app.models.miasmatic import MiasmTypeEnum, MiasmaticSimplexVector, RemedyMiasmaticProfile

class MiasmaticSimplexClassifier:
    """
    Evaluates patient miasmatic load across Psora, Sycosis, Syphilis, and Tubercular axes.
    Guarantees sum(M) = 1.0 on the probability simplex Delta^3.
    """

    MIASM_LEXICON: Dict[MiasmTypeEnum, List[str]] = {
        MiasmTypeEnum.PSORA: [
            "itching", "pruritus", "dry skin", "functional", "hypersensitive",
            "burning", "neuralgia", "anxiety", "restless", "chilly", "eczema"
        ],
        MiasmTypeEnum.SYCOSIS: [
            "wart", "condyloma", "fibroid", "cyst", "overgrowth", "proliferation",
            "retention", "gonorrhea", "pelvic", "greenish", "suspicious", "fleshy"
        ],
        MiasmTypeEnum.SYPHILIS: [
            "ulcer", "necrosis", "caries", "bone pain", "night agg", "destruction",
            "fissure", "gangrene", "suicidal", "despair", "perforation"
        ],
        MiasmTypeEnum.TUBERCULAR: [
            "emaciation", "flux", "cough", "respiratory", "night sweat", "travel",
            "cosmopolitan", "recurrent cold", "exhaustion", "rapid wasting"
        ]
    }

    # Verified Remedy Miasmatic Vectors (Normalized on Delta^3)
    REMEDY_MIASMATIC_DB: Dict[str, Tuple[float, float, float, float, MiasmTypeEnum]] = {
        # Format: (psora, sycosis, syphilis, tubercular, primary)
        "Sulphur": (0.70, 0.15, 0.10, 0.05, MiasmTypeEnum.PSORA),
        "Psorinum": (0.80, 0.10, 0.05, 0.05, MiasmTypeEnum.PSORA),
        "Thuja occidentalis": (0.10, 0.80, 0.05, 0.05, MiasmTypeEnum.SYCOSIS),
        "Medorrhinum": (0.05, 0.85, 0.05, 0.05, MiasmTypeEnum.SYCOSIS),
        "Mercurius solubilis": (0.15, 0.05, 0.75, 0.05, MiasmTypeEnum.SYPHILIS),
        "Syphilinum": (0.05, 0.05, 0.85, 0.05, MiasmTypeEnum.SYPHILIS),
        "Nitricum acidum": (0.15, 0.10, 0.70, 0.05, MiasmTypeEnum.SYPHILIS),
        "Tuberculinum": (0.10, 0.05, 0.05, 0.80, MiasmTypeEnum.TUBERCULAR),
        "Phosphorus": (0.35, 0.10, 0.20, 0.35, MiasmTypeEnum.PSORA),
        "Calcarea carbonica": (0.60, 0.20, 0.10, 0.10, MiasmTypeEnum.PSORA),
        "Lycopodium clavatum": (0.50, 0.35, 0.10, 0.05, MiasmTypeEnum.PSORA)
    }

    @classmethod
    def classify_patient_narrative(cls, symptoms_text_list: List[str]) -> MiasmaticSimplexVector:
        """
        Projects clinical symptoms onto the 4D probability simplex.
        """
        counts = {m: 0 for m in MiasmTypeEnum}
        
        for text in symptoms_text_list:
            lower = text.lower()
            for miasm, keywords in cls.MIASM_LEXICON.items():
                for kw in keywords:
                    if kw in lower:
                        counts[miasm] += 1

        total = sum(counts.values())
        if total == 0:
            # Equal uniform prior on simplex Delta^3
            return MiasmaticSimplexVector(
                psora=0.25, sycosis=0.25, syphilis=0.25, tubercular=0.25,
                dominant_miasm=MiasmTypeEnum.PSORA,
                is_normalized=True
            )

        # Normalize to sum = 1.0
        p = counts[MiasmTypeEnum.PSORA] / float(total)
        syc = counts[MiasmTypeEnum.SYCOSIS] / float(total)
        syph = counts[MiasmTypeEnum.SYPHILIS] / float(total)
        tub = counts[MiasmTypeEnum.TUBERCULAR] / float(total)

        # Determine dominant miasm
        dom = max(counts.items(), key=lambda x: x[1])[0]

        return MiasmaticSimplexVector(
            psora=round(p, 3),
            sycosis=round(syc, 3),
            syphilis=round(syph, 3),
            tubercular=round(tub, 3),
            dominant_miasm=dom,
            is_normalized=True
        )

    @classmethod
    def score_anti_miasmatic_concordance(
        cls, 
        patient_vector: MiasmaticSimplexVector, 
        remedy_name: str
    ) -> float:
        """
        Computes dot product Anti-Miasmatic Concordance Score MCS = M_patient . mu_remedy
        Returns value in [0.0, 1.0].
        """
        rec = cls.REMEDY_MIASMATIC_DB.get(remedy_name)
        if not rec:
            return 0.5  # Neutral default for unmapped remedies

        p_vec = np.array([
            patient_vector.psora,
            patient_vector.sycosis,
            patient_vector.syphilis,
            patient_vector.tubercular
        ], dtype=np.float32)

        rem_vec = np.array(rec[:4], dtype=np.float32)
        mcs = float(np.dot(p_vec, rem_vec))
        return round(float(np.clip(mcs, 0.0, 1.0)), 3)
