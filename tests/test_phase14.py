"""
Unit Tests for Phase 14: Four-Dimensional Miasmatic Simplex Classifier.
"""
from app.repertory.miasmatic_engine import MiasmaticSimplexClassifier
from app.models.miasmatic import MiasmTypeEnum

def test_miasmatic_simplex_sycotic_projection():
    """Verify projection of sycotic symptoms onto simplex and anti-miasmatic matching."""
    symptoms = [
        "Patient has large fleshy condylomata and multiple warts on hands.",
        "Pelvic examination reveals uterine fibroid with thick greenish discharge.",
        "MIND: Suspicious of family members, secretive and deceitful."
    ]

    m_vec = MiasmaticSimplexClassifier.classify_patient_narrative(symptoms)
    assert m_vec.is_normalized is True
    assert round(m_vec.psora + m_vec.sycosis + m_vec.syphilis + m_vec.tubercular, 2) == 1.00
    assert m_vec.dominant_miasm == MiasmTypeEnum.SYCOSIS
    assert m_vec.sycosis > 0.60

    # Test Concordance: Thuja should score high, Mercurius should score low
    mcs_thuja = MiasmaticSimplexClassifier.score_anti_miasmatic_concordance(m_vec, "Thuja occidentalis")
    mcs_merc = MiasmaticSimplexClassifier.score_anti_miasmatic_concordance(m_vec, "Mercurius solubilis")

    assert mcs_thuja > 0.65
    assert mcs_merc < 0.25

def test_miasmatic_simplex_syphilitic_projection():
    """Verify projection of syphilitic destructive symptoms."""
    symptoms = [
        "Deep destructive ulcer on tibia with foul necrotic base.",
        "Violent bone pains strictly worse at night, driving patient to despair of recovery."
    ]

    m_vec = MiasmaticSimplexClassifier.classify_patient_narrative(symptoms)
    assert m_vec.dominant_miasm == MiasmTypeEnum.SYPHILIS
    assert m_vec.syphilis > 0.60

    mcs_merc = MiasmaticSimplexClassifier.score_anti_miasmatic_concordance(m_vec, "Mercurius solubilis")
    mcs_thuja = MiasmaticSimplexClassifier.score_anti_miasmatic_concordance(m_vec, "Thuja occidentalis")

    assert mcs_merc > 0.60
    assert mcs_thuja < 0.25
