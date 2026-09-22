"""
Test Suite for Phase 70: Master Pipeline Unified Integration & SQLite Concurrency Hardening.
"""
import pytest
from app.core.config import settings
from app.core.database import db
from app.governance.nch_signature import RMPCredentials
from app.governance.tele_homoeopathy import DPDPPatientConsent
from app.clinical.master_verifier import (
    MasterClinicalPipeline,
    MasterHardenedClinicalResult
)
from app.clinical.break_glass import EmergencyVitals
from app.clinical.cpde import ClinicalPresentationInput, OncologicalBiopsyRequiredException
from app.clinical.acute_intercurrent import (
    AcuteIntercurrentEngine,
    RubricCategory,
    RubricItem,
    AcuteChronicContaminationException
)
from app.repertory.csr_kernel import csr_kernel
from app.dispensary.stock_ledger import StockBottle, DispensaryLedgerEngine


@pytest.fixture(autouse=True)
def setup_phase70_test_env():
    """Ensures kernel and inventory are initialized for Phase 70 testing."""
    if not csr_kernel.is_loaded:
        csr_kernel.load_memory_mapped()

    test_bottle = StockBottle(
        bottle_id="BTL-INV-SULPH-01",
        remedy_name="Sulphur",
        potency="30C",
        initial_volume_ml=100.0,
        current_volume_ml=100.0,
        reorder_threshold_ml=10.0,
        evaporation_tolerance_pct=10.0
    )
    DispensaryLedgerEngine.register_bottle(test_bottle)


def test_sqlite_30s_busy_timeout_and_wal_config():
    """Verify SQLite busy timeout is hardened to 30,000ms (30s) for high concurrency."""
    assert settings.SQLITE_BUSY_TIMEOUT_MS == 30000
    assert settings.SQLITE_TIMEOUT_SECONDS == 30.0
    conn = db.get_read_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA busy_timeout;")
        row = cursor.fetchone()
        assert row[0] == 30000
    finally:
        conn.close()


def test_sqlite_wal_checkpoint_truncate():
    """Verify explicit WAL checkpoint execution truncates log files without error."""
    checkpoint_res = db.wal_checkpoint(mode="TRUNCATE")
    assert "checkpoint_mode" in checkpoint_res
    assert checkpoint_res["checkpoint_mode"] == "TRUNCATE"
    assert "error" not in checkpoint_res


def test_master_pipeline_emergency_transfer_dossier_generation():
    """Emergency lockout in master pipeline automatically generates printable transfer dossier."""
    rmp = RMPCredentials(
        rmp_name="Dr. Bappaditya Roy, MD (Hom)",
        registration_number="WBHC-19842",
        state_council="WBHC",
        is_active_practitioner=True
    )
    consent = DPDPPatientConsent(
        consent_id="CNS-EMERG-01",
        patient_id="PT-EMERG-01",
        consultation_mode="IN_PERSON",
        consent_timestamp="2026-09-20T12:00:00Z",
        has_agreed_to_telemedicine_limitations=True,
        right_to_withdraw_acknowledged=True
    )
    # Severe physiological collapse vitals (NEWS2 >= 7)
    vitals = EmergencyVitals(
        patient_age_years=52,
        systolic_bp=65,  # Shock
        diastolic_bp=40,
        heart_rate=145,
        respiratory_rate=32,
        spo2_percentage=82,
        temperature_celsius=39.5,
        gcs_score=9
    )

    result = MasterClinicalPipeline.execute_hardened_clinical_workflow(
        patient_id="PT-EMERG-01",
        tenant_id="HOSPITAL-CENTRAL-DELHI",
        rmp_credentials=rmp,
        dpdp_consent=consent,
        patient_age_years=52,
        emergency_vitals=vitals
    )

    assert result.is_emergency_lockout is True
    assert result.is_workflow_successful is False
    assert result.transfer_dossier is not None
    assert result.transfer_dossier.emergency_category == "PHYSIOLOGICAL_COLLAPSE"
    assert result.transfer_dossier.severity_code == "CODE_RED_CRITICAL"
    printable = result.transfer_dossier.to_printable_text()
    assert "EMERGENCY CLINICAL TRANSFER DOSSIER" in printable
    assert "PT-EMERG-01" in printable


def test_master_pipeline_inv18_acute_contamination_lockout():
    """Passing acute trauma rubrics into chronic case without is_acute_intercurrent flag raises INV-18."""
    rmp = RMPCredentials(
        rmp_name="Dr. Bappaditya Roy, MD (Hom)",
        registration_number="WBHC-19842",
        state_council="WBHC",
        is_active_practitioner=True
    )
    consent = DPDPPatientConsent(
        consent_id="CNS-P70-01",
        patient_id="PT-P70-01",
        consultation_mode="IN_PERSON",
        consent_timestamp="2026-09-20T12:00:00Z",
        has_agreed_to_telemedicine_limitations=True,
        right_to_withdraw_acknowledged=True
    )

    acute_rubrics = [
        RubricItem(rubric_id="HEAD_TRAUMA_BLUNT", description="Blunt concussion", category=RubricCategory.ACUTE_TRAUMA),
    ]

    with pytest.raises(AcuteChronicContaminationException) as exc_info:
        MasterClinicalPipeline.execute_hardened_clinical_workflow(
            patient_id="PT-P70-01",
            tenant_id="HOSPITAL-CENTRAL-DELHI",
            rmp_credentials=rmp,
            dpdp_consent=consent,
            acute_rubrics=acute_rubrics,
            is_acute_intercurrent=False  # Contamination into chronic case!
        )
    assert "INV-18 VIOLATION" in str(exc_info.value)


def test_master_pipeline_inv18_acute_intercurrent_success():
    """Opening acute intercurrent correctly registers acute case and passes INV-18."""
    rmp = RMPCredentials(
        rmp_name="Dr. Bappaditya Roy, MD (Hom)",
        registration_number="WBHC-19842",
        state_council="WBHC",
        is_active_practitioner=True
    )
    consent = DPDPPatientConsent(
        consent_id="CNS-P70-02",
        patient_id="PT-P70-02",
        consultation_mode="IN_PERSON",
        consent_timestamp="2026-09-20T12:00:00Z",
        has_agreed_to_telemedicine_limitations=True,
        right_to_withdraw_acknowledged=True
    )

    acute_rubrics = [
        RubricItem(rubric_id="ACUTE_FOOD_POISONING", description="Acute gastroenteritis", category=RubricCategory.ACUTE_INTERCURRENT),
    ]

    result = MasterClinicalPipeline.execute_hardened_clinical_workflow(
        patient_id="PT-P70-02",
        tenant_id="HOSPITAL-CENTRAL-DELHI",
        rmp_credentials=rmp,
        dpdp_consent=consent,
        clinical_diagnosis="Acute Gastroenteritis Flare",
        rubric_indices=[0, 1, 2],
        acute_rubrics=acute_rubrics,
        is_acute_intercurrent=True,
        stock_bottle_id="BTL-INV-SULPH-01",
        physical_bottle_remedy="Sulphur",
        physical_bottle_potency="30C"
    )

    assert result.is_workflow_successful is True
    assert result.acute_case_id is not None
    assert any("INV-18" in inv for inv in result.invariants_verified)


def test_master_pipeline_inv17_oncological_lockout():
    """Oncological pre-malignancy presentation locks outpatient prescribing via CPDE."""
    rmp = RMPCredentials(
        rmp_name="Dr. Bappaditya Roy, MD (Hom)",
        registration_number="WBHC-19842",
        state_council="WBHC",
        is_active_practitioner=True
    )
    consent = DPDPPatientConsent(
        consent_id="CNS-P70-03",
        patient_id="PT-P70-03",
        consultation_mode="IN_PERSON",
        consent_timestamp="2026-09-20T12:00:00Z",
        has_agreed_to_telemedicine_limitations=True,
        right_to_withdraw_acknowledged=True
    )

    presentation = ClinicalPresentationInput(
        patient_id="PT-P70-03",
        patient_age_years=55,
        chief_complaint="Bleeding ulcerated keratosis on right palm for 15 years",
        duration_days=5475,
        physical_signs=["spontaneous bleeding", "induration", "central ulceration"]
    )

    with pytest.raises(OncologicalBiopsyRequiredException) as exc_info:
        MasterClinicalPipeline.execute_hardened_clinical_workflow(
            patient_id="PT-P70-03",
            tenant_id="HOSPITAL-CENTRAL-DELHI",
            rmp_credentials=rmp,
            dpdp_consent=consent,
            clinical_presentation=presentation
        )
    assert "INV-17" in str(exc_info.value)
    assert "Dermatopathology Punch Biopsy" in exc_info.value.recommended_investigation
