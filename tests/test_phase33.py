"""
Unit Tests for Phase 33: Gastrointestinal, Hepatobiliary & Dyspeptic Engine.
"""
from app.clinical.gastrointestinal import GastrointestinalEngine
from app.models.clinical import GastrointestinalProfile

def test_gastrointestinal_chelidonium_scapular_reflex():
    """Verify Chelidonium for hepatobiliary congestion with right scapular pain."""
    profile = GastrointestinalProfile(
        dyspepsia_type="HEPATIC_CONGESTION",
        time_modality="MIDNIGHT",
        stool_character="SHEEP_DUNG_HARD",
        food_modalities=["constant pain under lower right scapula", "desires boiling hot water"]
    )
    rx = GastrointestinalEngine.evaluate_gastrointestinal_case(profile)
    assert rx.indicated_remedy == "Chelidonium majus"
    assert rx.recommended_potency == "30C"
    assert "right scapula" in rx.clinical_focus

def test_gastrointestinal_lycopodium_bloating_4_to_8pm():
    """Verify Lycopodium for 4:00 PM - 8:00 PM flatulence after few mouthfuls."""
    profile = GastrointestinalProfile(
        dyspepsia_type="POSTPRANDIAL_BLOATING_IMMEDIATE",
        time_modality="4_PM_TO_8_PM",
        stool_character="SHEEP_DUNG_HARD",
        food_modalities=["craves sweets", "warm drinks"]
    )
    rx = GastrointestinalEngine.evaluate_gastrointestinal_case(profile)
    assert rx.indicated_remedy == "Lycopodium clavatum"
    assert rx.recommended_potency == "200C"
    assert "4:00 PM to 8:00 PM" in rx.clinical_focus

def test_gastrointestinal_nux_vomica_ineffectual_urging():
    """Verify Nux vomica for sedentary dyspepsia with frequent ineffectual urging."""
    profile = GastrointestinalProfile(
        dyspepsia_type="ACID_PYROSIS_SOUR_ERUCTATION",
        time_modality="MORNING_AFTER_STIMULANTS",
        stool_character="INEFFECTUAL_CONSTANT_URGING",
        food_modalities=["excess coffee and tobacco"]
    )
    rx = GastrointestinalEngine.evaluate_gastrointestinal_case(profile)
    assert rx.indicated_remedy == "Strychnos nux-vomica"
    assert rx.recommended_potency == "200C"

def test_gastrointestinal_sulphur_5am_diarrhea():
    """Verify Sulphur for 5:00 AM diarrhea driving out of bed."""
    profile = GastrointestinalProfile(
        dyspepsia_type="ACID_PYROSIS_SOUR_ERUCTATION",
        time_modality="MIDNIGHT",
        stool_character="DIARRHEA_DRIVES_OUT_OF_BED_5AM",
        food_modalities=["sinking sensation at 11 am"]
    )
    rx = GastrointestinalEngine.evaluate_gastrointestinal_case(profile)
    assert rx.indicated_remedy == "Sulphur"
    assert rx.recommended_potency == "200C"
