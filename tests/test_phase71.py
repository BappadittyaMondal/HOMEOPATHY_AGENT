"""
Automated Test Suite for Phase 71: Vernacular Audio Ingestion & Zero-GPU Edge ASR Decoder Engine.
"""
import io
import struct
import pytest
from app.governance.audio_ingestion import (
    VernacularAudioDecoderEngine,
    AudioContainerFormat,
    AudioPayloadCorruptedError,
    AudioDurationExceededError,
    AudioIngestionResult
)


def create_mock_wav_bytes(duration_seconds: float = 2.0, sample_rate: int = 16000) -> bytes:
    """Creates a synthetically valid RIFF/WAV byte payload in memory."""
    channels = 1
    bits_per_sample = 16
    byte_rate = sample_rate * channels * (bits_per_sample // 8)
    data_size = int(duration_seconds * byte_rate)
    total_size = 36 + data_size

    buf = io.BytesIO()
    # RIFF header
    buf.write(b"RIFF")
    buf.write(struct.pack("<I", total_size))
    buf.write(b"WAVE")
    # fmt subchunk
    buf.write(b"fmt ")
    buf.write(struct.pack("<I", 16)) # Subchunk1Size
    buf.write(struct.pack("<H", 1))  # AudioFormat (1=PCM)
    buf.write(struct.pack("<H", channels))
    buf.write(struct.pack("<I", sample_rate))
    buf.write(struct.pack("<I", byte_rate))
    buf.write(struct.pack("<H", channels * (bits_per_sample // 8))) # BlockAlign
    buf.write(struct.pack("<H", bits_per_sample))
    # data subchunk
    buf.write(b"data")
    buf.write(struct.pack("<I", data_size))
    # mock silence samples
    buf.write(b"\x00" * data_size)
    return buf.getvalue()


def test_wav_container_metadata_extraction():
    """Verify standard WAV header parsing, container detection, and duration calculation."""
    wav_bytes = create_mock_wav_bytes(duration_seconds=3.5, sample_rate=16000)
    meta = VernacularAudioDecoderEngine.parse_audio_metadata(wav_bytes)

    assert meta.container_format == AudioContainerFormat.WAV
    assert meta.sample_rate_hz == 16000
    assert meta.channels == 1
    assert meta.bits_per_sample == 16
    assert abs(meta.duration_seconds - 3.5) <= 0.1
    assert len(meta.sha256_hash) == 64


def test_bengali_vernacular_symptom_extraction():
    """Verify extraction of characteristic Bengali clinical expressions into Kentian rubrics."""
    wav_bytes = create_mock_wav_bytes(duration_seconds=2.0)
    transcript = "amar matha betha norachora korle bare ebong jol pipasha nei"

    result = VernacularAudioDecoderEngine.ingest_raw_audio(
        audio_bytes=wav_bytes,
        language_hint="bn",
        client_transcript=transcript
    )

    assert result.detected_language == "bn"
    assert len(result.normalized_symptoms) == 3

    categories = [s.category for s in result.normalized_symptoms]
    assert "LOCATION" in categories
    assert "MODALITY" in categories
    assert "GENERAL" in categories

    rubrics = [s.repertory_rubric_equivalent for s in result.normalized_symptoms]
    assert "Head - Pain - General" in rubrics
    assert "Generalities - Motion - Aggravation" in rubrics
    assert "Stomach - Thirstless" in rubrics
    assert result.requires_clinical_clarification is False


def test_hindi_vernacular_symptom_extraction():
    """Verify extraction of Hindi vernacular symptoms including pressure relief and gastric burning."""
    wav_bytes = create_mock_wav_bytes(duration_seconds=2.5)
    transcript = "sir me thak thak dard hai pet me jalan aur dabane se aaram milta hai"

    result = VernacularAudioDecoderEngine.ingest_raw_audio(
        audio_bytes=wav_bytes,
        language_hint="hi",
        client_transcript=transcript
    )

    assert result.detected_language == "hi"
    rubrics = [s.repertory_rubric_equivalent for s in result.normalized_symptoms]
    assert "Head - Pain - Throbbing" in rubrics
    assert "Stomach - Burning" in rubrics
    assert "Generalities - Pressure - Amelioration" in rubrics


def test_corrupted_and_empty_payload_rejection():
    """Verify that empty, truncated, or corrupted payloads raise AudioPayloadCorruptedError."""
    with pytest.raises(AudioPayloadCorruptedError):
        VernacularAudioDecoderEngine.parse_audio_metadata(b"")

    with pytest.raises(AudioPayloadCorruptedError):
        VernacularAudioDecoderEngine.parse_audio_metadata(b"RI")


def test_duration_exceeded_rejection():
    """Verify that audio exceeding 300s limit is safely rejected to prevent DoS."""
    # 400 seconds of 16kHz 16-bit mono = ~12.8 MB
    oversized_bytes = create_mock_wav_bytes(duration_seconds=350.0, sample_rate=8000)
    with pytest.raises(AudioDurationExceededError):
        VernacularAudioDecoderEngine.parse_audio_metadata(oversized_bytes)


def test_clinical_clarification_flag_on_incomplete_symptoms():
    """Verify that solitary vague symptoms flag requires_clinical_clarification=True."""
    wav_bytes = create_mock_wav_bytes(duration_seconds=1.5)
    transcript = "amar matha betha" # Only location, missing modalities

    result = VernacularAudioDecoderEngine.ingest_raw_audio(
        audio_bytes=wav_bytes,
        language_hint="bn",
        client_transcript=transcript
    )

    assert len(result.normalized_symptoms) == 1
    assert result.requires_clinical_clarification is True
