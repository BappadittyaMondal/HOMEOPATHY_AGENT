"""
Automated Test Suite for Phase 74: Distributed Event Outbox & S3 Object Storage Gateway.
"""
import sqlite3
import pytest
from app.core.object_storage import (
    ObjectStorageGateway,
    StorageMimeType,
    PreSignedUploadToken
)
from app.core.distributed_outbox import (
    DistributedOutboxEngine,
    OutboxAggregateType,
    OutboxEventStatus
)


def test_presigned_upload_token_generation():
    """Verify cryptographically signed pre-signed token generation."""
    token = ObjectStorageGateway.generate_presigned_upload(
        object_name="encounter_audio.wav",
        mime_type=StorageMimeType.AUDIO_WAV,
        max_size_bytes=5 * 1024 * 1024
    )

    assert token.bucket_name == "homeopathy-hospital-blobs"
    assert "blobs/" in token.object_key
    assert token.allowed_mime_type == StorageMimeType.AUDIO_WAV
    assert token.upload_url.startswith("https://s3.")
    assert len(token.signature) == 64


def test_verify_and_register_valid_upload():
    """Verify payload size check, SHA-256 calculation, and registration metadata."""
    token = ObjectStorageGateway.generate_presigned_upload(
        object_name="lab_scan.pdf",
        mime_type=StorageMimeType.APPLICATION_PDF,
        max_size_bytes=1024 * 1024
    )

    mock_pdf_bytes = b"%PDF-1.4 Mock PDF Content for Clinical Lab Report"
    meta = ObjectStorageGateway.verify_and_register_upload(
        token=token,
        uploaded_bytes=mock_pdf_bytes,
        patient_id="PT-S3-001"
    )

    assert meta.object_key == token.object_key
    assert meta.size_bytes == len(mock_pdf_bytes)
    assert meta.patient_id == "PT-S3-001"
    assert len(meta.sha256_hash) == 64


def test_tampered_token_signature_rejection():
    """Verify modifying pre-signed token parameters raises PermissionError."""
    token = ObjectStorageGateway.generate_presigned_upload(
        object_name="secure_image.jpg",
        mime_type=StorageMimeType.IMAGE_JPEG
    )

    # Tamper with signature
    tampered_token = token.model_copy(update={"signature": "0000000000000000000000000000000000000000000000000000000000000000"})
    with pytest.raises(PermissionError):
        ObjectStorageGateway.verify_and_register_upload(
            token=tampered_token,
            uploaded_bytes=b"\xff\xd8\xff Mock JPEG Image"
        )


def test_oversized_payload_rejection():
    """Verify payload exceeding allocated max_size_bytes raises ValueError."""
    token = ObjectStorageGateway.generate_presigned_upload(
        object_name="tiny.wav",
        mime_type=StorageMimeType.AUDIO_WAV,
        max_size_bytes=100
    )

    oversized = b"X" * 150
    with pytest.raises(ValueError, match="exceeds limit"):
        ObjectStorageGateway.verify_and_register_upload(
            token=token,
            uploaded_bytes=oversized
        )


def test_outbox_publish_and_fetch_pending():
    """Verify SQLite outbox transactional write and pending retrieval."""
    conn = sqlite3.connect(":memory:")
    DistributedOutboxEngine.init_schema(conn)

    evt = DistributedOutboxEngine.publish_event(
        conn=conn,
        aggregate_type=OutboxAggregateType.PRESCRIPTION,
        aggregate_id="RX-999-ABC",
        event_type="PRESCRIPTION_SIGNED",
        payload={"remedy": "Arsenicum album", "potency": "30C", "doctor": "DR-123"}
    )

    assert evt.status == OutboxEventStatus.PENDING

    pending = DistributedOutboxEngine.fetch_pending_events(conn)
    assert len(pending) == 1
    assert pending[0].aggregate_id == "RX-999-ABC"
    assert pending[0].payload["remedy"] == "Arsenicum album"


def test_outbox_batch_processing_and_retry_backoff():
    """Verify outbox batch dispatching, success mark, and retry error tracking."""
    conn = sqlite3.connect(":memory:")
    DistributedOutboxEngine.init_schema(conn)

    # Publish 2 events
    e1 = DistributedOutboxEngine.publish_event(
        conn=conn,
        aggregate_type=OutboxAggregateType.ENCOUNTER,
        aggregate_id="ENC-001",
        event_type="ENCOUNTER_COMPLETED",
        payload={"patient": "PT-1"}
    )
    e2 = DistributedOutboxEngine.publish_event(
        conn=conn,
        aggregate_type=OutboxAggregateType.LAB_PANIC,
        aggregate_id="LAB-002",
        event_type="PANIC_ALERT",
        payload={"hazard": "Troponin elevation"}
    )

    # Dispatcher callback: succeeds on ENC-001, fails on LAB-002
    def mock_dispatcher(evt):
        if evt.aggregate_id == "ENC-001":
            return True
        return False

    summary = DistributedOutboxEngine.process_outbox_batch(conn, dispatcher_callback=mock_dispatcher)
    assert summary["processed"] == 2
    assert summary["success"] == 1
    assert summary["failed"] == 1

    # Verify status in database
    pending_after = DistributedOutboxEngine.fetch_pending_events(conn)
    assert len(pending_after) == 1
    assert pending_after[0].aggregate_id == "LAB-002"
    assert pending_after[0].retry_count == 1
