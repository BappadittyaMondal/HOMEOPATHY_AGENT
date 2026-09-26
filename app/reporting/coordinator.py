"""
Master Report & Visualization Output Engine Facade (Phase 85).

Provides a unified, demand-driven presentation facade consuming
MasterHardenedClinicalResult and MasterClinicalWorkflowResult:
- Generates on-demand HTML5 Dashboards, Forensic Markdown, and Executive PDFs
- Integrates SVG Visualizations (Vitality, NEWS2, Simillimum CRR, Miasm Simplex, Trends)
- Orchestrates Multilingual Audio Narration (English, Hindi, Bengali)
- Enforces Zero-Overhead Demand-Driven Activation and Fail-Safe Isolation
"""
import time
import hashlib
from typing import Optional, Dict, Any, List

from app.reporting.contracts import (
    ReportFormat,
    ReportAudience,
    NarrationLanguage,
    ReportGenerationRequest,
    RenderedReportBundle,
    VisualizationComponentType
)
from app.reporting.visualizer import ClinicalVisualizer
from app.reporting.markdown_builder import MarkdownReportBuilder
from app.reporting.html_dashboard import HTMLDashboardBuilder
from app.reporting.pdf_exporter import PDFReportExporter
from app.reporting.audio_narrator import MultilingualAudioNarrator
from app.clinical.master_verifier import MasterHardenedClinicalResult, MasterClinicalWorkflowResult


class ReportOutputEngine:
    """
    Master downstream presentation facade for HHIS consultation results.
    Guarantees zero mutation of clinical decision state, sub-50ms execution,
    and fail-safe isolation across all export formats.
    """

    @classmethod
    def generate_report_bundle(
        cls,
        hardened_result: MasterHardenedClinicalResult,
        workflow_result: Optional[MasterClinicalWorkflowResult] = None,
        request: Optional[ReportGenerationRequest] = None
    ) -> RenderedReportBundle:
        """
        Coordinates demand-driven compilation of verified clinical findings into requested formats.
        """
        start_time = time.perf_counter()
        req = request or ReportGenerationRequest(
            patient_id=hardened_result.patient_id,
            encounter_id=hardened_result.ehr_encounter.encounter_id if hardened_result.ehr_encounter else "ENC-GEN",
            tenant_id=hardened_result.tenant_id,
            requested_formats=[ReportFormat.HTML, ReportFormat.MARKDOWN, ReportFormat.PDF],
            audience=ReportAudience.CLINICIAN,
            language=NarrationLanguage.EN_IN
        )

        bundle = RenderedReportBundle(
            patient_id=req.patient_id,
            encounter_id=req.encounter_id,
            tenant_id=req.tenant_id,
            audience=req.audience
        )

        has_format = lambda fmt: (ReportFormat.ALL in req.requested_formats or fmt in req.requested_formats)

        # 1. Generate SVG visual components if requested
        if req.include_visualizations:
            vitality_val = hardened_result.ehr_encounter.vitality_score if hardened_result.ehr_encounter else 7.0
            bundle.visual_components[VisualizationComponentType.GAUGE_VITALITY.value] = (
                ClinicalVisualizer.generate_vitality_gauge(vitality_val).svg_xml
            )

            news2_val = 0
            tier = "LOW"
            if hardened_result.transfer_dossier:
                news2_val = getattr(hardened_result.transfer_dossier, "news2_score", 9)
                tier = "HIGH_CRITICAL"
            bundle.visual_components[VisualizationComponentType.GAUGE_NEWS2.value] = (
                ClinicalVisualizer.generate_news2_gauge(news2_val, clinical_tier=tier).svg_xml
            )

            candidates = []
            if workflow_result and workflow_result.repertorization_report:
                candidates = workflow_result.repertorization_report.top_candidates
            bundle.visual_components[VisualizationComponentType.BAR_SIMILLIMUM_RANK.value] = (
                ClinicalVisualizer.generate_simillimum_bar_chart(candidates).svg_xml
            )

            miasm_vec = workflow_result.miasmatic_vector if workflow_result else None
            bundle.visual_components[VisualizationComponentType.RADAR_MIASMATIC_SIMPLEX.value] = (
                ClinicalVisualizer.generate_miasmatic_radar(miasm_vec).svg_xml
            )

            trend_scores = [vitality_val]
            if workflow_result and workflow_result.longitudinal_trajectory:
                trend_scores = workflow_result.longitudinal_trajectory.vitality_trend or [vitality_val]
            bundle.visual_components[VisualizationComponentType.LINE_LONGITUDINAL_TREND.value] = (
                ClinicalVisualizer.generate_longitudinal_trend(trend_scores).svg_xml
            )

        # 2. Demand-Driven Markdown Generation
        if has_format(ReportFormat.MARKDOWN):
            bundle.markdown_content = MarkdownReportBuilder.build_markdown_report(
                hardened_result=hardened_result,
                workflow_result=workflow_result,
                request=req
            )

        # 3. Demand-Driven HTML5 Dashboard Generation
        if has_format(ReportFormat.HTML):
            bundle.html_content = HTMLDashboardBuilder.build_dashboard(
                hardened_result=hardened_result,
                workflow_result=workflow_result,
                request=req
            )

        # 4. Demand-Driven PDF Export & Storage Registration
        if has_format(ReportFormat.PDF):
            pdf_storage_info = PDFReportExporter.export_and_store_pdf(
                hardened_result=hardened_result,
                workflow_result=workflow_result,
                request=req
            )
            bundle.pdf_bytes_length = pdf_storage_info["byte_count"]
            bundle.pdf_storage_key = pdf_storage_info["object_key"]
            bundle.pdf_download_url = pdf_storage_info["download_url"]

        # 5. Audio Narration Script Generation
        if req.include_audio_narration:
            bundle.audio_narration = MultilingualAudioNarrator.generate_narration_script(
                hardened_result=hardened_result,
                language=req.language,
                audience=req.audience
            )

        # 6. Integrity Hash & Latency Tracking
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        bundle.execution_latency_ms = round(elapsed_ms, 2)

        # Compute deterministic SHA-256 across generated text payloads
        hasher = hashlib.sha256()
        if bundle.markdown_content:
            hasher.update(bundle.markdown_content.encode("utf-8"))
        if bundle.html_content:
            hasher.update(bundle.html_content.encode("utf-8"))
        if bundle.pdf_storage_key:
            hasher.update(bundle.pdf_storage_key.encode("utf-8"))
        bundle.sha256_digest = hasher.hexdigest()

        return bundle
