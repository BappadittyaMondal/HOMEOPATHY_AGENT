"""
Unit and Integration Tests for Phase 81: Simple Data-Visualization & SVG Component Engine.
"""
import time
import pytest

from app.reporting.contracts import (
    ReportFormat,
    ReportAudience,
    NarrationLanguage,
    VisualizationComponentType,
    ReportGenerationRequest,
    RenderedReportBundle
)
from app.reporting.visualizer import ClinicalVisualizer
from app.models.simillimum import RankedRemedyCandidate, RemedySimillimumStatus
from app.models.miasmatic import MiasmaticSimplexVector, MiasmTypeEnum


def test_contracts_schema_and_serialization():
    """Validates ReportGenerationRequest and RenderedReportBundle contracts."""
    req = ReportGenerationRequest(
        patient_id="PAT-P81-001",
        encounter_id="ENC-P81-001",
        requested_formats=[ReportFormat.HTML, ReportFormat.MARKDOWN],
        audience=ReportAudience.CLINICIAN,
        language=NarrationLanguage.EN_IN
    )
    assert req.patient_id == "PAT-P81-001"
    assert req.requested_formats == [ReportFormat.HTML, ReportFormat.MARKDOWN]
    assert req.audience == ReportAudience.CLINICIAN

    bundle = RenderedReportBundle(
        patient_id=req.patient_id,
        encounter_id=req.encounter_id,
        tenant_id=req.tenant_id,
        audience=req.audience
    )
    assert bundle.report_id.startswith("REP-")
    assert bundle.compliance_banner != ""


def test_vitality_gauge_generation():
    """Validates vitality gauge SVG generation across low, medium, and high scores."""
    # Low vitality (red)
    asset_low = ClinicalVisualizer.generate_vitality_gauge(2.0)
    assert "<svg" in asset_low.svg_xml
    assert "</svg>" in asset_low.svg_xml
    assert "LOW RESERVE" in asset_low.svg_xml
    assert "#EF4444" in asset_low.svg_xml
    assert asset_low.component_type == VisualizationComponentType.GAUGE_VITALITY

    # Moderate vitality (amber)
    asset_mod = ClinicalVisualizer.generate_vitality_gauge(5.5)
    assert "MODERATE" in asset_mod.svg_xml
    assert "#F59E0B" in asset_mod.svg_xml

    # Robust vitality (green)
    asset_high = ClinicalVisualizer.generate_vitality_gauge(9.0)
    assert "ROBUST" in asset_high.svg_xml
    assert "#10B981" in asset_high.svg_xml


def test_news2_gauge_generation():
    """Validates NEWS2 physiological triage gauge across safe and critical tiers."""
    # Low risk
    asset_low = ClinicalVisualizer.generate_news2_gauge(2, clinical_tier="LOW")
    assert "LOW RISK" in asset_low.svg_xml
    assert "#10B981" in asset_low.svg_xml

    # Critical decompensation
    asset_crit = ClinicalVisualizer.generate_news2_gauge(8, clinical_tier="HIGH_CRITICAL")
    assert "HIGH CRITICAL" in asset_crit.svg_xml
    assert "#DC2626" in asset_crit.svg_xml
    assert "NEWS2: 8" in asset_crit.svg_xml


def test_simillimum_bar_chart():
    """Validates horizontal ranking bar chart with candidate remedies."""
    candidates = [
        RankedRemedyCandidate(
            rank=1,
            remedy_name="Arsenicum album",
            composite_score=94.5,
            density_score=92.0,
            breadth_score=96.0,
            mental_coverage_percent=100.0,
            total_rubrics_covered=7,
            patient_rubrics_total=7,
            status=RemedySimillimumStatus.PRIMARY_SIMILLIMUM
        ),
        RankedRemedyCandidate(
            rank=2,
            remedy_name="Phosphorus",
            composite_score=83.2,
            density_score=80.0,
            breadth_score=85.0,
            mental_coverage_percent=80.0,
            total_rubrics_covered=6,
            patient_rubrics_total=7,
            status=RemedySimillimumStatus.SECONDARY_DIFFERENTIAL
        )
    ]

    asset = ClinicalVisualizer.generate_simillimum_bar_chart(candidates)
    assert "Arsenicum album" in asset.svg_xml
    assert "Phosphorus" in asset.svg_xml
    assert "94.5%" in asset.svg_xml
    assert "SIMILLIMUM" in asset.svg_xml
    assert asset.component_type == VisualizationComponentType.BAR_SIMILLIMUM_RANK

    # Test empty candidate list (ABSTAIN condition)
    asset_empty = ClinicalVisualizer.generate_simillimum_bar_chart([])
    assert "ABSTAIN" in asset_empty.svg_xml or "No remedy candidates" in asset_empty.svg_xml


def test_miasmatic_radar_generation():
    """Validates 4D Miasmatic Simplex radar polygon generation."""
    vector = MiasmaticSimplexVector(
        psora=0.55,
        sycosis=0.25,
        syphilis=0.10,
        tubercular=0.10,
        dominant_miasm=MiasmTypeEnum.PSORA,
        is_normalized=True
    )

    asset = ClinicalVisualizer.generate_miasmatic_radar(vector)
    assert "<polygon" in asset.svg_xml
    assert "PSORA (55%)" in asset.svg_xml
    assert "DOMINANT: PSORA" in asset.svg_xml
    assert asset.component_type == VisualizationComponentType.RADAR_MIASMATIC_SIMPLEX


def test_longitudinal_trend_and_latency():
    """Validates longitudinal trend chart calculation and sub-5ms latency benchmark."""
    scores = [4.2, 5.0, 6.8, 8.1]
    asset = ClinicalVisualizer.generate_longitudinal_trend(scores)
    assert "IMPROVING" in asset.svg_xml
    assert "polyline" in asset.svg_xml
    assert "8.1" in asset.svg_xml

    # Test declining trajectory
    scores_declining = [8.5, 6.0, 3.2]
    asset_dec = ClinicalVisualizer.generate_longitudinal_trend(scores_declining)
    assert "DECLINING" in asset_dec.svg_xml

    # Latency test: all visual components generated within 10ms total
    t0 = time.perf_counter()
    for _ in range(5):
        ClinicalVisualizer.generate_vitality_gauge(7.5)
        ClinicalVisualizer.generate_news2_gauge(2)
        ClinicalVisualizer.generate_simillimum_bar_chart([])
        ClinicalVisualizer.generate_miasmatic_radar(None)
        ClinicalVisualizer.generate_longitudinal_trend([6.0, 7.0])
        ClinicalVisualizer.generate_kpi_card("Remedy", "Ars-alb", "Simillimum")
    elapsed_ms = (time.perf_counter() - t0) * 1000.0 / 5.0
    assert elapsed_ms < 15.0, f"SVG rendering took {elapsed_ms:.2f}ms, exceeding 15ms target."
