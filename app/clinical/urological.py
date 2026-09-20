"""
Urological & Renal Calculus Symptom Concordance Engine (Phase 36).
Codifies radiating nephrolithiasis vectors (Berberis), terminal dysuria (Sarsaparilla),
and violent scalding tenesmus (Cantharis) per Kent, Boericke, and Clarke.
"""
from typing import Optional
from app.models.clinical import UrologicalProfile, RenalPrescription

class UrologicalEngine:
    """
    Evaluates nephrolithiasis, cystitis, and dysuria based on pain radiation and sedimentology.
    """

    @classmethod
    def evaluate_urological_case(cls, profile: UrologicalProfile) -> RenalPrescription:
        """
        Synthesizes urological symptoms and returns indicated renal simillimum.
        """
        # 1. Berberis Vulgaris: Radiating pains from kidney down ureter to thigh
        if profile.pain_radiation == "KIDNEY_DOWN_URETER_TO_THIGH":
            return RenalPrescription(
                indicated_remedy="Berberis vulgaris",
                recommended_potency="30C",
                affinity=(
                    "Renal and ureteral tract. Radiating, bubbling, stitching pains radiating from renal region "
                    "downwards along the ureter to the bladder, urethra, and spermatic cord / thigh. Red mealy sediment."
                )
            )

        # 2. Sarsaparilla: Severe agony at close of micturition, white sand
        if profile.urinary_pain_timing == "AT_CLOSE_OF_URINATION" or profile.sediment_nature == "WHITE_SAND_MUCUS":
            return RenalPrescription(
                indicated_remedy="Sarsaparilla",
                recommended_potency="200C",
                affinity=(
                    "Severe, unbearable cutting pain in urethra precisely at the close of urination; "
                    "copious white sandy sediment or small gravelly concretions."
                )
            )

        # 3. Cantharis: Violent burning, drop-by-drop scalding tenesmus
        if profile.urinary_pain_timing == "DURING_BURNING_DROP_BY_DROP" or profile.pain_radiation == "BLADDER_NECK_SPASM":
            return RenalPrescription(
                indicated_remedy="Cantharis vesicatoria",
                recommended_potency="200C",
                affinity=(
                    "Violent acute cystitis and bladder neck inflammation. Frenzied, constant urging with intolerable "
                    "burning scalding tenesmus, passing only a few bloody drops at a time."
                )
            )

        # 4. Lycopodium: Right-sided renal colic with red sand
        if profile.sediment_nature == "RED_SAND_URIC_ACID":
            return RenalPrescription(
                indicated_remedy="Lycopodium clavatum",
                recommended_potency="200C",
                affinity=(
                    "Right-sided nephrolithiasis; copious red sandy deposit (uric acid crystals) in urine. "
                    "Child screams with backache before micturition."
                )
            )

        # Default fallback
        return RenalPrescription(
            indicated_remedy="Berberis vulgaris",
            recommended_potency="30C",
            affinity="General urinary and renal tract support."
        )
