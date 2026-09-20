"""
Unit Tests for Phase 04: Strange, Rare, and Peculiar (SRP - Aphorism 153) Isolation Kernel.
"""
from app.repertory.srp_engine import SRPEngine
from app.models.srp import SRPParadoxType

def test_srp_burning_relieved_by_heat():
    """Verify Arsenicum album thermal paradox (burning relieved by heat)."""
    text = "Patient has violent burning gastric pain, intensely relieved by hot water applications."
    res = SRPEngine.analyze_symptom(text)
    assert res.is_srp is True
    assert res.paradox_type == SRPParadoxType.THERMAL_MODALITY_PARADOX
    assert res.aphorism_153_weight == 5.0
    assert "Arsenicum album" in res.characteristic_remedies

def test_srp_fever_without_thirst():
    """Verify Apis / Pulsatilla fever paradox (high fever with total thirstlessness)."""
    text = "High febrile state with flushed face, but thirstless even with dry tongue."
    res = SRPEngine.analyze_symptom(text)
    assert res.is_srp is True
    assert res.paradox_type == SRPParadoxType.THIRST_FEVER_PARADOX
    assert res.aphorism_153_weight >= 4.8
    assert "Apis mellifica" in res.characteristic_remedies
    assert "Pulsatilla" in res.characteristic_remedies

def test_srp_throat_amel_solids():
    """Verify Ignatia physiological paradox (throat pain amel swallowing solids)."""
    text = "Severe sore throat with pain only on empty swallowing, but better swallowing solid food."
    res = SRPEngine.analyze_symptom(text)
    assert res.is_srp is True
    assert res.paradox_type == SRPParadoxType.PHYSIOLOGICAL_CONTRADICTION
    assert res.aphorism_153_weight == 5.0
    assert "Ignatia amara" in res.characteristic_remedies

def test_srp_fear_downward_motion():
    """Verify Borax vestibular paradox (fear of downward motion)."""
    text = "Infant screams with anxiety and fear of downward motion when being put into crib."
    res = SRPEngine.analyze_symptom(text)
    assert res.is_srp is True
    assert res.paradox_type == SRPParadoxType.MOTION_POSTURE_PARADOX
    assert res.aphorism_153_weight == 5.0
    assert "Borax" in res.characteristic_remedies

def test_non_srp_common_symptom():
    """Verify common non-paradoxical symptom receives is_srp=False and weight 1.0."""
    text = "Mild headache in evening after long day at work."
    res = SRPEngine.analyze_symptom(text)
    assert res.is_srp is False
    assert res.paradox_type is None
    assert res.aphorism_153_weight == 1.0
    assert len(res.characteristic_remedies) == 0
