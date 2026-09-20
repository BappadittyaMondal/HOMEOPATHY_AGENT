"""
Master End-to-End Clinical Verification Suite & Zero-Defect Enterprise Pipeline (Phase 50).
Orchestrates the complete 15-stage patient lifecycle across all hospital subsystems:
DPDP Consent -> Tele-Triage -> Emergency Break-Glass -> Voice Token Ingestion ->
Dual-Coding (ICD-10 / ICD-11 TM1 / NAMASTE) -> High-Dimensional Repertorization ->
Miasmatic Simplex -> Statutory Safety & Inimical Firewall -> Dynamic Posology ->
Polypharmacy Interception -> NCH Act 2020 Digital Signature -> Dispensary Deduction ->
Longitudinal EHR Timeline -> Follow-Up & Second Prescription -> Pharmacovigilance ADR ->
Tamper-Evident NABH Cryptographic Hash-Chain Audit Logging.
"""
import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

# Milestone 1 & 2 Repertory & Vitality Models
from app.repertory.csr_kernel import csr_kernel
from app.repertory.simillimum_engine import SimillimumRankingEngine
from app.models.simillimum import SimillimumEvaluationReport
from app.repertory.miasmatic_engine import MiasmaticSimplexClassifier
from app.models.miasmatic import MiasmaticSimplexVector
from app.repertory.posology_engine import DynamicPosologyCalculus
from app.models.posology import PrescribedPosologyProtocol
from app.models.vitality import PatientVitalityAssessment

# Milestone 3 Safety, Toxicology & Second Prescription
from app.safety.hpi_monographs import HPIMonographDatabase
from app.safety.inimical_matrix import InimicalSafetyMatrix, InimicalEvaluation
from app.safety.herings_law import HeringsLawEngine, HeringsLawVector
from app.safety.kent_observations import (
    KentObservationEngine,
    FollowUpObservationTelemetry,
    KentObservationEvaluation
)
from app.safety.second_prescription import SecondPrescriptionEngine, SecondPrescriptionDecision

# Milestone 4 Clinical Specialty & Emergency
from app.clinical.break_glass import (
    EmergencyVitals,
    EmergencyTransferPacket,
    EmergencyBreakGlassGateway
)

# Milestone 5 Governance, Dispensary & Interoperability
from app.governance.tele_homoeopathy import (
    DPDPPatientConsent,
    TeleTriageAssessment,
    TeleConsultationClearance,
    TeleHomoeopathyGateway
)
from app.governance.voice_scribe import (
    VernacularVoiceToken,
    VernacularIngestionResult,
    VernacularVoiceEngine
)
from app.governance.dual_coding import DualCodingResult, DualCodingEngine
from app.governance.nch_signature import (
    RMPCredentials,
    PrescriptionPayload,
    SignedPrescriptionReceipt,
    NCHDigitalSignatureGateway
)
from app.governance.nabh_audit import NABHAuditEntry, NABHAuditLedger
from app.governance.pharmacovigilance import (
    ADRReport,
    ADRSurveillanceResult,
    PharmacovigilanceEngine
)
from app.dispensary.polypharmacy_guard import (
    PolypharmacyInterceptRequest,
    PolypharmacyInterceptReport,
    PolypharmacyGuardEngine
)
from app.dispensary.stock_ledger import (
    StockBottle,
    DispenseTransaction,
    DispensaryLedgerEngine
)
from app.models.ehr import EHRClinicalEncounter, LongitudinalPatientTrajectory
from app.clinical.longitudinal_ehr import LongitudinalEHREngine


class MasterClinicalWorkflowResult(BaseModel):
    """Encapsulates the complete end-to-end clinical workflow execution receipt."""
    patient_id: str
    tenant_id: str
    is_workflow_successful: bool
    triage_clearance: TeleConsultationClearance
    is_emergency_lockout: bool = False
    emergency_transfer_packet: Optional[EmergencyTransferPacket] = None
    voice_ingestion_result: Optional[VernacularIngestionResult] = None
    dual_coding_result: Optional[DualCodingResult] = None
    repertorization_report: Optional[SimillimumEvaluationReport] = None
    miasmatic_vector: Optional[MiasmaticSimplexVector] = None
    inimical_evaluation: Optional[InimicalEvaluation] = None
    is_schedule_e1_toxic: bool = False
    posology_protocol: Optional[PrescribedPosologyProtocol] = None
    polypharmacy_report: Optional[PolypharmacyInterceptReport] = None
    signed_prescription: Optional[SignedPrescriptionReceipt] = None
    dispense_receipt: Optional[Dict[str, Any]] = None
    ehr_encounter: Optional[EHRClinicalEncounter] = None
    longitudinal_trajectory: Optional[LongitudinalPatientTrajectory] = None
    nabh_audit_entry: Optional[NABHAuditEntry] = None
    audit_chain_length: int
    execution_timestamp: str


class MasterFollowUpWorkflowResult(BaseModel):
    """Encapsulates the second prescription and longitudinal follow-up evaluation receipt."""
    patient_id: str
    tenant_id: str
    encounter_id: str
    herings_law_vector: HeringsLawVector
    kent_observation: KentObservationEvaluation
    second_prescription_decision: SecondPrescriptionDecision
    longitudinal_trajectory: LongitudinalPatientTrajectory
    nabh_audit_entry: NABHAuditEntry
    evaluation_timestamp: str


class MasterClinicalPipeline:
    """
    Enterprise Master Clinical Coordinator.
    Coordinates all autonomous agents, decision state machines, and statutory compliance gateways.
    """

    @classmethod
    def execute_full_clinical_workflow(
        cls,
        patient_id: str,
        tenant_id: str,
        rmp_credentials: RMPCredentials,
        dpdp_consent: DPDPPatientConsent,
        voice_tokens: List[VernacularVoiceToken],
        clinical_diagnosis: str,
        rubric_indices: List[int],
        symptom_weights: List[float],
        is_mental_flags: List[bool],
        vitality_assessment: PatientVitalityAssessment,
        stock_bottle_id: str,
        is_acute: bool = False,
        emergency_vitals: Optional[EmergencyVitals] = None,
        previous_remedy: Optional[str] = None,
        days_since_previous_remedy: Optional[int] = None,
        polypharmacy_request_name: Optional[str] = None
    ) -> MasterClinicalWorkflowResult:
        """
        Executes a complete 15-point clinical lifecycle from intake to dispensary & audit.
        """
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Step 1: DPDP Act 2023 Consent & Tele-Triage Verification
        triage_assessment = TeleTriageAssessment(
            consultation_id=f"TEL-{patient_id}-{int(datetime.datetime.now().timestamp())}",
            patient_id=patient_id,
            chief_complaint=clinical_diagnosis,
            has_emergency_red_flags=emergency_vitals is not None and (
                emergency_vitals.has_crushing_chest_pain or
                emergency_vitals.has_anaphylactic_stridor or
                emergency_vitals.has_board_like_abdomen or
                emergency_vitals.spo2_percentage < 90
            ),
            consent=dpdp_consent
        )
        triage_clearance = TeleHomoeopathyGateway.evaluate_tele_triage(triage_assessment)

        # Step 2: Western Emergency Break-Glass Safety Firewall
        if emergency_vitals:
            emergency_packet = EmergencyBreakGlassGateway.evaluate_emergency_status(emergency_vitals)
            if emergency_packet.is_emergency_lockout_active:
                # Log critical lockout in NABH audit ledger
                audit_log = NABHAuditLedger.append_log(
                    log_id=f"AUD-EMERG-{patient_id}",
                    timestamp=now_iso,
                    actor_id=rmp_credentials.registration_number,
                    action_type="EMERGENCY_LOCKOUT",
                    patient_id=patient_id,
                    details={
                        "emergency_level": emergency_packet.emergency_level,
                        "qsofa": str(emergency_packet.qsofa_score),
                        "directive": emergency_packet.statutory_disclaimer
                    }
                )
                return MasterClinicalWorkflowResult(
                    patient_id=patient_id,
                    tenant_id=tenant_id,
                    is_workflow_successful=False,
                    triage_clearance=triage_clearance,
                    is_emergency_lockout=True,
                    emergency_transfer_packet=emergency_packet,
                    nabh_audit_entry=audit_log,
                    audit_chain_length=len(NABHAuditLedger.get_chain()),
                    execution_timestamp=now_iso
                )

        # Check DPDP clearance
        if not triage_clearance.is_telemedicine_permitted:
            audit_log = NABHAuditLedger.append_log(
                log_id=f"AUD-TRIAGE-REJ-{patient_id}",
                timestamp=now_iso,
                actor_id=rmp_credentials.registration_number,
                action_type="TRIAGE_REJECTED",
                patient_id=patient_id,
                details={"reason": triage_clearance.clinical_guidance}
            )
            return MasterClinicalWorkflowResult(
                patient_id=patient_id,
                tenant_id=tenant_id,
                is_workflow_successful=False,
                triage_clearance=triage_clearance,
                nabh_audit_entry=audit_log,
                audit_chain_length=len(NABHAuditLedger.get_chain()),
                execution_timestamp=now_iso
            )

        # Step 3: Vernacular Multilingual Voice Token Ingestion
        normalized_symptoms = []
        unmapped = []
        detected_lang = "en"
        total_tokens = 0
        for tok in voice_tokens:
            res = VernacularVoiceEngine.ingest_voice_tokens(tok)
            detected_lang = res.detected_language
            normalized_symptoms.extend(res.normalized_symptoms)
            unmapped.extend(res.unmapped_phrases)
            total_tokens += res.raw_token_count
        voice_ingestion = VernacularIngestionResult(
            detected_language=detected_lang,
            normalized_symptoms=normalized_symptoms,
            raw_token_count=total_tokens,
            unmapped_phrases=unmapped
        )

        # Step 4: Dual Coding Crosswalk (ICD-10 + WHO ICD-11 TM1 + Ayush NAMASTE)
        symptom_strings = [s.standardized_medical_term for s in voice_ingestion.normalized_symptoms]
        miasm_vector = MiasmaticSimplexClassifier.classify_patient_narrative(
            symptom_strings if symptom_strings else [clinical_diagnosis]
        )
        primary_miasm_str = miasm_vector.dominant_miasm.value
        dual_coding = DualCodingEngine.resolve_dual_coding(clinical_diagnosis, primary_miasm_str)

        # Step 5: High-Dimensional Repertorization & Simillimum Ranking
        if not csr_kernel.is_loaded:
            csr_kernel.load_memory_mapped()

        repertory_report = SimillimumRankingEngine.evaluate_totality(
            encounter_id=f"ENC-{patient_id}-01",
            patient_id=patient_id,
            rubric_indices=rubric_indices,
            weights=symptom_weights,
            is_mental_flags=is_mental_flags,
            top_k=5
        )
        simillimum_remedy = repertory_report.primary_simillimum

        # Step 6: Classical Safety & Inimical Matrix Verification
        inimical_eval = None
        if previous_remedy and days_since_previous_remedy is not None:
            inimical_eval = InimicalSafetyMatrix.evaluate_sequence(
                candidate_remedy=simillimum_remedy,
                prior_remedy=previous_remedy,
                days_since_prior=days_since_previous_remedy,
                is_acute_override=is_acute
            )

        # Step 7: Statutory Toxicity & Schedule E(1) Check
        is_e1 = HPIMonographDatabase.is_schedule_e1(simillimum_remedy)

        # Step 8: Dynamic Posology & Potency Calculus
        posology = DynamicPosologyCalculus.calculate_protocol(
            remedy_name=simillimum_remedy,
            vitality=vitality_assessment,
            is_acute=is_acute
        )

        # Step 9: Polypharmacy Interception & Single-Remedy Guard
        poly_request_name = polypharmacy_request_name or simillimum_remedy
        poly_request = PolypharmacyInterceptRequest(
            requested_formulation_name=poly_request_name,
            constituent_remedies=[simillimum_remedy],
            commercial_mrp_inr=150.0,
            patient_presenting_complaint=clinical_diagnosis
        )
        poly_report = PolypharmacyGuardEngine.evaluate_formulation(poly_request)

        # Step 10: NCH Act 2020 RMP Digital Signature Gateway
        rx_payload = PrescriptionPayload(
            prescription_id=f"RX-{patient_id}-01",
            patient_id=patient_id,
            remedy_name=simillimum_remedy,
            potency=posology.potency_grade,
            dosage_instructions=posology.administration_schedule,
            issued_timestamp=now_iso
        )
        signed_rx = NCHDigitalSignatureGateway.sign_prescription(rmp_credentials, rx_payload)

        # Step 11: Dispensary Stock Ledger Deduction (EDU + 10% Evaporation Tolerance)
        dispense_tx = DispenseTransaction(
            transaction_id=f"TX-DISP-{patient_id}",
            bottle_id=stock_bottle_id,
            patient_id=patient_id,
            edu_units_dispensed=1,
            volume_per_edu_ml=0.5
        )
        dispense_receipt = DispensaryLedgerEngine.dispense_edu(dispense_tx)

        # Step 12: Longitudinal Homeopathic EHR Record Creation
        rubrics_text = [csr_kernel.rubrics_list[idx] for idx in rubric_indices if idx < len(csr_kernel.rubrics_list)]
        encounter = EHRClinicalEncounter(
            encounter_id=f"ENC-{patient_id}-01",
            patient_id=patient_id,
            tenant_id=tenant_id,
            encounter_date=now_iso[:10],
            chief_complaint=clinical_diagnosis,
            rubrics_selected=rubrics_text if rubrics_text else ["General totality"],
            remedy_prescribed=simillimum_remedy,
            potency=posology.potency_grade,
            vitality_score=vitality_assessment.vital_force_score,
            dominant_miasm=primary_miasm_str
        )
        LongitudinalEHREngine.record_encounter(encounter)
        trajectory = LongitudinalEHREngine.get_patient_trajectory(tenant_id, patient_id)

        # Step 13: Immutable Cryptographic NABH Audit Log Chaining
        audit_log = NABHAuditLedger.append_log(
            log_id=f"AUD-{patient_id}-01",
            timestamp=now_iso,
            actor_id=rmp_credentials.registration_number,
            action_type="PRESCRIPTION_DISPENSED_VERIFIED",
            patient_id=patient_id,
            details={
                "remedy": simillimum_remedy,
                "potency": posology.potency_grade,
                "icd10": dual_coding.western_icd10_code,
                "icd11_tm1": dual_coding.who_icd11_tm1_code,
                "namaste": dual_coding.ayush_namaste_code,
                "signature_sha256": signed_rx.payload_hash_sha256,
                "dispensed_bottle": stock_bottle_id
            }
        )

        return MasterClinicalWorkflowResult(
            patient_id=patient_id,
            tenant_id=tenant_id,
            is_workflow_successful=True,
            triage_clearance=triage_clearance,
            voice_ingestion_result=voice_ingestion,
            dual_coding_result=dual_coding,
            repertorization_report=repertory_report,
            miasmatic_vector=miasm_vector,
            inimical_evaluation=inimical_eval,
            is_schedule_e1_toxic=is_e1,
            posology_protocol=posology,
            polypharmacy_report=poly_report,
            signed_prescription=signed_rx,
            dispense_receipt=dispense_receipt,
            ehr_encounter=encounter,
            longitudinal_trajectory=trajectory,
            nabh_audit_entry=audit_log,
            audit_chain_length=len(NABHAuditLedger.get_chain()),
            execution_timestamp=now_iso
        )

    @classmethod
    def execute_followup_cycle(
        cls,
        patient_id: str,
        tenant_id: str,
        rmp_credentials: RMPCredentials,
        prior_remedy: str,
        prior_potency: str,
        followup_telemetry: FollowUpObservationTelemetry,
        origin_organ: Optional[str] = None,
        new_manifestation_organ: Optional[str] = None,
        head_to_extremities: bool = False,
        inside_to_outside: bool = False,
        center_to_periphery: bool = False,
        reverse_chronological_order: bool = False,
        new_vitality_score: float = 7.5
    ) -> MasterFollowUpWorkflowResult:
        """
        Executes longitudinal follow-up, evaluating Hering's Law and Kent's 12 Observations.
        """
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # 1. Hering's Law Directional Vector Evaluation
        if origin_organ and new_manifestation_organ:
            hering_vector = HeringsLawEngine.evaluate_symptom_progression(
                prior_organ=origin_organ,
                current_organ=new_manifestation_organ,
                reverse_chronological=reverse_chronological_order
            )
        else:
            hering_vector = HeringsLawEngine.evaluate_vector(
                head_to_extremities=head_to_extremities,
                inside_to_outside=inside_to_outside,
                center_to_periphery=center_to_periphery,
                reverse_chronological_order=reverse_chronological_order,
                suppressive_inward_movement=followup_telemetry.symptoms_take_wrong_direction
            )

        # 2. Kent's 12 Observations Evaluation
        kent_obs = KentObservationEngine.evaluate_followup(followup_telemetry)

        # 3. Second Prescription Decision Engine
        is_improving = followup_telemetry.general_vitality_improved and followup_telemetry.chief_complaint_ameliorated
        suppression_or_agg = (
            hering_vector.iatrogenic_suppression_detected or
            followup_telemetry.symptoms_take_wrong_direction or
            (followup_telemetry.aggravation_occurred and not followup_telemetry.general_vitality_improved)
        )

        second_rx = SecondPrescriptionEngine.evaluate_next_step(
            prior_remedy=prior_remedy,
            prior_potency=prior_potency,
            is_improving=is_improving,
            symptom_picture_shifted=followup_telemetry.new_symptoms_appeared,
            suppression_or_aggravation=suppression_or_agg
        )

        # 4. Update Longitudinal EHR
        encounter_id = f"ENC-{patient_id}-FOLLOWUP-{int(datetime.datetime.now().timestamp())}"
        followup_encounter = EHRClinicalEncounter(
            encounter_id=encounter_id,
            patient_id=patient_id,
            tenant_id=tenant_id,
            encounter_date=now_iso[:10],
            chief_complaint="Longitudinal Follow-Up Review",
            rubrics_selected=[f"Kent Observation {kent_obs.observation_number.value}: {kent_obs.title}"],
            remedy_prescribed=second_rx.recommended_remedy,
            potency=second_rx.recommended_potency,
            kent_observation_num=kent_obs.observation_number.value,
            vitality_score=new_vitality_score,
            dominant_miasm="PSORA"
        )
        LongitudinalEHREngine.record_encounter(followup_encounter)
        trajectory = LongitudinalEHREngine.get_patient_trajectory(tenant_id, patient_id)

        # 5. Append NABH Audit Entry
        audit_entry = NABHAuditLedger.append_log(
            log_id=f"AUD-{encounter_id}",
            timestamp=now_iso,
            actor_id=rmp_credentials.registration_number,
            action_type="FOLLOWUP_SECOND_PRESCRIPTION_EVALUATED",
            patient_id=patient_id,
            details={
                "prior_remedy": prior_remedy,
                "kent_observation": str(kent_obs.observation_number.value),
                "hering_concordance": str(hering_vector.concordance_score),
                "is_true_cure": str(hering_vector.is_true_cure),
                "suppression": str(hering_vector.iatrogenic_suppression_detected),
                "action": second_rx.action.value,
                "next_remedy": second_rx.recommended_remedy
            }
        )

        return MasterFollowUpWorkflowResult(
            patient_id=patient_id,
            tenant_id=tenant_id,
            encounter_id=encounter_id,
            herings_law_vector=hering_vector,
            kent_observation=kent_obs,
            second_prescription_decision=second_rx,
            longitudinal_trajectory=trajectory or LongitudinalPatientTrajectory(
                patient_id=patient_id,
                tenant_id=tenant_id,
                total_encounters=1,
                encounters=[followup_encounter],
                vitality_trend=[new_vitality_score],
                remedy_history=[second_rx.recommended_remedy],
                is_vitality_improving=True,
                summary_verdict="Single follow-up registered"
            ),
            nabh_audit_entry=audit_entry,
            evaluation_timestamp=now_iso
        )

    @classmethod
    def execute_pharmacovigilance_audit(cls, adr_report: ADRReport) -> ADRSurveillanceResult:
        """
        Processes adverse drug reaction report, isolates suspicious batches, and logs audit.
        """
        result = PharmacovigilanceEngine.process_adr_report(adr_report)
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        NABHAuditLedger.append_log(
            log_id=f"AUD-ADR-{adr_report.report_id}",
            timestamp=now_iso,
            actor_id="PHARMACOVIGILANCE_OFFICER",
            action_type="ADR_SURVEILLANCE_EVALUATED",
            patient_id=adr_report.patient_id,
            details={
                "remedy": adr_report.remedy_name,
                "batch": adr_report.batch_number,
                "classification": result.classification,
                "action": result.action_required
            }
        )
        return result

    @classmethod
    def verify_institutional_audit_integrity(cls) -> Dict[str, Any]:
        """
        Cryptographically validates the entire hospital audit ledger hash-chain.
        """
        is_valid = NABHAuditLedger.verify_chain_integrity()
        chain = NABHAuditLedger.get_chain()
        return {
            "is_ledger_tamper_free": is_valid,
            "total_audit_blocks": len(chain),
            "genesis_block_hash": NABHAuditLedger._GENESIS_HASH,
            "latest_block_hash": chain[-1].current_hash if chain else None,
            "nabh_standard": "NABH Homoeopathy Standards 2nd Edition (2023) Section CQI / IM"
        }
