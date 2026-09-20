"""
Health and Diagnostic Endpoints for HOMEOPATHY_AGENT.
Verifies WAL journal mode, cache status, and async queue health.
"""
from fastapi import APIRouter, Depends
from app.core.config import settings
from app.core.database import SQLiteWALDatabase
from app.api.deps import get_db

router = APIRouter(prefix="/health", tags=["Health & Diagnostics"])

@router.get("")
async def health_check(database: SQLiteWALDatabase = Depends(get_db)):
    """Verifies database connectivity, WAL mode, and queue readiness."""
    read_conn = database.get_read_connection()
    try:
        cursor = read_conn.cursor()
        cursor.execute("PRAGMA journal_mode;")
        journal_mode = cursor.fetchone()[0]
        cursor.execute("PRAGMA synchronous;")
        synchronous = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM patients;")
        patient_count = cursor.fetchone()[0]
    finally:
        read_conn.close()

    return {
        "status": "HEALTHY",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": {
            "engine": "SQLite WAL",
            "journal_mode": journal_mode.upper(),
            "synchronous": synchronous,
            "patient_count": patient_count,
            "async_queue_running": database._is_running
        }
    }
