"""
Unit Tests for Phase 29: Female Reproductive Health & Menstrual Modalities Engine.
"""
from app.clinical.female_health import FemaleHealthEngine
from app.models.clinical import MenstrualModalityProfile

def test_female_health_sepia_bearing_down():
    """Verify Sepia for severe bearing-down pelvic sensation and emotional indifference."""
    profile = MenstrualModalityProfile(
        cycle_length_days=35,
        flow_nature="SCANTY",
        flow_timing="DELAYED_SUPPRESSED",
        modality_with_flow="WANDERING",
        concomitants=["bearing down sensation as if organs would escape", "must cross legs tightly", "indifference to family"]
    )
    rx = FemaleHealthEngine.evaluate_menstrual_case(profile)
    assert rx.indicated_remedy == "Sepia officinalis"
    assert rx.recommended_potency == "200C"
    assert "protruding" in rx.key_concordance.lower()

def test_female_health_lachesis_relief_on_flow():
    """Verify Lachesis for dramatic relief as soon as flow begins."""
    profile = MenstrualModalityProfile(
        cycle_length_days=28,
        flow_nature="DARK_CLOTTED",
        flow_timing="REGULAR",
        modality_with_flow="BETTER_WHEN_FLOW_FLOWS",
        concomitants=["left ovary exquisitely tender", "intolerance of tight waistband"]
    )
    rx = FemaleHealthEngine.evaluate_menstrual_case(profile)
    assert rx.indicated_remedy == "Lachesis muta"
    assert "flow onset" in rx.key_concordance.lower()

def test_female_health_pulsatilla_delayed_scanty():
    """Verify Pulsatilla for delayed, scanty menses with weeping disposition."""
    profile = MenstrualModalityProfile(
        cycle_length_days=42,
        flow_nature="SCANTY",
        flow_timing="DELAYED_SUPPRESSED",
        modality_with_flow="WANDERING",
        concomitants=["weeps easily when speaking", "got feet chilled and wet"]
    )
    rx = FemaleHealthEngine.evaluate_menstrual_case(profile)
    assert rx.indicated_remedy == "Pulsatilla pratensis"
    assert rx.recommended_potency == "30C"

def test_female_health_cimicifuga_flow_pain():
    """Verify Cimicifuga where dysmenorrhea is directly proportional to flow."""
    profile = MenstrualModalityProfile(
        cycle_length_days=28,
        flow_nature="DARK_CLOTTED",
        flow_timing="REGULAR",
        modality_with_flow="PAIN_PROPORTIONAL_TO_FLOW",
        concomitants=["severe neuralgic shooting pains from hip to hip"]
    )
    rx = FemaleHealthEngine.evaluate_menstrual_case(profile)
    assert rx.indicated_remedy == "Cimicifuga racemosa"
