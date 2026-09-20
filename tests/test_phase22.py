"""
Unit Tests for Phase 22: Hering's Law Directional Vector Engine.
"""
from app.safety.herings_law import HeringsLawEngine

def test_true_curative_vector_inside_to_outside():
    """Verify true cure: progression from vital lungs to peripheral skin with reverse history."""
    vec = HeringsLawEngine.evaluate_symptom_progression(
        prior_organ="lungs",
        current_organ="skin",
        reverse_chronological=True
    )
    assert vec.is_true_cure is True
    assert vec.iatrogenic_suppression_detected is False
    assert vec.inside_to_outside is True
    assert vec.concordance_score >= 2
    assert "TRUE CURE IN PROGRESS" in vec.clinical_verdict

def test_suppression_detection_skin_to_lungs():
    """Verify suppression detection: eczema clearing while asthma erupts."""
    vec = HeringsLawEngine.evaluate_symptom_progression(
        prior_organ="skin",
        current_organ="lungs",
        reverse_chronological=False
    )
    assert vec.is_true_cure is False
    assert vec.iatrogenic_suppression_detected is True
    assert "DANGEROUS SUPPRESSION DETECTED" in vec.clinical_verdict

def test_head_to_extremities_direction():
    """Verify vertical direction from head downwards to extremities."""
    vec = HeringsLawEngine.evaluate_symptom_progression(
        prior_organ="head",
        current_organ="lower_limbs",
        reverse_chronological=False
    )
    assert vec.head_to_extremities is True
    assert vec.iatrogenic_suppression_detected is False

def test_direct_vector_concordance():
    """Verify direct 4D Boolean evaluation."""
    vec = HeringsLawEngine.evaluate_vector(
        head_to_extremities=True,
        inside_to_outside=True,
        center_to_periphery=True,
        reverse_chronological_order=True
    )
    assert vec.concordance_score == 4
    assert vec.is_true_cure is True
    assert vec.iatrogenic_suppression_detected is False

def test_non_directional_progression():
    """Verify handling when no directional movements are identified."""
    vec = HeringsLawEngine.evaluate_vector()
    assert vec.concordance_score == 0
    assert vec.is_true_cure is False
    assert vec.iatrogenic_suppression_detected is False
    assert "NON-DIRECTIONAL" in vec.clinical_verdict
