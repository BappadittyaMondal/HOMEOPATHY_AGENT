"""
Base Domain Enums and Abstract Models for HOMEOPATHY_AGENT.
Enforces strict schema validation and ISO-8601 timestamps.
"""
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class GenderEnum(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"
    UNDISCLOSED = "UNDISCLOSED"

class TriagePriorityEnum(str, Enum):
    RED = "RED"       # Emergent / Immediate Life-Threat (Break-Glass Protocol)
    YELLOW = "YELLOW" # Urgent / Severe Pain / High Fever
    GREEN = "GREEN"   # Standard Routine OPD

class EncounterTypeEnum(str, Enum):
    OPD = "OPD"
    IPD = "IPD"
    EMERGENCY = "EMERGENCY"
    DAYCARE = "DAYCARE"
    TELEMEDICINE = "TELEMEDICINE"

class EncounterStatusEnum(str, Enum):
    REGISTERED = "REGISTERED"
    TRIAGED = "TRIAGED"
    IN_CONSULTATION = "IN_CONSULTATION"
    INVESTIGATION_PENDING = "INVESTIGATION_PENDING"
    PHARMACY_PENDING = "PHARMACY_PENDING"
    COMPLETED = "COMPLETED"
    TRANSFERRED_EMERGENCY = "TRANSFERRED_EMERGENCY"
    CANCELLED = "CANCELLED"

class BaseAuditModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
