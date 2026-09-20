"""
Unit Tests for Phase 34: Musculoskeletal, Rheumatic & Pain Modality Engine.
"""
from app.clinical.musculoskeletal import MusculoskeletalEngine
from app.models.clinical import MusculoskeletalModality

def test_rheumatic_ledum_cold_applications():
    """Verify Ledum palustre for cold joints relieved by ice cold applications."""
    modality = MusculoskeletalModality(
        motion_modality="RESTLESS_MUST_MOVE",
        temperature_modality="BETTER_COLD_APPLICATIONS",
        tissue_involved="SYNOVIAL_JOINTS"
    )
    rx = MusculoskeletalEngine.evaluate_rheumatic_case(modality)
    assert rx.indicated_remedy == "Ledum palustre"
    assert rx.recommended_potency == "200C"
    assert "ice-cold bathing" in rx.tissue_affinity

def test_rheumatic_bryonia_slightest_motion():
    """Verify Bryonia alba for joint pain aggravated by slightest motion."""
    modality = MusculoskeletalModality(
        motion_modality="WORSE_ANY_SLIGHTEST_MOTION",
        temperature_modality="BETTER_HOT_HEAT",
        tissue_involved="SYNOVIAL_JOINTS"
    )
    rx = MusculoskeletalEngine.evaluate_rheumatic_case(modality)
    assert rx.indicated_remedy == "Bryonia alba"
    assert rx.recommended_potency == "200C"
    assert "synovial" in rx.tissue_affinity.lower()

def test_rheumatic_rhus_tox_first_motion():
    """Verify Rhus tox for stiffness worse first motion and better continued motion."""
    modality = MusculoskeletalModality(
        motion_modality="WORSE_FIRST_MOTION_BETTER_CONTINUED",
        temperature_modality="WORSE_COLD_DAMP",
        tissue_involved="FIBROUS_MUSCLES"
    )
    rx = MusculoskeletalEngine.evaluate_rheumatic_case(modality)
    assert rx.indicated_remedy == "Rhus toxicodendron"
    assert rx.recommended_potency == "200C"

def test_rheumatic_ruta_periosteum():
    """Verify Ruta for periosteal and flexor tendon bruised pain."""
    modality = MusculoskeletalModality(
        motion_modality="WORSE_FIRST_MOTION_BETTER_CONTINUED",
        temperature_modality="WORSE_COLD_DAMP",
        tissue_involved="PERIOSTEUM_TENDONS"
    )
    rx = MusculoskeletalEngine.evaluate_rheumatic_case(modality)
    assert rx.indicated_remedy == "Ruta graveolens"
    assert rx.recommended_potency == "30C"
    assert "periosteum" in rx.tissue_affinity.lower()
