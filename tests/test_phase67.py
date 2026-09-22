"""
Test Suite for Phase 67: Dynamic Triplet Keynote Disambiguation Engine.
"""
import pytest
from app.repertory.keynote_discriminator import (
    KeynoteDiscriminatorEngine,
    RemedyCandidateScore,
    DisambiguationResult,
)


def test_clear_winner_no_tie():
    """Wide margin between top remedies does not trigger tie disambiguation."""
    engine = KeynoteDiscriminatorEngine()
    candidates = [
        RemedyCandidateScore(remedy_name="Arsenicum album", score=120.0, rubric_count=5),
        RemedyCandidateScore(remedy_name="Sulphur", score=90.0, rubric_count=4),
        RemedyCandidateScore(remedy_name="Phosphorus", score=75.0, rubric_count=3),
    ]
    result = engine.evaluate_candidates(candidates)
    assert result.is_tie_detected is False
    assert result.tie_margin_pct == 0.0
    assert result.tied_remedies == ["Arsenicum album"]
    assert len(result.discriminating_questions) == 0


def test_two_remedy_tie_detection():
    """Delta <= 3.5% between top 2 triggers tie disambiguation."""
    engine = KeynoteDiscriminatorEngine()
    candidates = [
        RemedyCandidateScore(remedy_name="Arsenicum album", score=100.0, rubric_count=5),
        RemedyCandidateScore(remedy_name="Sulphur", score=98.0, rubric_count=5),  # 2% delta
        RemedyCandidateScore(remedy_name="Phosphorus", score=80.0, rubric_count=4),
    ]
    result = engine.evaluate_candidates(candidates)
    assert result.is_tie_detected is True
    assert result.tie_margin_pct == 2.0
    assert "Arsenicum album" in result.tied_remedies
    assert "Sulphur" in result.tied_remedies
    assert len(result.tied_remedies) == 2
    assert len(result.discriminating_questions) >= 2


def test_triplet_tie_detection():
    """Delta <= 3.5% across 3 remedies triggers triplet disambiguation."""
    engine = KeynoteDiscriminatorEngine()
    candidates = [
        RemedyCandidateScore(remedy_name="Arsenicum album", score=100.0, rubric_count=6),
        RemedyCandidateScore(remedy_name="Sulphur", score=98.5, rubric_count=6),  # 1.5% delta
        RemedyCandidateScore(remedy_name="Phosphorus", score=97.0, rubric_count=6),  # 3.0% delta
        RemedyCandidateScore(remedy_name="Bryonia alba", score=80.0, rubric_count=4),
    ]
    result = engine.evaluate_candidates(candidates)
    assert result.is_tie_detected is True
    assert len(result.tied_remedies) == 3
    assert result.tied_remedies == ["Arsenicum album", "Sulphur", "Phosphorus"]


def test_polar_questions_generated():
    """Questions contrast thermal state, thirst, and characteristic keynotes."""
    engine = KeynoteDiscriminatorEngine()
    candidates = [
        RemedyCandidateScore(remedy_name="Arsenicum album", score=100.0),
        RemedyCandidateScore(remedy_name="Sulphur", score=99.0),
    ]
    result = engine.evaluate_candidates(candidates)
    axes = [q.axis for q in result.discriminating_questions]
    assert "THERMAL_REACTION" in axes
    assert "THIRST_PATTERN" in axes
    assert "CHARACTERISTIC_KEYNOTE" in axes

    thermal_q = next(q for q in result.discriminating_questions if q.axis == "THERMAL_REACTION")
    assert "CHILLY" in thermal_q.remedy_options["Arsenicum album"]
    assert "HOT" in thermal_q.remedy_options["Sulphur"]


def test_break_tie_deterministic():
    """Applying confirmed keynote bonus breaks the tie deterministically."""
    engine = KeynoteDiscriminatorEngine()
    candidates = [
        RemedyCandidateScore(remedy_name="Arsenicum album", score=100.0),
        RemedyCandidateScore(remedy_name="Sulphur", score=99.0),
    ]
    initial = engine.evaluate_candidates(candidates)
    assert initial.is_tie_detected is True

    # Patient confirms Sulphur keynotes: burning soles, kicks off covers at night
    resolved = engine.break_tie(candidates, confirmed_modality_remedy="Sulphur", bonus_pct=0.15)
    assert resolved.is_tie_detected is False
    assert resolved.ranked_candidates[0].remedy_name == "Sulphur"
    assert resolved.ranked_candidates[0].final_score > resolved.ranked_candidates[1].final_score
    assert resolved.tie_margin_pct > 3.5
    assert "Sulphur" in resolved.tie_broken_by


def test_empty_and_single_candidate_graceful():
    engine = KeynoteDiscriminatorEngine()
    res_empty = engine.evaluate_candidates([])
    assert res_empty.is_tie_detected is False

    res_single = engine.evaluate_candidates([RemedyCandidateScore(remedy_name="Arsenicum album", score=50.0)])
    assert res_single.is_tie_detected is False
    assert res_single.tied_remedies == ["Arsenicum album"]
