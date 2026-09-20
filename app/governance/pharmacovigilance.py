"""
Homoeopathic Pharmacovigilance & Adverse Drug Reaction (ADR) Surveillance System (Phase 47 & Phase 54).
Codifies National Pharmacovigilance Centre for Ayush reporting protocols,
enforces Severity-First Ordering (INV-08), and issues automatic batch quarantines to dispensary stock.
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from app.dispensary.stock_ledger import DispensaryLedgerEngine


class ADRReport(BaseModel):
    report_id: str
    patient_id: str
    remedy_name: str
    potency: str
    batch_number: str
    manufacturer: str
    reaction_symptoms: List[str]
    is_general_vitality_improved: bool
    are_symptoms_new: bool  # New symptoms not belonging to patient's natural disease
    severity_grade: int = Field(..., ge=1, le=5)  # 1 = Mild, 5 = Fatal/Life-threatening


class ADRSurveillanceResult(BaseModel):
    report_id: str
    remedy_name: str
    batch_number: str
    classification: str  # "CURATIVE_HOMEOPATHIC_AGGRAVATION", "ADVERSE_DRUG_REACTION_CONFIRMED", "TOXIC_CONTAMINATION", "MILD_MEDICINAL_PROVING"
    action_required: str  # "SAC_LAC_WAIT", "ISOLATE_AND_QUARANTINE_BATCH", "NOTIFY_NATIONAL_PHARMACOVIGILANCE_CENTRE", "STOP_MEDICINE_AND_MONITOR"
    regulatory_notice: str
    requires_batch_quarantine: bool = False


class PharmacovigilanceEngine:
    """
    Evaluates reported adverse events, classifies homeopathic reactions, and triggers batch quarantines.
    Enforces INV-08 (Severity-First Ordering: Grade >= 3 is NEVER dismissed as curative aggravation).
    """

    _QUARANTINED_BATCHES: List[str] = []

    @classmethod
    def process_adr_report(cls, report: ADRReport) -> ADRSurveillanceResult:
        """
        Differentiates between curative homeopathic aggravation and true ADR, enforcing regulatory quarantine.
        SEVERITY-FIRST ORDERING (INV-08): Grade 3, 4, 5 reactions are unconditionally classified as ADR
        and trigger immediate batch quarantine regardless of reported vitality.
        """
        # 1. Severity-First Ordering (INV-08): Severe / Life-Threatening ADR or Contamination
        if report.severity_grade >= 3 or report.are_symptoms_new:
            if report.batch_number not in cls._QUARANTINED_BATCHES:
                cls._QUARANTINED_BATCHES.append(report.batch_number)
            
            # Synchronously quarantine in physical dispensary stock ledger
            DispensaryLedgerEngine.quarantine_batch(report.batch_number)

            return ADRSurveillanceResult(
                report_id=report.report_id,
                remedy_name=report.remedy_name,
                batch_number=report.batch_number,
                classification="ADVERSE_DRUG_REACTION_CONFIRMED",
                action_required="ISOLATE_AND_QUARANTINE_BATCH",
                requires_batch_quarantine=True,
                regulatory_notice=(
                    f"STATUTORY PHARMACOVIGILANCE ALERT (INV-08): Severe adverse event (Grade {report.severity_grade}). "
                    f"Batch {report.batch_number} of {report.remedy_name} is placed under IMMEDIATE QUARANTINE. "
                    f"Stop dispensing immediately. Mandatory submission of Form PvPI-Ayush-01 to National Pharmacovigilance Centre."
                )
            )

        # 2. Curative Homeopathic Aggravation (Aphorism 280): ONLY for mild/moderate (Grade 1-2) transient symptom flare
        if report.is_general_vitality_improved and not report.are_symptoms_new:
            return ADRSurveillanceResult(
                report_id=report.report_id,
                remedy_name=report.remedy_name,
                batch_number=report.batch_number,
                classification="CURATIVE_HOMEOPATHIC_AGGRAVATION",
                action_required="SAC_LAC_WAIT",
                requires_batch_quarantine=False,
                regulatory_notice=(
                    "Clinical evaluation confirms expected primary homeopathic aggravation (Aphorism 280). "
                    "Patient vitality is improved and reaction is mild (Grade <= 2). Do not repeat dose; administer placebo and observe."
                )
            )

        # 3. Mild Idiosyncratic or Pathogenetic Proving
        return ADRSurveillanceResult(
            report_id=report.report_id,
            remedy_name=report.remedy_name,
            batch_number=report.batch_number,
            classification="MILD_MEDICINAL_PROVING",
            action_required="STOP_MEDICINE_AND_MONITOR",
            requires_batch_quarantine=False,
            regulatory_notice="Mild pathogenetic proving symptoms detected. Antidote if symptoms persist."
        )

    @classmethod
    def is_batch_quarantined(cls, batch_number: str) -> bool:
        """Checks if a batch is under active pharmacovigilance quarantine."""
        return batch_number in cls._QUARANTINED_BATCHES

    @classmethod
    def reset_surveillance(cls) -> None:
        """Clears quarantine list for testing."""
        cls._QUARANTINED_BATCHES.clear()
