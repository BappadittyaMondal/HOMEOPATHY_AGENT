"""
Simillimum Vector Space Scoring & Composite Ranking Engine (Phase 12).
Implements the non-biased Composite Repertorial Rank (CRR) and multi-column differential matrix.
"""
import time
from typing import List, Dict, Optional
from app.models.simillimum import (
    RankedRemedyCandidate, 
    RemedySimillimumStatus, 
    SimillimumEvaluationReport
)
from app.repertory.csr_kernel import csr_kernel

class SimillimumRankingEngine:
    """
    Master Simillimum Ranking Engine.
    Executes balanced CRR matrix calculation and evaluates mental rubric coverage.
    """

    @classmethod
    def evaluate_totality(
        cls,
        encounter_id: str,
        patient_id: str,
        rubric_indices: List[int],
        weights: List[float],
        is_mental_flags: List[bool],
        polarity_penalties: Optional[Dict[str, float]] = None,
        top_k: int = 15
    ) -> SimillimumEvaluationReport:
        """
        Calculates ranked differentials with mental coverage and polarity penalties.
        """
        t0 = time.perf_counter()
        
        if not rubric_indices:
            return SimillimumEvaluationReport(
                encounter_id=encounter_id,
                patient_id=patient_id,
                primary_simillimum="None (No rubrics provided)",
                top_candidates=[],
                total_evaluated=0,
                execution_latency_ms=0.0
            )

        # 1. Query base scores from high-performance CSR sparse matrix kernel
        base_results = csr_kernel.query_simillimum(
            active_rubric_indices=rubric_indices,
            symptom_weights=weights,
            top_k=min(top_k * 2, len(csr_kernel.remedies_list))
        )

        total_patient_rubrics = len(rubric_indices)
        total_mental_rubrics = sum(1 for m in is_mental_flags if m)
        polarity_penalties = polarity_penalties or {}

        # 2. Slice sub-matrix to evaluate exact mental rubric coverage
        sub_matrix = csr_kernel.matrix[rubric_indices, :]
        candidates: List[RankedRemedyCandidate] = []

        for item in base_results:
            rem_idx = item["remedy_index"]
            rem_name = item["remedy_name"]
            
            # Extract remedy non-zero coverage
            col_slice = sub_matrix[:, rem_idx].toarray().flatten()
            covered_indices = [i for i, val in enumerate(col_slice) if val > 0]
            total_covered = len(covered_indices)

            # Mental coverage calculation
            if total_mental_rubrics > 0:
                mental_covered = sum(1 for i in covered_indices if is_mental_flags[i])
                mental_cov_pct = (mental_covered / float(total_mental_rubrics)) * 100.0
            else:
                mental_cov_pct = 100.0

            # Polarity subtraction penalty
            contra_penalty = polarity_penalties.get(rem_name, 0.0)
            adjusted_score = max(0.0, item["composite_score"] - (contra_penalty * 25.0))

            candidates.append(RankedRemedyCandidate(
                rank=0,  # Will be assigned after final sort
                remedy_name=rem_name,
                composite_score=round(adjusted_score, 2),
                density_score=item["density_score"],
                breadth_score=item["breadth_score"],
                mental_coverage_percent=round(mental_cov_pct, 1),
                total_rubrics_covered=total_covered,
                patient_rubrics_total=total_patient_rubrics,
                status=RemedySimillimumStatus.CONSIDERATION
            ))

        # Re-sort candidates based on adjusted composite score
        candidates.sort(key=lambda x: (x.composite_score, x.mental_coverage_percent), reverse=True)

        # Truncate to top_k and assign ranks and statuses
        final_list = candidates[:top_k]
        for idx, cand in enumerate(final_list):
            cand.rank = idx + 1
            if idx == 0:
                cand.status = RemedySimillimumStatus.PRIMARY_SIMILLIMUM
            elif idx in (1, 2, 3):
                cand.status = RemedySimillimumStatus.SECONDARY_DIFFERENTIAL
            elif cand.composite_score < 30.0:
                cand.status = RemedySimillimumStatus.RULED_OUT
            else:
                cand.status = RemedySimillimumStatus.CONSIDERATION

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        primary_name = final_list[0].remedy_name if final_list else "None"

        return SimillimumEvaluationReport(
            encounter_id=encounter_id,
            patient_id=patient_id,
            primary_simillimum=primary_name,
            top_candidates=final_list,
            total_evaluated=len(final_list),
            execution_latency_ms=round(elapsed_ms, 3)
        )
