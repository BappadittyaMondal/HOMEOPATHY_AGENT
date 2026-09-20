"""
Server-Side Authoritative Authorization & Secret Management (Phase 56).
Enforces zero-trust token authentication (RFC 7519 JWT HS256), role-based access control (RBAC),
and anti-spoofing identity verification for RMP digital prescribing.
"""
import os
import hmac
import hashlib
import json
import base64
import time
from enum import Enum
from typing import Dict, Optional, Any
from pydantic import BaseModel, Field


class UserRole(str, Enum):
    RMP_DOCTOR = "RMP_DOCTOR"
    DISPENSARY_PHARMACIST = "DISPENSARY_PHARMACIST"
    TRIAGE_NURSE = "TRIAGE_NURSE"
    AUDITOR = "AUDITOR"


class AuthenticationError(Exception):
    """Raised when authentication credentials are missing, expired, or invalid."""
    pass


class PermissionDeniedError(Exception):
    """Raised when an authenticated actor lacks the statutory role to perform an action."""
    pass


class IdentitySpoofingError(Exception):
    """Raised when an actor attempts to execute actions under another clinician's identity (INV-11)."""
    pass


class TokenPayload(BaseModel):
    sub: str  # User ID / Username
    role: UserRole
    full_name: str
    registration_number: Optional[str] = None  # Mandatory for RMP_DOCTOR
    state_council: Optional[str] = None
    exp: int
    iat: int


class AuthenticatedUser(BaseModel):
    user_id: str
    role: UserRole
    full_name: str
    registration_number: Optional[str] = None
    state_council: Optional[str] = None


class SecurityManager:
    """
    Zero-trust authentication and secret management engine.
    Uses RFC 7519 HS256 JSON Web Tokens with zero third-party dependencies.
    """
    _DEFAULT_SECRET: bytes = b"homoeopathy_zero_trust_jwt_signing_key_2026_enterprise_prod"

    @classmethod
    def get_jwt_secret(cls) -> bytes:
        """Retrieves signing key from environment or fallback default."""
        env_key = os.environ.get("NCH_JWT_SECRET_KEY")
        if env_key:
            return env_key.encode("utf-8")
        return cls._DEFAULT_SECRET

    @staticmethod
    def _base64url_encode(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

    @staticmethod
    def _base64url_decode(data_str: str) -> bytes:
        padding = 4 - (len(data_str) % 4)
        if padding != 4:
            data_str += "=" * padding
        return base64.urlsafe_b64decode(data_str.encode("ascii"))

    @classmethod
    def create_access_token(
        cls,
        user_id: str,
        role: UserRole,
        full_name: str,
        registration_number: Optional[str] = None,
        state_council: Optional[str] = None,
        expires_in_seconds: int = 3600
    ) -> str:
        """Generates an RFC 7519 compliant HS256 JWT."""
        now = int(time.time())
        header = {"alg": "HS256", "typ": "JWT"}
        payload = {
            "sub": user_id,
            "role": role.value,
            "full_name": full_name,
            "registration_number": registration_number,
            "state_council": state_council,
            "iat": now,
            "exp": now + expires_in_seconds
        }

        header_b64 = cls._base64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
        payload_b64 = cls._base64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")

        secret = cls.get_jwt_secret()
        signature = hmac.new(secret, signing_input, hashlib.sha256).digest()
        signature_b64 = cls._base64url_encode(signature)

        return f"{header_b64}.{payload_b64}.{signature_b64}"

    @classmethod
    def decode_access_token(cls, token: str) -> TokenPayload:
        """
        Validates token signature and expiration, returning decoded TokenPayload.
        Raises AuthenticationError if invalid or expired.
        """
        parts = token.strip().split(".")
        if len(parts) != 3:
            raise AuthenticationError("Malformed token: expected 3 parts separated by dots.")

        header_b64, payload_b64, signature_b64 = parts
        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")

        secret = cls.get_jwt_secret()
        expected_sig = hmac.new(secret, signing_input, hashlib.sha256).digest()
        expected_sig_b64 = cls._base64url_encode(expected_sig)

        if not hmac.compare_digest(signature_b64, expected_sig_b64):
            raise AuthenticationError("Invalid token signature: potential unauthorized tampering detected.")

        try:
            payload_bytes = cls._base64url_decode(payload_b64)
            payload_dict = json.loads(payload_bytes.decode("utf-8"))
        except Exception as e:
            raise AuthenticationError(f"Could not parse token payload: {e}")

        # Check expiration
        now = int(time.time())
        if payload_dict.get("exp", 0) < now:
            raise AuthenticationError("Token expired. Please re-authenticate.")

        return TokenPayload(**payload_dict)

    @classmethod
    def authenticate_header(cls, auth_header: Optional[str]) -> AuthenticatedUser:
        """Extracts and validates bearer token from an HTTP Authorization header."""
        if not auth_header:
            raise AuthenticationError("Missing Authorization header. Bearer token required.")

        parts = auth_header.strip().split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise AuthenticationError("Invalid Authorization header scheme. Must be 'Bearer <token>'.")

        payload = cls.decode_access_token(parts[1])
        return AuthenticatedUser(
            user_id=payload.sub,
            role=payload.role,
            full_name=payload.full_name,
            registration_number=payload.registration_number,
            state_council=payload.state_council
        )

    @classmethod
    def verify_rmp_identity_match(cls, authenticated_user: AuthenticatedUser, requested_reg_num: str) -> None:
        """
        Guarantees INV-11: RMP cannot sign using a registration number
        differing from their authenticated token claim.
        """
        if authenticated_user.role != UserRole.RMP_DOCTOR:
            raise PermissionDeniedError(
                f"Statutory Role Rejection: Role '{authenticated_user.role.value}' "
                f"is not authorized to sign clinical prescriptions under NCH Act 2020."
            )

        if not authenticated_user.registration_number or authenticated_user.registration_number.strip() != requested_reg_num.strip():
            raise IdentitySpoofingError(
                f"IDENTITY SPOOFING DETECTED (INV-11): Authenticated RMP registration "
                f"'{authenticated_user.registration_number}' does not match requested signature "
                f"registration number '{requested_reg_num}'."
            )
