"""
Master End-to-End Clinical Verification Suite (Phase 50).
Verifies complete 15-stage clinical lifecycle, fail-closed emergency break-glass lockout,
polypharmacy commercial mixture interception, Hering's Law suppression detection,
Kent's 12 Observations second prescription FSM, and cryptographic NABH audit integrity.
"""
import pytest
from app.clinical.master_verifier import (
    MasterClinicalPipeline,
    MasterClinicalWorkflowResult,
    MasterFollowUpWorkflowResult
)
from app.governance.tele_homoeopathy import DPDPPatientConsent
from app.governance.voice_scribe import VernacularVoiceToken
from app.governance.nch_signature import RMPCredentials
from app.clinical.break_glass import EmergencyVitals
from app.dispensary.stock_ledger import StockBottle, DispensaryLedgerEngine
from app.models.vitality import PatientVitalityAssessment, ConstitutionTemperamentEnum
from app.models.safety import FollowUpObservationTelemetry
from app.governance.pharmacovigilance import ADRReport
from app.safety.second_prescription import SecondPrescriptionAction


@pytest.fixture(autouse=True)
def setup_dispensary_and_env():
    """Seeds test inventory bottle for Phase 50 end-to-end testing."""
    test_bottle = StockBottle(
        bottle_id="BTL-MASTER-POLY-01",
        remedy_name="Sulphur",
        potency="30C",
        initial_volume_ml=100.0,
        current_volume_ml=100.0,
        reorder_threshold_ml=15.0,
        evaporation_tolerance_pct=10.0
    )
    DispensaryLedgerEngine.register_bottle(test_bottle)


def test_full_curative_lifecycle_end_to_end():
    """
    Validates complete clinical lifecycle from DPDP consent and vernacular voice intake
    to high-dimensional repertorization, posology, digital signature, EDU dispensing,
    and cryptographic NABH audit logging.
    """
    rmp = RMPCredentials(
        rmp_name="Dr. Bappaditya Roy, MD (Hom)",
        registration_number="WBHC-19842",
        state_council="WBHC",
        is_active_practitioner=True
    )

    consent = DPDPPatientConsent(
        consent_id="CNS-M50-001",
        patient_id="PT-MASTER-01",
        consultation_mode="VIDEO",
        consent_timestamp="2026-09-20T12:00:00Z",
        has_agreed_to_telemedicine_limitations=True,
        right_to_withdraw_acknowledged=True
    )

    # Vernacular voice scribe tokens in Bengali
    voice_tokens = [
        VernacularVoiceToken(language="bn", raw_transcript="matha betha khub hoy", confidence=0.96),
        VernacularVoiceToken(language="bn", raw_transcript="buk jala korche", confidence=0.94),
        VernacularVoiceToken(language="bn", raw_transcript="khub thanda lage", confidence=0.98)
    ]

    vitality = PatientVitalityAssessment(
        susceptibility_score=7.0,
        vital_force_score=7.5,
        pathological_depth=1,
        temperament=ConstitutionTemperamentEnum.NERVOUS_INTELLECTUAL,
        is_suppressed_by_allopathy=False,
        posology_scaling_factor=26.25,
        clinical_recommendation="Moderate-high vitality with minimal organic lesion: 30C or 200C indicated."
    )

    result = MasterClinicalPipeline.execute_full_clinical_workflow(
        patient_id="PT-MASTER-01",
        tenant_id="HOSPITAL-CENTRAL-DELHI",
        rmp_credentials=rmp,
        dpdp_consent=consent,
        voice_tokens=voice_tokens,
        clinical_diagnosis="allergic asthma",
        rubric_indices=[0, 1, 2],
        symptom_weights=[5.0, 4.0, 3.5],
        is_mental_flags=[True, True, False],
        vitality_assessment=vitality,
        stock_bottle_id="BTL-MASTER-POLY-01",
        is_acute=False
    )

    # 1. Verification of Workflow Success
    assert result.is_workflow_successful is True
    assert result.is_emergency_lockout is False
    assert result.triage_clearance.is_telemedicine_permitted is True

    # 2. Voice Scribe & Dual-Coding
    assert result.voice_ingestion_result.detected_language == "bn"
    assert len(result.voice_ingestion_result.normalized_symptoms) == 3
    assert result.dual_coding_result.western_icd10_code == "J45.0"
    assert result.dual_coding_result.who_icd11_tm1_code == "TM1-HOM-01"
    assert result.dual_coding_result.ayush_namaste_code == "HOM-PSO-001"

    # 3. High-Dimensional Repertorization & Posology
    assert result.repertorization_report.total_evaluated > 0
    assert result.repertorization_report.primary_simillimum != "None"
    assert result.posology_protocol.potency_grade in ["30C", "200C", "LM 0/1"]

    # 4. NCH Act 2020 Statutory Digital Signature
    assert result.signed_prescription.is_statutorily_valid is True
    assert len(result.signed_prescription.cryptographic_signature) == 64

    # 5. Dispensary Stock Deduction (1 EDU = 0.5 mL)
    assert result.dispense_receipt["volume_deducted_ml"] == 0.5
    assert result.dispense_receipt["remaining_volume_ml"] == 99.5

    # 6. Longitudinal EHR Record
    assert result.ehr_encounter.patient_id == "PT-MASTER-01"
    assert result.longitudinal_trajectory.total_encounters >= 1

    # 7. NABH Cryptographic Hash-Chain
    assert result.nabh_audit_entry is not None
    assert result.audit_chain_length >= 1


def test_emergency_break_glass_critical_lockout():
    """
    Validates fail-closed clinical lockout when patient presents with
    acute life-threatening red flags (Code Red Critical).
    """
    rmp = RMPCredentials(
        rmp_name="Dr. S. Mukherjee, MD",
        registration_number="WBHC-22011",
        state_council="WBHC",
        is_active_practitioner=True
    )
    consent = DPDPPatientConsent(
        consent_id="CNS-EMERG-01",
        patient_id="PT-EMERG-99",
        consultation_mode="VIDEO",
        consent_timestamp="2026-09-20T12:05:00Z",
        has_agreed_to_telemedicine_limitations=True,
        right_to_withdraw_acknowledged=True
    )
    # Severe decompensation vitals (Cardiogenic shock / Impending Infarct)
    critical_vitals = EmergencyVitals(
        systolic_bp=82,
        diastolic_bp=50,
        respiratory_rate=28,
        heart_rate=125,
        gcs_score=14,
        spo2_percentage=88,
        has_crushing_chest_pain=True
    )
    vitality = PatientVitalityAssessment(
        susceptibility_score=2.0,
        vital_force_score=2.0,
        pathological_depth=4,
        temperament=ConstitutionTemperamentEnum.DEBILITATED_EXHAUSTED,
        posology_scaling_factor=0.8,
        clinical_recommendation="Critical exhaustion"
    )

    result = MasterClinicalPipeline.execute_full_clinical_workflow(
        patient_id="PT-EMERG-99",
        tenant_id="HOSPITAL-CENTRAL-DELHI",
        rmp_credentials=rmp,
        dpdp_consent=consent,
        voice_tokens=[],
        clinical_diagnosis="hypertension",
        rubric_indices=[0],
        symptom_weights=[1.0],
        is_mental_flags=[False],
        vitality_assessment=vitality,
        stock_bottle_id="BTL-MASTER-POLY-01",
        emergency_vitals=critical_vitals
    )

    assert result.is_workflow_successful is False
    assert result.is_emergency_lockout is True
    assert result.emergency_transfer_packet is not None
    assert result.emergency_transfer_packet.emergency_level == "CODE_RED_CRITICAL"
    assert result.signed_prescription is None
    assert result.dispense_receipt is None
    assert "STATUTORY CRITICAL CARE DIRECTIVE" in result.emergency_transfer_packet.statutory_disclaimer


def test_polypharmacy_commercial_complex_interception():
    """
    Validates interception of unscientific commercial polypharmacy mixtures
    and conversion to single classical simillimum per Organon Aphorism 273.
    """
    rmp = RMPCredentials(
        rmp_name="Dr. Bappaditya Roy",
        registration_number="WBHC-19842",
        state_council="WBHC",
        is_active_practitioner=True
    )
    consent = DPDPPatientConsent(
        consent_id="CNS-POLY-01",
        patient_id="PT-POLY-02",
        consultation_mode="AUDIO",
        consent_timestamp="2026-09-20T12:10:00Z",
        has_agreed_to_telemedicine_limitations=True,
        right_to_withdraw_acknowledged=True
    )
    vitality = PatientVitalityAssessment(
        susceptibility_score=6.0,
        vital_force_score=6.5,
        pathological_depth=1,
        temperament=ConstitutionTemperamentEnum.SANGUINE_ACTIVE,
        posology_scaling_factor=19.5,
        clinical_recommendation="Standard vitality"
    )

    result = MasterClinicalPipeline.execute_full_clinical_workflow(
        patient_id="PT-POLY-02",
        tenant_id="HOSPITAL-CENTRAL-DELHI",
        rmp_credentials=rmp,
        dpdp_consent=consent,
        voice_tokens=[],
        clinical_diagnosis="asthma",
        rubric_indices=[0, 1],
        symptom_weights=[4.0, 3.0],
        is_mental_flags=[False, False],
        vitality_assessment=vitality,
        stock_bottle_id="BTL-MASTER-POLY-01",
        polypharmacy_request_name="Cough Syrup Complex"
    )

    assert result.is_workflow_successful is True
    assert result.polypharmacy_report.is_polypharmacy_detected is True
    assert result.polypharmacy_report.single_simillimum_recommended == "Bryonia alba"
    assert result.polypharmacy_report.cost_savings_percentage >= 90.0


def test_followup_curative_hering_and_kent_observation():
    """
    Validates follow-up evaluation when patient demonstrates Hering's Law of Cure
    and Kent Observation 3 (Quick aggravation, rapid lasting recovery) -> Sac Lac.
    """
    rmp = RMPCredentials(
        rmp_name="Dr. Bappaditya Roy",
        registration_number="WBHC-19842",
        state_council="WBHC",
        is_active_practitioner=True
    )

    telemetry = FollowUpObservationTelemetry(
        aggravation_occurred=True,
        aggravation_duration_days=2,
        aggravation_severity="MILD",
        general_vitality_improved=True,
        chief_complaint_ameliorated=True,
        new_symptoms_appeared=False,
        old_symptoms_returned=False,
        days_since_prescription=14
    )

    followup = MasterClinicalPipeline.execute_followup_cycle(
        patient_id="PT-MASTER-01",
        tenant_id="HOSPITAL-CENTRAL-DELHI",
        rmp_credentials=rmp,
        prior_remedy="Sulphur",
        prior_potency="30C",
        followup_telemetry=telemetry,
        origin_organ="lungs",
        new_manifestation_organ="skin",
        reverse_chronological_order=True,
        new_vitality_score=8.5
    )

    assert followup.herings_law_vector.is_true_cure is True
    assert followup.herings_law_vector.iatrogenic_suppression_detected is False
    assert followup.kent_observation.observation_number.value == 3
    assert followup.second_prescription_decision.action == SecondPrescriptionAction.SAC_LAC_PLACEBO
    assert followup.second_prescription_decision.recommended_remedy == "Sac Lac"


def test_followup_suppression_and_antidote_directive():
    """
    Validates detection of iatrogenic suppression (symptoms driven centripetally
    from skin to internal viscera / wrong direction) triggering mandatory antidote.
    """
    rmp = RMPCredentials(
        rmp_name="Dr. Bappaditya Roy",
        registration_number="WBHC-19842",
        state_council="WBHC",
        is_active_practitioner=True
    )

    telemetry = FollowUpObservationTelemetry(
        aggravation_occurred=True,
        aggravation_duration_days=10,
        aggravation_severity="SEVERE_VIOLENT",
        general_vitality_improved=False,
        chief_complaint_ameliorated=False,
        new_symptoms_appeared=True,
        old_symptoms_returned=False,
        days_since_prescription=7,
        symptoms_take_wrong_direction=True
    )

    followup = MasterClinicalPipeline.execute_followup_cycle(
        patient_id="PT-SUPPR-01",
        tenant_id="HOSPITAL-CENTRAL-DELHI",
        rmp_credentials=rmp,
        prior_remedy="Sulphur",
        prior_potency="200C",
        followup_telemetry=telemetry,
        origin_organ="skin",
        new_manifestation_organ="heart",
        new_vitality_score=3.0
    )

    assert followup.herings_law_vector.iatrogenic_suppression_detected is True
    assert followup.kent_observation.observation_number.value == 12
    assert followup.second_prescription_decision.action == SecondPrescriptionAction.ADMINISTER_ANTIDOTE


def test_pharmacovigilance_and_nabh_audit_integrity():
    """
    Validates ADR surveillance classifying severe toxic contamination,
    isolating batches, and verifying 100% cryptographic integrity of NABH audit ledger.
    """
    adr = ADRReport(
        report_id="ADR-M50-01",
        patient_id="PT-ADR-50",
        remedy_name="Aconitum napellus",
        potency="3X",
        batch_number="BATCH-TOXIC-778",
        manufacturer="Ayush Lab Ltd",
        reaction_symptoms=["Severe cardiac arrhythmia", "Paresthesias"],
        is_general_vitality_improved=False,
        are_symptoms_new=True,
        severity_grade=4
    )

    adr_result = MasterClinicalPipeline.execute_pharmacovigilance_audit(adr)
    assert adr_result.classification == "ADVERSE_DRUG_REACTION_CONFIRMED"
    assert adr_result.action_required == "ISOLATE_AND_QUARANTINE_BATCH"

    # Verify complete hospital cryptographic audit ledger
    audit_check = MasterClinicalPipeline.verify_institutional_audit_integrity()
    assert audit_check["is_ledger_tamper_free"] is True
    assert audit_check["total_audit_blocks"] > 0
    assert audit_check["latest_block_hash"] is not None


def test_clinical_api_endpoints_via_fastapi():
    """
    Validates that FastAPI exposes the clinical endpoints over HTTP
    for live browser/OPD clients without error.
    """
    import asyncio
    from httpx import AsyncClient, ASGITransport
    from app.main import app

    async def _test():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # 1. Test audit ledger status endpoint
            resp = await client.get("/api/v1/clinical/audit-ledger/status")
            assert resp.status_code == 200
            data = resp.json()
            assert data["is_ledger_tamper_free"] is True
            assert "NABH Homoeopathy Standards" in data["nabh_standard"]

            # 2. Test emergency break-glass endpoint
            vitals_payload = {
                "systolic_bp": 80,
                "diastolic_bp": 50,
                "respiratory_rate": 26,
                "heart_rate": 120,
                "gcs_score": 13,
                "spo2_percentage": 88,
                "has_crushing_chest_pain": True,
                "has_board_like_abdomen": False,
                "has_anaphylactic_stridor": False
            }
            resp = await client.post("/api/v1/clinical/break-glass", json=vitals_payload)
            assert resp.status_code == 200
            data = resp.json()
            assert data["is_emergency_lockout_active"] is True
            assert data["emergency_level"] == "CODE_RED_CRITICAL"

            # 3. Test polypharmacy interception endpoint
            poly_payload = {
                "requested_formulation_name": "Cough Syrup Complex",
                "constituent_remedies": ["Bryonia", "Drosera", "Ipecac", "Belladonna"],
                "commercial_mrp_inr": 220.0,
                "patient_presenting_complaint": "Violent spasmodic dry cough"
            }
            resp = await client.post("/api/v1/clinical/polypharmacy-intercept", json=poly_payload)
            assert resp.status_code == 200
            data = resp.json()
            assert data["is_polypharmacy_detected"] is True
            assert data["single_simillimum_recommended"] == "Bryonia alba"
            assert data["cost_savings_percentage"] > 90.0

    asyncio.run(_test())
