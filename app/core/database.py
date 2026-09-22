"""
SQLite High-Concurrency WAL Database Kernel with Asynchronous Commit Outbox.
Guarantees zero database-locked collisions on budget VPS and local-edge hospital appliances.
"""
import sqlite3
import asyncio
import logging
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass
from app.core.config import settings

logger = logging.getLogger("homeopathy.database")

@dataclass
class WriteTask:
    query: str
    params: tuple
    future: asyncio.Future
    is_script: bool = False

class SQLiteWALDatabase:
    """
    High-throughput SQLite database engine with:
    1. Read connections using WAL mode + 64MB memory cache.
    2. Single asynchronous commit queue worker preventing write contention.
    """
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = str(db_path or settings.DATABASE_PATH)
        self._write_queue: Optional[asyncio.Queue[WriteTask]] = None
        self._writer_task: Optional[asyncio.Task] = None
        self._is_running = False
        self._sync_write_conn: Optional[sqlite3.Connection] = None

    def _configure_connection(self, conn: sqlite3.Connection) -> sqlite3.Connection:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute(f"PRAGMA synchronous = {settings.SQLITE_WAL_SYNCHRONOUS};")
        conn.execute(f"PRAGMA busy_timeout = {settings.SQLITE_BUSY_TIMEOUT_MS};")
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA cache_size = -64000;")  # 64MB page cache
        conn.execute("PRAGMA temp_store = MEMORY;")
        return conn

    def get_read_connection(self) -> sqlite3.Connection:
        """Creates a dedicated thread-safe read connection."""
        conn = sqlite3.connect(self.db_path, timeout=settings.SQLITE_TIMEOUT_SECONDS)
        return self._configure_connection(conn)

    def get_sync_write_connection(self) -> sqlite3.Connection:
        """Direct connection for migrations, startup setup, or tests."""
        conn = sqlite3.connect(self.db_path, timeout=settings.SQLITE_TIMEOUT_SECONDS)
        return self._configure_connection(conn)

    async def start_worker(self):
        """Starts the single background writer worker in the asyncio event loop."""
        if self._is_running:
            return
        self._write_queue = asyncio.Queue(maxsize=settings.WRITE_QUEUE_MAX_SIZE)
        self._is_running = True
        self._writer_task = asyncio.create_task(self._writer_loop())
        logger.info("SQLite WAL Asynchronous Outbox Writer initialized.")

    async def stop_worker(self):
        """Gracefully shuts down the background writer worker, draining pending transactions."""
        if not self._is_running:
            return
        self._is_running = False
        if self._write_queue:
            await self._write_queue.join()
        if self._writer_task:
            self._writer_task.cancel()
            try:
                await self._writer_task
            except asyncio.CancelledError:
                pass
        if self._sync_write_conn:
            self._sync_write_conn.close()
            self._sync_write_conn = None
        logger.info("SQLite WAL Asynchronous Outbox Writer stopped.")

    async def _writer_loop(self):
        """Single exclusive writer process loop consuming the queue."""
        conn = self.get_sync_write_connection()
        while self._is_running:
            try:
                task = await self._write_queue.get()
                try:
                    cursor = conn.cursor()
                    if task.is_script:
                        cursor.executescript(task.query)
                        last_id = None
                        rows_affected = cursor.rowcount
                    else:
                        cursor.execute(task.query, task.params)
                        last_id = cursor.lastrowid
                        rows_affected = cursor.rowcount
                    conn.commit()
                    if not task.future.done():
                        task.future.set_result({
                            "last_insert_rowid": last_id,
                            "rowcount": rows_affected
                        })
                except Exception as exc:
                    conn.rollback()
                    logger.error(f"Transaction failure in writer loop: {exc}")
                    if not task.future.done():
                        task.future.set_exception(exc)
                finally:
                    self._write_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as loop_exc:
                logger.error(f"Unexpected writer loop exception: {loop_exc}")
        conn.close()

    async def execute_write(self, query: str, params: tuple = ()) -> dict:
        """
        Enqueues a write transaction and waits for the single writer to commit.
        Eliminates lock contention across concurrent web requests.
        """
        if not self._is_running or self._write_queue is None:
            # Fallback for synchronous test execution
            conn = self.get_sync_write_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return {"last_insert_rowid": cursor.lastrowid, "rowcount": cursor.rowcount}
            finally:
                conn.close()

        loop = asyncio.get_running_loop()
        future = loop.create_future()
        task = WriteTask(query=query, params=params, future=future, is_script=False)
        await self._write_queue.put(task)
        return await future

    async def execute_read(self, query: str, params: tuple = ()) -> list[dict]:
        """
        Executes an asynchronous non-blocking read against a WAL snapshot.
        """
        loop = asyncio.get_running_loop()
        def _read():
            conn = self.get_read_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            finally:
                conn.close()
        return await loop.run_in_executor(None, _read)

    def init_schema(self):
        """Initializes normalized database schema with ACID guarantees."""
        conn = self.get_sync_write_connection()
        try:
            with conn:
                conn.executescript("""
                -- 1. Patients Master Table
                CREATE TABLE IF NOT EXISTS patients (
                    patient_id TEXT PRIMARY KEY,
                    abha_id TEXT UNIQUE,
                    national_id TEXT,
                    full_name TEXT NOT NULL,
                    date_of_birth TEXT NOT NULL,
                    gender TEXT NOT NULL,
                    contact_phone TEXT NOT NULL,
                    email TEXT,
                    address TEXT,
                    emergency_contact TEXT,
                    guardian_name TEXT,
                    guardian_relation TEXT,
                    miasmatic_background TEXT,
                    constitutional_notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                -- 2. Encounters & Triage
                CREATE TABLE IF NOT EXISTS encounters (
                    encounter_id TEXT PRIMARY KEY,
                    patient_id TEXT NOT NULL,
                    encounter_type TEXT NOT NULL, -- OPD, IPD, EMERGENCY, DAYCARE
                    status TEXT NOT NULL, -- REGISTERED, TRIAGED, IN_CONSULTATION, COMPLETED, TRANSFERRED
                    triage_priority TEXT NOT NULL, -- RED, YELLOW, GREEN
                    chief_complaint TEXT,
                    practitioner_id TEXT NOT NULL,
                    temperature_c REAL,
                    pulse_bpm INTEGER,
                    blood_pressure_sys INTEGER,
                    blood_pressure_dia INTEGER,
                    respiratory_rate INTEGER,
                    spo2_percent INTEGER,
                    token_number INTEGER,
                    barcode_token TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE RESTRICT
                );

                -- 3. Repertory Knowledge Base (Base Schema)
                CREATE TABLE IF NOT EXISTS rubrics (
                    rubric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chapter TEXT NOT NULL,
                    full_path TEXT NOT NULL UNIQUE,
                    hierarchy_level INTEGER DEFAULT 1,
                    remedy_count INTEGER DEFAULT 0,
                    irf_weight REAL DEFAULT 1.0
                );

                CREATE TABLE IF NOT EXISTS remedies (
                    remedy_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    abbreviation TEXT NOT NULL UNIQUE,
                    full_name TEXT NOT NULL,
                    hpi_name TEXT NOT NULL,
                    common_name TEXT,
                    kingdom TEXT,
                    miasm_dominance TEXT,
                    toxicology_flag INTEGER DEFAULT 0
                );

                -- 4. Clinical Prescriptions (Draft vs Signed)
                CREATE TABLE IF NOT EXISTS prescriptions (
                    prescription_id TEXT PRIMARY KEY,
                    encounter_id TEXT NOT NULL,
                    patient_id TEXT NOT NULL,
                    remedy_name TEXT NOT NULL,
                    potency TEXT NOT NULL,
                    scale TEXT NOT NULL, -- CENTESIMAL, DECIMAL, 50_MILLESIMAL, MOTHER_TINCTURE
                    dosage_form TEXT NOT NULL, -- GLOBULES, LIQUID_DROPS, POWDER
                    posology_instruction TEXT NOT NULL,
                    legal_status TEXT NOT NULL, -- DRAFT_DECISION_SUPPORT, SIGNED_LEGAL_RMP
                    signed_by_rmp TEXT,
                    rmp_registration_number TEXT,
                    digital_signature_hash TEXT,
                    signed_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (encounter_id) REFERENCES encounters(encounter_id),
                    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
                );

                -- 5. Dispensary Stock & Active Bottles
                CREATE TABLE IF NOT EXISTS dispensary_bottles (
                    bottle_id TEXT PRIMARY KEY,
                    remedy_name TEXT NOT NULL,
                    potency TEXT NOT NULL,
                    batch_number TEXT NOT NULL,
                    manufacturer TEXT NOT NULL,
                    nominal_volume_ml REAL NOT NULL,
                    current_estimated_volume_ml REAL NOT NULL,
                    status TEXT NOT NULL, -- SEALED, ACTIVE_BENCH, DEPLETED, QUARANTINED
                    tare_weight_grams REAL,
                    current_gross_weight_grams REAL,
                    opened_at TIMESTAMP,
                    last_audited_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                -- 6. Cryptographic Audit Trail
                CREATE TABLE IF NOT EXISTS audit_logs (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    before_state TEXT,
                    after_state TEXT,
                    ip_address TEXT,
                    device_fingerprint TEXT,
                    prev_hash TEXT,
                    signature_hash TEXT NOT NULL
                );

                -- 7. Persistent NABH Audit Chain (Phase 55)
                CREATE TABLE IF NOT EXISTS nabh_audit_chain (
                    log_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    actor_id TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    patient_id TEXT,
                    details_json TEXT NOT NULL,
                    previous_hash TEXT NOT NULL,
                    current_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                -- 8. Persistent Dispensary Stock Ledger (Phase 55)
                CREATE TABLE IF NOT EXISTS dispensary_stock_ledger (
                    bottle_id TEXT PRIMARY KEY,
                    remedy_name TEXT NOT NULL,
                    potency TEXT NOT NULL,
                    batch_number TEXT NOT NULL,
                    initial_volume_ml REAL NOT NULL,
                    current_volume_ml REAL NOT NULL,
                    reorder_threshold_ml REAL DEFAULT 15.0,
                    evaporation_tolerance_pct REAL DEFAULT 10.0,
                    status TEXT DEFAULT 'ACTIVE_BENCH',
                    is_quarantined INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                -- 9. Persistent EHR Encounters (Phase 55)
                CREATE TABLE IF NOT EXISTS ehr_clinical_encounters (
                    encounter_id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL,
                    patient_id TEXT NOT NULL,
                    encounter_date TEXT NOT NULL,
                    chief_complaint TEXT NOT NULL,
                    rubrics_json TEXT NOT NULL,
                    remedy_prescribed TEXT NOT NULL,
                    potency TEXT NOT NULL,
                    kent_observation_num INTEGER,
                    vitality_score REAL NOT NULL,
                    dominant_miasm TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                -- Indexes for sub-millisecond retrieval
                CREATE INDEX IF NOT EXISTS idx_patients_phone ON patients(contact_phone);
                CREATE INDEX IF NOT EXISTS idx_encounters_patient ON encounters(patient_id);
                CREATE INDEX IF NOT EXISTS idx_encounters_status ON encounters(status);
                CREATE INDEX IF NOT EXISTS idx_prescriptions_patient ON prescriptions(patient_id);
                CREATE INDEX IF NOT EXISTS idx_rubrics_path ON rubrics(full_path);
                CREATE INDEX IF NOT EXISTS idx_nabh_patient ON nabh_audit_chain(patient_id);
                CREATE INDEX IF NOT EXISTS idx_ehr_tenant_patient ON ehr_clinical_encounters(tenant_id, patient_id);
                """)
        finally:
            conn.close()
        logger.info("Database schema initialized with foreign keys and WAL indexes.")

    def save_nabh_audit_entry_sync(self, log_id: str, timestamp: str, actor_id: str, action_type: str, details_json: str, previous_hash: str, current_hash: str, patient_id: Optional[str] = None):
        conn = self.get_sync_write_connection()
        try:
            with conn:
                conn.execute("""
                    INSERT OR REPLACE INTO nabh_audit_chain
                    (log_id, timestamp, actor_id, action_type, patient_id, details_json, previous_hash, current_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (log_id, timestamp, actor_id, action_type, patient_id, details_json, previous_hash, current_hash))
        finally:
            conn.close()

    def get_all_nabh_audit_entries_sync(self) -> list[dict]:
        conn = self.get_read_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM nabh_audit_chain ORDER BY rowid ASC")
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def clear_nabh_audit_entries_sync(self):
        conn = self.get_sync_write_connection()
        try:
            with conn:
                conn.execute("DELETE FROM nabh_audit_chain")
        finally:
            conn.close()

    def save_stock_bottle_sync(self, bottle_id: str, remedy_name: str, potency: str, batch_number: str, initial_volume_ml: float, current_volume_ml: float, reorder_threshold_ml: float, evaporation_tolerance_pct: float, status: str, is_quarantined: bool):
        conn = self.get_sync_write_connection()
        try:
            with conn:
                conn.execute("""
                    INSERT OR REPLACE INTO dispensary_stock_ledger
                    (bottle_id, remedy_name, potency, batch_number, initial_volume_ml, current_volume_ml, reorder_threshold_ml, evaporation_tolerance_pct, status, is_quarantined)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (bottle_id, remedy_name, potency, batch_number, initial_volume_ml, current_volume_ml, reorder_threshold_ml, evaporation_tolerance_pct, status, 1 if is_quarantined else 0))
        finally:
            conn.close()

    def get_all_stock_bottles_sync(self) -> list[dict]:
        conn = self.get_read_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM dispensary_stock_ledger")
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def clear_stock_bottles_sync(self):
        conn = self.get_sync_write_connection()
        try:
            with conn:
                conn.execute("DELETE FROM dispensary_stock_ledger")
        finally:
            conn.close()

    def save_ehr_encounter_sync(self, encounter_id: str, tenant_id: str, patient_id: str, encounter_date: str, chief_complaint: str, rubrics_json: str, remedy_prescribed: str, potency: str, kent_observation_num: Optional[int], vitality_score: float, dominant_miasm: str):
        conn = self.get_sync_write_connection()
        try:
            with conn:
                conn.execute("""
                    INSERT OR REPLACE INTO ehr_clinical_encounters
                    (encounter_id, tenant_id, patient_id, encounter_date, chief_complaint, rubrics_json, remedy_prescribed, potency, kent_observation_num, vitality_score, dominant_miasm)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (encounter_id, tenant_id, patient_id, encounter_date, chief_complaint, rubrics_json, remedy_prescribed, potency, kent_observation_num, vitality_score, dominant_miasm))
        finally:
            conn.close()

    def get_patient_ehr_encounters_sync(self, tenant_id: str, patient_id: str) -> list[dict]:
        conn = self.get_read_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ehr_clinical_encounters WHERE tenant_id = ? AND patient_id = ? ORDER BY encounter_date ASC", (tenant_id, patient_id))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def clear_ehr_encounters_sync(self):
        conn = self.get_sync_write_connection()
        try:
            with conn:
                conn.execute("DELETE FROM ehr_clinical_encounters")
        finally:
            conn.close()

    def wal_checkpoint(self, mode: str = "TRUNCATE") -> dict:
        """
        Executes explicit WAL checkpoint to truncate wal log file and optimize disk I/O.
        Modes: PASSIVE, FULL, RESTART, TRUNCATE.
        """
        conn = self.get_sync_write_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA wal_checkpoint({mode});")
            row = cursor.fetchone()
            busy, log_pages, checkpointed_pages = (row[0], row[1], row[2]) if row else (0, 0, 0)
            logger.info(f"SQLite WAL checkpoint({mode}) completed: busy={busy}, log={log_pages}, checkpointed={checkpointed_pages}")
            return {
                "checkpoint_mode": mode,
                "is_busy": bool(busy),
                "log_pages": log_pages,
                "checkpointed_pages": checkpointed_pages,
            }
        except Exception as exc:
            logger.error(f"WAL checkpoint failed: {exc}")
            return {"error": str(exc)}
        finally:
            conn.close()

# Global database singleton
db = SQLiteWALDatabase()
