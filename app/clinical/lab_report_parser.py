"""
Multi-Parameter Laboratory Diagnostic Report Parser & Automated Panic Pipeline (Phase 73).

Provides deterministic clinical entity extraction, unit standardization, and reference-range
evaluation for scanned or transcribed laboratory reports (CBC, KFT, LFT, Electrolytes,
Cardiac Biomarkers, and Heavy Metal Environmental Toxicology).
Directly interfaces with LaboratoryPanicGateway to enforce INV-14 without manual clinician data entry.
"""
import re
import uuid
from typing import Dict, List, Optional, Tuple, Any
from pydantic import BaseModel, Field

from app.clinical.lab_gateway import (
    LaboratoryPanicGateway,
    LabObservation,
    LabPanelObservation,
    LabEvaluationResult
)


class ParsedLabItem(BaseModel):
    analyte_canonical_name: str
    raw_text: str
    value: float
    unit: str
    reference_low: Optional[float] = None
    reference_high: Optional[float] = None
    is_abnormal: bool = False
    is_panic: bool = False
    clinical_risk: Optional[str] = None


class ParsedLabReport(BaseModel):
    report_id: str = Field(default_factory=lambda: f"LAB-{uuid.uuid4().hex[:8].upper()}")
    patient_id: str
    lab_facility_name: Optional[str] = "CENTRAL_CLINICAL_LAB"
    report_date: Optional[str] = None
    items: List[ParsedLabItem] = Field(default_factory=list)
    has_panic_values: bool = False
    panic_findings: List[str] = Field(default_factory=list)
    statutory_action_mandated: str = "PROCEED_WITH_STANDARD_CARE"
    overall_confidence: float = Field(default=0.95, ge=0.0, le=1.0)


class LabReportParserEngine:
    """
    Parses unstructured and semi-structured laboratory report text into structured clinical telemetry.
    """

    # Comprehensive Analyte Lexicon and Extraction Regex Patterns
    ANALYTE_DEFINITIONS: Dict[str, Dict[str, Any]] = {
        # --- CARDIAC BIOMARKERS ---
        "troponin_i": {
            "aliases": [r"troponin[- ]?i", r"trop[- ]?i", r"c-tn-i", r"cardiac troponin i"],
            "unit": "ng/mL",
            "ref_low": 0.0,
            "ref_high": 0.04,
            "panic_high": 0.04,
            "hazard": "Acute myocardial infarction / active myocardial necrosis"
        },
        # --- ELECTROLYTES ---
        "potassium": {
            "aliases": [r"potassium", r"serum k\+?", r"\bk\+\b"],
            "unit": "mEq/L",
            "ref_low": 3.5,
            "ref_high": 5.1,
            "panic_low": 2.5,
            "panic_high": 6.2,
            "hazard": "Lethal ventricular arrhythmia / cardiac arrest"
        },
        "sodium": {
            "aliases": [r"sodium", r"serum na\+?", r"\bna\+\b"],
            "unit": "mEq/L",
            "ref_low": 135.0,
            "ref_high": 145.0,
            "panic_low": 120.0,
            "panic_high": 160.0,
            "hazard": "Severe hyponatremic encephalopathy / central pontine myelinolysis"
        },
        # --- HEMATOLOGY (CBC) ---
        "platelets": {
            "aliases": [r"platelets?(?: count)?", r"plt", r"thrombocytes?(?: count)?"],
            "unit": "/uL",
            "ref_low": 150000.0,
            "ref_high": 450000.0,
            "panic_low": 20000.0,
            "panic_high": 1000000.0,
            "hazard": "Spontaneous fatal intracranial / visceral hemorrhage"
        },
        "hemoglobin": {
            "aliases": [r"hemoglobin", r"haemoglobin", r"\bhb\b"],
            "unit": "g/dL",
            "ref_low": 12.0,
            "ref_high": 17.0,
            "panic_low": 6.5,
            "panic_high": 20.0,
            "hazard": "Severe hemodynamic anemia / high output heart failure"
        },
        "wbc_count": {
            "aliases": [r"total wbc(?: count)?", r"tlc", r"white blood cells?", r"leukocyte count"],
            "unit": "/uL",
            "ref_low": 4000.0,
            "ref_high": 11000.0,
            "panic_low": 2000.0,
            "panic_high": 30000.0,
            "hazard": "Agranulocytosis or hyperleukocytosis leukostasis"
        },
        # --- RENAL FUNCTION (KFT) ---
        "creatinine": {
            "aliases": [r"serum creatinine", r"creatinine", r"s\.?creat"],
            "unit": "mg/dL",
            "ref_low": 0.6,
            "ref_high": 1.2,
            "panic_high": 4.0,
            "hazard": "Acute renal failure with uremic encephalopathy"
        },
        "blood_urea": {
            "aliases": [r"blood urea(?: nitrogen)?", r"urea", r"bun"],
            "unit": "mg/dL",
            "ref_low": 15.0,
            "ref_high": 45.0,
            "panic_high": 100.0,
            "hazard": "Severe uremic toxemia"
        },
        # --- HEPATIC FUNCTION (LFT) ---
        "bilirubin": {
            "aliases": [r"total bilirubin", r"serum bilirubin", r"s\.?bili"],
            "unit": "mg/dL",
            "ref_low": 0.2,
            "ref_high": 1.2,
            "panic_high": 12.0,
            "hazard": "Fulminant hepatic failure / kernicterus risk"
        },
        "sgpt_alt": {
            "aliases": [r"sgpt", r"alt", r"alanine aminotransferase"],
            "unit": "U/L",
            "ref_low": 7.0,
            "ref_high": 56.0,
            "panic_high": 1000.0,
            "hazard": "Acute acute hepatic necrosis"
        },
        # --- METABOLIC ---
        "glucose": {
            "aliases": [r"fasting blood sugar", r"fbs", r"blood glucose(?: random)?", r"rbs", r"ppbs"],
            "unit": "mg/dL",
            "ref_low": 70.0,
            "ref_high": 140.0,
            "panic_low": 50.0,
            "panic_high": 450.0,
            "hazard": "Severe neuroglycopenic coma (low) or DKA / HHS (high)"
        },
        # --- HEAVY METALS (INV-14 Extended) ---
        "urine_arsenic": {
            "aliases": [r"urine arsenic", r"arsenic in urine", r"u\.?arsenic"],
            "unit": "ug/L",
            "ref_low": 0.0,
            "ref_high": 35.0,
            "panic_high": 50.0,
            "hazard": "Active chronic / acute arsenic toxicity with multiorgan collapse risk"
        },
        "blood_lead": {
            "aliases": [r"blood lead(?: level)?", r"bll", r"lead in blood"],
            "unit": "ug/dL",
            "ref_low": 0.0,
            "ref_high": 3.5,
            "panic_high": 5.0,
            "hazard": "Severe plumbism, encephalopathy and microcytic sideroblastic crisis"
        }
    }

    @classmethod
    def parse_lab_text(cls, patient_id: str, report_text: str) -> ParsedLabReport:
        """
        Extracts numerical lab analytes, standardizes units, checks reference boundaries and panic thresholds.
        """
        lines = report_text.splitlines()
        extracted_items: List[ParsedLabItem] = []
        panic_findings: List[str] = []

        for canonical_name, cfg in cls.ANALYTE_DEFINITIONS.items():
            pattern_str = r"(?:" + "|".join(cfg["aliases"]) + r")[:\s\-]+([0-9]+(?:\.[0-9]+)?)"
            
            # Search line by line or across text
            for line in lines:
                match = re.search(pattern_str, line, re.IGNORECASE)
                if match:
                    raw_val_str = match.group(1)
                    val = float(raw_val_str)
                    
                    # Normalize special platelet representations (e.g. 1.2 lakhs -> 120,000)
                    if canonical_name == "platelets":
                        if "lakh" in line.lower() or val < 1000.0:
                            val = val * 100000.0 if "lakh" in line.lower() else val * 1000.0

                    ref_low = cfg.get("ref_low")
                    ref_high = cfg.get("ref_high")
                    panic_low = cfg.get("panic_low")
                    panic_high = cfg.get("panic_high")

                    is_panic = False
                    clinical_risk = None

                    if panic_low is not None and val < panic_low:
                        is_panic = True
                        clinical_risk = f"CRITICAL LOW: {cfg['hazard']} (< {panic_low} {cfg['unit']})"
                    elif panic_high is not None and val >= panic_high:
                        is_panic = True
                        clinical_risk = f"CRITICAL HIGH: {cfg['hazard']} (>= {panic_high} {cfg['unit']})"

                    is_abnormal = is_panic
                    if not is_abnormal:
                        if ref_low is not None and val < ref_low:
                            is_abnormal = True
                        elif ref_high is not None and val > ref_high:
                            is_abnormal = True

                    if is_panic:
                        panic_findings.append(f"{canonical_name.upper()} = {val} {cfg['unit']} -> {clinical_risk}")

                    item = ParsedLabItem(
                        analyte_canonical_name=canonical_name,
                        raw_text=line.strip(),
                        value=val,
                        unit=cfg["unit"],
                        reference_low=ref_low,
                        reference_high=ref_high,
                        is_abnormal=is_abnormal,
                        is_panic=is_panic,
                        clinical_risk=clinical_risk
                    )
                    extracted_items.append(item)
                    break # Take first matching instance for this analyte

        has_panic = len(panic_findings) > 0
        statutory_action = (
            "EMERGENCY_LOCKOUT_TRANSFER_MANDATED" if has_panic else "PROCEED_WITH_STANDARD_CARE"
        )

        return ParsedLabReport(
            patient_id=patient_id,
            items=extracted_items,
            has_panic_values=has_panic,
            panic_findings=panic_findings,
            statutory_action_mandated=statutory_action
        )

    @classmethod
    def convert_to_gateway_panel(cls, report: ParsedLabReport) -> LabPanelObservation:
        """
        Converts parsed report directly into LaboratoryPanicGateway observation format.
        """
        observations = []
        for item in report.items:
            observations.append(LabObservation(
                analyte=item.analyte_canonical_name,
                value=item.value,
                unit=item.unit,
                is_panic_value=item.is_panic,
                clinical_risk=item.clinical_risk
            ))

        return LabPanelObservation(
            patient_id=report.patient_id,
            panel_name="AUTOMATED_INGESTED_LAB_PANEL",
            timestamp="2026-09-24T22:20:00Z",
            observations=observations
        )
