"""
Unit Tests for Phase 35: Cardiovascular & Peripheral Vascular Decision Support Engine.
"""
from app.clinical.cardiovascular import CardiovascularEngine
from app.models.clinical import CardiovascularProfile

def test_cardiovascular_cactus_iron_band():
    """Verify Cactus grandiflorus for sensation of heart clutched by an iron band."""
    profile = CardiovascularProfile(
        symptom_syndrome="CONSTRICTION_IRON_BAND",
        pulse_character="RAPID_HARD_FULL",
        chest_concomitants=["heart feels grasped by iron hand", "shooting pain down left arm"]
    )
    rx = CardiovascularEngine.evaluate_cardiovascular_case(profile)
    assert rx.indicated_remedy == "Cactus grandiflorus"
    assert rx.recommended_potency == "30C"
    assert "iron hand" in rx.statutory_safety_caution.lower()

def test_cardiovascular_digitalis_bradycardia_safety():
    """Verify Digitalis purpurea for severe bradycardia with statutory safety alert."""
    profile = CardiovascularProfile(
        symptom_syndrome="ARRHYTHMIC_BRADYCARDIA",
        pulse_character="SLOW_IRREGULAR",
        chest_concomitants=["heart feels like it would stop if moved", "sinking at epigastrium"]
    )
    rx = CardiovascularEngine.evaluate_cardiovascular_case(profile)
    assert rx.indicated_remedy == "Digitalis purpurea"
    assert rx.recommended_potency == "30C"
    assert "STATUTORY SAFETY MANDATE" in rx.statutory_safety_caution

def test_cardiovascular_crataegus_myocardial_tonic():
    """Verify Crataegus for chronic myocardial debility and exertion dyspnea."""
    profile = CardiovascularProfile(
        symptom_syndrome="CARDIAC_HYPERTROPHY_DEBILITY",
        pulse_character="THREADY_WEAK",
        chest_concomitants=["dyspnea on exertion", "failing compensation"]
    )
    rx = CardiovascularEngine.evaluate_cardiovascular_case(profile)
    assert rx.indicated_remedy == "Crataegus oxyacantha"
    assert rx.recommended_potency == "Q"
    assert "myocardial tonic" in rx.statutory_safety_caution.lower()

def test_cardiovascular_lachesis_constriction():
    """Verify Lachesis for intolerance of neck constriction and suffocative waking."""
    profile = CardiovascularProfile(
        symptom_syndrome="EXTREME_VENOUS_STASIS",
        pulse_character="RAPID_HARD_FULL",
        chest_concomitants=["cannot bear tight collar", "wakes suffocating from sleep"]
    )
    rx = CardiovascularEngine.evaluate_cardiovascular_case(profile)
    assert rx.indicated_remedy == "Lachesis muta"
    assert rx.recommended_potency == "200C"
