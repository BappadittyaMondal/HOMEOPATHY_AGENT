"""
Unit Tests for Phase 40: Vernacular Multilingual Voice Token Ingestion Engine.
"""
from app.governance.voice_scribe import VernacularVoiceEngine, VernacularVoiceToken

def test_voice_scribe_hindi_token_mapping():
    """Verify Hindi clinical voice tokens mapped to classical rubrics."""
    token = VernacularVoiceToken(
        language="hi",
        raw_transcript="mujhe do din se sir dard hai aur pet me jalan hoti hai",
        confidence=0.96
    )
    result = VernacularVoiceEngine.ingest_voice_tokens(token)
    assert result.detected_language == "hi"
    assert len(result.normalized_symptoms) == 2
    terms = [s.standardized_medical_term for s in result.normalized_symptoms]
    assert "headache" in terms
    assert "burning in stomach" in terms
    assert any("Head - Pain" in s.repertory_rubric_equivalent for s in result.normalized_symptoms)

def test_voice_scribe_bengali_token_mapping():
    """Verify Bengali clinical voice tokens mapped to rubrics."""
    token = VernacularVoiceToken(
        language="bn",
        raw_transcript="amar matha betha ar khub thanda lage ar ghom hoy na",
        confidence=0.94
    )
    result = VernacularVoiceEngine.ingest_voice_tokens(token)
    assert result.detected_language == "bn"
    terms = [s.standardized_medical_term for s in result.normalized_symptoms]
    assert "headache" in terms
    assert "chilly thermal disposition" in terms
    assert "insomnia" in terms

def test_voice_scribe_marathi_token_mapping():
    """Verify Marathi colloquial idioms."""
    token = VernacularVoiceToken(
        language="mr",
        raw_transcript="kharab doke dukhi ani potat jallan",
        confidence=0.91
    )
    result = VernacularVoiceEngine.ingest_voice_tokens(token)
    assert result.detected_language == "mr"
    terms = [s.standardized_medical_term for s in result.normalized_symptoms]
    assert "headache" in terms
    assert "burning in stomach" in terms
