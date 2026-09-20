"""
Tests for Phase 52: Boundary Validation, Anti-Wraparound & Case Totality ABSTAIN Engine.
Validates INV-03 (ABSTAIN on < 3 rubrics) and INV-04 (Anti-wraparound boundary guard).
"""
import pytest
from pydantic import ValidationError
from app.models.repertory_boundary import CaseTotalityInput
from app.repertory.simillimum_engine import SimillimumRankingEngine
from app.repertory.csr_kernel import csr_kernel


def setup_module():
    """Ensure CSR matrix is loaded."""
    csr_kernel.load_memory_mapped()


def test_inv_03_empty_totality_returns_abstain():
    """INV-03: Empty rubric list must return ABSTAIN with primary_simillimum=None."""
    report = SimillimumRankingEngine.evaluate_totality(
        encounter_id="ENC-EMPTY-01",
        patient_id="PAT-EMPTY-01",
        rubric_indices=[],
        weights=[],
        is_mental_flags=[]
    )
    assert report.status == "ABSTAIN"
    assert report.primary_simillimum is None
    assert len(report.top_candidates) == 0
    assert "INSUFFICIENT_SYMPTOM_TOTALITY" in report.abstention_reason


def test_inv_03_thin_totality_below_threshold_returns_abstain():
    """INV-03: Case with only 1 or 2 rubrics (< 3) must ABSTAIN per Aphorism 153."""
    report = SimillimumRankingEngine.evaluate_totality(
        encounter_id="ENC-THIN-01",
        patient_id="PAT-THIN-01",
        rubric_indices=[0, 1],
        weights=[5.0, 4.0],
        is_mental_flags=[True, False],
        min_required_rubrics=3
    )
    assert report.status == "ABSTAIN"
    assert report.primary_simillimum is None
    assert "minimum 3 characteristic rubrics required" in report.abstention_reason


def test_inv_04_negative_index_raises_validation_error():
    """INV-04: Negative rubric index must be rejected by Pydantic validator, preventing NumPy wraparound."""
    with pytest.raises(ValidationError) as exc_info:
        SimillimumRankingEngine.evaluate_totality(
            encounter_id="ENC-WRAP-01",
            patient_id="PAT-WRAP-01",
            rubric_indices=[-1, 2, 3],
            weights=[5.0, 4.0, 3.0],
            is_mental_flags=[True, False, False]
        )
    assert "Negative rubric index -1 rejected" in str(exc_info.value)


def test_dimensional_mismatch_raises_validation_error():
    """Lengths of rubrics, weights, and mental flags must match exactly."""
    with pytest.raises(ValidationError) as exc_info:
        CaseTotalityInput(
            patient_id="PAT-DIM-01",
            encounter_id="ENC-DIM-01",
            rubric_indices=[0, 1, 2],
            symptom_weights=[5.0, 4.0],  # only 2 weights for 3 rubrics
            is_mental_flags=[True, False, False]
        )
    assert "Dimensional mismatch" in str(exc_info.value)


def test_sufficient_totality_completes_successfully():
    """A valid case with >= 3 non-negative rubrics must complete with rank-1 simillimum."""
    report = SimillimumRankingEngine.evaluate_totality(
        encounter_id="ENC-VALID-01",
        patient_id="PAT-VALID-01",
        rubric_indices=[0, 1, 2],
        weights=[5.0, 4.0, 3.0],
        is_mental_flags=[True, True, False]
    )
    assert report.status == "COMPLETED"
    assert report.primary_simillimum is not None
    assert len(report.top_candidates) > 0
    assert report.execution_latency_ms < 10.0
