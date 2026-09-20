"""
Unit Tests for Phase 32: Respiratory, Allergic Rhinitis & Chronic Asthma Engine.
"""
from app.clinical.respiratory import RespiratoryEngine
from app.models.clinical import RespiratoryProfile

def test_respiratory_arsenicum_midnight_paroxysm():
    """Verify Arsenicum album for suffocative asthma at 1:00 AM - 2:00 AM."""
    profile = RespiratoryProfile(
        condition_category="BRONCHIAL_ASTHMA",
        time_aggravation="1_AM_TO_2_AM",
        postural_modality="CANNOT_LIE_DOWN",
        weather_modality="DRY_COLD_WIND"
    )
    rx = RespiratoryEngine.evaluate_respiratory_case(profile)
    assert rx.indicated_remedy == "Arsenicum album"
    assert rx.recommended_potency == "200C"
    assert "1-2 AM" in rx.clinical_sphere

def test_respiratory_kali_carb_3am_elbows_knees():
    """Verify Kali carbonicum for asthma paroxysm at 2:00 AM - 5:00 AM."""
    profile = RespiratoryProfile(
        condition_category="BRONCHIAL_ASTHMA",
        time_aggravation="2_AM_TO_5_AM",
        postural_modality="MUST_SIT_BENT_FORWARD",
        weather_modality="COLD_DAMP_FOGGY"
    )
    rx = RespiratoryEngine.evaluate_respiratory_case(profile)
    assert rx.indicated_remedy == "Kali carbonicum"
    assert rx.recommended_potency == "200C"
    assert "2:00 AM and 5:00 AM" in rx.clinical_sphere

def test_respiratory_natrum_sulph_humid_asthma():
    """Verify Natrum sulph in humid asthma from damp foggy weather."""
    profile = RespiratoryProfile(
        condition_category="BRONCHIAL_ASTHMA",
        time_aggravation="EVENING_TWILIGHT",
        postural_modality="CANNOT_LIE_DOWN",
        weather_modality="COLD_DAMP_FOGGY"
    )
    rx = RespiratoryEngine.evaluate_respiratory_case(profile)
    assert rx.indicated_remedy == "Natrum sulphuricum"
    assert rx.recommended_potency == "200C"

def test_respiratory_bryonia_motion_pressure():
    """Verify Bryonia alba for dry painful cough relieved by lying on affected side."""
    profile = RespiratoryProfile(
        condition_category="PNEUMONIA",
        time_aggravation="SLIGHTEST_MOTION",
        postural_modality="BETTER_LYING_ON_AFFECTED_SIDE",
        weather_modality="DRY_COLD_WIND"
    )
    rx = RespiratoryEngine.evaluate_respiratory_case(profile)
    assert rx.indicated_remedy == "Bryonia alba"
    assert rx.recommended_potency == "200C"
