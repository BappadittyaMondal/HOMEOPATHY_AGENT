"""
Unit Tests for Phase 49: Hostinger KVM Linux VPS Deployment & Containerization Pipeline.
"""
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

def test_dockerfile_hardening():
    """Verify production multi-stage Dockerfile and non-root execution."""
    df_path = BASE_DIR / "docker" / "Dockerfile"
    assert df_path.exists(), "Dockerfile missing"
    content = df_path.read_text(encoding="utf-8")

    assert "FROM python:3.14-slim AS builder" in content
    assert "FROM python:3.14-slim AS runner" in content
    assert "useradd -u 10001" in content
    assert "USER appuser" in content
    assert "HEALTHCHECK" in content
    assert "uvicorn" in content

def test_docker_compose_resource_limits():
    """Verify memory and CPU constraints in docker-compose.yml for budget VPS."""
    dc_path = BASE_DIR / "docker" / "docker-compose.yml"
    assert dc_path.exists(), "docker-compose.yml missing"
    content = dc_path.read_text(encoding="utf-8")

    assert "memory: 1536M" in content
    assert "cpus: \"1.5\"" in content
    assert "sqlite_wal_data:" in content
    assert "restart: unless-stopped" in content

def test_nginx_security_headers_and_rate_limits():
    """Verify Nginx reverse proxy security headers and IP rate limiting."""
    ng_path = BASE_DIR / "docker" / "nginx.conf"
    assert ng_path.exists(), "nginx.conf missing"
    content = ng_path.read_text(encoding="utf-8")

    assert "limit_req_zone" in content
    assert "rate=30r/s" in content
    assert "X-Content-Type-Options \"nosniff\"" in content
    assert "X-Frame-Options \"DENY\"" in content
    assert "Strict-Transport-Security" in content

def test_deployment_script_sysctl_and_permissions():
    """Verify host provisioning bash script."""
    sh_path = BASE_DIR / "scripts" / "deploy_hostinger.sh"
    assert sh_path.exists(), "deploy_hostinger.sh missing"
    content = sh_path.read_text(encoding="utf-8")

    assert "vm.max_map_count=262144" in content
    assert "10001:10001" in content
    assert "docker compose up -d" in content
