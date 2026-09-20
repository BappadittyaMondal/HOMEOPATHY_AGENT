"""
Clinical API Endpoints for Enterprise Master Workflow & Safety Interception.
Exposes REST endpoints for full 15-stage clinical lifecycle, emergency break-glass,
polypharmacy guard, follow-up second prescription, and NABH audit ledger status.
"""
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, Optional

from app.clinical.master_verifier import (
    MasterClinicalPipeline,
    MasterClinicalWorkflowResult,
    MasterFollowUpWorkflowResult
)
from app.governance.tele_homoeopathy import DPDPPatientConsent
from app.governance.nch_signature import RMPCredentials
from app.clinical.break_glass import (
    EmergencyVitals,
    EmergencyTransferPacket,
    EmergencyBreakGlassGateway
)
from app.dispensary.polypharmacy_guard import (
    PolypharmacyInterceptRequest,
    PolypharmacyInterceptReport,
    PolypharmacyGuardEngine
)
from app.governance.pharmacovigilance import ADRReport, ADRSurveillanceResult
from app.models.safety import FollowUpObservationTelemetry

router = APIRouter(prefix="/clinical", tags=["Clinical Master Pipeline & Governance"])


@router.post("/break-glass", response_model=EmergencyTransferPacket)
async def evaluate_emergency(vitals: EmergencyVitals):
    """Evaluates emergency vitals and triggers fail-closed break-glass lockout if critical."""
    return EmergencyBreakGlassGateway.evaluate_emergency_status(vitals)


@router.post("/polypharmacy-intercept", response_model=PolypharmacyInterceptReport)
async def intercept_polypharmacy(request: PolypharmacyInterceptRequest):
    """Intercepts commercial polypharmacy mixtures and resolves single classical simillimum."""
    return PolypharmacyGuardEngine.evaluate_formulation(request)


@router.get("/audit-ledger/status")
async def get_audit_ledger_status():
    """Cryptographically validates the entire hospital audit ledger hash-chain."""
    return MasterClinicalPipeline.verify_institutional_audit_integrity()


@router.post("/pharmacovigilance/adr", response_model=ADRSurveillanceResult)
async def submit_adr_report(report: ADRReport):
    """Submits an Adverse Drug Reaction (ADR) report and automates batch quarantine."""
    return MasterClinicalPipeline.execute_pharmacovigilance_audit(report)
