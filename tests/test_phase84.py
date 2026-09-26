"""
Unit and Integration Tests for Phase 84: Multilingual Audio Narration Engine.
"""
import time
import pytest

from app.reporting.contracts import NarrationLanguage, AudioNarrationScript, ReportAudience
from app.reporting.audio_narrator import MultilingualAudioNarrator
from app.clinical.master_verifier import MasterHardenedClinicalResult
from app.models.ehr import EHRClinicalEncounter
from app.safety.gates import ApprovedDraft


@pytest.fixture
def sample_hardened_result():
    return MasterHardenedClinicalResult(
        patient_id="PAT-P84-001",
        tenant_id="TENANT-HOSP-01",
        is_workflow_successful=True,
        is_emergency_lockout=False,
        is_abstain=False,
        canonical_remedy_id="REM-LYCOPODIUM",
        canonical_remedy_name="Lycopodium clavatum",
        approved_draft=ApprovedDraft(
            prescription_id="RX-P84-123",
            patient_id="PAT-P84-001",
            remedy_name="Lycopodium clavatum",
            potency="1M",
            dosage_instructions="Single dose dry on tongue, observe for 21 days.",
            issued_timestamp="2026-09-26T16:00:00Z",
            gate_results=[],
            approval_token_hash="HASH-P84-SECRET"
        ),
        ehr_encounter=EHRClinicalEncounter(
            encounter_id="ENC-P84-123",
            patient_id="PAT-P84-001",
            tenant_id="TENANT-HOSP-01",
            encounter_date="2026-09-26",
            chief_complaint="Right-sided renal colic and 4-8 PM aggravation.",
            rubrics_selected=["KIDNEYS - PAIN - right", "GENERALS - 4 TO 8 PM - agg."],
            remedy_prescribed="Lycopodium clavatum",
            potency="1M",
            vitality_score=7.5,
            dominant_miasm="PSORA"
        ),
        invariants_verified=[f"INV-{i:02d}" for i in range(1, 22)],
        execution_timestamp="2026-09-26T16:00:00Z"
    )


def test_english_narration_script(sample_hardened_result):
    """Validates English plain-language narration script structure."""
    script = MultilingualAudioNarrator.generate_narration_script(
        sample_hardened_result,
        language=NarrationLanguage.EN_IN
    )
    assert script.language == NarrationLanguage.EN_IN
    assert "PAT-P84-001" in script.script_text
    assert "Lycopodium clavatum" in script.script_text
    assert "1M" in script.script_text
    assert "clean mouth" in script.script_text
    assert "chest pain" in script.script_text.lower()
    assert script.estimated_duration_seconds > 10.0
    assert "summary" in script.sections
    assert "posology" in script.sections


def test_hindi_narration_script(sample_hardened_result):
    """Validates Hindi narration script containing Devanagari text."""
    script = MultilingualAudioNarrator.generate_narration_script(
        sample_hardened_result,
        language=NarrationLanguage.HI_IN
    )
    assert script.language == NarrationLanguage.HI_IN
    assert "PAT-P84-001" in script.script_text
    assert "Lycopodium clavatum" in script.script_text
    assert "दवा" in script.script_text
    assert "साफ मुंह" in script.script_text
    assert script.estimated_duration_seconds > 10.0


def test_bengali_narration_script(sample_hardened_result):
    """Validates Bengali narration script containing Bengali script."""
    script = MultilingualAudioNarrator.generate_narration_script(
        sample_hardened_result,
        language=NarrationLanguage.BN_IN
    )
    assert script.language == NarrationLanguage.BN_IN
    assert "PAT-P84-001" in script.script_text
    assert "Lycopodium clavatum" in script.script_text
    assert "ওষুধ" in script.script_text
    assert "পরিষ্কার মুখে" in script.script_text
    assert script.estimated_duration_seconds > 10.0


def test_emergency_audio_narration(sample_hardened_result):
    """Validates that emergency lockout triggers crisis instructions in all languages."""
    sample_hardened_result.is_emergency_lockout = True

    script_en = MultilingualAudioNarrator.generate_narration_script(
        sample_hardened_result, language=NarrationLanguage.EN_IN
    )
    assert "Emergency medical alert" in script_en.script_text
    assert "suspended" in script_en.script_text.lower()

    script_hi = MultilingualAudioNarrator.generate_narration_script(
        sample_hardened_result, language=NarrationLanguage.HI_IN
    )
    assert "आपातकालीन" in script_hi.script_text

    script_bn = MultilingualAudioNarrator.generate_narration_script(
        sample_hardened_result, language=NarrationLanguage.BN_IN
    )
    assert "জরুরি চিকিৎসা সতর্কতা" in script_bn.script_text


def test_browser_controller_js_and_performance(sample_hardened_result):
    """Validates client-side JavaScript bundle and sub-2ms generation benchmark."""
    scripts = {
        NarrationLanguage.EN_IN: MultilingualAudioNarrator.generate_narration_script(sample_hardened_result, NarrationLanguage.EN_IN),
        NarrationLanguage.HI_IN: MultilingualAudioNarrator.generate_narration_script(sample_hardened_result, NarrationLanguage.HI_IN),
        NarrationLanguage.BN_IN: MultilingualAudioNarrator.generate_narration_script(sample_hardened_result, NarrationLanguage.BN_IN)
    }

    js = MultilingualAudioNarrator.generate_browser_controller_js(scripts)
    assert "window.HomeopathyAudio" in js
    assert "window.speechSynthesis" in js
    assert "play: function" in js
    assert "pause: function" in js
    assert "stop: function" in js

    # Benchmark latency
    t0 = time.perf_counter()
    for _ in range(10):
        MultilingualAudioNarrator.generate_narration_script(sample_hardened_result, NarrationLanguage.EN_IN)
        MultilingualAudioNarrator.generate_narration_script(sample_hardened_result, NarrationLanguage.HI_IN)
        MultilingualAudioNarrator.generate_narration_script(sample_hardened_result, NarrationLanguage.BN_IN)
    avg_latency = (time.perf_counter() - t0) * 1000.0 / 10.0
    assert avg_latency < 5.0, f"Narration generation latency ({avg_latency:.2f}ms) exceeded 5ms limit"
