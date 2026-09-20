"""
Inverse Rubric Frequency (IRF) & Information-Theoretic Entropy Weighting Kernel (Phase 11).
Penalizes diffuse common rubrics and elevates highly discriminative rare rubrics.
"""
import numpy as np
from typing import List, Dict, Tuple

class IRFEntropyEngine:
    """
    Computes Shannon Information Entropy and Inverse Rubric Frequency (IRF).
    IRF(r_i) = ln( (|K| / |{k_j : A_ij > 0}|) + 1 )
    """

    @classmethod
    def calculate_irf(cls, total_remedies: int, rubric_remedy_count: int) -> float:
        """Calculates exact logarithmic IRF weight."""
        if rubric_remedy_count <= 0:
            return 1.0
        ratio = total_remedies / float(rubric_remedy_count)
        return float(np.log(ratio + 1.0))

    @classmethod
    def calculate_normalized_irf(
        cls, 
        total_remedies: int, 
        rubric_remedy_count: int,
        min_weight: float = 1.0,
        max_weight: float = 2.5
    ) -> float:
        """
        Calculates bounded normalized IRF multiplier in [min_weight, max_weight].
        Common non-specific rubrics receive ~1.0; rare keynotes receive ~2.5.
        """
        raw_irf = cls.calculate_irf(total_remedies, rubric_remedy_count)
        max_raw = float(np.log(total_remedies + 1.0))
        min_raw = float(np.log(1.0 + 1.0))  # when rubric contains all remedies
        
        normalized = (raw_irf - min_raw) / (max_raw - min_raw + 1e-9)
        scaled = min_weight + (normalized * (max_weight - min_weight))
        return round(float(np.clip(scaled, min_weight, max_weight)), 3)

    @classmethod
    def compute_composite_weight_vector(
        cls, 
        kentian_weights: List[float], 
        remedy_counts: List[int], 
        total_remedies: int
    ) -> np.ndarray:
        """
        Generates composite diagonal weight matrix vector:
        W_i = w_i * IRF(r_i)
        """
        weights = np.array(kentian_weights, dtype=np.float32)
        irf_factors = np.array([
            cls.calculate_normalized_irf(total_remedies, count) 
            for count in remedy_counts
        ], dtype=np.float32)

        composite = weights * irf_factors
        return composite
