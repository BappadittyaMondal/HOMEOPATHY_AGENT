"""
Unit Tests for Phase 16: Centesimal, Decimal, and 50-Millesimal Potency Selection Calculus.
"""
from app.repertory.posology_engine import DynamicPosologyCalculus
from app.repertory.vitality_engine import VitalityAssessmentEngine
from app.models.vitality import ConstitutionTemperamentEnum
from app.models.posology import PotencyScaleEnum, PosologyVehicleEnum

def test_posology_50_millesimal_lm_scale():
    """Verify LM 0/1 aqueous solution protocol for high susceptibility with structural pathology."""
    vitality = VitalityAssessmentEngine.assess_patient(
        age_years=32,
        temperament=ConstitutionTemperamentEnum.NERVOUS_INTELLECTUAL,
        has_active_inflammation=True,
        pathological_depth=3,  # Deep tissue pathology
        chronic_disease_duration_months=36
    )

    protocol = DynamicPosologyCalculus.calculate_protocol("Lycopodium clavatum", vitality, is_acute=False)

    assert protocol.scale == PotencyScaleEnum.FIFTY_MILLESIMAL
    assert protocol.potency_grade == "LM 0/1"
    assert protocol.vehicle == PosologyVehicleEnum.SUCCUSSED_AQUEOUS_SOLUTION
    assert "Aphorisms 246-248" in protocol.aphorism_reference
    assert "succuss bottle 8-10 times" in protocol.administration_schedule

def test_posology_acute_split_dose_in_water():
    """Verify split aqueous dose with stop-on-improvement protocol for acute disease."""
    vitality = VitalityAssessmentEngine.assess_patient(
        age_years=22,
        temperament=ConstitutionTemperamentEnum.SANGUINE_ACTIVE,
        has_active_inflammation=True,
        pathological_depth=0
    )

    protocol = DynamicPosologyCalculus.calculate_protocol("Aconitum napellus", vitality, is_acute=True)

    assert protocol.scale == PotencyScaleEnum.CENTESIMAL
    assert protocol.potency_grade in ("200C", "30C")
    assert protocol.vehicle == PosologyVehicleEnum.SUCCUSSED_AQUEOUS_SOLUTION
    assert "STOP IMMEDIATELY" in protocol.administration_schedule

def test_posology_high_centesimal_robust_chronic():
    """Verify single high-potency dose (200C) + Sac Lac for robust chronic case."""
    vitality = VitalityAssessmentEngine.assess_patient(
        age_years=28,
        temperament=ConstitutionTemperamentEnum.NERVOUS_INTELLECTUAL,
        has_active_inflammation=False,
        pathological_depth=0,
        chronic_disease_duration_months=6
    )

    protocol = DynamicPosologyCalculus.calculate_protocol("Sulphur", vitality, is_acute=False)

    assert protocol.scale == PotencyScaleEnum.CENTESIMAL
    assert protocol.potency_grade == "200C"
    assert protocol.vehicle == PosologyVehicleEnum.CANE_SUGAR_GLOBULES_NO_30
    assert "Sac Lac" in protocol.placebo_sac_lac_schedule

def test_posology_low_decimal_severe_organic_pathology():
    """Verify 6X decimal powder for advanced pathology / low vitality."""
    vitality = VitalityAssessmentEngine.assess_patient(
        age_years=75,
        temperament=ConstitutionTemperamentEnum.DEBILITATED_EXHAUSTED,
        has_active_inflammation=False,
        pathological_depth=4,
        chronic_disease_duration_months=120
    )

    protocol = DynamicPosologyCalculus.calculate_protocol("Silicea", vitality, is_acute=False)

    assert protocol.scale == PotencyScaleEnum.DECIMAL
    assert protocol.potency_grade == "6X"
    assert protocol.vehicle == PosologyVehicleEnum.SACCHARUM_LACTIS_POWDER
