"""
Unit Tests for Phase 11: Inverse Rubric Frequency (IRF) & Information Entropy Kernel.
"""
import numpy as np
from app.repertory.irf_engine import IRFEntropyEngine

def test_irf_entropy_scaling():
    """Verify that rare rubrics carry significantly higher entropy than common rubrics."""
    total_remedies = 1000
    
    # Common rubric (e.g. Headache in forehead, 400 remedies)
    common_irf = IRFEntropyEngine.calculate_irf(total_remedies, 400)
    
    # Rare rubric (e.g. Fear of downward motion, 6 remedies)
    rare_irf = IRFEntropyEngine.calculate_irf(total_remedies, 6)

    assert rare_irf > common_irf
    assert (rare_irf / common_irf) > 3.0, "Rare rubric should carry at least 3x the information entropy"

def test_normalized_irf_bounds():
    """Verify that normalized IRF is strictly bounded in [1.0, 2.5]."""
    total = 500
    norm_common = IRFEntropyEngine.calculate_normalized_irf(total, 500)
    norm_rare = IRFEntropyEngine.calculate_normalized_irf(total, 1)

    assert norm_common >= 1.0
    assert norm_rare <= 2.5
    assert norm_rare > norm_common

def test_composite_weight_vector_calculation():
    """Verify element-wise multiplication of Kentian weights and IRF entropy multipliers."""
    kent_weights = [5.0, 2.5]  # Mental (5.0), Particular (2.5)
    remedy_counts = [5, 300]   # Rare mental (5), Common particular (300)
    total_remedies = 600

    comp_vector = IRFEntropyEngine.compute_composite_weight_vector(
        kent_weights, remedy_counts, total_remedies
    )

    assert len(comp_vector) == 2
    # Rare mental should be heavily boosted
    assert comp_vector[0] > 10.0
    # Common particular should remain modest
    assert comp_vector[1] < 4.0
