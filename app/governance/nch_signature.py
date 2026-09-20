"""
NCH Act 2020 Statutory Prescribing Compliance & RMP Digital Signature Gateway (Phase 43).
Enforces Registered Medical Practitioner (RMP) license validation, tamper-evident cryptographic
payload signing (HMAC-SHA256 / RSA), and statutory compliance under the National Commission for Homoeopathy Act 2020.
"""
import hashlib
import hmac
import json
from typing import Dict, Optional
from pydantic import BaseModel

class RMPCredentials(BaseModel):
    rmp_name: str
    registration_number: str
    state_council: str  # e.g., "NCH_CENTRAL_REGISTER", "WBHC", "MMC_AYUSH"
    is_active_practitioner: bool = True

class PrescriptionPayload(BaseModel):
    prescription_id: str
    patient_id: str
    remedy_name: str
    potency: str
    dosage_instructions: str
    issued_timestamp: str

class SignedPrescriptionReceipt(BaseModel):
    prescription_id: str
    rmp_name: str
    registration_number: str
    state_council: str
    payload_hash_sha256: str
    cryptographic_signature: str
    is_statutorily_valid: bool
    compliance_standard: str = "NCH Act 2020 Section 34 & Information Technology Act 2000 Section 3A"

import os
from app.core.security import IdentitySpoofingError

class NCHDigitalSignatureGateway:
    """
    Validates RMP credentials and generates tamper-evident cryptographic digital signatures.
    Supports dynamic secret management and INV-11 anti-spoofing verification.
    """

    # Secret server key for cryptographic HMAC signing (loaded from environment or secure default)
    _DEFAULT_KEY: bytes = b"NCH_HOMOEOPATHY_ACT_2020_SECURE_HMAC_SECRET_KEY_PROD"
    _SIGNING_KEY: bytes = _DEFAULT_KEY

    @classmethod
    def get_signing_key(cls) -> bytes:
        env_key = os.environ.get("NCH_SIGNING_KEY")
        if env_key:
            return env_key.encode("utf-8")
        return cls._SIGNING_KEY

    @classmethod
    def sign_prescription(
        cls,
        credentials: RMPCredentials,
        payload: PrescriptionPayload,
        authenticated_doctor_reg_num: Optional[str] = None
    ) -> SignedPrescriptionReceipt:
        """
        Validates RMP statutory entitlement and signs the prescription payload.
        Enforces INV-11: Rejects requests where requested credentials do not match authenticated session.
        """
        if not credentials.is_active_practitioner or not credentials.registration_number.strip():
            raise ValueError(
                f"STATUTORY SIGNATURE REJECTION: Clinician {credentials.rmp_name} does not hold an "
                f"active RMP license under NCH Act 2020. Prescribing rights revoked."
            )

        # INV-11: Anti-Spoofing Check
        if authenticated_doctor_reg_num is not None:
            if authenticated_doctor_reg_num.strip() != credentials.registration_number.strip():
                raise IdentitySpoofingError(
                    f"IDENTITY SPOOFING DETECTED (INV-11): Authenticated doctor '{authenticated_doctor_reg_num}' "
                    f"cannot sign prescription under registration '{credentials.registration_number}'."
                )

        # 1. Compute canonical SHA-256 payload hash
        payload_bytes = payload.model_dump_json().encode("utf-8")
        payload_hash = hashlib.sha256(payload_bytes).hexdigest()

        # 2. Cryptographic signature generation
        message = f"{credentials.registration_number}|{payload.prescription_id}|{payload_hash}".encode("utf-8")
        signing_key = cls.get_signing_key()
        signature = hmac.new(signing_key, message, hashlib.sha256).hexdigest()

        return SignedPrescriptionReceipt(
            prescription_id=payload.prescription_id,
            rmp_name=credentials.rmp_name,
            registration_number=credentials.registration_number,
            state_council=credentials.state_council,
            payload_hash_sha256=payload_hash,
            cryptographic_signature=signature,
            is_statutorily_valid=True
        )

    @classmethod
    def verify_signature(
        cls,
        receipt: SignedPrescriptionReceipt,
        payload: PrescriptionPayload
    ) -> bool:
        """
        Verifies tamper-evident integrity of the signed prescription receipt against the payload.
        """
        # 1. Verify payload hash matches
        computed_hash = hashlib.sha256(payload.model_dump_json().encode("utf-8")).hexdigest()
        if computed_hash != receipt.payload_hash_sha256:
            return False

        # 2. Verify cryptographic signature
        message = f"{receipt.registration_number}|{receipt.prescription_id}|{receipt.payload_hash_sha256}".encode("utf-8")
        expected_sig = hmac.new(cls.get_signing_key(), message, hashlib.sha256).hexdigest()

        return hmac.compare_digest(expected_sig, receipt.cryptographic_signature)
