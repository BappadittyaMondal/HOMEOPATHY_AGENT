"""
Patient Master Identity & Registration Endpoints.
Zero-Trust identity verification with duplicate prevention and ABHA linking.
"""
from fastapi import APIRouter, HTTPException, Query, status
from app.models.patient import PatientCreate, PatientResponse, PatientUpdate
from app.core.database import db
import uuid
from typing import Optional

router = APIRouter(prefix="/patients", tags=["Patient Identity (MPI)"])

@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def register_patient(payload: PatientCreate):
    """Registers a new patient with unique ID and duplicate prevention."""
    # Check duplicate phone or ABHA
    check_query = "SELECT patient_id FROM patients WHERE contact_phone = ?"
    params = [payload.contact_phone]
    if payload.abha_id:
        check_query += " OR abha_id = ?"
        params.append(payload.abha_id)
    
    existing = await db.execute_read(check_query, tuple(params))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Patient record already exists with matching phone or ABHA ID (Patient ID: {existing[0]['patient_id']})"
        )

    patient_id = payload.patient_id or f"PAT-{uuid.uuid4().hex[:10].upper()}"
    insert_query = """
    INSERT INTO patients (
        patient_id, abha_id, national_id, full_name, date_of_birth,
        gender, contact_phone, email, address, emergency_contact,
        guardian_name, guardian_relation, miasmatic_background, constitutional_notes
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """
    insert_params = (
        patient_id, payload.abha_id, payload.national_id, payload.full_name,
        payload.date_of_birth, payload.gender.value, payload.contact_phone,
        payload.email, payload.address, payload.emergency_contact,
        payload.guardian_name, payload.guardian_relation,
        payload.miasmatic_background, payload.constitutional_notes
    )
    
    await db.execute_write(insert_query, insert_params)
    
    rows = await db.execute_read("SELECT * FROM patients WHERE patient_id = ?", (patient_id,))
    if not rows:
        raise HTTPException(status_code=500, detail="Failed to retrieve created patient record")
    
    return PatientResponse(**rows[0])

@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: str):
    """Retrieves patient details by Master Patient ID."""
    rows = await db.execute_read("SELECT * FROM patients WHERE patient_id = ?", (patient_id,))
    if not rows:
        raise HTTPException(status_code=404, detail="Patient not found")
    return PatientResponse(**rows[0])

@router.get("", response_model=list[PatientResponse])
async def search_patients(
    query: Optional[str] = Query(None, description="Search by name, phone, or ABHA"),
    limit: int = Query(20, ge=1, le=100)
):
    """Searches patient master index with limit."""
    if query:
        search_pattern = f"%{query.strip()}%"
        sql = """
        SELECT * FROM patients 
        WHERE full_name LIKE ? OR contact_phone LIKE ? OR abha_id LIKE ? 
        ORDER BY created_at DESC LIMIT ?
        """
        rows = await db.execute_read(sql, (search_pattern, search_pattern, search_pattern, limit))
    else:
        sql = "SELECT * FROM patients ORDER BY created_at DESC LIMIT ?"
        rows = await db.execute_read(sql, (limit,))
    
    return [PatientResponse(**row) for row in rows]
