"""
Unit Tests for Phase 43: NCH Act 2020 Statutory Prescribing & Digital Signature Gateway.
"""
import pytest
from app.governance.nch_signature import (
    NCHDigitalSignatureGateway,
    RMPCredentials,
    PrescriptionPayload
)

def test_rmp_signature_generation_and_verification():
    """Verify cryptographic signing and verification of electronic prescription."""
    rmp = RMPCredentials(
        rmp_name="Dr. Bappaditya Homoeopath",
        registration_number="WBHC-HOM-12345",
        state_council="West Bengal Council of Homoeopathy",
        is_active_practitioner=True
    )
    payload = PrescriptionPayload(
        prescription_id="RX-2026-09-001",
        patient_id="PT-500",
        remedy_name="Sulphur",
        potency="200C",
        dosage_instructions="1 dose dry on tongue weekly",
        issued_timestamp="2026-09-20T11:55:00Z"
    )

    receipt = NCHDigitalSignatureGateway.sign_prescription(rmp, payload)
    assert receipt.is_statutorily_valid is True
    assert receipt.rmp_name == "Dr. Bappaditya Homoeopath"
    assert len(receipt.cryptographic_signature) == 64  # SHA256 hex string

    # Verification must succeed on original payload
    is_valid = NCHDigitalSignatureGateway.verify_signature(receipt, payload)
    assert is_valid is True

def test_rmp_tamper_detection():
    """Verify that tampering with any field in prescription payload breaks verification."""
    rmp = RMPCredentials(
        rmp_name="Dr. Valid Practitioner",
        registration_number="NCH-REG-9999",
        state_council="NCH Central Register",
        is_active_practitioner=True
    )
    payload = PrescriptionPayload(
        prescription_id="RX-SAFE-01",
        patient_id="PT-200",
        remedy_name="Arsenicum album",
        potency="30C",
        dosage_instructions="1 teaspoonful 3 times daily",
        issued_timestamp="2026-09-20T12:00:00Z"
    )
    receipt = NCHDigitalSignatureGateway.sign_prescription(rmp, payload)

    # Malicious tampering: changing remedy from Arsenicum album to Strychnos nux-vomica
    tampered_payload = PrescriptionPayload(
        prescription_id="RX-SAFE-01",
        patient_id="PT-200",
        remedy_name="Strychnos nux-vomica",
        potency="30C",
        dosage_instructions="1 teaspoonful 3 times daily",
        issued_timestamp="2026-09-20T12:00:00Z"
    )
    is_valid = NCHDigitalSignatureGateway.verify_signature(receipt, tampered_payload)
    assert is_valid is False

def test_unregistered_practitioner_rejection():
    """Verify that prescribing is blocked if RMP license is inactive or absent."""
    invalid_rmp = RMPCredentials(
        rmp_name="Unauthorized Person",
        registration_number="",
        state_council="None",
        is_active_practitioner=False
    )
    payload = PrescriptionPayload(
        prescription_id="RX-ILLEGAL-01",
        patient_id="PT-300",
        remedy_name="Aconitum",
        potency="30C",
        dosage_instructions="take as needed",
        issued_timestamp="2026-09-20T12:00:00Z"
    )

    with pytest.raises(ValueError) as exc:
        NCHDigitalSignatureGateway.sign_prescription(invalid_rmp, payload)
    assert "STATUTORY SIGNATURE REJECTION" in str(exc.value)
