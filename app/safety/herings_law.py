"""
Hering's Law Directional Vector Engine (Phase 22).
Evaluates post-prescription symptom movements along the 4 classical vectors of cure
and detects iatrogenic disease suppression using an anatomical-vitality hierarchy.
"""
from typing import Dict, List, Optional, Tuple
from app.models.safety import HeringsLawVector

class HeringsLawEngine:
    """
    Mathematical and clinical implementation of Constantine Hering's Law of Cure.
    Evaluates vector H in {0, 1}^4 and identifies disease suppression vs genuine cure.
    """

    # Anatomical Vitality Hierarchy (1 = Most Vital Internal Center, 8 = Least Vital External Periphery)
    ORGAN_VITALITY_HIERARCHY: Dict[str, int] = {
        "mind": 1,
        "psyche": 1,
        "brain": 2,
        "cns": 2,
        "heart": 3,
        "cardiovascular": 3,
        "lungs": 4,
        "respiratory": 4,
        "liver": 5,
        "kidneys": 5,
        "internal_viscera": 5,
        "stomach": 6,
        "intestines": 6,
        "gastrointestinal": 6,
        "joints": 7,
        "muscles": 7,
        "extremities": 7,
        "skin": 8,
        "mucous_membranes": 8,
        "hair_nails": 8
    }

    # Anatomical Vertical Level (1 = Highest / Head, 4 = Lowest / Feet)
    VERTICAL_HIERARCHY: Dict[str, int] = {
        "head": 1,
        "face": 1,
        "throat": 2,
        "chest": 2,
        "trunk": 3,
        "abdomen": 3,
        "upper_limbs": 3,
        "lower_limbs": 4,
        "feet": 4
    }

    @classmethod
    def evaluate_vector(
        cls,
        head_to_extremities: bool = False,
        inside_to_outside: bool = False,
        center_to_periphery: bool = False,
        reverse_chronological_order: bool = False,
        suppressive_inward_movement: bool = False
    ) -> HeringsLawVector:
        """
        Direct Boolean vector evaluation of Hering's 4 axioms.
        """
        score = int(head_to_extremities) + int(inside_to_outside) + int(center_to_periphery) + int(reverse_chronological_order)

        if suppressive_inward_movement:
            return HeringsLawVector(
                head_to_extremities=head_to_extremities,
                inside_to_outside=False,
                center_to_periphery=center_to_periphery,
                reverse_chronological_order=reverse_chronological_order,
                concordance_score=score,
                is_true_cure=False,
                iatrogenic_suppression_detected=True,
                clinical_verdict=(
                    "DANGEROUS SUPPRESSION DETECTED: Symptoms are moving centripetally into more vital organs. "
                    "Remedy action must be stopped or antidoted immediately."
                )
            )

        if score >= 2:
            return HeringsLawVector(
                head_to_extremities=head_to_extremities,
                inside_to_outside=inside_to_outside,
                center_to_periphery=center_to_periphery,
                reverse_chronological_order=reverse_chronological_order,
                concordance_score=score,
                is_true_cure=True,
                iatrogenic_suppression_detected=False,
                clinical_verdict=(
                    f"TRUE CURE IN PROGRESS (Hering Concordance {score}/4): Disease is departing in accordance "
                    f"with natural laws of cure. Continue placebos (Sac Lac) and do not interfere."
                )
            )
        elif score == 1:
            return HeringsLawVector(
                head_to_extremities=head_to_extremities,
                inside_to_outside=inside_to_outside,
                center_to_periphery=center_to_periphery,
                reverse_chronological_order=reverse_chronological_order,
                concordance_score=score,
                is_true_cure=True,
                iatrogenic_suppression_detected=False,
                clinical_verdict="PARTIAL CONCORDANCE: 1 vector satisfied. Observe closely without repetition."
            )
        else:
            return HeringsLawVector(
                head_to_extremities=False,
                inside_to_outside=False,
                center_to_periphery=False,
                reverse_chronological_order=False,
                concordance_score=0,
                is_true_cure=False,
                iatrogenic_suppression_detected=False,
                clinical_verdict="NON-DIRECTIONAL: No Hering directionality observed. Re-evaluate case totality."
            )

    @classmethod
    def evaluate_symptom_progression(
        cls,
        prior_organ: str,
        current_organ: str,
        reverse_chronological: bool = False
    ) -> HeringsLawVector:
        """
        Evaluates directional movement between prior and newly emerged or remaining symptoms.
        Detects suppression when disease shifts from higher vitality level (e.g. skin 8) to lower level (e.g. lungs 4).
        """
        p_vital = cls.ORGAN_VITALITY_HIERARCHY.get(prior_organ.lower(), 5)
        c_vital = cls.ORGAN_VITALITY_HIERARCHY.get(current_organ.lower(), 5)

        # Inside to outside: from more vital (lower number) to less vital (higher number)
        inside_to_outside = c_vital > p_vital

        # Suppression: from less vital (higher number, e.g. skin 8) to more vital (lower number, e.g. lungs 4)
        is_suppression = c_vital < p_vital

        # Check vertical hierarchy
        p_vert = cls.VERTICAL_HIERARCHY.get(prior_organ.lower())
        c_vert = cls.VERTICAL_HIERARCHY.get(current_organ.lower())
        head_to_extremities = False
        if p_vert is not None and c_vert is not None:
            head_to_extremities = c_vert > p_vert
            if c_vert < p_vert:
                is_suppression = True

        center_to_periphery = inside_to_outside

        return cls.evaluate_vector(
            head_to_extremities=head_to_extremities,
            inside_to_outside=inside_to_outside,
            center_to_periphery=center_to_periphery,
            reverse_chronological_order=reverse_chronological,
            suppressive_inward_movement=is_suppression
        )
