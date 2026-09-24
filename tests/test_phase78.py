"""
Automated Test Suite for Phase 78: Observability, Health Probes & Prometheus APM Metrics.
"""
import sqlite3
import pytest
from starlette.testclient import TestClient

from app.core.observability import HealthProbeEngine, PrometheusMetricsEngine
from app.repertory.csr_kernel import csr_kernel
from app.main import app


@pytest.fixture(autouse=True)
def ensure_kernel():
    if not csr_kernel.is_loaded:
        csr_kernel.load_memory_mapped()
    PrometheusMetricsEngine.reset_metrics()


def test_health_probe_liveness():
    """Verify liveness probe returns process status and uptime."""
    live = HealthProbeEngine.check_liveness()
    assert live["status"] == "ALIVE"
    assert live["is_alive"] is True
    assert isinstance(live["uptime_seconds"], float)
    assert live["uptime_seconds"] >= 0.0
    assert isinstance(live["pid"], int)


def test_health_probe_readiness_ready():
    """Verify readiness probe returns READY when DB and CSR kernel are available."""
    conn = sqlite3.connect(":memory:")
    res = HealthProbeEngine.check_readiness(conn)
    conn.close()

    assert res["status"] == "READY"
    assert res["is_ready"] is True
    assert res["database"] == "CONNECTED"
    assert res["csr_kernel"] == "LOADED"
    assert "readiness_latency_ms" in res


def test_health_probe_readiness_not_ready_when_csr_unloaded(monkeypatch):
    """Verify readiness probe returns NOT_READY when CSR kernel is unloaded."""
    monkeypatch.setattr(csr_kernel, "is_loaded", False)
    conn = sqlite3.connect(":memory:")
    res = HealthProbeEngine.check_readiness(conn)
    conn.close()

    assert res["status"] == "NOT_READY"
    assert res["is_ready"] is False
    assert res["csr_kernel"] == "NOT_LOADED"


def test_prometheus_metrics_recording():
    """Verify metrics recording across requests, durations, emergency lockouts, and outbox."""
    PrometheusMetricsEngine.record_http_request("GET", "/api/v1/patients", 200)
    PrometheusMetricsEngine.record_http_request("GET", "/api/v1/patients", 200)
    PrometheusMetricsEngine.record_http_request("POST", "/api/v1/clinical/prescribe", 400)

    PrometheusMetricsEngine.record_repertorization(0.00142)
    PrometheusMetricsEngine.record_repertorization(0.00210)

    PrometheusMetricsEngine.record_emergency_lockout()
    PrometheusMetricsEngine.record_prescription_signed()
    PrometheusMetricsEngine.set_outbox_pending(5)

    text = PrometheusMetricsEngine.export_prometheus_text()

    assert 'homeopathy_http_requests_total{method="GET",path="/api/v1/patients",status="200"} 2' in text
    assert 'homeopathy_http_requests_total{method="POST",path="/api/v1/clinical/prescribe",status="400"} 1' in text
    assert "homeopathy_csr_kernel_loaded 1" in text
    assert "homeopathy_emergency_lockouts_total 1" in text
    assert "homeopathy_prescriptions_signed_total 1" in text
    assert "homeopathy_outbox_pending_events 5" in text
    assert "homeopathy_repertorization_duration_seconds_count 2" in text


def test_prometheus_text_export_format():
    """Verify output contains correct Prometheus exposition headers."""
    text = PrometheusMetricsEngine.export_prometheus_text()
    assert "# HELP homeopathy_http_requests_total" in text
    assert "# TYPE homeopathy_http_requests_total counter"
    assert "# HELP homeopathy_csr_kernel_loaded" in text
    assert "# TYPE homeopathy_csr_kernel_loaded gauge"
    assert "# HELP homeopathy_repertorization_duration_seconds" in text


def test_health_router_fastapi_endpoints():
    """Verify HTTP probe and metrics endpoints through FastAPI TestClient."""
    client = TestClient(app)

    # 1. /live
    r_live = client.get("/api/v1/health/live")
    assert r_live.status_code == 200
    assert r_live.json()["status"] == "ALIVE"

    # 2. /ready
    r_ready = client.get("/api/v1/health/ready")
    assert r_ready.status_code == 200
    assert r_ready.json()["status"] == "READY"

    # 3. /metrics
    r_metrics = client.get("/api/v1/health/metrics")
    assert r_metrics.status_code == 200
    assert "text/plain" in r_metrics.headers["content-type"]
    assert "homeopathy_csr_kernel_loaded" in r_metrics.text
