"""
Unit Tests for Phase 12: Simillimum Vector Space Scoring & Composite Ranking Engine.
"""
from app.repertory.simillimum_engine import SimillimumRankingEngine
from app.models.simillimum import RemedySimillimumStatus
from app.repertory.csr_kernel import csr_kernel

def test_simillimum_evaluation_matrix():
    """Verify Simillimum ranking, mental coverage, and differential status assignment."""
    csr_kernel.load_memory_mapped()

    rubric_indices = [0, 1, 2, 7, 8, 11]  # 3 mental (0, 1, 2), 3 physical
    weights = [5.0, 4.5, 4.0, 3.5, 3.0, 3.0]
    is_mental = [True, True, True, False, False, False]

    report = SimillimumRankingEngine.evaluate_totality(
        encounter_id="ENC-EVAL-01",
        patient_id="PAT-EVAL-01",
        rubric_indices=rubric_indices,
        weights=weights,
        is_mental_flags=is_mental,
        top_k=5
    )

    assert report.total_evaluated > 0
    assert report.primary_simillimum != "None"
    assert len(report.top_candidates) <= 5

    # Check Rank 1 is PRIMARY_SIMILLIMUM
    top1 = report.top_candidates[0]
    assert top1.rank == 1
    assert top1.status == RemedySimillimumStatus.PRIMARY_SIMILLIMUM
    assert top1.composite_score > 0.0
    assert 0.0 <= top1.mental_coverage_percent <= 100.0

    # Check Ranks 2-4 are SECONDARY_DIFFERENTIAL
    if len(report.top_candidates) > 1:
        top2 = report.top_candidates[1]
        assert top2.rank == 2
        assert top2.status == RemedySimillimumStatus.SECONDARY_DIFFERENTIAL

    assert report.execution_latency_ms < 10.0

def test_simillimum_polarity_penalty_adjustment():
    """Verify that remedies with polarity penalties have their score docked."""
    csr_kernel.load_memory_mapped()
    rubric_indices = [0, 1, 2]
    weights = [5.0, 5.0, 5.0]
    is_mental = [True, True, True]

    # Baseline without penalty
    baseline = SimillimumRankingEngine.evaluate_totality(
        encounter_id="ENC-01",
        patient_id="PAT-01",
        rubric_indices=rubric_indices,
        weights=weights,
        is_mental_flags=is_mental,
        top_k=5
    )
    top_name = baseline.top_candidates[0].remedy_name
    baseline_score = baseline.top_candidates[0].composite_score

    # Apply penalty to top remedy
    penalized = SimillimumRankingEngine.evaluate_totality(
        encounter_id="ENC-01",
        patient_id="PAT-01",
        rubric_indices=rubric_indices,
        weights=weights,
        is_mental_flags=is_mental,
        polarity_penalties={top_name: 1.0},
        top_k=5
    )
    penalized_top = next((c for c in penalized.top_candidates if c.remedy_name == top_name), None)
    if penalized_top:
        assert penalized_top.composite_score < baseline_score
