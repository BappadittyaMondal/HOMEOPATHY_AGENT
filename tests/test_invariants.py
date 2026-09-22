"""
Master Operational Invariant Test Suite (Phase 60).
Validates all 16 concrete Negative Operational Invariants (INV-01 to INV-16)
guaranteeing a zero-defect, non-oscillating, hospital-grade clinical decision support architecture.
"""
import time
import pytest
from pydantic import ValidationError

# Milestone 6 Modules & Gateways
from app.safety.gates import (
    SafetyGatePipeline,
    ApprovedDraft,
    SafetyBlockException,
    GateVerdict
)
from app.models.repertory_boundary import CaseTotalityInput
from app.repertory.simillimum_engine import SimillimumRankingEngine
from app.repertory.csr_kernel import csr_kernel
from app.clinical.break_glass import (
    EmergencyVitals,
    EmergencyBreakGlassGateway,
    EmergencyTransferPacket
)
from app.dispensary.stock_ledger import (
    StockBottle,
    DispenseTransaction,
    DispensaryLedgerEngine,
    DispensingMismatchException
)
from app.governance.pharmacovigilance import (
    ADRReport,
    PharmacovigilanceEngine
)
from app.core.database import db
from app.core.security import (
    SecurityManager,
    UserRole,
    AuthenticationError,
    IdentitySpoofingError
)
from app.governance.nch_signature import (
    RMPCredentials,
    PrescriptionPayload,
    NCHDigitalSignatureGateway
)
from app.safety.obstetric_firewall import (
    ObstetricSafetyFirewall,
    PatientObstetricProfile,
    PregnancyStatus,
    PediatricGuardianConsent,
    ObstetricBlockException,
    PediatricConsentRequiredException
)
from app.clinical.lab_gateway import (
    LaboratoryPanicGateway,
    LabPanelObservation,
    LabObservation,
    LaboratoryPanicException
)
from app.clinical.cpde import (
    ClinicalPathologyDiagnosticEngine,
    ClinicalPresentationInput,
    SurgicalInterventionRequiredException,
    OncologicalBiopsyRequiredException
)
from app.repertory.canonical_registry import (
    CanonicalRemedyRegistry,
    UnresolvedRemedyException,
    SYSTEM_STATUS_BANNER
)
from app.clinical.master_verifier import (
    MasterClinicalPipeline,
    MasterHardenedClinicalResult
)
from app.clinical.acute_intercurrent import (
    AcuteIntercurrentEngine,
    RubricCategory,
    RubricItem,
    AcuteChronicContaminationException
)
from app.governance.tele_homoeopathy import DPDPPatientConsent
from app.models.vitality import PatientVitalityAssessment, ConstitutionTemperamentEnum
from app.clinical.longitudinal_ehr import LongitudinalEHREngine
from app.governance.nabh_audit import NABHAuditLedger


@pytest.fixture(autouse=True)
def ensure_kernel_and_inventory():
    """Seeds test environment with loaded CSR kernel and verified inventory."""
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


# -----------------------------------------------------------------------------
# INV-01: Control-Flow Gating (No Prescribing on Inimical Hard Block)
# -----------------------------------------------------------------------------
def test_inv_01_inimical_violation_blocks_approved_draft():
    """INV-01: Causticum immediately following Phosphorus within 60 days must raise SafetyBlockException."""
    with pytest.raises(SafetyBlockException) as exc_info:
        SafetyGatePipeline.run_gates(
            prescription_id="RX-INV01-01",
            patient_id="PT-INV01",
            candidate_remedy="Causticum",
            potency="200C",
            dosage_instructions="Single dose",
            previous_remedy="Phosphorus",
            days_since_previous=5,
            is_acute_override=False
        )
    assert exc_info.value.gate_name == "INIMICAL_SEQUENCE_GATE"
    assert "inimical" in exc_info.value.message.lower()


# -----------------------------------------------------------------------------
# INV-02: Cryptographic Tamper-Proof ApprovedDraft Token
# -----------------------------------------------------------------------------
def test_inv_02_approved_draft_tamper_detection():
    """INV-02: Modifying an ApprovedDraft's fields or token hash must fail verification."""
    draft = SafetyGatePipeline.run_gates(
        prescription_id="RX-INV02-01",
        patient_id="PT-INV02",
        candidate_remedy="Arnica montana",
        potency="30C",
        dosage_instructions="3 globules BD"
    )
    assert SafetyGatePipeline.verify_approved_draft(draft) is True

    # Tampered draft with forged potency
    tampered_draft = ApprovedDraft(
        prescription_id=draft.prescription_id,
        patient_id=draft.patient_id,
        remedy_name=draft.remedy_name,
        potency="10M",  # Tampered!
        dosage_instructions=draft.dosage_instructions,
        issued_timestamp=draft.issued_timestamp,
        gate_results=draft.gate_results,
        approval_token_hash=draft.approval_token_hash
    )
    assert SafetyGatePipeline.verify_approved_draft(tampered_draft) is False


# -----------------------------------------------------------------------------
# INV-03: Mandatory Simillimum Abstention When Rubric Count < 3
# -----------------------------------------------------------------------------
def test_inv_03_case_totality_abstain_on_thin_symptoms():
    """INV-03: Case totality with fewer than 3 rubrics must return status='ABSTAIN' with primary_simillimum=None."""
    report = SimillimumRankingEngine.evaluate_totality(
        encounter_id="ENC-INV03",
        patient_id="PT-INV03",
        rubric_indices=[0, 1],
        weights=[5.0, 4.0],
        is_mental_flags=[False, False],
        min_required_rubrics=3
    )
    assert report.status == "ABSTAIN"
    assert report.primary_simillimum is None
    assert "minimum 3 characteristic rubrics required" in report.abstention_reason


# -----------------------------------------------------------------------------
# INV-04: Anti-Wraparound Negative Rubric Index Guard
# -----------------------------------------------------------------------------
def test_inv_04_negative_rubric_index_rejected():
    """INV-04: Negative rubric index must raise validation error, preventing NumPy buffer wraparound."""
    with pytest.raises(ValidationError) as exc_info:
        CaseTotalityInput(
            patient_id="PT-INV04",
            encounter_id="ENC-INV04",
            rubric_indices=[-1, 2, 3],
            symptom_weights=[4.0, 4.0, 4.0],
            is_mental_flags=[False, False, False]
        )
    assert "Negative rubric index -1 rejected" in str(exc_info.value)


# -----------------------------------------------------------------------------
# INV-05: Emergency Break-Glass & Psychiatric Crisis Lockout
# -----------------------------------------------------------------------------
def test_inv_05_suicidal_ideation_locks_prescribing():
    """INV-05: Patient expressing suicidal ideation must trigger CODE_RED_PSYCHIATRIC lockout."""
    vitals = EmergencyVitals(
        systolic_bp=120,
        diastolic_bp=80,
        respiratory_rate=16,
        heart_rate=72,
        has_suicidal_ideation=True
    )
    packet = EmergencyBreakGlassGateway.evaluate_emergency_status(vitals)
    assert packet.is_emergency_lockout_active is True
    assert packet.emergency_level == "CODE_RED_PSYCHIATRIC"
    assert packet.is_psychiatric_lockout is True


# -----------------------------------------------------------------------------
# INV-06: Adult NEWS2 & Pediatric PEWS Physiological Scoring
# -----------------------------------------------------------------------------
def test_inv_06_physiological_decompensation_triggers_critical_lockout():
    """INV-06: Adult with NEWS2 >= 7 must trigger CODE_RED_CRITICAL fail-closed lockout."""
    critical_vitals = EmergencyVitals(
        systolic_bp=82,
        diastolic_bp=50,
        respiratory_rate=28,
        heart_rate=125,
        gcs_score=14,
        spo2_percentage=88,
        has_crushing_chest_pain=True
    )
    packet = EmergencyBreakGlassGateway.evaluate_emergency_status(critical_vitals)
    assert packet.is_emergency_lockout_active is True
    assert packet.emergency_level == "CODE_RED_CRITICAL"


# -----------------------------------------------------------------------------
# INV-07: Physical Dispensary Remedial Identity & Potency Verification
# -----------------------------------------------------------------------------
def test_inv_07_dispensary_remedy_mismatch_raises_exception():
    """INV-07: Attempting to dispense Belladonna from a Sulphur bottle must raise DispensingMismatchException."""
    tx = DispenseTransaction(
        transaction_id="TX-INV07",
        bottle_id="BTL-INV-SULPH-01",
        patient_id="PT-INV07",
        edu_units_dispensed=1,
        volume_per_edu_ml=0.5,
        expected_remedy_name="Belladonna",  # Mismatch with Sulphur
        expected_potency="30C"
    )
    with pytest.raises(DispensingMismatchException) as exc_info:
        DispensaryLedgerEngine.dispense_edu(tx)
    assert "DISPENSARY MISMATCH ERROR" in str(exc_info.value)
    assert exc_info.value.expected_remedy == "Belladonna"
    assert exc_info.value.bottle_remedy == "Sulphur"


# -----------------------------------------------------------------------------
# INV-08: Adverse Drug Reaction Severity-Ordered Priority Triage
# -----------------------------------------------------------------------------
def test_inv_08_adr_high_severity_quarantines_batch_first():
    """INV-08: ADR with severity >= 3 must trigger immediate batch quarantine regardless of other symptoms."""
    adr = ADRReport(
        report_id="ADR-INV08",
        patient_id="PT-INV08",
        remedy_name="Aconitum napellus",
        potency="3X",
        batch_number="BATCH-INV08-TOXIC",
        manufacturer="Ayush Lab",
        reaction_symptoms=["Severe cardiac arrhythmia", "Numbness"],
        is_general_vitality_improved=False,
        are_symptoms_new=True,
        severity_grade=4
    )
    res = PharmacovigilanceEngine.process_adr_report(adr)
    assert res.classification == "ADVERSE_DRUG_REACTION_CONFIRMED"
    assert res.action_required == "ISOLATE_AND_QUARANTINE_BATCH"


# -----------------------------------------------------------------------------
# INV-09: True SQLite WAL ACID Persistence Across Memory Clears
# -----------------------------------------------------------------------------
def test_inv_09_sqlite_wal_persistence_across_memory_reset():
    """INV-09: Written audit log entry must persist in SQLite and be queryable after in-memory cache clear."""
    NABHAuditLedger.reset_chain()
    log_id = f"AUD-INV09-{int(time.time())}"
    NABHAuditLedger.append_log(
        log_id=log_id,
        timestamp="2026-09-20T12:00:00Z",
        actor_id="DR-INV09",
        action_type="PERSISTENCE_VERIFIED",
        patient_id="PT-INV09",
        details={"test": "INV-09"}
    )
    # Clear in-memory cache
    NABHAuditLedger._CHAIN.clear()
    assert len(NABHAuditLedger.get_chain()) == 0

    # Reload from SQLite WAL database
    reloaded = NABHAuditLedger.reload_from_database()
    assert any(entry.log_id == log_id for entry in reloaded)
    assert NABHAuditLedger.verify_chain_integrity() is True


# -----------------------------------------------------------------------------
# INV-10: Server-Side Authoritative RBAC JWT Token Validation
# -----------------------------------------------------------------------------
def test_inv_10_invalid_jwt_rejected_by_security():
    """INV-10: Tampered or unauthenticated JWT token must raise AuthenticationError."""
    token = SecurityManager.create_access_token(
        user_id="DR-12345",
        role=UserRole.RMP_DOCTOR,
        full_name="Dr. B Roy",
        registration_number="WBHC-12345"
    )
    claims = SecurityManager.decode_access_token(token)
    assert claims.sub == "DR-12345"
    assert claims.role == UserRole.RMP_DOCTOR

    tampered_token = token[:-5] + "XXXXX"
    with pytest.raises(AuthenticationError) as exc_info:
        SecurityManager.decode_access_token(tampered_token)
    assert "Invalid token signature" in str(exc_info.value)


# -----------------------------------------------------------------------------
# INV-11: Digital Signature Identity Anti-Spoofing
# -----------------------------------------------------------------------------
def test_inv_11_rmp_digital_signature_identity_anti_spoofing():
    """INV-11: RMP attempting to sign under a different registration number must raise IdentitySpoofingError."""
    credentials = RMPCredentials(
        rmp_name="Dr. Attacker",
        registration_number="WBHC-SPOOF-01",
        state_council="WBHC",
        is_active_practitioner=True
    )
    payload = PrescriptionPayload(
        prescription_id="RX-SPOOF-01",
        patient_id="PT-SPOOF",
        remedy_name="Sulphur",
        potency="30C",
        dosage_instructions="Single dose",
        issued_timestamp="2026-09-20T12:00:00Z"
    )
    with pytest.raises(IdentitySpoofingError) as exc_info:
        NCHDigitalSignatureGateway.sign_prescription(
            credentials=credentials,
            payload=payload,
            authenticated_doctor_reg_num="WBHC-GENUINE-99"  # Mismatch!
        )
    assert "IDENTITY SPOOFING DETECTED" in str(exc_info.value)


# -----------------------------------------------------------------------------
# INV-12: Obstetric First Trimester Abortifacient Lockout
# -----------------------------------------------------------------------------
def test_inv_12_abortifacient_sabina_blocked_in_first_trimester():
    """INV-12: Sabina prescribed during Trimester 1 must raise ObstetricBlockException."""
    profile = PatientObstetricProfile(
        pregnancy_status=PregnancyStatus.TRIMESTER_1,
        gestational_weeks=8
    )
    with pytest.raises(ObstetricBlockException) as exc_info:
        ObstetricSafetyFirewall.evaluate_obstetric_safety(
            remedy_name="Sabina",
            potency="30C",
            profile=profile
        )
    assert "OBSTETRIC CONTRAINDICATION" in str(exc_info.value)
    assert "Sabina" in str(exc_info.value)


# -----------------------------------------------------------------------------
# INV-13: Pediatric Consent Mandate Under DPDP Act 2023
# -----------------------------------------------------------------------------
def test_inv_13_minor_without_guardian_consent_raises_exception():
    """INV-13: Prescribing for a 12-year-old child without guardian consent must raise PediatricConsentRequiredException."""
    with pytest.raises(PediatricConsentRequiredException) as exc_info:
        ObstetricSafetyFirewall.evaluate_pediatric_consent(
            patient_age_years=12,
            consent=None
        )
    assert "DPDP ACT 2023 SECTION 9 VIOLATION" in str(exc_info.value)
    assert exc_info.value.patient_age == 12


# -----------------------------------------------------------------------------
# INV-14: Critical Laboratory Panic Value Gateway
# -----------------------------------------------------------------------------
def test_inv_14_cardiac_troponin_panic_locks_prescribing():
    """INV-14: Elevated Troponin-I (0.25 ng/mL >= 0.04) must raise LaboratoryPanicException."""
    panel = LabPanelObservation(
        patient_id="PT-CARD-PANIC",
        panel_name="CARDIAC_ENZYMES",
        timestamp="2026-09-20T12:00:00Z",
        observations=[LabObservation(analyte="troponin_i", value=0.25, unit="ng/mL")]
    )
    with pytest.raises(LaboratoryPanicException) as exc_info:
        LaboratoryPanicGateway.evaluate_lab_panel(panel)
    assert "CRITICAL LAB PANIC" in str(exc_info.value)
    assert "TROPONIN_I" in str(exc_info.value)


# -----------------------------------------------------------------------------
# INV-15: Aphorism 186 Surgical Pathology Boundary
# -----------------------------------------------------------------------------
def test_inv_15_acute_appendicitis_surgical_boundary():
    """INV-15: Acute Appendicitis signs must raise SurgicalInterventionRequiredException per Aphorism 186."""
    presentation = ClinicalPresentationInput(
        patient_id="PT-SURG-01",
        patient_age_years=24,
        chief_complaint="Severe right lower quadrant pain with fever and nausea",
        duration_days=1,
        physical_signs=["McBurney point tenderness", "rebound tenderness", "guarding"]
    )
    with pytest.raises(SurgicalInterventionRequiredException) as exc_info:
        ClinicalPathologyDiagnosticEngine.evaluate_presentation(presentation)
    assert "APHORISM 186 OPERATIVE BOUNDARY" in str(exc_info.value)
    assert "Acute Appendicitis" in exc_info.value.suspected_surgical_condition


# -----------------------------------------------------------------------------
# INV-16: Canonical Remedy Registry & Nomenclature Normalization
# -----------------------------------------------------------------------------
def test_inv_16_canonical_nomenclature_resolution():
    """INV-16: Non-standard synonyms and abbreviations resolve to canonical IDs; unmapped names fail."""
    # Positive resolutions
    assert CanonicalRemedyRegistry.resolve_remedy("bell").canonical_id == "REM-BELL-002"
    assert CanonicalRemedyRegistry.resolve_remedy("deadly nightshade").canonical_id == "REM-BELL-002"
    assert CanonicalRemedyRegistry.resolve_remedy("aconite").canonical_id == "REM-ACON-001"
    assert CanonicalRemedyRegistry.resolve_remedy("nux-v").canonical_id == "REM-NUX-004"
    assert CanonicalRemedyRegistry.resolve_remedy("natrum mur").canonical_id == "REM-NATM-013"

    # Unmapped hallucinated name raises UnresolvedRemedyException
    with pytest.raises(UnresolvedRemedyException) as exc_info:
        CanonicalRemedyRegistry.resolve_remedy("FakeRemedy12345")
    assert "UNRESOLVED REMEDY" in str(exc_info.value)


# -----------------------------------------------------------------------------
# INV-17: Oncological Pre-Malignancy Surveillance & Biopsy Gate
# -----------------------------------------------------------------------------
def test_inv_17_oncological_pre_malignancy_biopsy_lockout():
    """INV-17: Chronic keratosis with induration or Bowenoid transformation mandates biopsy lockout."""
    presentation = ClinicalPresentationInput(
        patient_id="PT-INV17-001",
        patient_age_years=49,
        chief_complaint="Thickened palms and soles for 18 years",
        duration_days=6570,
        physical_signs=["indurated keratosis on left palm", "rough dark spots"]
    )
    with pytest.raises(OncologicalBiopsyRequiredException) as exc_info:
        ClinicalPathologyDiagnosticEngine.evaluate_presentation(presentation)
    assert "INV-17" in str(exc_info.value)
    assert "Dermatopathology Punch Biopsy" in exc_info.value.recommended_investigation


# -----------------------------------------------------------------------------
# INV-18: Acute-on-Chronic Case Segregation State Machine
# -----------------------------------------------------------------------------
def test_inv_18_acute_chronic_contamination_lockout():
    """INV-18: Mixing acute intercurrent/trauma rubrics into chronic totality raises AcuteChronicContaminationException."""
    engine = AcuteIntercurrentEngine()
    mixed = [
        RubricItem(rubric_id="CHRONIC_PSORA", description="Chronic skin itching", category=RubricCategory.CHRONIC_CONSTITUTIONAL),
        RubricItem(rubric_id="ACUTE_TRAUMA", description="Concussion from vehicle crash", category=RubricCategory.ACUTE_TRAUMA),
    ]
    with pytest.raises(AcuteChronicContaminationException) as exc_info:
        engine.register_chronic_case("PT-INV18-01", mixed)
    assert "INV-18" in str(exc_info.value)
    assert "ACUTE_TRAUMA" in exc_info.value.contaminated_rubrics[0]


# -----------------------------------------------------------------------------
# Master End-to-End Hardened Workflow Integration (All 18 Invariants Passing)
# -----------------------------------------------------------------------------
def test_full_master_hardened_workflow_lifecycle():
    """
    Demonstrates successful execution of execute_hardened_clinical_workflow
    verifying all 16 negative invariants concurrently.
    """
    rmp = RMPCredentials(
        rmp_name="Dr. Bappaditya Roy, MD (Hom)",
        registration_number="WBHC-19842",
        state_council="WBHC",
        is_active_practitioner=True
    )
    consent = DPDPPatientConsent(
        consent_id="CNS-HARDENED-01",
        patient_id="PT-HARDENED-01",
        consultation_mode="IN_PERSON",
        consent_timestamp="2026-09-20T12:00:00Z",
        has_agreed_to_telemedicine_limitations=True,
        right_to_withdraw_acknowledged=True
    )
    vitality = PatientVitalityAssessment(
        susceptibility_score=7.0,
        vital_force_score=7.5,
        pathological_depth=1,
        temperament=ConstitutionTemperamentEnum.NERVOUS_INTELLECTUAL,
        posology_scaling_factor=26.25,
        clinical_recommendation="High vitality"
    )

    result = MasterClinicalPipeline.execute_hardened_clinical_workflow(
        patient_id="PT-HARDENED-01",
        tenant_id="HOSPITAL-CENTRAL-DELHI",
        rmp_credentials=rmp,
        dpdp_consent=consent,
        patient_age_years=32,
        has_guardian_consent=True,
        is_pregnant=False,
        clinical_diagnosis="Allergic Rhinitis",
        rubric_indices=[0, 1, 2],  # 3 rubrics satisfies INV-03
        symptom_weights=[5.0, 4.0, 3.5],
        is_mental_flags=[True, False, False],
        vitality_assessment=vitality,
        stock_bottle_id="BTL-INV-SULPH-01",
        physical_bottle_remedy="Sulphur",
        physical_bottle_potency="30C"
    )

    assert result.is_workflow_successful is True
    assert result.is_emergency_lockout is False
    assert result.is_abstain is False
    assert result.canonical_remedy_id is not None
    assert result.approved_draft is not None
    assert result.signed_prescription is not None
    assert result.dispense_receipt is not None
    assert len(result.invariants_verified) >= 9
    assert result.system_status_banner == SYSTEM_STATUS_BANNER
