"""
Unit Tests for Phase 15: Susceptibility & Vital Force Assessment Engine.
"""
from app.repertory.vitality_engine import VitalityAssessmentEngine
from app.models.vitality import ConstitutionTemperamentEnum

def test_vitality_high_susceptibility_robust():
    """Verify high sigma for young nervous/intellectual robust patient."""
    assessment = VitalityAssessmentEngine.assess_patient(
        age_years=12,
        temperament=ConstitutionTemperamentEnum.NERVOUS_INTELLECTUAL,
        has_active_inflammation=True,
        pathological_depth=0,
        chronic_disease_duration_months=1
    )

    assert assessment.susceptibility_score >= 8.0
    assert assessment.vital_force_score >= 6.0
    assert assessment.posology_scaling_factor >= 50.0
    assert "High Centesimals" in assessment.clinical_recommendation

def test_vitality_low_vitality_severe_pathology():
    """Verify low sigma and cautious posology for elderly cachectic patient."""
    assessment = VitalityAssessmentEngine.assess_patient(
        age_years=78,
        temperament=ConstitutionTemperamentEnum.DEBILITATED_EXHAUSTED,
        has_active_inflammation=False,
        pathological_depth=4,
        chronic_disease_duration_months=120,
        is_on_corticosteroids=True
    )

    assert assessment.vital_force_score <= 3.0
    assert assessment.pathological_depth == 4
    assert assessment.posology_scaling_factor <= 10.0
    assert "Low Decimal/Centesimal" in assessment.clinical_recommendation or "LM" in assessment.clinical_recommendation

def test_vitality_lm_scale_trigger():
    """Verify LM scale recommendation for high susceptibility with structural tissue depth."""
    assessment = VitalityAssessmentEngine.assess_patient(
        age_years=35,
        temperament=ConstitutionTemperamentEnum.NERVOUS_INTELLECTUAL,
        has_active_inflammation=True,
        pathological_depth=3,  # Deep tissue infiltration / ulceration
        chronic_disease_duration_months=24
    )

    assert assessment.pathological_depth == 3
    assert assessment.susceptibility_score >= 6.0
    assert "50-Millesimal (LM)" in assessment.clinical_recommendation
