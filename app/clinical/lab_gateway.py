"""
Laboratory Telemetry Interface & Panic-Value Safety Gateway (Phase 58).
Ingests HL7/FHIR observation panels and halts homeopathic dispensing upon detecting
critical life-threatening panic values (INV-14).
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class LaboratoryPanicException(Exception):
    """Raised when a critical panic-level laboratory value is detected (INV-14)."""
    def __init__(self, message: str, analyte_name: str, observed_value: float, reference_panic_limit: str):
        super().__init__(message)
        self.message = message
        self.analyte_name = analyte_name
        self.observed_value = observed_value
        self.reference_panic_limit = reference_panic_limit


class LabObservation(BaseModel):
    analyte: str  # e.g., "potassium", "troponin_i", "platelets", "creatinine", "glucose", "bilirubin"
    value: float
    unit: str
    is_panic_value: bool = False
    clinical_risk: Optional[str] = None


class LabPanelObservation(BaseModel):
    patient_id: str
    panel_name: str  # e.g., "COMPREHENSIVE_METABOLIC", "CARDIAC_ENZYMES", "CBC"
    timestamp: str
    observations: List[LabObservation]


class LabEvaluationResult(BaseModel):
    patient_id: str
    is_safe_for_outpatient_care: bool
    has_critical_panic_values: bool
    panic_findings: List[str]
    statutory_action_mandated: str


class LaboratoryPanicGateway:
    """
    Evaluates objective laboratory telemetry against international critical panic value limits.
    Enforces INV-14: Panic values immediately lock outpatient homeopathic dispensing.
    """

    # Critical Panic Limits
    # analyte -> (low_panic, high_panic, unit, risk_description)
    PANIC_THRESHOLDS: Dict[str, Dict] = {
        "potassium": {
            "low": 2.5,
            "high": 6.2,
            "unit": "mEq/L",
            "hazard": "Lethal ventricular arrhythmia / cardiac arrest"
        },
        "troponin_i": {
            "low": None,
            "high": 0.04,
            "unit": "ng/mL",
            "hazard": "Acute myocardial infarction / active myocardial necrosis"
        },
        "platelets": {
            "low": 20000.0,
            "high": 1000000.0,
            "unit": "/uL",
            "hazard": "Spontaneous fatal intracranial / visceral hemorrhage"
        },
        "creatinine": {
            "low": None,
            "high": 4.0,
            "unit": "mg/dL",
            "hazard": "Acute renal failure with uremic encephalopathy"
        },
        "glucose": {
            "low": 50.0,
            "high": 450.0,
            "unit": "mg/dL",
            "hazard": "Severe neuroglycopenic coma (low) or Diabetic Ketoacidosis / HHS (high)"
        },
        "bilirubin": {
            "low": None,
            "high": 12.0,
            "unit": "mg/dL",
            "hazard": "Fulminant hepatic failure / kernicterus risk"
        },
        # Heavy Metal & Environmental Trace Element Toxicology (INV-14 Extended)
        "urine_arsenic": {
            "low": None,
            "high": 50.0,
            "unit": "ug/L",
            "hazard": "Active chronic / acute arsenic toxicity with multiorgan collapse risk"
        },
        "hair_arsenic": {
            "low": None,
            "high": 1.0,
            "unit": "ug/g",
            "hazard": "Severe chronic tissue arsenic bioaccumulation and premalignant keratopathy"
        },
        "nail_arsenic": {
            "low": None,
            "high": 1.0,
            "unit": "ug/g",
            "hazard": "Deep chronobiological heavy metal sequestration and vascular endothelial injury"
        },
        "blood_lead": {
            "low": None,
            "high": 5.0,
            "unit": "ug/dL",
            "hazard": "Plumbism / lead neurotoxicity, motor neuropathy, and encephalopathy"
        },
        "blood_mercury": {
            "low": None,
            "high": 10.0,
            "unit": "ug/L",
            "hazard": "Hydrargyrism / toxic mercury encephalopathy and tubular nephropathy"
        },
        "serum_fluoride": {
            "low": None,
            "high": 0.2,
            "unit": "mg/L",
            "hazard": "Fluorosis / toxic fluoride osseous and ligamentous calcification"
        }
    }

    @classmethod
    def evaluate_lab_panel(
        cls,
        panel: LabPanelObservation,
        raise_on_panic: bool = True
    ) -> LabEvaluationResult:
        """
        Evaluates a panel of laboratory observations.
        If any panic threshold is crossed, raises LaboratoryPanicException (INV-14).
        """
        panic_findings: List[str] = []

        for obs in panel.observations:
            analyte_key = obs.analyte.strip().lower()
            threshold = cls.PANIC_THRESHOLDS.get(analyte_key)
            if not threshold:
                continue

            low_limit = threshold.get("low")
            high_limit = threshold.get("high")

            if low_limit is not None and obs.value < low_limit:
                msg = (
                    f"CRITICAL LAB PANIC (INV-14): {obs.analyte.upper()} = {obs.value} {obs.unit} "
                    f"(Panic Low < {low_limit} {obs.unit}). Hazard: {threshold['hazard']}."
                )
                panic_findings.append(msg)
                obs.is_panic_value = True
                obs.clinical_risk = threshold["hazard"]

                if raise_on_panic:
                    raise LaboratoryPanicException(
                        message=msg,
                        analyte_name=obs.analyte,
                        observed_value=obs.value,
                        reference_panic_limit=f"< {low_limit} {obs.unit}"
                    )

            elif high_limit is not None and obs.value > high_limit:
                msg = (
                    f"CRITICAL LAB PANIC (INV-14): {obs.analyte.upper()} = {obs.value} {obs.unit} "
                    f"(Panic High > {high_limit} {obs.unit}). Hazard: {threshold['hazard']}."
                )
                panic_findings.append(msg)
                obs.is_panic_value = True
                obs.clinical_risk = threshold["hazard"]

                if raise_on_panic:
                    raise LaboratoryPanicException(
                        message=msg,
                        analyte_name=obs.analyte,
                        observed_value=obs.value,
                        reference_panic_limit=f"> {high_limit} {obs.unit}"
                    )

        if panic_findings:
            return LabEvaluationResult(
                patient_id=panel.patient_id,
                is_safe_for_outpatient_care=False,
                has_critical_panic_values=True,
                panic_findings=panic_findings,
                statutory_action_mandated="MANDATORY EMERGENCY ICU DISPATCH & TRANSFER: Outpatient prescribing locked."
            )

        return LabEvaluationResult(
            patient_id=panel.patient_id,
            is_safe_for_outpatient_care=True,
            has_critical_panic_values=False,
            panic_findings=[],
            statutory_action_mandated="Laboratory parameters within acceptable outpatient boundaries."
        )
