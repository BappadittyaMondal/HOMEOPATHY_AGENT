"""
Clinical Pathology Diagnostic Engine - CPDE (Phase 58).
Differentiates pathology diagnosis from repertorial totality, maps Western ICD nosology,
and enforces Samuel Hahnemann's Organon Aphorism 186 Operative Boundaries (INV-15).
"""
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ClinicalDomainCategory(str, Enum):
    MEDICAL_OUTPATIENT_HOMOEOPATHY = "MEDICAL_OUTPATIENT_HOMOEOPATHY"
    INTEGRATED_CO_MANAGEMENT = "INTEGRATED_CO_MANAGEMENT"
    ACUTE_SURGICAL_INTERVENTION = "ACUTE_SURGICAL_INTERVENTION"


class SurgicalInterventionRequiredException(Exception):
    """Raised when an acute surgical presentation is detected per Aphorism 186 (INV-15)."""
    def __init__(self, message: str, suspected_surgical_condition: str, recommended_surgical_specialty: str):
        super().__init__(message)
        self.message = message
        self.suspected_surgical_condition = suspected_surgical_condition
        self.recommended_surgical_specialty = recommended_surgical_specialty


class ClinicalPresentationInput(BaseModel):
    patient_id: str
    patient_age_years: int
    chief_complaint: str
    duration_days: int
    physical_signs: List[str] = Field(default_factory=list)
    temperature_c: float = 37.0
    known_diagnoses: List[str] = Field(default_factory=list)


class DiagnosticReport(BaseModel):
    patient_id: str
    primary_icd10_diagnosis: str
    icd10_code: str
    category: ClinicalDomainCategory
    is_homeopathy_permitted_as_monotherapy: bool
    requires_integrated_allopathic_co_management: bool
    surgical_referral_mandated: bool
    clinical_rationale: str
    aphorism_reference: str


class ClinicalPathologyDiagnosticEngine:
    """
    Evaluates clinical presentation, distinguishing purely medical homeopathic cases
    from integrated co-management and acute surgical boundaries (Aphorism 186).
    """

    # Acute Surgical Red Flags per Aphorism 186
    SURGICAL_CONDITIONS: Dict[str, Dict[str, str]] = {
        "acute_appendicitis": {
            "triggers": ["mcburney", "rebound tenderness", "right iliac fossa guarding", "appendicitis"],
            "icd10": "K35.80",
            "condition": "Acute Appendicitis with perforation / abscess risk",
            "specialty": "General Surgery"
        },
        "bowel_obstruction": {
            "triggers": ["feculent vomiting", "bilious vomiting", "absolute constipation", "strangulated hernia"],
            "icd10": "K56.60",
            "condition": "Acute Mechanical Bowel Obstruction / Strangulation",
            "specialty": "General Surgery"
        },
        "ruptured_ectopic": {
            "triggers": ["ruptured ectopic", "cervical motion tenderness", "adnexal mass with hypotension"],
            "icd10": "O00.9",
            "condition": "Ruptured Ectopic Pregnancy with internal hemorrhage",
            "specialty": "Obstetrics & Gynecology"
        },
        "testicular_torsion": {
            "triggers": ["testicular torsion", "absent cremasteric reflex", "sudden scrotal swelling"],
            "icd10": "N44.0",
            "condition": "Acute Testicular Torsion with testicular ischemia",
            "specialty": "Urology"
        }
    }

    # Integrated Co-Management (Requires Allopathic Pharmacotherapy alongside Homeopathy)
    INTEGRATED_CONDITIONS: Dict[str, Dict[str, str]] = {
        "type_1_diabetes": {
            "triggers": ["type 1 diabetes", "t1dm", "insulin dependent"],
            "icd10": "E10.9",
            "condition": "Type 1 Diabetes Mellitus (Exogenous Insulin Mandatory)"
        },
        "severe_hypertension": {
            "triggers": ["hypertensive urgency", "hypertension stage 2", "bp > 180"],
            "icd10": "I10",
            "condition": "Severe Essential Hypertension Stage 2"
        },
        "end_stage_renal": {
            "triggers": ["ckd stage 5", "dialysis dependent", "end stage renal disease"],
            "icd10": "N18.5",
            "condition": "Chronic Kidney Disease Stage 5 (Dialysis / Transplant Required)"
        }
    }

    @classmethod
    def evaluate_presentation(
        cls,
        presentation: ClinicalPresentationInput,
        raise_on_surgical: bool = True
    ) -> DiagnosticReport:
        """
        Evaluates clinical findings to establish nosological diagnosis and surgical/medical boundaries.
        Enforces INV-15: Acute surgical conditions block outpatient medical repertorization.
        """
        combined_text = (
            f"{presentation.chief_complaint} {' '.join(presentation.physical_signs)} "
            f"{' '.join(presentation.known_diagnoses)}"
        ).lower()

        # 1. Evaluate Acute Surgical Boundary per Organon Aphorism 186 (INV-15)
        for cond_key, info in cls.SURGICAL_CONDITIONS.items():
            if any(t in combined_text for t in info["triggers"]):
                msg = (
                    f"APHORISM 186 OPERATIVE BOUNDARY (INV-15): Patient presentation indicates an acute surgical "
                    f"condition ('{info['condition']}'). Outpatient medical repertorization is contraindicated. "
                    f"Immediate operative referral to {info['specialty']} is legally and clinically mandated."
                )
                if raise_on_surgical:
                    raise SurgicalInterventionRequiredException(
                        message=msg,
                        suspected_surgical_condition=info["condition"],
                        recommended_surgical_specialty=info["specialty"]
                    )
                return DiagnosticReport(
                    patient_id=presentation.patient_id,
                    primary_icd10_diagnosis=info["condition"],
                    icd10_code=info["icd10"],
                    category=ClinicalDomainCategory.ACUTE_SURGICAL_INTERVENTION,
                    is_homeopathy_permitted_as_monotherapy=False,
                    requires_integrated_allopathic_co_management=True,
                    surgical_referral_mandated=True,
                    clinical_rationale=msg,
                    aphorism_reference="Organon Aphorism 186: Dynamic medicine cannot substitute for operative mechanical intervention."
                )

        # 2. Evaluate Integrated Co-Management
        for cond_key, info in cls.INTEGRATED_CONDITIONS.items():
            if any(t in combined_text for t in info["triggers"]):
                return DiagnosticReport(
                    patient_id=presentation.patient_id,
                    primary_icd10_diagnosis=info["condition"],
                    icd10_code=info["icd10"],
                    category=ClinicalDomainCategory.INTEGRATED_CO_MANAGEMENT,
                    is_homeopathy_permitted_as_monotherapy=False,
                    requires_integrated_allopathic_co_management=True,
                    surgical_referral_mandated=False,
                    clinical_rationale=(
                        f"Integrated co-management mandated for {info['condition']}. "
                        f"Homeopathic constitutional prescribing acts as adjuvant support only; "
                        f"never withdraw critical conventional pharmaceuticals (e.g. insulin, anti-hypertensives)."
                    ),
                    aphorism_reference="Organon Aphorisms 74-76: Management of chronic iatrogenic & irreversible pathology."
                )

        # 3. Standard Medical Outpatient Homeopathy
        return DiagnosticReport(
            patient_id=presentation.patient_id,
            primary_icd10_diagnosis=presentation.chief_complaint,
            icd10_code="R69",  # General illness / functional complaint
            category=ClinicalDomainCategory.MEDICAL_OUTPATIENT_HOMOEOPATHY,
            is_homeopathy_permitted_as_monotherapy=True,
            requires_integrated_allopathic_co_management=False,
            surgical_referral_mandated=False,
            clinical_rationale="Patient condition represents dynamic constitutional or acute medical disturbance amenable to classical homeopathic simillimum.",
            aphorism_reference="Organon Aphorisms 105-145: Pure dynamic disease totality."
        )
