"""
Unit Tests for Phase 05: Boenninghausen Complete Symptom Parser (LSMC).
"""
from app.repertory.boenninghausen_parser import BoenninghausenParser
from app.models.boenninghausen import PolarAxisEnum

def test_boenninghausen_complete_symptom_parsing():
    """Verify 4-part deconstruction: Location, Sensation, Modality, Concomitant."""
    text = (
        "Stitching pain in right hypochondrium, worse from movement, "
        "better from hard pressure, accompanied by nausea."
    )
    parsed = BoenninghausenParser.parse_symptom(text)

    # 1. Location
    assert parsed.location == "Right Hypochondrium"

    # 2. Sensation
    assert parsed.sensation == "Stitching"

    # 3. Modalities
    assert len(parsed.modalities) >= 2
    agg_motion = next((m for m in parsed.modalities if m.polar_axis == PolarAxisEnum.MOTION), None)
    assert agg_motion is not None
    assert agg_motion.is_aggravation is True

    amel_press = next((m for m in parsed.modalities if m.polar_axis == PolarAxisEnum.PRESSURE), None)
    assert amel_press is not None
    assert amel_press.is_aggravation is False

    # 4. Concomitant
    assert len(parsed.concomitants) >= 1
    assert "Nausea" in parsed.concomitants

    # Completeness
    assert parsed.completeness_score == 1.0
    assert parsed.is_fully_qualified is True
    assert parsed.grand_generalization_eligible is True

def test_boenninghausen_incomplete_symptom():
    """Verify bare symptom receives low completeness score and is_fully_qualified=False."""
    text = "Pain in throat."
    parsed = BoenninghausenParser.parse_symptom(text)
    assert parsed.location == "Throat"
    assert parsed.sensation is None
    assert len(parsed.modalities) == 0
    assert len(parsed.concomitants) == 0
    assert parsed.completeness_score < 0.75
    assert parsed.is_fully_qualified is False
