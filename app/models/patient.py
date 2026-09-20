"""
Patient Master Identity Domain Contracts.
Compliant with ABDM (ABHA) and National Commission for Homoeopathy (NCH) registration norms.
"""
from typing import Optional
from pydantic import BaseModel, Field, field_validator
import re
import uuid
from app.models.base import BaseAuditModel, GenderEnum

class PatientBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=150, description="Full legal name of patient")
    date_of_birth: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="DOB in YYYY-MM-DD")
    gender: GenderEnum = Field(...)
    contact_phone: str = Field(..., min_length=10, max_length=15, description="Primary contact mobile number")
    email: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = Field(None, max_length=255)
    emergency_contact: Optional[str] = Field(None, max_length=100)
    guardian_name: Optional[str] = Field(None, max_length=150)
    guardian_relation: Optional[str] = Field(None, max_length=50)
    abha_id: Optional[str] = Field(None, max_length=50, description="14-digit ABHA ID or ABHA Address")
    national_id: Optional[str] = Field(None, max_length=50)
    miasmatic_background: Optional[str] = Field(None, description="Known family/constitutional miasmatic tendencies")
    constitutional_notes: Optional[str] = Field(None)

    @field_validator("contact_phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        cleaned = re.sub(r"[^\d+]", "", v)
        if len(cleaned) < 10:
            raise ValueError("Contact phone must contain at least 10 digits")
        return cleaned

class PatientCreate(PatientBase):
    patient_id: Optional[str] = Field(default_factory=lambda: f"PAT-{uuid.uuid4().hex[:10].upper()}")

class PatientUpdate(BaseModel):
    full_name: Optional[str] = None
    contact_phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_relation: Optional[str] = None
    abha_id: Optional[str] = None
    miasmatic_background: Optional[str] = None
    constitutional_notes: Optional[str] = None

class PatientResponse(PatientBase, BaseAuditModel):
    patient_id: str
