"""
Unit Tests for Phase 36: Urological & Renal Calculus Symptom Concordance Engine.
"""
from app.clinical.urological import UrologicalEngine
from app.models.clinical import UrologicalProfile

def test_urological_berberis_radiating_colic():
    """Verify Berberis vulgaris for radiating renal colic down the ureter to thigh."""
    profile = UrologicalProfile(
        urinary_pain_timing="DURING_BURNING_DROP_BY_DROP",
        pain_radiation="KIDNEY_DOWN_URETER_TO_THIGH",
        sediment_nature="RED_SAND_URIC_ACID"
    )
    rx = UrologicalEngine.evaluate_urological_case(profile)
    assert rx.indicated_remedy == "Berberis vulgaris"
    assert rx.recommended_potency == "30C"
    assert "ureter to the bladder" in rx.affinity

def test_urological_sarsaparilla_close_of_urination():
    """Verify Sarsaparilla for severe cutting pain at the close of urination."""
    profile = UrologicalProfile(
        urinary_pain_timing="AT_CLOSE_OF_URINATION",
        pain_radiation="LOCALIZED_LUMBAR",
        sediment_nature="WHITE_SAND_MUCUS"
    )
    rx = UrologicalEngine.evaluate_urological_case(profile)
    assert rx.indicated_remedy == "Sarsaparilla"
    assert rx.recommended_potency == "200C"
    assert "close of urination" in rx.affinity

def test_urological_cantharis_violent_tenesmus():
    """Verify Cantharis for violent scalding burning tenesmus drop by drop."""
    profile = UrologicalProfile(
        urinary_pain_timing="DURING_BURNING_DROP_BY_DROP",
        pain_radiation="BLADDER_NECK_SPASM",
        sediment_nature="BLOOD_CLOTS"
    )
    rx = UrologicalEngine.evaluate_urological_case(profile)
    assert rx.indicated_remedy == "Cantharis vesicatoria"
    assert rx.recommended_potency == "200C"

def test_urological_lycopodium_red_sand():
    """Verify Lycopodium for red sand in urine."""
    profile = UrologicalProfile(
        urinary_pain_timing="BEFORE_MICTURITION",
        pain_radiation="LOCALIZED_LUMBAR",
        sediment_nature="RED_SAND_URIC_ACID"
    )
    rx = UrologicalEngine.evaluate_urological_case(profile)
    assert rx.indicated_remedy == "Lycopodium clavatum"
    assert rx.recommended_potency == "200C"
