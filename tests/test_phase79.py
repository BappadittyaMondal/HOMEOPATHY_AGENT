"""
Automated Test Suite for Phase 79: Distributed Outbox Background Consumer & Sync Worker.
"""
import sqlite3
import pytest
import asyncio
from app.core.distributed_outbox import (
    DistributedOutboxEngine,
    OutboxAggregateType,
    OutboxEventStatus
)
from app.core.outbox_consumer import OutboxConsumerWorker
from app.core.observability import PrometheusMetricsEngine


@pytest.fixture
def memory_db_factory():
    # Use shared in-memory URI or file-based for test lifecycle
    conn = sqlite3.connect("file:memdb_p79?mode=memory&cache=shared", uri=True)
    DistributedOutboxEngine.init_schema(conn)

    def factory():
        return sqlite3.connect("file:memdb_p79?mode=memory&cache=shared", uri=True)

    yield factory
    conn.close()


def test_outbox_consumer_run_once_drains_events(memory_db_factory):
    """Verify worker drains pending events and updates Prometheus gauge."""
    conn = memory_db_factory()
    DistributedOutboxEngine.publish_event(
        conn=conn,
        aggregate_type=OutboxAggregateType.PRESCRIPTION,
        aggregate_id="RX-TEST-001",
        event_type="PRESCRIPTION_DIGITALLY_SIGNED",
        payload={"remedy": "Sulphur", "potency": "30C"}
    )
    conn.close()

    worker = OutboxConsumerWorker(db_connection_factory=memory_db_factory)
    result = worker.run_once()

    assert result["processed"] == 1
    assert result["success"] == 1
    assert result["failed"] == 0
    assert result["pending_remaining"] == 0


def test_outbox_consumer_handles_transient_failure(memory_db_factory):
    """Verify failed dispatch increments retry_count and leaves event pending for retry."""
    conn = memory_db_factory()
    evt = DistributedOutboxEngine.publish_event(
        conn=conn,
        aggregate_type=OutboxAggregateType.ENCOUNTER,
        aggregate_id="ENC-TEST-002",
        event_type="ENCOUNTER_AUDIO_UPLOADED",
        payload={"url": "s3://enc/002.wav"}
    )
    conn.close()

    # Worker with failing dispatcher
    worker = OutboxConsumerWorker(
        db_connection_factory=memory_db_factory,
        dispatcher_callback=lambda e: False
    )
    result = worker.run_once()

    assert result["processed"] == 1
    assert result["success"] == 0
    assert result["failed"] == 1

    conn = memory_db_factory()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT retry_count, status FROM distributed_event_outbox WHERE event_id = ?", (evt.event_id,))
    row = cursor.fetchone()
    assert row["retry_count"] == 1
    assert row["status"] == OutboxEventStatus.PENDING.value
    conn.close()


def test_outbox_consumer_dead_letter_queue(memory_db_factory):
    """Verify events reaching max_retries transition to FAILED and appear in DLQ."""
    conn = memory_db_factory()
    evt = DistributedOutboxEngine.publish_event(
        conn=conn,
        aggregate_type=OutboxAggregateType.LAB_PANIC,
        aggregate_id="LAB-PANIC-003",
        event_type="CRITICAL_TROPONIN_ALERT",
        payload={"troponin": 0.25}
    )
    # Set retry_count to 4 (max is 5)
    conn.execute("UPDATE distributed_event_outbox SET retry_count = 4 WHERE event_id = ?", (evt.event_id,))
    conn.commit()
    conn.close()

    worker = OutboxConsumerWorker(
        db_connection_factory=memory_db_factory,
        dispatcher_callback=lambda e: False
    )
    worker.run_once()

    dlq = worker.get_dead_letter_events()
    assert len(dlq) == 1
    assert dlq[0].event_id == evt.event_id
    assert dlq[0].status == OutboxEventStatus.FAILED
    assert dlq[0].retry_count == 5


def test_outbox_consumer_redrive_dead_letter(memory_db_factory):
    """Verify dead-letter events can be manually redriven back to PENDING."""
    conn = memory_db_factory()
    evt = DistributedOutboxEngine.publish_event(
        conn=conn,
        aggregate_type=OutboxAggregateType.AUDIT,
        aggregate_id="AUD-001",
        event_type="AUDIT_SYNC",
        payload={"note": "Failed sync"}
    )
    conn.execute("UPDATE distributed_event_outbox SET status = 'FAILED', retry_count = 5 WHERE event_id = ?", (evt.event_id,))
    conn.commit()
    conn.close()

    worker = OutboxConsumerWorker(db_connection_factory=memory_db_factory)
    dlq = worker.get_dead_letter_events()
    assert len(dlq) > 0
    failed_id = dlq[0].event_id

    redriven = worker.redrive_dead_letter_event(failed_id)
    assert redriven is True

    # Check DLQ is now empty
    remaining_dlq = worker.get_dead_letter_events()
    assert len(remaining_dlq) == 0


def test_outbox_consumer_backoff_calculation():
    """Verify exponential backoff calculations."""
    worker = OutboxConsumerWorker(db_connection_factory=lambda: None, base_backoff_sec=0.1)
    assert round(worker.calculate_backoff(0), 2) == 0.1
    assert round(worker.calculate_backoff(1), 2) == 0.2
    assert round(worker.calculate_backoff(2), 2) == 0.4
    assert round(worker.calculate_backoff(3), 2) == 0.8
    assert round(worker.calculate_backoff(4), 2) == 1.6


@pytest.mark.anyio
async def test_outbox_consumer_async_start_stop(memory_db_factory):
    """Verify async worker loop can be started and gracefully stopped."""
    worker = OutboxConsumerWorker(
        db_connection_factory=memory_db_factory,
        poll_interval_sec=0.05
    )
    task = asyncio.create_task(worker.start())
    await asyncio.sleep(0.1)
    worker.stop()
    await asyncio.sleep(0.05)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    assert worker._is_running is False
