"""
Unit Tests for Phase 28: Geriatric Degenerative Disease & Low-Potency Support Engine.
"""
from app.clinical.geriatric import GeriatricEngine
from app.models.clinical import GeriatricAssessment

def test_geriatric_cardiorenal_crataegus_low_decimal():
    """Verify Crataegus 3X organ support in fragile cardiorenal geriatric patient."""
    assessment = GeriatricAssessment(
        age_years=78,
        vitality_score=2.8,
        organ_pathology_depth=4,
        arteriosclerotic_degeneration=True,
        cardiorenal_compromise=True
    )
    plan = GeriatricEngine.evaluate_geriatric_case(assessment)
    assert plan.indicated_remedy == "Crataegus oxyacantha"
    assert plan.recommended_potency == "3X"
    assert plan.posology_strategy == "LOW_DECIMAL_ORGAN_SUPPORT"
    assert "strictly contraindicated" in plan.safety_warning.lower()

def test_geriatric_baryta_carb_lm():
    """Verify Baryta carb LM 0/1 in cerebral arteriosclerosis."""
    assessment = GeriatricAssessment(
        age_years=72,
        vitality_score=3.8,
        organ_pathology_depth=3,
        arteriosclerotic_degeneration=True,
        cardiorenal_compromise=False
    )
    plan = GeriatricEngine.evaluate_geriatric_case(assessment)
    assert plan.indicated_remedy == "Baryta carbonica"
    assert plan.recommended_potency == "LM 0/1"
    assert plan.posology_strategy == "50_MILLESIMAL_MINIMAL"

def test_geriatric_profound_prostration_kali_phos():
    """Verify Kali phos in profound vital exhaustion."""
    assessment = GeriatricAssessment(
        age_years=82,
        vitality_score=2.0,
        organ_pathology_depth=2,
        arteriosclerotic_degeneration=False,
        cardiorenal_compromise=False
    )
    plan = GeriatricEngine.evaluate_geriatric_case(assessment)
    assert plan.indicated_remedy == "Kali phosphoricum"
