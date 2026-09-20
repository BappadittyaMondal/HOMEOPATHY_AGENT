"""
API Dependencies and Security Injections (Phase 56).
Enforces server-side OAuth2 / Bearer JWT validation and role-based access control.
"""
from typing import Generator, Optional
from fastapi import Header, HTTPException, status
from app.core.database import db
from app.core.security import (
    SecurityManager,
    AuthenticatedUser,
    UserRole,
    AuthenticationError,
    PermissionDeniedError
)


def get_db_read():
    """Provides a thread-safe read-only connection to the WAL database."""
    conn = db.get_read_connection()
    try:
        yield conn
    finally:
        conn.close()


def get_db():
    """Provides access to the global high-concurrency database instance."""
    return db


def get_current_user(authorization: Optional[str] = Header(None)) -> AuthenticatedUser:
    """Validates bearer token from request header, returning the authenticated user (INV-10)."""
    try:
        return SecurityManager.authenticate_header(authorization)
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"}
        )


def get_current_doctor(authorization: Optional[str] = Header(None)) -> AuthenticatedUser:
    """Guarantees caller is an authenticated RMP Doctor (INV-10)."""
    user = get_current_user(authorization)
    if user.role != UserRole.RMP_DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Role '{user.role.value}' lacks statutory prescribing rights."
        )
    return user


def get_current_pharmacist(authorization: Optional[str] = Header(None)) -> AuthenticatedUser:
    """Guarantees caller is an authenticated Dispensary Pharmacist."""
    user = get_current_user(authorization)
    if user.role != UserRole.DISPENSARY_PHARMACIST and user.role != UserRole.RMP_DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Role '{user.role.value}' is not authorized to dispense medication."
        )
    return user
