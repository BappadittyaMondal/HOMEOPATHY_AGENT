"""
Unit Tests for Phase 09: Boger Boenninghausen Characteristics & Repertory (BBCR) Indexer.
"""
from app.repertory.bbcr_indexer import BBCRPathologicalIndexer
from app.models.bbcr import TissueAffinityEnum, LateralAffinityEnum, PathologicalGeneralEnum

def test_bbcr_profiles_remedy_properties():
    """Verify Boger profiles for Lycopodium and Lachesis."""
    lyc = BBCRPathologicalIndexer.get_profile("Lycopodium clavatum")
    assert lyc is not None
    assert TissueAffinityEnum.HEPATOBILIARY in lyc.primary_tissues
    assert lyc.lateral_affinity == LateralAffinityEnum.RIGHT_TO_LEFT
    assert lyc.characteristic_time_key == "4 PM to 8 PM"

    lach = BBCRPathologicalIndexer.get_profile("Lachesis muta")
    assert lach is not None
    assert TissueAffinityEnum.VASCULAR_CIRCULATORY in lach.primary_tissues
    assert lach.lateral_affinity == LateralAffinityEnum.LEFT_TO_RIGHT
    assert PathologicalGeneralEnum.HEMORRHAGIC_DIATHESIS in lach.pathological_generals

def test_bbcr_pathological_fit_scoring():
    """Verify scoring based on tissue affinity, laterality, and pathological generals."""
    # Scenario 1: Liver affection with Right-to-Left directionality
    score_lyc = BBCRPathologicalIndexer.score_pathological_fit(
        remedy_name="Lycopodium clavatum",
        target_tissues=[TissueAffinityEnum.HEPATOBILIARY],
        target_laterality=LateralAffinityEnum.RIGHT_TO_LEFT,
        target_pathology=PathologicalGeneralEnum.INDURATION_FIBROSIS
    )
    assert score_lyc == 1.0

    # Scenario 2: Severe suppuration of bone/periosteum
    score_sil = BBCRPathologicalIndexer.score_pathological_fit(
        remedy_name="Silicea",
        target_tissues=[TissueAffinityEnum.BONES_PERIOSTEUM],
        target_laterality=LateralAffinityEnum.RIGHT_SIDED,
        target_pathology=PathologicalGeneralEnum.SUPPURATION
    )
    assert score_sil == 1.0

    # Scenario 3: Mismatched profile
    score_mismatch = BBCRPathologicalIndexer.score_pathological_fit(
        remedy_name="Lachesis muta",
        target_tissues=[TissueAffinityEnum.BONES_PERIOSTEUM],
        target_laterality=LateralAffinityEnum.RIGHT_SIDED,
        target_pathology=PathologicalGeneralEnum.SUPPURATION
    )
    assert score_mismatch == 0.0
