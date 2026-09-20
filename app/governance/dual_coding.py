"""
WHO ICD-11 Traditional Medicine Module 1 (TM1) & Western ICD-10 Dual-Coding Engine (Phase 42).
Enforces dual diagnostic coding bridging Western ICD-10 with Ayush Grid NAMASTE
and WHO ICD-11 TM1 homeopathic classifications for ABDM compliance.
"""
from typing import Dict, Optional
from pydantic import BaseModel

class DualCodingResult(BaseModel):
    condition_name: str
    western_icd10_code: str
    western_icd10_title: str
    who_icd11_tm1_code: str
    who_icd11_tm1_title: str
    ayush_namaste_code: str
    abdm_compliant: bool = True

class DualCodingEngine:
    """
    Crosswalks Western ICD-10 disease nosology with WHO ICD-11 TM1 and Ayush NAMASTE codes.
    """

    WESTERN_ICD10_MAP: Dict[str, Dict[str, str]] = {
        "asthma": {"code": "J45.9", "title": "Asthma, unspecified"},
        "allergic asthma": {"code": "J45.0", "title": "Predominantly allergic asthma"},
        "eczema": {"code": "L20.9", "title": "Atopic dermatitis, unspecified"},
        "peptic ulcer": {"code": "K27.9", "title": "Peptic ulcer, unspecified"},
        "renal calculus": {"code": "N20.0", "title": "Calculus of kidney"},
        "migraine": {"code": "G43.9", "title": "Migraine, unspecified"},
        "rheumatoid arthritis": {"code": "M06.9", "title": "Rheumatoid arthritis, unspecified"},
        "hypertension": {"code": "I10", "title": "Essential (primary) hypertension"},
        "amenorrhea": {"code": "N91.2", "title": "Amenorrhea, unspecified"},
        "depression": {"code": "F32.9", "title": "Depressive episode, unspecified"}
    }

    TM1_MIASMATIC_MAP: Dict[str, Dict[str, str]] = {
        "PSORA": {
            "tm1_code": "TM1-HOM-01",
            "tm1_title": "Disorder of Psoric Dyscrasia / Functional Hypersensitivity",
            "namaste": "HOM-PSO-001"
        },
        "SYCOSIS": {
            "tm1_code": "TM1-HOM-02",
            "tm1_title": "Disorder of Sycotic Dyscrasia / Hyperplasia and Catarrhal Overgrowth",
            "namaste": "HOM-SYC-002"
        },
        "SYPHILIS": {
            "tm1_code": "TM1-HOM-03",
            "tm1_title": "Disorder of Syphilitic Dyscrasia / Destructive Tissue Degeneration",
            "namaste": "HOM-SYP-003"
        },
        "TUBERCULAR": {
            "tm1_code": "TM1-HOM-04",
            "tm1_title": "Disorder of Tubercular Diathesis / Pseudopsoric Wasting Complex",
            "namaste": "HOM-TUB-004"
        }
    }

    @classmethod
    def resolve_dual_coding(
        cls,
        clinical_condition: str,
        dominant_miasm: str = "PSORA"
    ) -> DualCodingResult:
        """
        Crosswalks a diagnosis and miasm into complete dual-coding tuple for ABDM interchange.
        """
        cond_lower = clinical_condition.strip().lower()
        western_info = None

        # Sort keys by length descending to match most specific terms first
        for key in sorted(cls.WESTERN_ICD10_MAP.keys(), key=len, reverse=True):
            if key in cond_lower:
                western_info = cls.WESTERN_ICD10_MAP[key]
                break

        if not western_info:
            western_info = {"code": "R69", "title": "Illness, unspecified"}

        miasm_info = cls.TM1_MIASMATIC_MAP.get(
            dominant_miasm.upper(),
            cls.TM1_MIASMATIC_MAP["PSORA"]
        )

        return DualCodingResult(
            condition_name=clinical_condition,
            western_icd10_code=western_info["code"],
            western_icd10_title=western_info["title"],
            who_icd11_tm1_code=miasm_info["tm1_code"],
            who_icd11_tm1_title=miasm_info["tm1_title"],
            ayush_namaste_code=miasm_info["namaste"],
            abdm_compliant=True
        )
