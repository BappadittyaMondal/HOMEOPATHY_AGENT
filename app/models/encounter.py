"""
Clinical Encounter & Triage Domain Contracts.
Implements the Smart Paper Bridge non-semantic encounter token and vital sign validation.
"""
from typing import Optional
from pydantic import BaseModel, Field, field_validator
import uuid
from app.models.base import (
    BaseAuditModel, 
    EncounterTypeEnum, 
    EncounterStatusEnum, 
    TriagePriorityEnum
)

class VitalSigns(BaseModel):
    temperature_c: Optional[float] = Field(None, ge=30.0, le=45.0, description="Body temperature in Celsius")
    pulse_bpm: Optional[int] = Field(None, ge=30, le=250, description="Heart rate in BPM")
    blood_pressure_sys: Optional[int] = Field(None, ge=50, le=300, description="Systolic blood pressure mmHg")
    blood_pressure_dia: Optional[int] = Field(None, ge=30, le=200, description="Diastolic blood pressure mmHg")
    respiratory_rate: Optional[int] = Field(None, ge=5, le=80, description="Breaths per minute")
    spo2_percent: Optional[int] = Field(None, ge=40, le=100, description="Oxygen saturation %")

    @field_validator("blood_pressure_dia")
    @classmethod
    def validate_bp(cls, v: Optional[int], info) -> Optional[int]:
        sys = info.data.get("blood_pressure_sys")
        if sys is not None and v is not None and v >= sys:
            raise ValueError("Diastolic BP must be lower than systolic BP")
        return v

class EncounterCreate(BaseModel):
    patient_id: str = Field(..., description="Foreign key to patients table")
    encounter_type: EncounterTypeEnum = Field(default=EncounterTypeEnum.OPD)
    triage_priority: TriagePriorityEnum = Field(default=TriagePriorityEnum.GREEN)
    chief_complaint: Optional[str] = Field(None, max_length=500)
    practitioner_id: str = Field(..., min_length=2, max_length=50)
    vitals: Optional[VitalSigns] = Field(default_factory=VitalSigns)

class EncounterResponse(BaseAuditModel):
    encounter_id: str
    patient_id: str
    encounter_type: EncounterTypeEnum
    status: EncounterStatusEnum
    triage_priority: TriagePriorityEnum
    chief_complaint: Optional[str]
    practitioner_id: str
    vitals: VitalSigns
    token_number: int
    barcode_token: str
