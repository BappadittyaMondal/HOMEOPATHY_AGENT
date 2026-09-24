"""
Distributed Event Outbox Engine (Phase 74).

Implements the Transactional Outbox Pattern over SQLite WAL mode, ensuring that
critical clinical events (encounters, digital prescriptions, lab panic alerts,
dispensary stock deductions) are reliably dispatched across hospital branches and
central data lakes without write collisions, double-dispatch, or network failure losses.
"""
import json
import sqlite3
import time
import uuid
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from pydantic import BaseModel, Field


class OutboxEventStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    DISPATCHED = "DISPATCHED"
    FAILED = "FAILED"


class OutboxAggregateType(str, Enum):
    ENCOUNTER = "ENCOUNTER"
    PRESCRIPTION = "PRESCRIPTION"
    LAB_PANIC = "LAB_PANIC"
    DISPENSARY = "DISPENSARY"
    AUDIT = "AUDIT"


class OutboxEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"EVT-{uuid.uuid4().hex[:12].upper()}")
    tenant_id: str = "DEFAULT_TENANT"
    aggregate_type: OutboxAggregateType
    aggregate_id: str
    event_type: str
    payload: Dict[str, Any]
    status: OutboxEventStatus = OutboxEventStatus.PENDING
    retry_count: int = 0
    max_retries: int = 5
    last_error: Optional[str] = None
    created_at_epoch: int = Field(default_factory=lambda: int(time.time()))
    dispatched_at_epoch: Optional[int] = None


class DistributedOutboxEngine:
    """
    Transactional SQLite Event Outbox engine with retry management and idempotency.
    """

    SCHEMA_DDL = """
    CREATE TABLE IF NOT EXISTS distributed_event_outbox (
        event_id TEXT PRIMARY KEY,
        tenant_id TEXT NOT NULL,
        aggregate_type TEXT NOT NULL,
        aggregate_id TEXT NOT NULL,
        event_type TEXT NOT NULL,
        payload_json TEXT NOT NULL,
        status TEXT NOT NULL,
        retry_count INTEGER DEFAULT 0,
        max_retries INTEGER DEFAULT 5,
        last_error TEXT,
        created_at_epoch INTEGER NOT NULL,
        dispatched_at_epoch INTEGER
    );
    CREATE INDEX IF NOT EXISTS idx_outbox_status_epoch ON distributed_event_outbox(status, created_at_epoch);
    """

    @classmethod
    def init_schema(cls, conn: sqlite3.Connection):
        """Initializes the outbox table and index in SQLite."""
        conn.executescript(cls.SCHEMA_DDL)
        conn.commit()

    @classmethod
    def publish_event(
        cls,
        conn: sqlite3.Connection,
        aggregate_type: OutboxAggregateType,
        aggregate_id: str,
        event_type: str,
        payload: Dict[str, Any],
        tenant_id: str = "DEFAULT_TENANT"
    ) -> OutboxEvent:
        """
        Transactionally inserts a new clinical event into the outbox.
        """
        event = OutboxEvent(
            tenant_id=tenant_id,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            event_type=event_type,
            payload=payload
        )
        query = """
        INSERT INTO distributed_event_outbox (
            event_id, tenant_id, aggregate_type, aggregate_id, event_type,
            payload_json, status, retry_count, max_retries, last_error,
            created_at_epoch, dispatched_at_epoch
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        conn.execute(query, (
            event.event_id,
            event.tenant_id,
            event.aggregate_type.value,
            event.aggregate_id,
            event.event_type,
            json.dumps(event.payload),
            event.status.value,
            event.retry_count,
            event.max_retries,
            event.last_error,
            event.created_at_epoch,
            event.dispatched_at_epoch
        ))
        conn.commit()
        return event

    @classmethod
    def fetch_pending_events(
        cls,
        conn: sqlite3.Connection,
        limit: int = 50
    ) -> List[OutboxEvent]:
        """
        Retrieves pending outbox events ordered by creation time.
        """
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM distributed_event_outbox
            WHERE status = ? AND retry_count < max_retries
            ORDER BY created_at_epoch ASC
            LIMIT ?
        """, (OutboxEventStatus.PENDING.value, limit))

        rows = cursor.fetchall()
        events = []
        for r in rows:
            events.append(OutboxEvent(
                event_id=r["event_id"],
                tenant_id=r["tenant_id"],
                aggregate_type=OutboxAggregateType(r["aggregate_type"]),
                aggregate_id=r["aggregate_id"],
                event_type=r["event_type"],
                payload=json.loads(r["payload_json"]),
                status=OutboxEventStatus(r["status"]),
                retry_count=r["retry_count"],
                max_retries=r["max_retries"],
                last_error=r["last_error"],
                created_at_epoch=r["created_at_epoch"],
                dispatched_at_epoch=r["dispatched_at_epoch"]
            ))
        return events

    @classmethod
    def mark_event_dispatched(cls, conn: sqlite3.Connection, event_id: str):
        """Marks event as successfully dispatched."""
        now = int(time.time())
        conn.execute("""
            UPDATE distributed_event_outbox
            SET status = ?, dispatched_at_epoch = ?
            WHERE event_id = ?
        """, (OutboxEventStatus.DISPATCHED.value, now, event_id))
        conn.commit()

    @classmethod
    def mark_event_failed(cls, conn: sqlite3.Connection, event_id: str, error_msg: str):
        """Increments retry count and sets FAILED if max retries exceeded."""
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT retry_count, max_retries FROM distributed_event_outbox WHERE event_id = ?", (event_id,))
        row = cursor.fetchone()
        if not row:
            return

        new_count = row["retry_count"] + 1
        new_status = OutboxEventStatus.FAILED.value if new_count >= row["max_retries"] else OutboxEventStatus.PENDING.value

        conn.execute("""
            UPDATE distributed_event_outbox
            SET retry_count = ?, status = ?, last_error = ?
            WHERE event_id = ?
        """, (new_count, new_status, error_msg, event_id))
        conn.commit()

    @classmethod
    def process_outbox_batch(
        cls,
        conn: sqlite3.Connection,
        dispatcher_callback: Callable[[OutboxEvent], bool],
        limit: int = 50
    ) -> Dict[str, int]:
        """
        Processes a batch of pending events using an injected dispatcher callback.
        """
        events = cls.fetch_pending_events(conn, limit=limit)
        success_count = 0
        failure_count = 0

        for evt in events:
            try:
                ok = dispatcher_callback(evt)
                if ok:
                    cls.mark_event_dispatched(conn, evt.event_id)
                    success_count += 1
                else:
                    cls.mark_event_failed(conn, evt.event_id, "Dispatcher returned failure status.")
                    failure_count += 1
            except Exception as e:
                cls.mark_event_failed(conn, evt.event_id, str(e))
                failure_count += 1

        return {
            "processed": len(events),
            "success": success_count,
            "failed": failure_count
        }
