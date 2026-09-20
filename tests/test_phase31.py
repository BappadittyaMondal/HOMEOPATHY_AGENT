"""
Unit Tests for Phase 31: Dermatological Rubric Analysis & Anti-Suppression Warning Engine.
"""
from app.clinical.dermatology import DermatologyEngine
from app.models.clinical import DermatologicalLesion

def test_dermatology_graphites_honey_discharge():
    """Verify Graphites for moist eczema with sticky honey-like exudation."""
    lesion = DermatologicalLesion(
        lesion_type="VESICULAR_MOIST",
        topical_suppression_history=False,
        thermal_modality="WORSE_HEAT_OF_BED",
        discharge_nature="HONEY_LIKE_STICKY"
    )
    eval_res = DermatologyEngine.evaluate_dermatological_case(lesion)
    assert eval_res.indicated_remedy == "Graphites"
    assert eval_res.recommended_potency == "200C"
    assert eval_res.is_suppression_danger is False

def test_dermatology_sulphur_burning_pruritus():
    """Verify Sulphur for voluptuous pruritus worse heat of bed."""
    lesion = DermatologicalLesion(
        lesion_type="PRURITIC_BURNING",
        topical_suppression_history=False,
        thermal_modality="WORSE_HEAT_OF_BED",
        discharge_nature="NONE"
    )
    eval_res = DermatologyEngine.evaluate_dermatological_case(lesion)
    assert eval_res.indicated_remedy == "Sulphur"
    assert eval_res.recommended_potency == "200C"

def test_dermatology_topical_suppression_firewall_alert():
    """Verify anti-suppression warning when topical corticosteroids have been applied."""
    lesion = DermatologicalLesion(
        lesion_type="PRURITIC_BURNING",
        topical_suppression_history=True,
        thermal_modality="WORSE_HEAT_OF_BED",
        discharge_nature="NONE"
    )
    eval_res = DermatologyEngine.evaluate_dermatological_case(lesion)
    assert eval_res.is_suppression_danger is True
    assert "ANTI-SUPPRESSION CLINICAL WARNING" in eval_res.warning
    assert "Hering's Law" in eval_res.warning
