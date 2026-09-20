"""
Boger Boenninghausen Characteristics & Repertory (BBCR 1905) Domain Contracts.
Codifies Tissue Affinity, Lateral Directionality, and Pathological Generals.
"""
from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional

class TissueAffinityEnum(str, Enum):
    VASCULAR_CIRCULATORY = "VASCULAR_CIRCULATORY"
    MUCOUS_MEMBRANES = "MUCOUS_MEMBRANES"
    SEROUS_FIBROUS_TISSUES = "SEROUS_FIBROUS_TISSUES"
    CENTRAL_NERVOUS_SYSTEM = "CENTRAL_NERVOUS_SYSTEM"
    BONES_PERIOSTEUM = "BONES_PERIOSTEUM"
    SKIN_EPITHELIUM = "SKIN_EPITHELIUM"
    HEPATOBILIARY = "HEPATOBILIARY"
    LYMPHATIC_GLANDS = "LYMPHATIC_GLANDS"

class LateralAffinityEnum(str, Enum):
    RIGHT_SIDED = "RIGHT_SIDED"
    LEFT_SIDED = "LEFT_SIDED"
    RIGHT_TO_LEFT = "RIGHT_TO_LEFT"       # e.g., Lycopodium
    LEFT_TO_RIGHT = "LEFT_TO_RIGHT"       # e.g., Lachesis
    DIAGONAL_UPPER_R_LOWER_L = "DIAGONAL_UPPER_R_LOWER_L"
    DIAGONAL_UPPER_L_LOWER_R = "DIAGONAL_UPPER_L_LOWER_R"
    BILATERAL = "BILATERAL"

class PathologicalGeneralEnum(str, Enum):
    SUPPURATION = "SUPPURATION"           # Hepar, Silicea, Merc
    ULCERATION = "ULCERATION"             # Kali-bi, Nit-ac, Merc
    HEMORRHAGIC_DIATHESIS = "HEMORRHAGIC" # Phos, Crot-h, Lachesis
    INDURATION_FIBROSIS = "INDURATION"   # Conium, Silicea, Calc-f
    GANGRENOUS_NECROSIS = "GANGRENE"      # Ars, Secale, Anthracinum

class BBCRRemedyProfile(BaseModel):
    remedy_name: str
    primary_tissues: List[TissueAffinityEnum]
    lateral_affinity: LateralAffinityEnum
    pathological_generals: List[PathologicalGeneralEnum]
    characteristic_time_key: Optional[str] = None
