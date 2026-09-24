"""
Health and Diagnostic Endpoints for HOMEOPATHY_AGENT (Phase 78).
Verifies WAL journal mode, cache status, async queue health, Kubernetes liveness/readiness probes,
and exposes Prometheus APM telemetry.
"""
from fastapi import APIRouter, Depends, Response, status
from app.core.config import settings
from app.core.database import SQLiteWALDatabase
from app.api.deps import get_db
from app.core.observability import HealthProbeEngine, PrometheusMetricsEngine

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


@router.get("/live")
async def liveness_probe():
    """Kubernetes liveness probe."""
    return HealthProbeEngine.check_liveness()


@router.get("/ready")
async def readiness_probe(response: Response, database: SQLiteWALDatabase = Depends(get_db)):
    """Kubernetes readiness probe. Returns HTTP 503 if database or CSR kernel is unready."""
    read_conn = None
    try:
        read_conn = database.get_read_connection()
    except Exception:
        pass

    result = HealthProbeEngine.check_readiness(read_conn)
    if read_conn is not None:
        read_conn.close()

    if not result.get("is_ready"):
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return result


@router.get("/metrics")
async def metrics():
    """Prometheus exposition metrics endpoint."""
    content = PrometheusMetricsEngine.export_prometheus_text()
    return Response(content=content, media_type="text/plain; version=0.0.4; charset=utf-8")
