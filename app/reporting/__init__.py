"""
Report & Visualization Output Engine Package (Milestone 11, Phases 81–85).

Exposes public interfaces for multi-format clinical report rendering,
mathematical SVG visualization, and multilingual audio narration.
"""
from app.reporting.contracts import (
    ReportFormat,
    ReportAudience,
    NarrationLanguage,
    VisualizationComponentType,
    ReportGenerationRequest,
    RenderedVisualAsset,
    AudioNarrationScript,
    RenderedReportBundle
)
from app.reporting.visualizer import ClinicalVisualizer
from app.reporting.markdown_builder import MarkdownReportBuilder
from app.reporting.html_dashboard import HTMLDashboardBuilder
from app.reporting.pdf_exporter import PDFReportExporter
from app.reporting.audio_narrator import MultilingualAudioNarrator
from app.reporting.coordinator import ReportOutputEngine

__all__ = [
    "ReportFormat",
    "ReportAudience",
    "NarrationLanguage",
    "VisualizationComponentType",
    "ReportGenerationRequest",
    "RenderedVisualAsset",
    "AudioNarrationScript",
    "RenderedReportBundle",
    "ClinicalVisualizer",
    "MarkdownReportBuilder",
    "HTMLDashboardBuilder",
    "PDFReportExporter",
    "MultilingualAudioNarrator",
    "ReportOutputEngine",
]
