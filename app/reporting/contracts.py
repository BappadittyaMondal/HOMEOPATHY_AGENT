"""
Report & Visualization Output Engine Domain Contracts (Phase 81).

Defines standard schemas, data transfer objects, enumeration types,
and immutable receipt containers for multi-format report generation,
SVG clinical visualizations, and browser-native audio narration.
"""
import uuid
import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ReportFormat(str, Enum):
    """Supported export formats for clinical reports."""
    HTML = "HTML"
    MARKDOWN = "MARKDOWN"
    PDF = "PDF"
    ALL = "ALL"


class ReportAudience(str, Enum):
    """Target reader audience tailoring terminology and presentation density."""
    CLINICIAN = "CLINICIAN"      # High technical density: repertorial rubrics, miasmatic simplex, posology calculus
    PATIENT = "PATIENT"          # Plain language: dosage schedules, dietary modalities, follow-up guidance
    EXECUTIVE = "EXECUTIVE"      # Hospital governance: NABH compliance, cost savings, safety gate audit chain


class NarrationLanguage(str, Enum):
    """Supported languages for browser-native audio narration (W3C Web Speech API)."""
    EN_IN = "en-IN"              # Indian English
    EN_US = "en-US"              # Standard English
    HI_IN = "hi-IN"              # Hindi
    BN_IN = "bn-IN"              # Bengali


class VisualizationComponentType(str, Enum):
    """Identifies individual SVG visual components."""
    GAUGE_VITALITY = "GAUGE_VITALITY"
    GAUGE_NEWS2 = "GAUGE_NEWS2"
    BAR_SIMILLIMUM_RANK = "BAR_SIMILLIMUM_RANK"
    RADAR_MIASMATIC_SIMPLEX = "RADAR_MIASMATIC_SIMPLEX"
    LINE_LONGITUDINAL_TREND = "LINE_LONGITUDINAL_TREND"
    KPI_STAT_CARD = "KPI_STAT_CARD"


class ReportGenerationRequest(BaseModel):
    """User request payload for demand-driven report and visualization generation."""
    patient_id: str
    encounter_id: str
    tenant_id: str = "DEFAULT_TENANT"
    requested_formats: List[ReportFormat] = Field(default_factory=lambda: [ReportFormat.HTML, ReportFormat.MARKDOWN])
    audience: ReportAudience = ReportAudience.CLINICIAN
    language: NarrationLanguage = NarrationLanguage.EN_IN
    include_visualizations: bool = True
    include_audio_narration: bool = True
    include_audit_trail: bool = True


class RenderedVisualAsset(BaseModel):
    """Encapsulates a generated inline SVG visualization component."""
    component_type: VisualizationComponentType
    title: str
    svg_xml: str
    width_px: int
    height_px: int
    description: str


class AudioNarrationScript(BaseModel):
    """Plain-language speech narration script generated for client-side TTS."""
    language: NarrationLanguage
    script_text: str
    estimated_duration_seconds: float
    sections: Dict[str, str] = Field(default_factory=dict)


class RenderedReportBundle(BaseModel):
    """
    Immutable container holding rendered multi-format reports,
    embedded SVG visualizations, client-side audio narration scripts,
    and cryptographic SHA-256 integrity digests.
    """
    report_id: str = Field(default_factory=lambda: f"REP-{uuid.uuid4().hex[:10].upper()}")
    patient_id: str
    encounter_id: str
    tenant_id: str
    audience: ReportAudience
    generated_at: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    
    # Rendered output payloads
    html_content: Optional[str] = None
    markdown_content: Optional[str] = None
    pdf_bytes_length: Optional[int] = None
    pdf_storage_key: Optional[str] = None
    pdf_download_url: Optional[str] = None
    
    # Visual and audio assets
    visual_components: Dict[str, str] = Field(default_factory=dict)  # ComponentType -> SVG XML string
    audio_narration: Optional[AudioNarrationScript] = None
    
    # Performance & Governance
    execution_latency_ms: float = 0.0
    sha256_digest: str = ""
    compliance_banner: str = "NABH Homoeopathy 2nd Edition & NCH Act 2020 Statutory Verified"
