"""
Distributed Outbox Background Consumer & Sync Worker (Phase 79).

Continuously drains transactional outbox events, dispatches them to distributed endpoints,
applies exponential retry backoff, manages dead-letter queues (DLQ), and updates APM metrics.
"""
import asyncio
import logging
import sqlite3
import time
from typing import Callable, Dict, List, Optional
from app.core.distributed_outbox import (
    DistributedOutboxEngine,
    OutboxEvent,
    OutboxEventStatus
)
from app.core.observability import PrometheusMetricsEngine

logger = logging.getLogger("homeopathy.outbox_consumer")


class OutboxConsumerWorker:
    """
    Background asynchronous consumer worker for draining the transactional outbox table.
    """

    def __init__(
        self,
        db_connection_factory: Callable[[], sqlite3.Connection],
        dispatcher_callback: Optional[Callable[[OutboxEvent], bool]] = None,
        poll_interval_sec: float = 0.5,
        max_batch_size: int = 50,
        base_backoff_sec: float = 0.1
    ):
        self.db_connection_factory = db_connection_factory
        self.dispatcher_callback = dispatcher_callback or self._default_mock_dispatcher
        self.poll_interval_sec = poll_interval_sec
        self.max_batch_size = max_batch_size
        self.base_backoff_sec = base_backoff_sec
        self._is_running = False
        self._task: Optional[asyncio.Task] = None

    @staticmethod
    def _default_mock_dispatcher(event: OutboxEvent) -> bool:
        """Default in-memory dispatcher confirming receipt."""
        return True

    def calculate_backoff(self, retry_count: int) -> float:
        """Calculates exponential backoff delay: base * 2^retry_count."""
        return self.base_backoff_sec * (2 ** min(retry_count, 6))

    def run_once(self) -> Dict[str, int]:
        """
        Executes a single polling iteration:
        1. Reads pending events.
        2. Dispatches events via callback.
        3. Updates Prometheus pending gauge.
        """
        conn = self.db_connection_factory()
        try:
            # Check total pending
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM distributed_event_outbox WHERE status = ?", (OutboxEventStatus.PENDING.value,))
            pending_before = cursor.fetchone()[0]

            batch_res = DistributedOutboxEngine.process_outbox_batch(
                conn=conn,
                dispatcher_callback=self.dispatcher_callback,
                limit=self.max_batch_size
            )

            cursor.execute("SELECT COUNT(*) FROM distributed_event_outbox WHERE status = ?", (OutboxEventStatus.PENDING.value,))
            pending_after = cursor.fetchone()[0]
            PrometheusMetricsEngine.set_outbox_pending(pending_after)

            return {
                "processed": batch_res["processed"],
                "success": batch_res["success"],
                "failed": batch_res["failed"],
                "pending_remaining": pending_after
            }
        finally:
            conn.close()

    def get_dead_letter_events(self, limit: int = 50) -> List[OutboxEvent]:
        """Fetches events that exceeded max retries (Dead Letter Queue)."""
        conn = self.db_connection_factory()
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM distributed_event_outbox
                WHERE status = ?
                ORDER BY created_at_epoch DESC
                LIMIT ?
            """, (OutboxEventStatus.FAILED.value, limit))
            rows = cursor.fetchall()
            from app.core.distributed_outbox import OutboxAggregateType
            import json

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
        finally:
            conn.close()

    def redrive_dead_letter_event(self, event_id: str) -> bool:
        """Resets a dead-letter event back to PENDING with retry_count = 0."""
        conn = self.db_connection_factory()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE distributed_event_outbox
                SET status = ?, retry_count = 0, last_error = NULL
                WHERE event_id = ? AND status = ?
            """, (OutboxEventStatus.PENDING.value, event_id, OutboxEventStatus.FAILED.value))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    async def start(self):
        """Starts background loop."""
        self._is_running = True
        while self._is_running:
            try:
                self.run_once()
            except Exception as e:
                logger.error(f"Error in outbox consumer iteration: {e}", exc_info=True)
            await asyncio.sleep(self.poll_interval_sec)

    def stop(self):
        """Stops background loop."""
        self._is_running = False
        if self._task and not self._task.done():
            self._task.cancel()
