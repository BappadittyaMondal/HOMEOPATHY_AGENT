"""
Boger Boenninghausen Characteristics & Repertory (BBCR 1905) Pathological Indexer (Phase 09).
Maps Tissue Affinity, Lateral Directionality, and Pathological Generals to remedies.
"""
from typing import List, Dict, Optional
from app.models.bbcr import (
    TissueAffinityEnum,
    LateralAffinityEnum,
    PathologicalGeneralEnum,
    BBCRRemedyProfile
)

class BBCRPathologicalIndexer:
    """
    Evaluates remedies against Dr. C.M. Boger's clinical pathological generals,
    tissue affinities, and directional modalities.
    """

    REMEDY_PROFILES: Dict[str, BBCRRemedyProfile] = {
        "Lycopodium clavatum": BBCRRemedyProfile(
            remedy_name="Lycopodium clavatum",
            primary_tissues=[TissueAffinityEnum.HEPATOBILIARY, TissueAffinityEnum.MUCOUS_MEMBRANES],
            lateral_affinity=LateralAffinityEnum.RIGHT_TO_LEFT,
            pathological_generals=[PathologicalGeneralEnum.INDURATION_FIBROSIS],
            characteristic_time_key="4 PM to 8 PM"
        ),
        "Lachesis muta": BBCRRemedyProfile(
            remedy_name="Lachesis muta",
            primary_tissues=[TissueAffinityEnum.VASCULAR_CIRCULATORY, TissueAffinityEnum.CENTRAL_NERVOUS_SYSTEM],
            lateral_affinity=LateralAffinityEnum.LEFT_TO_RIGHT,
            pathological_generals=[PathologicalGeneralEnum.HEMORRHAGIC_DIATHESIS, PathologicalGeneralEnum.GANGRENOUS_NECROSIS],
            characteristic_time_key="Worse after sleep"
        ),
        "Bryonia alba": BBCRRemedyProfile(
            remedy_name="Bryonia alba",
            primary_tissues=[TissueAffinityEnum.SEROUS_FIBROUS_TISSUES, TissueAffinityEnum.HEPATOBILIARY],
            lateral_affinity=LateralAffinityEnum.RIGHT_SIDED,
            pathological_generals=[PathologicalGeneralEnum.INDURATION_FIBROSIS],
            characteristic_time_key="9 PM"
        ),
        "Phosphorus": BBCRRemedyProfile(
            remedy_name="Phosphorus",
            primary_tissues=[TissueAffinityEnum.VASCULAR_CIRCULATORY, TissueAffinityEnum.BONES_PERIOSTEUM],
            lateral_affinity=LateralAffinityEnum.LEFT_SIDED,
            pathological_generals=[PathologicalGeneralEnum.HEMORRHAGIC_DIATHESIS],
            characteristic_time_key="Twilight / Before midnight"
        ),
        "Hepar sulphuris": BBCRRemedyProfile(
            remedy_name="Hepar sulphuris",
            primary_tissues=[TissueAffinityEnum.SKIN_EPITHELIUM, TissueAffinityEnum.LYMPHATIC_GLANDS],
            lateral_affinity=LateralAffinityEnum.BILATERAL,
            pathological_generals=[PathologicalGeneralEnum.SUPPURATION],
            characteristic_time_key="Cool weather / Dry cold winds"
        ),
        "Silicea": BBCRRemedyProfile(
            remedy_name="Silicea",
            primary_tissues=[TissueAffinityEnum.BONES_PERIOSTEUM, TissueAffinityEnum.LYMPHATIC_GLANDS],
            lateral_affinity=LateralAffinityEnum.RIGHT_SIDED,
            pathological_generals=[PathologicalGeneralEnum.SUPPURATION, PathologicalGeneralEnum.INDURATION_FIBROSIS],
            characteristic_time_key="New moon / Full moon"
        )
    }

    @classmethod
    def get_profile(cls, remedy_name: str) -> Optional[BBCRRemedyProfile]:
        return cls.REMEDY_PROFILES.get(remedy_name)

    @classmethod
    def score_pathological_fit(
        cls, 
        remedy_name: str,
        target_tissues: List[TissueAffinityEnum],
        target_laterality: Optional[LateralAffinityEnum] = None,
        target_pathology: Optional[PathologicalGeneralEnum] = None
    ) -> float:
        """
        Calculates Boger affinity score from 0.0 to 1.0 based on tissue, laterality, and pathological generals.
        """
        profile = cls.get_profile(remedy_name)
        if not profile:
            return 0.5  # Neutral fallback for unindexed remedies

        score = 0.0
        total_possible = 0.0

        # 1. Tissue Affinity match (Weight 0.5)
        total_possible += 0.5
        matched_tissues = set(target_tissues).intersection(set(profile.primary_tissues))
        if matched_tissues:
            score += 0.5 * (len(matched_tissues) / max(1, len(target_tissues)))

        # 2. Laterality match (Weight 0.3)
        if target_laterality:
            total_possible += 0.3
            if profile.lateral_affinity == target_laterality:
                score += 0.3
            elif (target_laterality == LateralAffinityEnum.RIGHT_SIDED and 
                  profile.lateral_affinity == LateralAffinityEnum.RIGHT_TO_LEFT):
                score += 0.25
            elif (target_laterality == LateralAffinityEnum.LEFT_SIDED and 
                  profile.lateral_affinity == LateralAffinityEnum.LEFT_TO_RIGHT):
                score += 0.25

        # 3. Pathological General match (Weight 0.2)
        if target_pathology:
            total_possible += 0.2
            if target_pathology in profile.pathological_generals:
                score += 0.2

        return round(score / total_possible, 3) if total_possible > 0 else 0.0
