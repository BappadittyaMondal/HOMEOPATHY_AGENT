"""
Tests for Phase 56: Server-Side Authoritative Authorization (OAuth2/JWT) & Secret Management.
Validates INV-10 (Server-Side Bearer JWT Enforcement) and INV-11 (RMP Anti-Spoofing Identity Guard).
"""
import pytest
from fastapi import HTTPException
from app.core.security import (
    SecurityManager,
    UserRole,
    AuthenticationError,
    PermissionDeniedError,
    IdentitySpoofingError
)
from app.api.deps import get_current_user, get_current_doctor
from app.governance.nch_signature import (
    NCHDigitalSignatureGateway,
    RMPCredentials,
    PrescriptionPayload
)


def test_inv_10_missing_authorization_header_raises_error():
    """INV-10: Missing Authorization header must raise AuthenticationError / HTTP 401."""
    with pytest.raises(AuthenticationError) as exc_info:
        SecurityManager.authenticate_header(None)
    assert "Missing Authorization header" in str(exc_info.value)

    with pytest.raises(HTTPException) as http_exc:
        get_current_user(None)
    assert http_exc.value.status_code == 401


def test_inv_10_tampered_or_invalid_jwt_raises_error():
    """INV-10: Tampered JWT signature must be rejected."""
    token = SecurityManager.create_access_token(
        user_id="dr_sen",
        role=UserRole.RMP_DOCTOR,
        full_name="Dr. B. K. Sen",
        registration_number="WBHC-1001"
    )
    # Tamper with signature
    tampered_token = token[:-5] + "XXXXX"
    with pytest.raises(AuthenticationError) as exc_info:
        SecurityManager.decode_access_token(tampered_token)
    assert "Invalid token signature" in str(exc_info.value)


def test_rbac_role_enforcement_doctor_only():
    """Verify that a Pharmacist or Nurse cannot access Doctor-only prescribing routes."""
    pharma_token = SecurityManager.create_access_token(
        user_id="pharma_01",
        role=UserRole.DISPENSARY_PHARMACIST,
        full_name="Pharmacist Roy"
    )
    auth_header = f"Bearer {pharma_token}"

    with pytest.raises(HTTPException) as exc_info:
        get_current_doctor(auth_header)
    assert exc_info.value.status_code == 403
    assert "lacks statutory prescribing rights" in str(exc_info.value.detail)


def test_inv_11_rmp_identity_spoofing_prevented():
    """
    INV-11: An authenticated doctor (e.g. WBHC-1001) attempting to sign a prescription
    under another clinician's registration number (e.g. WBHC-9999) must be rejected
    with IdentitySpoofingError.
    """
    token = SecurityManager.create_access_token(
        user_id="dr_real",
        role=UserRole.RMP_DOCTOR,
        full_name="Dr. Real Physician",
        registration_number="WBHC-1001"
    )
    authenticated_user = SecurityManager.authenticate_header(f"Bearer {token}")

    # Doctor tries to sign claiming to be WBHC-9999
    requested_creds = RMPCredentials(
        rmp_name="Dr. Impersonated",
        registration_number="WBHC-9999",  # Mismatch!
        state_council="WBHC"
    )
    payload = PrescriptionPayload(
        prescription_id="RX-SPOOF-01",
        patient_id="PT-001",
        remedy_name="Sulphur",
        potency="200C",
        dosage_instructions="Single dose",
        issued_timestamp="2026-09-20T12:00:00Z"
    )

    with pytest.raises(IdentitySpoofingError) as exc_info:
        NCHDigitalSignatureGateway.sign_prescription(
            credentials=requested_creds,
            payload=payload,
            authenticated_doctor_reg_num=authenticated_user.registration_number
        )
    assert "IDENTITY SPOOFING DETECTED" in str(exc_info.value)


def test_authenticated_valid_signature_succeeds():
    """Valid authenticated doctor with matching registration successfully signs prescription."""
    token = SecurityManager.create_access_token(
        user_id="dr_valid",
        role=UserRole.RMP_DOCTOR,
        full_name="Dr. Valid RMP",
        registration_number="WBHC-7777"
    )
    authenticated_user = SecurityManager.authenticate_header(f"Bearer {token}")

    creds = RMPCredentials(
        rmp_name="Dr. Valid RMP",
        registration_number="WBHC-7777",
        state_council="WBHC"
    )
    payload = PrescriptionPayload(
        prescription_id="RX-LEGIT-01",
        patient_id="PT-002",
        remedy_name="Nux vomica",
        potency="30C",
        dosage_instructions="At bedtime",
        issued_timestamp="2026-09-20T12:00:00Z"
    )
    receipt = NCHDigitalSignatureGateway.sign_prescription(
        credentials=creds,
        payload=payload,
        authenticated_doctor_reg_num=authenticated_user.registration_number
    )
    assert receipt.is_statutorily_valid is True
    assert receipt.registration_number == "WBHC-7777"
    assert NCHDigitalSignatureGateway.verify_signature(receipt, payload) is True
