"""
Unit & Concurrency Tests for Phase 01: Core Scaffolding & SQLite WAL Outbox.
Uses native asyncio.run() to ensure portable execution without requiring third-party async plugins.
"""
import asyncio
import uuid
import random
from httpx import AsyncClient, ASGITransport
from app.core.config import settings
from app.core.database import db
from app.main import app

def test_sqlite_wal_pragmas():
    """Verify SQLite WAL mode, foreign keys, and synchronous setting."""
    async def _test():
        conn = db.get_read_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode;")
            journal_mode = cursor.fetchone()[0]
            assert journal_mode.upper() == "WAL", f"Expected WAL mode, got {journal_mode}"

            cursor.execute("PRAGMA foreign_keys;")
            foreign_keys = cursor.fetchone()[0]
            assert foreign_keys == 1, f"Expected foreign_keys=ON, got {foreign_keys}"

            cursor.execute("PRAGMA synchronous;")
            synchronous = cursor.fetchone()[0]
            # NORMAL is 1 in SQLite
            assert synchronous in (1, "1", "NORMAL"), f"Expected synchronous=NORMAL, got {synchronous}"
        finally:
            conn.close()
    
    asyncio.run(_test())

def test_concurrent_writes_zero_lock():
    """Verify 25 simultaneous writes execute cleanly without SQLITE_BUSY."""
    async def _test():
        await db.start_worker()
        
        async def write_patient(idx: int):
            pid = f"PAT-CONCUR-{idx}-{uuid.uuid4().hex[:6]}"
            phone = f"+9198765{random.randint(10000, 99999)}"
            query = """
            INSERT INTO patients (
                patient_id, full_name, date_of_birth, gender, contact_phone
            ) VALUES (?, ?, ?, ?, ?);
            """
            params = (pid, f"Concurrency Patient {idx}", "1990-01-01", "FEMALE", phone)
            res = await db.execute_write(query, params)
            assert res["rowcount"] == 1
            return pid

        # Launch 25 concurrent write tasks simultaneously
        tasks = [write_patient(i) for i in range(25)]
        results = await asyncio.gather(*tasks)
        assert len(results) == 25

        # Verify all 25 are readable
        read_results = await db.execute_read(
            "SELECT COUNT(*) as cnt FROM patients WHERE patient_id LIKE 'PAT-CONCUR-%'"
        )
        assert read_results[0]["cnt"] >= 25
        await db.stop_worker()

    asyncio.run(_test())

def test_api_health_endpoint():
    """Verify FastAPI /api/v1/health returns HEALTHY and WAL status."""
    async def _test():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/api/v1/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "HEALTHY"
            assert data["database"]["journal_mode"] == "WAL"
    
    asyncio.run(_test())

def test_api_patient_registration_and_duplicate_check():
    """Verify patient registration endpoint and duplicate check."""
    async def _test():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            unique_phone = f"+9191112{random.randint(10000, 99999)}"
            patient_data = {
                "full_name": "Dr. Hahnemann Test Patient",
                "date_of_birth": "1985-04-10",
                "gender": "MALE",
                "contact_phone": unique_phone,
                "email": "hahnemann.patient@example.com",
                "address": "Kolkata, WB, India",
                "miasmatic_background": "Psora dominant, history of eczema"
            }
            
            # 1. Register new patient
            res1 = await ac.post("/api/v1/patients", json=patient_data)
            assert res1.status_code == 201, res1.text
            created = res1.json()
            assert created["full_name"] == patient_data["full_name"]
            patient_id = created["patient_id"]

            # 2. Retrieve patient
            res_get = await ac.get(f"/api/v1/patients/{patient_id}")
            assert res_get.status_code == 200
            assert res_get.json()["contact_phone"] == unique_phone

            # 3. Attempt duplicate registration with same phone -> must return 409 Conflict
            res_dup = await ac.post("/api/v1/patients", json=patient_data)
            assert res_dup.status_code == 409
            assert "already exists" in res_dup.json()["detail"]

    asyncio.run(_test())
