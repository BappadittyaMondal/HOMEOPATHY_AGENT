"""
Vernacular Multilingual Voice Token Ingestion Engine (Phase 40).
Processes client-side offloaded voice scribe tokens across Indian languages
(Hindi, Bengali, Marathi, Tamil, English) and maps colloquial expressions
into standardized homeopathic clinical symptom entities without server-side GPU overhead.
"""
from typing import Dict, List, Optional
from pydantic import BaseModel

class VernacularVoiceToken(BaseModel):
    language: str  # "hi", "bn", "mr", "ta", "en"
    raw_transcript: str
    confidence: float
    device_source: str = "BROWSER_WEB_SPEECH_API"

class NormalizedClinicalSymptom(BaseModel):
    original_phrase: str
    standardized_medical_term: str
    category: str  # "LOCATION", "SENSATION", "MODALITY", "GENERAL"
    repertory_rubric_equivalent: str

class VernacularIngestionResult(BaseModel):
    detected_language: str
    normalized_symptoms: List[NormalizedClinicalSymptom]
    raw_token_count: int
    unmapped_phrases: List[str]

class VernacularVoiceEngine:
    """
    Normalizes vernacular voice tokens into classical homeopathic repertorial rubrics.
    """

    COLLOQUIAL_LEXICON: Dict[str, Dict[str, str]] = {
        # Hindi
        "sir dard": {"term": "headache", "cat": "LOCATION", "rubric": "Head - Pain - General"},
        "matha dard": {"term": "headache", "cat": "LOCATION", "rubric": "Head - Pain - General"},
        "pet me jalan": {"term": "burning in stomach", "cat": "SENSATION", "rubric": "Stomach - Burning"},
        "thand lagti hai": {"term": "chilly thermal disposition", "cat": "MODALITY", "rubric": "Generalities - Cold - Tendency to become"},
        "neend nahi aati": {"term": "insomnia", "cat": "GENERAL", "rubric": "Sleep - Sleeplessness"},
        "pani ki pyas nahi": {"term": "thirstlessness", "cat": "GENERAL", "rubric": "Stomach - Thirstless"},
        
        # Bengali
        "matha betha": {"term": "headache", "cat": "LOCATION", "rubric": "Head - Pain - General"},
        "buk jala": {"term": "heartburn pyrosis", "cat": "SENSATION", "rubric": "Stomach - Heartburn"},
        "khub thanda lage": {"term": "chilly thermal disposition", "cat": "MODALITY", "rubric": "Generalities - Cold - Aggravation"},
        "ghom hoy na": {"term": "insomnia", "cat": "GENERAL", "rubric": "Sleep - Sleeplessness"},
        "jol pipasha nei": {"term": "thirstlessness", "cat": "GENERAL", "rubric": "Stomach - Thirstless"},

        # Marathi
        "doke dukhi": {"term": "headache", "cat": "LOCATION", "rubric": "Head - Pain - General"},
        "potat jallan": {"term": "burning in stomach", "cat": "SENSATION", "rubric": "Stomach - Burning"},
        "khup thandi vajte": {"term": "chilly thermal disposition", "cat": "MODALITY", "rubric": "Generalities - Cold - Aggravation"},

        # Tamil
        "thalai vali": {"term": "headache", "cat": "LOCATION", "rubric": "Head - Pain - General"},
        "vayitru eri-chal": {"term": "burning in stomach", "cat": "SENSATION", "rubric": "Stomach - Burning"},

        # English Colloquials
        "splitting headache": {"term": "violent bursting headache", "cat": "SENSATION", "rubric": "Head - Pain - Bursting"},
        "cannot sleep": {"term": "insomnia", "cat": "GENERAL", "rubric": "Sleep - Sleeplessness"},
        "burning stomach": {"term": "gastric burning", "cat": "SENSATION", "rubric": "Stomach - Burning"}
    }

    @classmethod
    def ingest_voice_tokens(cls, token: VernacularVoiceToken) -> VernacularIngestionResult:
        """
        Parses raw transcript and maps vernacular idioms to repertorial terms.
        """
        text = token.raw_transcript.lower()
        normalized = []
        unmapped = []

        words = text.split()
        total_words = len(words)

        # Multi-word matching against colloquial lexicon
        for idiom, meta in cls.COLLOQUIAL_LEXICON.items():
            if idiom in text:
                normalized.append(NormalizedClinicalSymptom(
                    original_phrase=idiom,
                    standardized_medical_term=meta["term"],
                    category=meta["cat"],
                    repertory_rubric_equivalent=meta["rubric"]
                ))
                text = text.replace(idiom, "")

        # Remaining non-trivial words considered unmapped
        remaining_words = [w for w in text.split() if len(w) > 3]
        if remaining_words:
            unmapped = remaining_words

        return VernacularIngestionResult(
            detected_language=token.language,
            normalized_symptoms=normalized,
            raw_token_count=total_words,
            unmapped_phrases=unmapped
        )
