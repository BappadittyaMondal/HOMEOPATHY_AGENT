"""
Unit & Performance Benchmark Tests for Phase 06: Compressed Sparse Row (CSR) Kernel.
Uses local workspace test directory to avoid Windows %TEMP% permission issues.
"""
import time
import shutil
from pathlib import Path
from app.repertory.csr_kernel import RepertoryCSRKernel
from app.core.config import settings

TEST_DIR = settings.DATA_DIR / "test_scratch_phase06"

def setup_module():
    """Ensure clean test scratch directory."""
    if TEST_DIR.exists():
        shutil.rmtree(TEST_DIR, ignore_errors=True)
    TEST_DIR.mkdir(parents=True, exist_ok=True)

def teardown_module():
    """Cleanup test scratch directory."""
    if TEST_DIR.exists():
        shutil.rmtree(TEST_DIR, ignore_errors=True)

def test_csr_matrix_build_and_load():
    """Verify building and memory-mapped loading of CSR sparse matrix."""
    test_path = TEST_DIR / "csr_build_test"
    kernel = RepertoryCSRKernel(data_dir=test_path)
    kernel.build_synthetic_base_matrix(num_rubrics=200, num_remedies=50)
    
    assert kernel.indptr_path.exists()
    assert kernel.indices_path.exists()
    assert kernel.data_path.exists()
    assert kernel.shape_path.exists()
    assert kernel.irf_path.exists()

    # Load in memory-mapped mode
    kernel.load_memory_mapped()
    assert kernel.is_loaded is True
    assert kernel.matrix.shape == (200, 50)
    assert len(kernel.rubrics_list) == 200
    assert len(kernel.remedies_list) == 50

def test_csr_sub_5ms_query_latency():
    """Benchmark: Verify multi-rubric simillimum ranking executes in sub-5ms."""
    test_path = TEST_DIR / "csr_bench_test"
    kernel = RepertoryCSRKernel(data_dir=test_path)
    kernel.build_synthetic_base_matrix(num_rubrics=1000, num_remedies=200)
    kernel.load_memory_mapped()

    # Select 8 active rubrics with varying Kentian weights
    patient_rubrics = [0, 1, 2, 3, 7, 8, 11, 14]
    weights = [5.0, 4.5, 4.0, 4.0, 3.5, 3.0, 2.5, 2.0]

    # Warmup
    _ = kernel.query_simillimum(patient_rubrics, weights, top_k=10)

    # Benchmark run
    t0 = time.perf_counter()
    results = kernel.query_simillimum(patient_rubrics, weights, top_k=10)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    assert len(results) > 0
    assert elapsed_ms < 5.0, f"Query latency exceeded 5ms threshold: took {elapsed_ms:.3f}ms"
    
    top1 = results[0]
    assert "remedy_name" in top1
    assert "composite_score" in top1
    assert top1["composite_score"] > 0.0
    assert "rubric_coverage" in top1
    print(f"\n[BENCHMARK] 1000x200 CSR Query Latency: {elapsed_ms:.3f} ms (Target: < 5.0 ms)")

def test_csr_empty_query():
    """Verify graceful handling of empty rubric input."""
    kernel = RepertoryCSRKernel(data_dir=TEST_DIR / "csr_empty_test")
    res = kernel.query_simillimum([], [])
    assert res == []
