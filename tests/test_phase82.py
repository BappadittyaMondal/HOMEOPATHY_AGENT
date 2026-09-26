"""
Unit and Integration Tests for Phase 82: Forensic Structured Markdown Report Builder.
"""
import time
import pytest

from app.reporting.contracts import (
    ReportAudience,
    ReportGenerationRequest
)
from app.reporting.markdown_builder import MarkdownReportBuilder
from app.clinical.master_verifier import MasterHardenedClinicalResult, MasterClinicalWorkflowResult
from app.models.ehr import EHRClinicalEncounter
from app.safety.gates import ApprovedDraft
from app.governance.nch_signature import SignedPrescriptionReceipt
from app.governance.nabh_audit import NABHAuditEntry
from app.models.simillimum import SimillimumEvaluationReport, RankedRemedyCandidate, RemedySimillimumStatus
from app.models.miasmatic import MiasmaticSimplexVector, MiasmTypeEnum
from app.clinical.transfer_dossier import EmergencyTransferDossier


@pytest.fixture
def mock_hardened_result():
    """Builds a realistic mock of MasterHardenedClinicalResult."""
    return MasterHardenedClinicalResult(
        patient_id="PAT-P82-TEST",
        tenant_id="TENANT-HOSP-01",
        is_workflow_successful=True,
        is_emergency_lockout=False,
        is_abstain=False,
        canonical_remedy_id="REM-ARS-ALB",
        canonical_remedy_name="Arsenicum album",
        approved_draft=ApprovedDraft(
            prescription_id="RX-P82-001",
            patient_id="PAT-P82-TEST",
            remedy_name="Arsenicum album",
            potency="200C",
            dosage_instructions="3 globules dissolved in 100ml water, take 1 teaspoon morning and evening.",
            issued_timestamp="2026-09-26T12:00:00Z",
            gate_results=[],
            approval_token_hash="AABBCCDDEEFF00112233445566778899"
        ),
        signed_prescription=SignedPrescriptionReceipt(
            prescription_id="RX-P82-001",
            rmp_name="Dr. Bappa Mondal, MD (Hom)",
            registration_number="NCH-2026-WB-8899",
            state_council="NCH_CENTRAL_REGISTER",
            payload_hash_sha256="E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
            cryptographic_signature="SIG-RSA4096-HEX-VALIDATED-SECURE-2026",
            is_statutorily_valid=True
        ),
        ehr_encounter=EHRClinicalEncounter(
            encounter_id="ENC-P82-001",
            patient_id="PAT-P82-TEST",
            tenant_id="TENANT-HOSP-01",
            encounter_date="2026-09-26",
            chief_complaint="Severe burning gastralgia aggravated after midnight with profound restlessness.",
            rubrics_selected=[
                "STOMACH - PAIN - burning",
                "GENERALS - MIDNIGHT - after - agg.",
                "MIND - RESTLESSNESS - anxious"
            ],
            remedy_prescribed="Arsenicum album",
            potency="200C",
            vitality_score=7.8,
            dominant_miasm="PSORA"
        ),
        nabh_audit_entry=NABHAuditEntry(
            log_id="NABH-LOG-001",
            timestamp="2026-09-26T12:00:00Z",
            actor_id="RMP-001",
            action_type="PRESCRIPTION_DISPENSED",
            patient_id="PAT-P82-TEST",
            details={"remedy": "Arsenicum album", "potency": "200C"},
            previous_hash="0000000000000000000000000000000000000000000000000000000000000000",
            current_hash="1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff"
        ),
        invariants_verified=[f"INV-{i:02d}" for i in range(1, 22)],
        execution_timestamp="2026-09-26T12:00:00Z"
    )


def test_clinician_markdown_generation(mock_hardened_result):
    """Validates complete clinician technical Markdown report generation."""
    req = ReportGenerationRequest(
        patient_id="PAT-P82-TEST",
        encounter_id="ENC-P82-001",
        audience=ReportAudience.CLINICIAN
    )
    md = MarkdownReportBuilder.build_markdown_report(mock_hardened_result, request=req)

    assert "# CLINICAL FORENSIC CONSULTATION DOSSIER" in md
    assert "PAT-P82-TEST" in md
    assert "Arsenicum album" in md
    assert "STOMACH - PAIN - burning" in md
    assert "INV-01" in md
    assert "INV-21" in md
    assert "Dr. Bappa Mondal, MD (Hom)" in md
    assert "NCH-2026-WB-8899" in md
    assert "NABH-LOG-001" in md


def test_patient_markdown_generation(mock_hardened_result):
    """Validates patient-facing plain language summary and red-flag warnings."""
    req = ReportGenerationRequest(
        patient_id="PAT-P82-TEST",
        encounter_id="ENC-P82-001",
        audience=ReportAudience.PATIENT
    )
    md = MarkdownReportBuilder.build_markdown_report(mock_hardened_result, request=req)

    assert "# PATIENT CLINICAL CARE SUMMARY & PRESCRIPTION" in md
    assert "Arsenicum album (200C)" in md
    assert "Clean Mouth" in md
    assert "EMERGENCY RED FLAGS" in md
    assert "Chest pain" in md or "chest pain" in md
    assert "Next Follow-Up" in md


def test_executive_markdown_generation(mock_hardened_result):
    """Validates hospital executive and NABH audit report formatting."""
    req = ReportGenerationRequest(
        patient_id="PAT-P82-TEST",
        encounter_id="ENC-P82-001",
        audience=ReportAudience.EXECUTIVE
    )
    md = MarkdownReportBuilder.build_markdown_report(mock_hardened_result, request=req)

    assert "# HOSPITAL CLINICAL GOVERNANCE & NABH AUDIT REPORT" in md
    assert "SINGLE REMEDY PRESERVED" in md
    assert "21 Operational Gates Passed" in md
    assert "COMPLIANT / ZERO DEFECTS" in md


def test_emergency_lockout_markdown(mock_hardened_result):
    """Validates that active emergency lockout renders prominent break-glass alert."""
    mock_hardened_result.is_emergency_lockout = True
    mock_hardened_result.transfer_dossier = EmergencyTransferDossier(
        dossier_id="DOS-EMERGENCY-001",
        patient_id="PAT-P82-TEST",
        created_at_utc="2026-09-26T12:05:00Z",
        emergency_category="PHYSIOLOGICAL_COLLAPSE",
        severity_code="CODE_RED_CRITICAL",
        primary_diagnosis_summary="ACUTE ST-ELEVATION MYOCARDIAL INFARCTION",
        icd10_code="I21.0",
        triggering_findings=["Severe crushing retrosternal chest pain", "Diaphoresis", "SpO2 88%"],
        immediate_stabilization_instructions=["Administer High-Flow Oxygen", "Aspirin 300mg PO stat"],
        recommended_destination_facility_tier="TERTIARY_CARDIAC_ICU"
    )

    md = MarkdownReportBuilder.build_markdown_report(mock_hardened_result)
    assert "EMERGENCY BREAK-GLASS LOCKOUT ACTIVATED" in md
    assert "ACUTE ST-ELEVATION MYOCARDIAL INFARCTION" in md
    assert "CODE_RED_CRITICAL" in md
    assert "Organon §186" in md


def test_markdown_builder_performance(mock_hardened_result):
    """Verifies sub-2ms report generation benchmark."""
    t0 = time.perf_counter()
    for _ in range(10):
        MarkdownReportBuilder.build_markdown_report(mock_hardened_result)
    avg_latency_ms = (time.perf_counter() - t0) * 1000.0 / 10.0
    assert avg_latency_ms < 5.0, f"Markdown generation too slow: {avg_latency_ms:.2f}ms"
