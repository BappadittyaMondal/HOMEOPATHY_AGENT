"""
Unit and Integration Tests for Phase 85: Master Report Facade, API Integration & Grand 85-Phase Verification.
"""
import time
import pytest
from starlette.testclient import TestClient

from app.main import app
from app.reporting.contracts import (
    ReportFormat,
    ReportAudience,
    NarrationLanguage,
    ReportGenerationRequest,
    RenderedReportBundle,
    VisualizationComponentType
)
from app.reporting.coordinator import ReportOutputEngine
from app.clinical.master_verifier import MasterHardenedClinicalResult
from app.models.ehr import EHRClinicalEncounter
from app.safety.gates import ApprovedDraft
from app.governance.nch_signature import SignedPrescriptionReceipt
from app.governance.nabh_audit import NABHAuditEntry


@pytest.fixture
def mock_clinical_data():
    hardened_res = MasterHardenedClinicalResult(
        patient_id="PAT-P85-AUDIT",
        tenant_id="TENANT-HOSP-01",
        is_workflow_successful=True,
        is_emergency_lockout=False,
        is_abstain=False,
        canonical_remedy_id="REM-NUX-VOMICA",
        canonical_remedy_name="Nux vomica",
        approved_draft=ApprovedDraft(
            prescription_id="RX-P85-888",
            patient_id="PAT-P85-AUDIT",
            remedy_name="Nux vomica",
            potency="200C",
            dosage_instructions="3 pellets at bed time, avoid sedentary lifestyle.",
            issued_timestamp="2026-09-26T18:00:00Z",
            gate_results=[],
            approval_token_hash="HASH-NUX-2026-TOKEN"
        ),
        signed_prescription=SignedPrescriptionReceipt(
            prescription_id="RX-P85-888",
            rmp_name="Dr. Bappa Mondal, MD (Hom)",
            registration_number="NCH-2026-WB-8899",
            state_council="NCH_CENTRAL_REGISTER",
            payload_hash_sha256="11223344556677889900AABBCCDDEEFF0011223344556677889900AABBCCDDEE",
            cryptographic_signature="SIG-RSA4096-P85-PROD-CERT",
            is_statutorily_valid=True
        ),
        ehr_encounter=EHRClinicalEncounter(
            encounter_id="ENC-P85-888",
            patient_id="PAT-P85-AUDIT",
            tenant_id="TENANT-HOSP-01",
            encounter_date="2026-09-26",
            chief_complaint="Dyspepsia from sedentary habits, irritability, ineffectual urging for stool.",
            rubrics_selected=[
                "STOMACH - INDIGESTION - sedentary habits, from",
                "RECTUM - INEFFECTUAL urging for stool",
                "MIND - IRRITABILITY"
            ],
            remedy_prescribed="Nux vomica",
            potency="200C",
            vitality_score=7.6,
            dominant_miasm="PSORA"
        ),
        nabh_audit_entry=NABHAuditEntry(
            log_id="NABH-LOG-P85",
            timestamp="2026-09-26T18:00:00Z",
            actor_id="RMP-001",
            action_type="PRESCRIPTION_DISPENSED",
            patient_id="PAT-P85-AUDIT",
            details={"remedy": "Nux vomica", "potency": "200C"},
            previous_hash="0000000000000000000000000000000000000000000000000000000000000000",
            current_hash="1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff"
        ),
        invariants_verified=[f"INV-{i:02d}" for i in range(1, 22)],
        execution_timestamp="2026-09-26T18:00:00Z"
    )
    return hardened_res


def test_full_bundle_generation(mock_clinical_data):
    """Validates full bundle generation across all formats with SVG and audio narration."""
    req = ReportGenerationRequest(
        patient_id="PAT-P85-AUDIT",
        encounter_id="ENC-P85-888",
        requested_formats=[ReportFormat.ALL],
        audience=ReportAudience.CLINICIAN,
        language=NarrationLanguage.EN_IN,
        include_visualizations=True,
        include_audio_narration=True
    )

    bundle = ReportOutputEngine.generate_report_bundle(mock_clinical_data, request=req)

    assert bundle.report_id.startswith("REP-")
    assert bundle.html_content is not None
    assert "<!DOCTYPE html>" in bundle.html_content
    assert bundle.markdown_content is not None
    assert "# CLINICAL FORENSIC CONSULTATION DOSSIER" in bundle.markdown_content
    assert bundle.pdf_download_url is not None
    assert bundle.pdf_bytes_length > 1000
    assert len(bundle.visual_components) == 5
    assert VisualizationComponentType.GAUGE_VITALITY.value in bundle.visual_components
    assert bundle.audio_narration is not None
    assert bundle.sha256_digest != ""
    assert bundle.execution_latency_ms > 0.0


def test_demand_driven_selective_rendering(mock_clinical_data):
    """Validates that unrequested formats and assets are not computed (zero waste)."""
    # Request ONLY Markdown, no visuals, no audio
    req = ReportGenerationRequest(
        patient_id="PAT-P85-AUDIT",
        encounter_id="ENC-P85-888",
        requested_formats=[ReportFormat.MARKDOWN],
        include_visualizations=False,
        include_audio_narration=False
    )

    bundle = ReportOutputEngine.generate_report_bundle(mock_clinical_data, request=req)

    assert bundle.markdown_content is not None
    assert bundle.html_content is None
    assert bundle.pdf_download_url is None
    assert len(bundle.visual_components) == 0
    assert bundle.audio_narration is None


def test_api_export_endpoint():
    """Validates POST /clinical/encounters/{encounter_id}/export HTTP REST API."""
    client = TestClient(app)
    payload = {
        "patient_id": "PAT-P85-API",
        "encounter_id": "ENC-API-TEST",
        "tenant_id": "DEFAULT_TENANT",
        "requested_formats": ["HTML", "MARKDOWN"],
        "audience": "PATIENT",
        "language": "hi-IN",
        "include_visualizations": True,
        "include_audio_narration": True
    }

    response = client.post("/api/v1/clinical/encounters/ENC-API-TEST/export", json=payload)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()
    assert data["patient_id"] == "PAT-P85-API"
    assert data["html_content"] is not None
    assert data["markdown_content"] is not None
    assert data["audio_narration"]["language"] == "hi-IN"
    assert "दवा" in data["audio_narration"]["script_text"] or "परामर्श" in data["audio_narration"]["script_text"]
    assert len(data["sha256_digest"]) == 64
