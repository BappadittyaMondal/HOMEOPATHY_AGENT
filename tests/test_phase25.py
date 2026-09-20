"""
Unit Tests for Phase 25: Bach-Paterson Bowel Nosodes Engine.
"""
from app.safety.bowel_nosodes import BowelNosodeEngine
from app.models.safety import ToxicitySafetyStatus

def test_bowel_nosode_profile_retrieval():
    """Verify retrieval of classical Bach-Paterson bowel nosode profiles."""
    morgan = BowelNosodeEngine.get_profile("Morgan Pure")
    assert morgan is not None
    assert morgan.bach_paterson_group == "Morgan (B. morgani)"
    assert "Sulphur" in morgan.related_non_bowel_remedies
    assert any("pruritus" in s.lower() for s in morgan.dysbiosis_symptoms)

    proteus = BowelNosodeEngine.get_profile("Proteus")
    assert proteus is not None
    assert "Natrum muriaticum" in proteus.related_non_bowel_remedies

def test_find_bowel_nosode_for_constitutional_remedy():
    """Verify mapping of constitutional remedies to corresponding bowel nosodes."""
    sulph_nosodes = BowelNosodeEngine.find_by_constitutional_remedy("Sulphur")
    assert len(sulph_nosodes) >= 1
    assert any(n.nosode_name == "Morgan Pure" for n in sulph_nosodes)

    nat_mur_nosodes = BowelNosodeEngine.find_by_constitutional_remedy("Natrum muriaticum")
    assert any(n.nosode_name == "Proteus" for n in nat_mur_nosodes)

    phos_nosodes = BowelNosodeEngine.find_by_constitutional_remedy("Phosphorus")
    assert any(n.nosode_name == "Gaertner" for n in phos_nosodes)

def test_bowel_nosode_repetition_lockout():
    """Verify strict 3-month lockout on bowel nosode repetition."""
    # Attempting to repeat within 1 month
    eval_early = BowelNosodeEngine.evaluate_prescription("Morgan Pure", months_since_prior=1)
    assert eval_early["status"] == ToxicitySafetyStatus.HARD_BLOCKED
    assert eval_early["permitted"] is False
    assert "PATERSION LOCKOUT VIOLATION" in eval_early["message"]

    # Prescribing after 4 months
    eval_safe = BowelNosodeEngine.evaluate_prescription("Morgan Pure", months_since_prior=4)
    assert eval_safe["status"] == ToxicitySafetyStatus.APPROVED
    assert eval_safe["permitted"] is True

def test_non_bowel_nosode():
    """Verify non-bowel remedies pass through cleanly."""
    eval_non = BowelNosodeEngine.evaluate_prescription("Aconitum napellus")
    assert eval_non["status"] == ToxicitySafetyStatus.APPROVED
    assert eval_non["permitted"] is True
