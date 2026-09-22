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
    ONCOLOGICAL_BIOPSY_MANDATED = "ONCOLOGICAL_BIOPSY_MANDATED"


class SurgicalInterventionRequiredException(Exception):
    """Raised when an acute surgical presentation is detected per Aphorism 186 (INV-15)."""
    def __init__(self, message: str, suspected_surgical_condition: str, recommended_surgical_specialty: str):
        super().__init__(message)
        self.message = message
        self.suspected_surgical_condition = suspected_surgical_condition
        self.recommended_surgical_specialty = recommended_surgical_specialty


class OncologicalBiopsyRequiredException(Exception):
    """Raised when pre-malignant or suspected neoplastic transformation is detected (INV-17)."""
    def __init__(self, message: str, suspected_lesion: str, recommended_investigation: str = "Dermatopathology Punch Biopsy"):
        super().__init__(message)
        self.message = message
        self.suspected_lesion = suspected_lesion
        self.recommended_investigation = recommended_investigation


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
    biopsy_mandated: bool = False
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

    # Pre-Malignant / Suspected Neoplastic Transformations per INV-17
    PRE_MALIGNANT_CONDITIONS: Dict[str, Dict[str, str]] = {
        "arsenical_keratosis_malignant_risk": {
            "triggers": ["indurated keratosis", "ulcerated keratosis", "bleeding palm", "bleeding sole", "fissured keratosis with induration"],
            "icd10": "L85.8",
            "condition": "Chronic Arsenical Keratoderma with Suspected Bowenoid / Neoplastic Transformation",
            "investigation": "Urgent Dermatopathology Punch Biopsy"
        },
        "bowen_disease": {
            "triggers": ["bowen", "squamous cell carcinoma in situ", "erythroplasia of queyrat"],
            "icd10": "D04.9",
            "condition": "Cutaneous Squamous Cell Carcinoma in situ (Bowen's Disease)",
            "investigation": "Full-Thickness Punch Biopsy & Wide Local Excision Assessment"
        },
        "marjolin_ulcer": {
            "triggers": ["marjolin", "non-healing chronic ulcer with everted edges", "indurated ulcer edge", "malignant ulcer"],
            "icd10": "C44.92",
            "condition": "Suspected Invasive Cutaneous Carcinoma / Marjolin's Ulcer",
            "investigation": "Edge Wedge Biopsy & Regional Lymph Node Assessment"
        },
        "oral_premalignancy": {
            "triggers": ["speckled leukoplakia", "erythroplakia with induration", "ulcerated leukoplakia", "oral submucous fibrosis with ulcer"],
            "icd10": "K13.21",
            "condition": "High-Risk Oral Dysplasia / Suspicious Malignant Transformation",
            "investigation": "Incisional Biopsy of Oral Mucosa"
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
        raise_on_surgical: bool = True,
        raise_on_oncological: bool = True
    ) -> DiagnosticReport:
        """
        Evaluates clinical findings to establish nosological diagnosis, surgical boundaries (INV-15),
        and oncological pre-malignancy surveillance gates (INV-17).
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
                    biopsy_mandated=False,
                    clinical_rationale=msg,
                    aphorism_reference="Organon Aphorism 186: Dynamic medicine cannot substitute for operative mechanical intervention."
                )

        # 2. Evaluate Oncological Pre-Malignancy & Neoplastic Transformation Gate (INV-17)
        for cond_key, info in cls.PRE_MALIGNANT_CONDITIONS.items():
            if any(t in combined_text for t in info["triggers"]):
                msg = (
                    f"ONCOLOGICAL PRE-MALIGNANCY BOUNDARY (INV-17): Patient presentation exhibits features of "
                    f"suspected neoplastic or pre-malignant transformation ('{info['condition']}'). "
                    f"Standalone outpatient homeopathic prescribing is HALTED. Mandatory investigation: "
                    f"{info['investigation']} to rule out invasive malignancy."
                )
                if raise_on_oncological:
                    raise OncologicalBiopsyRequiredException(
                        message=msg,
                        suspected_lesion=info["condition"],
                        recommended_investigation=info["investigation"]
                    )
                return DiagnosticReport(
                    patient_id=presentation.patient_id,
                    primary_icd10_diagnosis=info["condition"],
                    icd10_code=info["icd10"],
                    category=ClinicalDomainCategory.ONCOLOGICAL_BIOPSY_MANDATED,
                    is_homeopathy_permitted_as_monotherapy=False,
                    requires_integrated_allopathic_co_management=True,
                    surgical_referral_mandated=False,
                    biopsy_mandated=True,
                    clinical_rationale=msg,
                    aphorism_reference="Organon Aphorism 186 & Modern Oncological Safety: Local structural neoplasia requires histopathological diagnosis before dynamic treatment."
                )

        # Multi-decade chronic keratosis heuristic with induration / ulceration (>10 years)
        if presentation.duration_days >= 3650 and any(w in combined_text for w in ["indurat", "ulcer", "bleed", "stony"]) and any(w in combined_text for w in ["kerato", "palm", "sole", "lesion", "foot", "feet"]):
            cond_desc = "Chronic Palmoplantar Keratopathy (>10y) with Induration/Ulceration (High-Risk Bowenoid Degeneration)"
            msg = (
                f"ONCOLOGICAL PRE-MALIGNANCY BOUNDARY (INV-17): Multi-decade chronic keratosis ({presentation.duration_days // 365} years) "
                f"with secondary ulceration/induration carries significant risk of Squamous Cell Carcinoma in situ. "
                f"Standalone homeopathic prescribing is HALTED pending histopathological clearance."
            )
            if raise_on_oncological:
                raise OncologicalBiopsyRequiredException(
                    message=msg,
                    suspected_lesion=cond_desc,
                    recommended_investigation="Dermatopathology Punch Biopsy"
                )
            return DiagnosticReport(
                patient_id=presentation.patient_id,
                primary_icd10_diagnosis=cond_desc,
                icd10_code="L85.8",
                category=ClinicalDomainCategory.ONCOLOGICAL_BIOPSY_MANDATED,
                is_homeopathy_permitted_as_monotherapy=False,
                requires_integrated_allopathic_co_management=True,
                surgical_referral_mandated=False,
                biopsy_mandated=True,
                clinical_rationale=msg,
                aphorism_reference="Organon Aphorism 186 & Oncological Biopsy Mandate (INV-17)."
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
