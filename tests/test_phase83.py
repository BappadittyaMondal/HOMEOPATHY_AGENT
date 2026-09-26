"""
Unit and Integration Tests for Phase 83: Interactive Responsive HTML5 Dashboard & PDF Exporter.
"""
import hashlib
import time
import pytest

from app.reporting.contracts import (
    ReportAudience,
    ReportGenerationRequest
)
from app.reporting.html_dashboard import HTMLDashboardBuilder
from app.reporting.pdf_exporter import PDFReportExporter
from app.clinical.master_verifier import MasterHardenedClinicalResult
from app.models.ehr import EHRClinicalEncounter
from app.safety.gates import ApprovedDraft
from app.governance.nch_signature import SignedPrescriptionReceipt
from app.governance.nabh_audit import NABHAuditEntry
from app.clinical.transfer_dossier import EmergencyTransferDossier


@pytest.fixture
def sample_hardened_result():
    return MasterHardenedClinicalResult(
        patient_id="PAT-P83-001",
        tenant_id="TENANT-HOSP-01",
        is_workflow_successful=True,
        is_emergency_lockout=False,
        is_abstain=False,
        canonical_remedy_id="REM-PULSATILLA",
        canonical_remedy_name="Pulsatilla nigricans",
        approved_draft=ApprovedDraft(
            prescription_id="RX-P83-999",
            patient_id="PAT-P83-001",
            remedy_name="Pulsatilla nigricans",
            potency="30C",
            dosage_instructions="4 globules dry on tongue at bedtime.",
            issued_timestamp="2026-09-26T14:00:00Z",
            gate_results=[],
            approval_token_hash="99887766554433221100FFEEDDCCBBAA"
        ),
        signed_prescription=SignedPrescriptionReceipt(
            prescription_id="RX-P83-999",
            rmp_name="Dr. Bappa Mondal, MD (Hom)",
            registration_number="NCH-2026-WB-8899",
            state_council="NCH_CENTRAL_REGISTER",
            payload_hash_sha256="AABB11223344556677889900FFEEDDCCBBAA0011223344556677889900112233",
            cryptographic_signature="SIG-RSA4096-HEX-VALIDATED-SECURE-2026",
            is_statutorily_valid=True
        ),
        ehr_encounter=EHRClinicalEncounter(
            encounter_id="ENC-P83-999",
            patient_id="PAT-P83-001",
            tenant_id="TENANT-HOSP-01",
            encounter_date="2026-09-26",
            chief_complaint="Mild weeping mood, thirstlessness, worse in warm room, better open air.",
            rubrics_selected=[
                "MIND - WEEPING - mood",
                "STOMACH - THIRSTLESSNESS",
                "GENERALS - WARM - room - agg.",
                "GENERALS - AIR - open - amel."
            ],
            remedy_prescribed="Pulsatilla nigricans",
            potency="30C",
            vitality_score=8.2,
            dominant_miasm="PSORA"
        ),
        nabh_audit_entry=NABHAuditEntry(
            log_id="NABH-LOG-P83",
            timestamp="2026-09-26T14:00:00Z",
            actor_id="RMP-001",
            action_type="PRESCRIPTION_DISPENSED",
            patient_id="PAT-P83-001",
            details={"remedy": "Pulsatilla nigricans", "potency": "30C"},
            previous_hash="0000000000000000000000000000000000000000000000000000000000000000",
            current_hash="1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff"
        ),
        invariants_verified=[f"INV-{i:02d}" for i in range(1, 22)],
        execution_timestamp="2026-09-26T14:00:00Z"
    )


def test_html_dashboard_generation(sample_hardened_result):
    """Validates HTML5 dashboard output structure and embedded assets."""
    html_output = HTMLDashboardBuilder.build_dashboard(sample_hardened_result)

    assert "<!DOCTYPE html>" in html_output
    assert "PAT-P83-001" in html_output
    assert "Pulsatilla nigricans" in html_output
    assert "@media print" in html_output
    assert "vitality-gauge-svg" in html_output
    assert "news2-gauge-svg" in html_output
    assert "simillimum-bar-svg" in html_output
    assert "miasmatic-radar-svg" in html_output
    assert "clinician-view" in html_output
    assert "patient-view" in html_output
    assert "audio-narration-widget" in html_output
    assert "INV-01" in html_output
    assert "INV-21" in html_output


def test_pdf_exporter_bytes(sample_hardened_result):
    """Validates ReportLab pure-Python streaming PDF generator."""
    pdf_bytes = PDFReportExporter.generate_pdf_bytes(sample_hardened_result)

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF-")


def test_pdf_export_and_storage(sample_hardened_result):
    """Validates PDF generation and registration with ObjectStorageGateway."""
    storage_res = PDFReportExporter.export_and_store_pdf(sample_hardened_result)

    assert "pdf_bytes" in storage_res
    assert storage_res["byte_count"] > 1000
    assert storage_res["object_key"].startswith("blobs/")
    assert storage_res["object_key"].endswith(".pdf")
    assert storage_res["download_url"].startswith("https://")

    # Verify SHA-256 integrity
    computed_hash = hashlib.sha256(storage_res["pdf_bytes"]).hexdigest()
    assert computed_hash == storage_res["sha256_hash"]


def test_emergency_lockout_in_html_and_pdf(sample_hardened_result):
    """Validates prominent emergency break-glass alert in both HTML and PDF."""
    sample_hardened_result.is_emergency_lockout = True
    sample_hardened_result.transfer_dossier = EmergencyTransferDossier(
        dossier_id="DOS-EMERGENCY-P83",
        patient_id="PAT-P83-001",
        created_at_utc="2026-09-26T14:05:00Z",
        emergency_category="PHYSIOLOGICAL_COLLAPSE",
        severity_code="CODE_RED_CRITICAL",
        primary_diagnosis_summary="HYPOVOLEMIC SHOCK & PERITONITIS",
        icd10_code="K65.0",
        triggering_findings=["BP 70/40", "Pulse 140", "Board-like abdominal rigidity"],
        immediate_stabilization_instructions=["Immediate IV Crystalloid Resuscitation", "Urgent Surgical Consult"],
        recommended_destination_facility_tier="TERTIARY_SURGICAL_ICU"
    )

    html_out = HTMLDashboardBuilder.build_dashboard(sample_hardened_result)
    assert "EMERGENCY BREAK-GLASS LOCKOUT ACTIVE (ORGANON &sect;186)" in html_out
    assert "HYPOVOLEMIC SHOCK &amp; PERITONITIS" in html_out or "HYPOVOLEMIC SHOCK & PERITONITIS" in html_out

    pdf_bytes = PDFReportExporter.generate_pdf_bytes(sample_hardened_result)
    assert b"%PDF-" in pdf_bytes
    assert len(pdf_bytes) > 1000


def test_rendering_latencies(sample_hardened_result):
    """Verifies that HTML generation is < 15ms and PDF generation is < 80ms."""
    # HTML Latency
    t0 = time.perf_counter()
    for _ in range(5):
        HTMLDashboardBuilder.build_dashboard(sample_hardened_result)
    html_lat_ms = (time.perf_counter() - t0) * 1000.0 / 5.0
    assert html_lat_ms < 15.0, f"HTML generation latency ({html_lat_ms:.2f}ms) exceeded 15ms limit"

    # PDF Latency
    t0 = time.perf_counter()
    for _ in range(3):
        PDFReportExporter.generate_pdf_bytes(sample_hardened_result)
    pdf_lat_ms = (time.perf_counter() - t0) * 1000.0 / 3.0
    assert pdf_lat_ms < 80.0, f"PDF generation latency ({pdf_lat_ms:.2f}ms) exceeded 80ms limit"
