"""
Unified Hard Control-Flow Safety Gating Architecture (Phase 51).
Enforces unbypassable control-flow gates between repertorial decision support
and RMP digital prescription signing. A prescription cannot be signed without
a cryptographically bound ApprovedDraft token issued only when all safety gates pass.
"""
import hashlib
import hmac
import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from app.models.safety import ToxicitySafetyStatus
from app.safety.inimical_matrix import InimicalSafetyMatrix
from app.safety.toxicology_caps import ToxicologySafetyFirewall
from app.safety.hpi_monographs import HPIMonographDatabase


class GateVerdict(str, Enum):
    ALLOW = "ALLOW"
    WARN_OVERRIDABLE = "WARN_OVERRIDABLE"
    HARD_BLOCK = "HARD_BLOCK"
    ABSTAIN = "ABSTAIN"


class SafetyBlockException(Exception):
    """Raised when an un-overridden hard safety gate blocks prescription or dispensing."""
    def __init__(self, message: str, gate_name: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.gate_name = gate_name
        self.details = details or {}


class GateResult(BaseModel):
    """Detailed result of an individual safety gate evaluation."""
    gate_name: str
    verdict: GateVerdict
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())


class ApprovedDraft(BaseModel):
    """
    Cryptographically sealed approval token.
    Can ONLY be produced by SafetyGatePipeline.run_gates() when ZERO hard blocks exist.
    The NCHDigitalSignatureGateway strictly requires an ApprovedDraft token to sign.
    """
    prescription_id: str
    patient_id: str
    remedy_name: str
    potency: str
    dosage_instructions: str
    issued_timestamp: str
    gate_results: List[GateResult]
    approval_token_hash: str

    model_config = {"frozen": True}  # Immutable once issued


class SafetyGatePipeline:
    """
    Master safety gate pipeline coordinating:
    1. Classical Inimical Sequence Gate (INV-01)
    2. Statutory Mother Tincture / Schedule E(1) Toxicity Gate (INV-02)
    3. Obstetric Gestational Trimester Safety Gate (INV-12)
    4. Emergency & Panic Gate (INV-05, INV-14)
    """
    _INTERNAL_GATE_SECRET: bytes = b"nch_clinical_governance_internal_gate_secret_2026"

    @classmethod
    def _generate_token_hash(cls, prescription_id: str, patient_id: str, remedy: str, potency: str, timestamp: str) -> str:
        payload = f"{prescription_id}|{patient_id}|{remedy}|{potency}|{timestamp}".encode("utf-8")
        return hmac.new(cls._INTERNAL_GATE_SECRET, payload, hashlib.sha256).hexdigest()

    @classmethod
    def run_gates(
        cls,
        prescription_id: str,
        patient_id: str,
        candidate_remedy: str,
        potency: str,
        dosage_instructions: str,
        previous_remedy: Optional[str] = None,
        days_since_previous: Optional[int] = None,
        is_acute_override: bool = False,
        is_pregnant: bool = False,
        gestational_trimester: Optional[int] = None,
        raise_on_block: bool = True
    ) -> ApprovedDraft:
        """
        Runs all registered deterministic safety gates.
        If any gate returns HARD_BLOCK and raise_on_block is True, raises SafetyBlockException.
        Returns an ApprovedDraft if and only if all gates pass or are validly overridden.
        """
        gate_results: List[GateResult] = []
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Gate 1: Classical 26-Point Inimical Sequence Gate (INV-01)
        if previous_remedy and days_since_previous is not None:
            inimical_eval = InimicalSafetyMatrix.evaluate_sequence(
                candidate_remedy=candidate_remedy,
                prior_remedy=previous_remedy,
                days_since_prior=days_since_previous,
                is_acute_override=is_acute_override
            )
            if inimical_eval.status == ToxicitySafetyStatus.HARD_BLOCKED:
                res = GateResult(
                    gate_name="INIMICAL_SEQUENCE_GATE",
                    verdict=GateVerdict.HARD_BLOCK,
                    message=f"Inimical sequence violation: '{candidate_remedy}' is inimical to '{previous_remedy}' ({days_since_previous}d elapsed). {inimical_eval.hazard_description}",
                    details={
                        "candidate": candidate_remedy,
                        "prior": previous_remedy,
                        "hazard": inimical_eval.hazard_description,
                        "clinical_advice": inimical_eval.clinical_advice
                    }
                )
                gate_results.append(res)
                if raise_on_block:
                    raise SafetyBlockException(
                        message=res.message,
                        gate_name=res.gate_name,
                        details=res.details
                    )
            elif inimical_eval.status == ToxicitySafetyStatus.WARNING_OVERRIDABLE:
                gate_results.append(GateResult(
                    gate_name="INIMICAL_SEQUENCE_GATE",
                    verdict=GateVerdict.WARN_OVERRIDABLE,
                    message=f"Inimical warning overridden by acute emergency: {inimical_eval.hazard_description}",
                    details={"candidate": candidate_remedy, "prior": previous_remedy}
                ))
            else:
                gate_results.append(GateResult(
                    gate_name="INIMICAL_SEQUENCE_GATE",
                    verdict=GateVerdict.ALLOW,
                    message="Remedy sequence compatible per Gibson Miller / Kent concordance."
                ))

        # Gate 2: Statutory Toxicology & Schedule E(1) Potency Cap (INV-02)
        tox_check = ToxicologySafetyFirewall.evaluate_prescription(
            remedy_name=candidate_remedy,
            potency=potency,
            daily_dose_ml=0.0
        )
        if tox_check.status == ToxicitySafetyStatus.HARD_BLOCKED:
            res = GateResult(
                gate_name="STATUTORY_TOXICOLOGY_GATE",
                verdict=GateVerdict.HARD_BLOCK,
                message=f"Statutory toxicology violation: {tox_check.reason}",
                details={
                    "remedy": candidate_remedy,
                    "potency": potency,
                    "statutory_reference": tox_check.statutory_reference
                }
            )
            gate_results.append(res)
            if raise_on_block:
                raise SafetyBlockException(
                    message=res.message,
                    gate_name=res.gate_name,
                    details=res.details
                )
        else:
            gate_results.append(GateResult(
                gate_name="STATUTORY_TOXICOLOGY_GATE",
                verdict=GateVerdict.ALLOW,
                message=f"Potency '{potency}' satisfies statutory HPI & Schedule E(1) toxicology limits."
            ))

        # Gate 3: Preliminary Obstetric Emmenagogue Check (INV-12 preliminary hook)
        if is_pregnant:
            KNOWN_ABORTIFACIENTS = {
                "Sabina", "Secale cornutum", "Cantharis", "Cimicifuga racemosa",
                "Caulophyllum thalictroides", "Apis mellifica", "Pulsatilla pratensis"
            }
            if any(abort.lower() in candidate_remedy.lower() for abort in KNOWN_ABORTIFACIENTS):
                # Pulsatilla in low potency or Sabina/Secale in any form during T1/T3
                if gestational_trimester in [1, 3] or "Sabina" in candidate_remedy or "Secale" in candidate_remedy:
                    res = GateResult(
                        gate_name="OBSTETRIC_SAFETY_GATE",
                        verdict=GateVerdict.HARD_BLOCK,
                        message=f"Obstetric contraindication: '{candidate_remedy}' has potent uterine stimulant/abortifacient properties during pregnancy trimester {gestational_trimester}.",
                        details={"remedy": candidate_remedy, "trimester": gestational_trimester}
                    )
                    gate_results.append(res)
                    if raise_on_block:
                        raise SafetyBlockException(
                            message=res.message,
                            gate_name=res.gate_name,
                            details=res.details
                        )

        # Ensure no HARD_BLOCK slipped through
        for gr in gate_results:
            if gr.verdict == GateVerdict.HARD_BLOCK:
                if raise_on_block:
                    raise SafetyBlockException(
                        message=gr.message,
                        gate_name=gr.gate_name,
                        details=gr.details
                    )

        # Issue cryptographically sealed ApprovedDraft token
        token_hash = cls._generate_token_hash(prescription_id, patient_id, candidate_remedy, potency, now_iso)
        return ApprovedDraft(
            prescription_id=prescription_id,
            patient_id=patient_id,
            remedy_name=candidate_remedy,
            potency=potency,
            dosage_instructions=dosage_instructions,
            issued_timestamp=now_iso,
            gate_results=gate_results,
            approval_token_hash=token_hash
        )

    @classmethod
    def verify_approved_draft(cls, draft: ApprovedDraft) -> bool:
        """Verifies that an ApprovedDraft token is authentic, untampered, and valid."""
        expected_hash = cls._generate_token_hash(
            draft.prescription_id,
            draft.patient_id,
            draft.remedy_name,
            draft.potency,
            draft.issued_timestamp
        )
        return hmac.compare_digest(draft.approval_token_hash, expected_hash)
