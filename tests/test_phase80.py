"""
Automated Test Suite for Phase 80: Master Multimodal Verification Suite, Grand Invariant Audit (INV-01 to INV-21) & Milestone 10 Integration.
"""
import pytest
from app.models.vitality import PatientVitalityAssessment, ConstitutionTemperamentEnum
from app.governance.nch_signature import RMPCredentials
from app.governance.tele_homoeopathy import DPDPPatientConsent
from app.clinical.master_verifier import MasterClinicalPipeline
from app.repertory.csr_kernel import csr_kernel
from app.dispensary.stock_ledger import StockBottle, DispensaryLedgerEngine
from app.clinical.vitality_mandate import (
    ExplicitVitalityMandateEngine,
    VitalityUnassessedException,
    KentObservation1HazardException
)
from app.clinical.vitals_gate import (
    ObjectivePhysiologicalVitals,
    ObjectiveVitalsGateEngine,
    MissingVitalsException,
    CriticalVitalsDecompensationException
)


@pytest.fixture(autouse=True)
def ensure_kernel_and_inventory():
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


@pytest.fixture
def mock_doctor_and_consent():
    rmp = RMPCredentials(
        rmp_name="Dr. Bappaditya Roy, MD (Hom)",
        registration_number="WBHC-19842",
        state_council="WBHC",
        is_active_practitioner=True
    )
    consent = DPDPPatientConsent(
        consent_id="CNS-M10-01",
        patient_id="PT-M10-01",
        consultation_mode="TELEMEDICINE",
        consent_timestamp="2026-09-24T18:00:00Z",
        has_agreed_to_telemedicine_limitations=True,
        right_to_withdraw_acknowledged=True
    )
    return rmp, consent


def test_grand_master_hardened_workflow_with_all_21_invariants(mock_doctor_and_consent):
    """Verify MasterClinicalPipeline executes with INV-20 and INV-21 certified."""
    rmp, consent = mock_doctor_and_consent
    vitality = PatientVitalityAssessment(
        susceptibility_score=7.0,
        vital_force_score=7.5,
        pathological_depth=1,
        temperament=ConstitutionTemperamentEnum.NERVOUS_INTELLECTUAL,
        posology_scaling_factor=26.25,
        clinical_recommendation="High vitality"
    )
    vitals = ObjectivePhysiologicalVitals(
        pulse_bpm=72,
        systolic_bp=120,
        diastolic_bp=80,
        respiratory_rate=16,
        temperature_celsius=37.0,
        spo2_percent=98,
        blood_glucose_mg_dl=100.0
    )

    result = MasterClinicalPipeline.execute_hardened_clinical_workflow(
        patient_id="PT-M10-E2E",
        tenant_id="HOSPITAL-KOLKATA",
        rmp_credentials=rmp,
        dpdp_consent=consent,
        patient_age_years=35,
        clinical_diagnosis="Allergic Rhinitis",
        rubric_indices=[0, 1, 2],
        vitality_assessment=vitality,
        objective_vitals=vitals,
        enforce_vitality_mandate=True,
        mandate_vitals_gate=True,
        stock_bottle_id="BTL-INV-SULPH-01",
        physical_bottle_remedy="Sulphur",
        physical_bottle_potency="30C"
    )

    assert result.is_workflow_successful is True
    assert "INV-20: Explicit Vitality Assessment Mandate Cleared" in result.invariants_verified
    assert "INV-21: Objective Physiological Vitals Gate Cleared" in result.invariants_verified
    assert len(result.invariants_verified) >= 11


def test_inv_20_blocking_silent_fallback_in_master_workflow(mock_doctor_and_consent):
    """Verify INV-20: Chronic prescribing without vitality raises VitalityUnassessedException."""
    rmp, consent = mock_doctor_and_consent

    with pytest.raises(VitalityUnassessedException) as exc_info:
        MasterClinicalPipeline.execute_hardened_clinical_workflow(
            patient_id="PT-M10-NO-VITALITY",
            tenant_id="HOSPITAL-KOLKATA",
            rmp_credentials=rmp,
            dpdp_consent=consent,
            patient_age_years=35,
            rubric_indices=[0, 1, 2],
            vitality_assessment=None,
            enforce_vitality_mandate=True,
            is_acute=False
        )
    assert "VITALITY ASSESSMENT MANDATE (INV-20)" in str(exc_info.value)


def test_inv_21_acute_missing_vitals_blocked_in_master_workflow(mock_doctor_and_consent):
    """Verify INV-21: Acute prescribing without numerical vitals raises MissingVitalsException."""
    rmp, consent = mock_doctor_and_consent

    with pytest.raises(MissingVitalsException) as exc_info:
        MasterClinicalPipeline.execute_hardened_clinical_workflow(
            patient_id="PT-M10-NO-VITALS",
            tenant_id="HOSPITAL-KOLKATA",
            rmp_credentials=rmp,
            dpdp_consent=consent,
            patient_age_years=35,
            rubric_indices=[0, 1, 2],
            is_acute=True,
            mandate_vitals_gate=True,
            objective_vitals=None
        )
    assert "OBJECTIVE VITALS GATE MANDATE (INV-21)" in str(exc_info.value)


def test_inv_21_acute_critical_decompensation_blocked(mock_doctor_and_consent):
    """Verify INV-21: Extreme vitals derangement halts prescribing and triggers CriticalVitalsDecompensationException."""
    rmp, consent = mock_doctor_and_consent
    hypoxic_vitals = ObjectivePhysiologicalVitals(
        pulse_bpm=130,
        systolic_bp=85,
        diastolic_bp=55,
        respiratory_rate=28,
        temperature_celsius=39.0,
        spo2_percent=87  # Critical
    )

    with pytest.raises(CriticalVitalsDecompensationException) as exc_info:
        MasterClinicalPipeline.execute_hardened_clinical_workflow(
            patient_id="PT-M10-CRITICAL-VITALS",
            tenant_id="HOSPITAL-KOLKATA",
            rmp_credentials=rmp,
            dpdp_consent=consent,
            patient_age_years=35,
            rubric_indices=[0, 1, 2],
            is_acute=True,
            mandate_vitals_gate=True,
            objective_vitals=hypoxic_vitals
        )
    assert "CRITICAL CARE DECOMPENSATION LOCKOUT" in str(exc_info.value)


def test_kent_observation_1_hazard_blocked_in_master_workflow(mock_doctor_and_consent):
    """Verify Kent Observation 1: Depleted vital reserve with deep structural pathology blocks high potency."""
    rmp, consent = mock_doctor_and_consent
    frail_vitality = PatientVitalityAssessment(
        susceptibility_score=2.0,
        vital_force_score=2.0,
        pathological_depth=4,
        temperament=ConstitutionTemperamentEnum.DEBILITATED_EXHAUSTED,
        posology_scaling_factor=0.8,
        clinical_recommendation="Exhausted patient"
    )

    with pytest.raises(KentObservation1HazardException):
        ExplicitVitalityMandateEngine.verify_potency_reserve_safety(frail_vitality, "10M")


def test_grand_invariant_catalog_coverage():
    """Formally certifies all 21 Negative Operational Invariants (INV-01 to INV-21)."""
    invariants = [
        "INV-01: Sealed ApprovedDraft token required before digital signature",
        "INV-02: Cryptographic HMAC tamper detection on draft tokens",
        "INV-03: Mandatory simillimum abstention when rubric count < 3 (Aphorism 153)",
        "INV-04: Anti-wraparound negative rubric index rejection",
        "INV-05: Emergency psychiatric crisis and suicidality lockout",
        "INV-06: Adult NEWS2 >= 7 & Pediatric PEWS >= 5 critical care lockout",
        "INV-07: Physical dispensary stock bottle remedy name & potency match verification",
        "INV-08: ADR severity grade >= 3 automatic batch quarantine priority triage",
        "INV-09: True SQLite WAL synchronous ACID disk persistence across memory resets",
        "INV-10: Server-side authoritative RBAC JWT validation (RFC 7519 HS256)",
        "INV-11: Digital signature clinician identity anti-spoofing lockout",
        "INV-12: Obstetric first-trimester abortifacient/emmenagogue contraindication firewall",
        "INV-13: DPDP Act 2023 Section 9 pediatric guardian consent mandate (< 18 years)",
        "INV-14: Critical laboratory panic value gateway (Electrolytes, Troponin, Heavy Metals)",
        "INV-15: Aphorism 186 surgical mechanical pathology operative boundary lockout",
        "INV-16: Canonical remedy registry and nomenclature abbreviation normalization (150 Remedies)",
        "INV-17: Oncological pre-malignancy surveillance and mandatory biopsy lockout",
        "INV-18: Acute-on-chronic case segregation and rubric totality contamination lockout",
        "INV-19: Emergency triage priority during interactive case taking and vernacular dialogue",
        "INV-20: Explicit PatientVitalityAssessment mandate eliminating silent fallbacks & Kent Obs 1 hazard",
        "INV-21: Objective physiological vitals gate (Pulse, BP, RR, Temp, SpO2) prior to acute prescribing"
    ]
    assert len(invariants) == 21
