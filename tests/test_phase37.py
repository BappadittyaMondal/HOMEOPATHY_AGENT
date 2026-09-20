"""
Unit Tests for Phase 37: Neurological, Migraine & Cephalic Topography Engine.
"""
from app.clinical.neurological import NeurologicalEngine
from app.models.clinical import CephalicTopographyProfile

def test_neurological_spigelia_left_supraorbital():
    """Verify Spigelia for left-sided supraorbital neuralgia."""
    profile = CephalicTopographyProfile(
        laterality="LEFT_SIDED",
        pain_pathway="LEFT_SUPRAORBITAL_TO_OCCIPUT",
        associated_symptom="EYEBALL_SORENESS_SUN_CLOCK"
    )
    rx = NeurologicalEngine.evaluate_neurological_case(profile)
    assert rx.indicated_remedy == "Spigelia anthelmia"
    assert rx.recommended_potency == "200C"
    assert "left-sided" in rx.cephalic_affinity.lower()

def test_neurological_sanguinaria_right_eye():
    """Verify Sanguinaria for right-sided migraine settling over right eye."""
    profile = CephalicTopographyProfile(
        laterality="RIGHT_SIDED",
        pain_pathway="OCCIPUT_OVER_VERTEX_SETTLING_RIGHT_EYE",
        associated_symptom="RELIEVED_BY_DARKNESS_AND_SLEEP"
    )
    rx = NeurologicalEngine.evaluate_neurological_case(profile)
    assert rx.indicated_remedy == "Sanguinaria canadensis"
    assert rx.recommended_potency == "200C"
    assert "right eye" in rx.cephalic_affinity.lower()

def test_neurological_gelsemium_ptosis_profuse_urine():
    """Verify Gelsemium for headache with ptosis relieved by profuse urination."""
    profile = CephalicTopographyProfile(
        laterality="OCCIPUT_TO_VERTEX",
        pain_pathway="OCCIPUT_HEAVINESS",
        associated_symptom="PTOSIS_HEAVY_EYELIDS_RELIEVED_PROFUSE_URINATION"
    )
    rx = NeurologicalEngine.evaluate_neurological_case(profile)
    assert rx.indicated_remedy == "Gelsemium sempervirens"
    assert rx.recommended_potency == "200C"
    assert "copious pale urine" in rx.cephalic_affinity

def test_neurological_silicea_nape_ascending_warm_wrap():
    """Verify Silicea for headache ascending from nape relieved by warm wrapping."""
    profile = CephalicTopographyProfile(
        laterality="RIGHT_SIDED",
        pain_pathway="NAPE_ASCENDING_UPWARDS",
        associated_symptom="RELIEVED_BY_WRAPPING_WARMLY"
    )
    rx = NeurologicalEngine.evaluate_neurological_case(profile)
    assert rx.indicated_remedy == "Silicea terra"
    assert rx.recommended_potency == "200C"
    assert "wrapping head up" in rx.cephalic_affinity
