"""
Unit Tests for Phase 27: Pediatric Constitutional Types & Infant Posology Engine.
"""
from app.clinical.pediatric import PediatricEngine
from app.models.clinical import PediatricConstitution

def test_infant_calcarea_carb_aqueous_droplet():
    """Verify infant Calcarea carb diagnosis and mandatory liquid aqueous administration."""
    profile = PediatricConstitution(
        age_months=8,
        weight_kg=8.5,
        fontanelles_closed=False,
        dentition_delayed=True,
        sweat_pattern="HEAD_DURING_SLEEP",
        temperament="OBSTINATE_TIRED",
        thermals="CHILLY"
    )
    advice = PediatricEngine.evaluate_pediatric_case(profile)
    assert advice.indicated_remedy == "Calcarea carbonica"
    assert advice.recommended_potency == "30C"
    assert advice.administration_vehicle == "AQUEOUS_DROPLET"
    assert "aspiration risk" in advice.posology_instructions.lower()

def test_toddler_chamomilla_dentition():
    """Verify toddler Chamomilla dentition distress."""
    profile = PediatricConstitution(
        age_months=14,
        weight_kg=10.2,
        fontanelles_closed=True,
        dentition_delayed=False,
        sweat_pattern="NORMAL",
        temperament="IRRITABLE_WANTS_TO_BE_CARRIED",
        thermals="HOT"
    )
    advice = PediatricEngine.evaluate_pediatric_case(profile)
    assert advice.indicated_remedy == "Chamomilla"
    assert advice.recommended_potency == "200C"
    assert advice.administration_vehicle == "SUGAR_GLOBULE_DISSOLVED"

def test_child_baryta_carb():
    """Verify Baryta carb in timid child with developmental delay."""
    profile = PediatricConstitution(
        age_months=48,
        weight_kg=14.0,
        fontanelles_closed=True,
        dentition_delayed=True,
        sweat_pattern="NORMAL",
        temperament="TIMID_FEARFUL",
        thermals="CHILLY"
    )
    advice = PediatricEngine.evaluate_pediatric_case(profile)
    assert advice.indicated_remedy == "Baryta carbonica"
    assert advice.recommended_potency == "200C"
