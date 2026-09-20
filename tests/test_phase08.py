"""
Unit Tests for Phase 08: Boenninghausen's Therapeutic Pocket Book (BTPB) Concordance Engine.
"""
from app.repertory.btpb_engine import BTPBConcordanceEngine
from app.models.btpb import BTPBSectionEnum

def test_btpb_sections_enum():
    """Verify BTPB 7 sections are represented."""
    assert len(BTPBSectionEnum) == 7
    assert BTPBSectionEnum.CONCORDANCES == "CONCORDANCES"
    assert BTPBSectionEnum.PARTS_OF_BODY == "PARTS_OF_BODY"

def test_btpb_concordances_belladonna():
    """Verify Belladonna -> Calcarea carbonica chronic complement relationship."""
    concordances = BTPBConcordanceEngine.get_concordances("Belladonna")
    assert len(concordances) >= 2
    top = concordances[0]
    assert top.related_remedy == "Calcarea carbonica"
    assert top.total_concordance_score >= 75
    assert top.relationship_type == "CHRONIC_COMPLEMENT"

def test_btpb_chronic_complement_lookup():
    """Verify quick lookup of chronic complementary remedies."""
    comp_acon = BTPBConcordanceEngine.get_chronic_complement("Aconitum napellus")
    assert comp_acon == "Sulphur"

    comp_puls = BTPBConcordanceEngine.get_chronic_complement("Pulsatilla pratensis")
    assert comp_puls == "Silicea"

    comp_nux = BTPBConcordanceEngine.get_chronic_complement("Nux vomica")
    assert comp_nux == "Sepia officinalis"
