"""
Homoeopathic Pharmacovigilance & Adverse Drug Reaction (ADR) Surveillance System (Phase 47).
Codifies National Pharmacovigilance Centre for Ayush reporting protocols,
differentiates homeopathic aggravation from toxic adverse reactions, and issues batch quarantines.
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

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
    classification: str  # "CURATIVE_HOMEOPATHIC_AGGRAVATION", "ADVERSE_DRUG_REACTION_CONFIRMED", "TOXIC_CONTAMINATION"
    action_required: str  # "SAC_LAC_WAIT", "ISOLATE_AND_QUARANTINE_BATCH", "NOTIFY_NATIONAL_PHARMACOVIGILANCE_CENTRE"
    regulatory_notice: str

class PharmacovigilanceEngine:
    """
    Evaluates reported adverse events, classifies homeopathic reactions, and triggers batch quarantines.
    """

    _QUARANTINED_BATCHES: List[str] = []

    @classmethod
    def process_adr_report(cls, report: ADRReport) -> ADRSurveillanceResult:
        """
        Differentiates between curative homeopathic aggravation and true ADR, enforcing regulatory quarantine.
        """
        # 1. Curative Homeopathic Aggravation: Existing symptoms intensified but mental/general vitality improved
        if report.is_general_vitality_improved and not report.are_symptoms_new:
            return ADRSurveillanceResult(
                report_id=report.report_id,
                remedy_name=report.remedy_name,
                batch_number=report.batch_number,
                classification="CURATIVE_HOMEOPATHIC_AGGRAVATION",
                action_required="SAC_LAC_WAIT",
                regulatory_notice=(
                    "Clinical evaluation confirms expected primary homeopathic aggravation (Aphorism 280). "
                    "Patient vitality is improved. Do not repeat dose; administer placebo and observe."
                )
            )

        # 2. Severe ADR or Contamination: New toxic symptoms, severe grade, or vitality worsening
        if report.severity_grade >= 3 or report.are_symptoms_new:
            if report.batch_number not in cls._QUARANTINED_BATCHES:
                cls._QUARANTINED_BATCHES.append(report.batch_number)

            return ADRSurveillanceResult(
                report_id=report.report_id,
                remedy_name=report.remedy_name,
                batch_number=report.batch_number,
                classification="ADVERSE_DRUG_REACTION_CONFIRMED",
                action_required="ISOLATE_AND_QUARANTINE_BATCH",
                regulatory_notice=(
                    f"STATUTORY PHARMACOVIGILANCE ALERT: Batch {report.batch_number} of {report.remedy_name} "
                    f"is placed under IMMEDIATE QUARANTINE. Stop dispensing immediately. "
                    f"Mandatory submission of Form PvPI-Ayush-01 to National Pharmacovigilance Centre."
                )
            )

        # 3. Mild Idiosyncratic or Pathogenetic Proving
        return ADRSurveillanceResult(
            report_id=report.report_id,
            remedy_name=report.remedy_name,
            batch_number=report.batch_number,
            classification="MILD_MEDICINAL_PROVING",
            action_required="STOP_MEDICINE_AND_MONITOR",
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
