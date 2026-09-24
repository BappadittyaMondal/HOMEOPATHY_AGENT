"""
Interactive Hahnemannian Case-Taking Dialogue & LSMC Disambiguation Engine (Phase 72).

Codifies Samuel Hahnemann's case-taking methodology per Organon of Medicine Aphorisms 83-104.
Detects incomplete symptom totalities (< 3 characteristic rubrics), systematically queries
the patient for missing Location, Sensation, Modality, and Concomitant (LSMC) dimensions
in their native vernacular (Bengali, Hindi, English), and safely transitions complete
cases into the repertory kernel while enforcing emergency sentinel locks.
"""
import uuid
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from pydantic import BaseModel, Field

from app.governance.voice_scribe import NormalizedClinicalSymptom
from app.governance.audio_ingestion import VernacularAudioDecoderEngine


class DialogueState(str, Enum):
    INITIAL = "INITIAL"
    AWAITING_CLARIFICATION = "AWAITING_CLARIFICATION"
    COMPLETE = "COMPLETE"
    ABSTAIN_INSUFFICIENT = "ABSTAIN_INSUFFICIENT"
    EMERGENCY_HALTED = "EMERGENCY_HALTED"


class ClarificationDimension(str, Enum):
    LOCATION = "LOCATION"
    SENSATION = "SENSATION"
    MODALITY_TIME = "MODALITY_TIME"
    MODALITY_THERMAL = "MODALITY_THERMAL"
    MODALITY_MOTION = "MODALITY_MOTION"
    MODALITY_PRESSURE = "MODALITY_PRESSURE"
    CONCOMITANT = "CONCOMITANT"
    MENTAL_DISPOSITION = "MENTAL_DISPOSITION"
    THIRST_DISPOSITION = "THIRST_DISPOSITION"


class EmergencySentinelTriggeredException(Exception):
    """Raised when an interactive dialogue detects an acute emergency or psychiatric red flag."""
    def __init__(self, message: str, emergency_category: str):
        super().__init__(message)
        self.message = message
        self.emergency_category = emergency_category


class HahnemannianQuery(BaseModel):
    query_id: str = Field(default_factory=lambda: f"QRY-{uuid.uuid4().hex[:6].upper()}")
    dimension: ClarificationDimension
    prompt_english: str
    prompt_bengali: str
    prompt_hindi: str
    suggested_options: List[str]


class DialogueSession(BaseModel):
    session_id: str = Field(default_factory=lambda: f"SES-{uuid.uuid4().hex[:8].upper()}")
    patient_id: str
    state: DialogueState = DialogueState.INITIAL
    language: str = "bn"
    primary_complaint: str
    collected_symptoms: List[NormalizedClinicalSymptom] = Field(default_factory=list)
    pending_queries: List[HahnemannianQuery] = Field(default_factory=list)
    completed_answers: List[Dict[str, str]] = Field(default_factory=list)
    emergency_flag: Optional[str] = None
    can_proceed_to_repertorization: bool = False
    repertory_rubric_count: int = 0


class InteractiveCaseTakingEngine:
    """
    Manages multi-turn Hahnemannian case clarification per Organon Aphorisms 83-104.
    """

    # Non-Leading Standard Clarification Queries per Organon §85-95
    STANDARD_QUERIES: Dict[ClarificationDimension, Dict[str, Any]] = {
        ClarificationDimension.SENSATION: {
            "en": "What kind of pain or sensation do you feel?",
            "bn": "ব্যথার ধরন বা অনুভূতিটি কেমন? (যেমন: দপদপ করে, জ্বালা করে, কামড়ায়, টনটন করে)",
            "hi": "दर्द किस तरह का महसूस होता है? (जैसे: धड़कने वाला, जलन वाला, चुभने वाला, भारीपन)",
            "options": ["throbbing", "burning", "stitching", "bursting", "dull heavy"]
        },
        ClarificationDimension.MODALITY_MOTION: {
            "en": "How does movement, walking, or rest affect your trouble?",
            "bn": "নড়াচড়া করলে বা হাঁটাহাঁটি করলে কষ্ট বাড়ে না কি আরাম লাগে?",
            "hi": "हिलने-डुलने या चलने से तकलीफ बढ़ती है या आराम मिलता है?",
            "options": ["worse from motion", "better from continued motion", "better from complete rest"]
        },
        ClarificationDimension.MODALITY_PRESSURE: {
            "en": "Does pressure or tight binding relieve or aggravate the pain?",
            "bn": "জায়গাটিতে জোরে চেপে ধরলে বা বাঁধলে কি আরাম লাগে না কি ব্যথা বাড়ে?",
            "hi": "दबाने से या कसकर बांधने से आराम मिलता है या दर्द बढ़ जाता है?",
            "options": ["better from hard pressure", "worse from touch or slight pressure", "no change"]
        },
        ClarificationDimension.MODALITY_THERMAL: {
            "en": "Are you generally a chilly or warm-blooded person, and how does heat/cold affect it?",
            "bn": "আপনার কি বেশি ঠান্ডা লাগে না গরম লাগে? ঠান্ডা জলে বা গরমে কষ্ট কেমন থাকে?",
            "hi": "आपको ज्यादा ठंड लगती है या गर्मी? गर्म या ठंडे से तकलीफ में क्या फर्क पड़ता है?",
            "options": ["chilly patient, worse cold", "hot patient, worse heat", "better in open fresh air"]
        },
        ClarificationDimension.THIRST_DISPOSITION: {
            "en": "How is your thirst? Do you crave large gulps or small frequent sips, or feel thirstless?",
            "bn": "আপনার জল পিপাসা কেমন? ঘন ঘন অল্প জল খান, একসাথে বেশি জল খান, না কি পিপাসা একদম নেই?",
            "hi": "आपकी प्यास कैसी है? बार-बार थोड़ा पानी पीते हैं, ज्यादा पानी पीते हैं, या बिल्कुल प्यास नहीं लगती?",
            "options": ["thirstless", "thirst for small sips frequently", "unquenchable thirst for large cold gulps"]
        },
        ClarificationDimension.MODALITY_TIME: {
            "en": "At what specific time of the day or night does your suffering increase?",
            "bn": "দিনের বা রাতের কোন নির্দিষ্ট সময়ে আপনার কষ্ট বেশি বৃদ্ধি পায়?",
            "hi": "दिन या रात के किस खास समय पर आपकी तकलीफ ज्यादा बढ़ जाती है?",
            "options": ["morning aggravation", "afternoon 4pm-8pm", "after midnight 1am-3am", "night aggravation"]
        },
        ClarificationDimension.MENTAL_DISPOSITION: {
            "en": "How is your mood and mental disposition during the illness?",
            "bn": "অসুস্থ অবস্থায় আপনার মনের অবস্থা কেমন থাকে? (যেমন: খুব অস্থিরতা, খিটখিটে মেজাজ, কান্না পায়, ভয় লাগে)",
            "hi": "बीमारी के दौरान आपका स्वभाव और मन कैसा रहता है? (जैसे: बेचैनी, चिड़चिड़ापन, रोना आना, डर)",
            "options": ["extreme restlessness", "weeping tearful mood", "irritable wanting to be alone", "anxiety about health"]
        }
    }

    # Emergency Sentinels (Must halt interactive dialogue immediately per INV-05, INV-14, INV-15)
    EMERGENCY_KEYWORDS = [
        "suicide", "suicidal", "kill myself", "morite chai", "atmohotya", "khudkushi",
        "crushing chest pain", "buker majhe prochondo chaap", "seene me bhari dard",
        "vomiting blood", "roktopat", "khoon ki ulti", "unconscious", "ogyan"
    ]

    @classmethod
    def check_emergency_sentinel(cls, text: str) -> Optional[str]:
        """Scans input text for catastrophic emergency keywords."""
        lower = text.lower()
        for kw in cls.EMERGENCY_KEYWORDS:
            if kw in lower:
                return kw
        return None

    @classmethod
    def initialize_session(
        cls,
        patient_id: str,
        initial_narrative: str,
        language: str = "bn"
    ) -> DialogueSession:
        """
        Initializes an interactive Hahnemannian case-taking session.
        Parses initial narrative and generates targeted clarification queries.
        """
        # 1. Emergency sentinel check
        emergency_kw = cls.check_emergency_sentinel(initial_narrative)
        if emergency_kw:
            session = DialogueSession(
                patient_id=patient_id,
                state=DialogueState.EMERGENCY_HALTED,
                language=language,
                primary_complaint=initial_narrative,
                emergency_flag=f"Emergency red flag detected: '{emergency_kw}'. Outpatient dialogue halted immediately.",
                can_proceed_to_repertorization=False
            )
            return session

        # 2. Extract initial symptoms using the rich vernacular engine
        working_text = initial_narrative.lower()
        collected: List[NormalizedClinicalSymptom] = []

        for phrase, meta in VernacularAudioDecoderEngine.EXPANDED_VERNACULAR_LEXICON.items():
            if phrase in working_text:
                collected.append(NormalizedClinicalSymptom(
                    original_phrase=phrase,
                    standardized_medical_term=meta["term"],
                    category=meta["cat"],
                    repertory_rubric_equivalent=meta["rubric"]
                ))
                working_text = working_text.replace(phrase, " ")

        # 3. Analyze missing LSMC dimensions
        has_location = any(s.category == "LOCATION" for s in collected)
        has_sensation = any(s.category == "SENSATION" for s in collected)
        has_modality = any(s.category == "MODALITY" for s in collected)
        has_general = any(s.category in ("GENERAL", "MENTAL") for s in collected)

        queries: List[HahnemannianQuery] = []

        if not has_sensation:
            queries.append(cls._create_query(ClarificationDimension.SENSATION))
        if not has_modality:
            queries.append(cls._create_query(ClarificationDimension.MODALITY_MOTION))
            queries.append(cls._create_query(ClarificationDimension.MODALITY_PRESSURE))
        if not has_general:
            queries.append(cls._create_query(ClarificationDimension.THIRST_DISPOSITION))
            queries.append(cls._create_query(ClarificationDimension.MODALITY_THERMAL))

        # Check if session is already complete (>= 3 rubrics and has modality)
        is_complete = (len(collected) >= 3 and has_modality)
        state = DialogueState.COMPLETE if is_complete else DialogueState.AWAITING_CLARIFICATION

        return DialogueSession(
            patient_id=patient_id,
            state=state,
            language=language,
            primary_complaint=initial_narrative,
            collected_symptoms=collected,
            pending_queries=queries,
            can_proceed_to_repertorization=is_complete,
            repertory_rubric_count=len(collected)
        )

    @classmethod
    def _create_query(cls, dimension: ClarificationDimension) -> HahnemannianQuery:
        cfg = cls.STANDARD_QUERIES[dimension]
        return HahnemannianQuery(
            dimension=dimension,
            prompt_english=cfg["en"],
            prompt_bengali=cfg["bn"],
            prompt_hindi=cfg["hi"],
            suggested_options=cfg["options"]
        )

    @classmethod
    def submit_clarification_answer(
        cls,
        session: DialogueSession,
        query_id: str,
        patient_answer: str
    ) -> DialogueSession:
        """
        Ingests a patient's clarification answer, parses new symptoms, and updates case completeness.
        """
        # 1. Emergency sentinel check
        emergency_kw = cls.check_emergency_sentinel(patient_answer)
        if emergency_kw:
            session.state = DialogueState.EMERGENCY_HALTED
            session.emergency_flag = f"Emergency red flag detected in answer: '{emergency_kw}'."
            session.can_proceed_to_repertorization = False
            return session

        # 2. Match answer against vernacular lexicon
        lower_ans = patient_answer.lower()
        new_symptoms: List[NormalizedClinicalSymptom] = []

        for phrase, meta in VernacularAudioDecoderEngine.EXPANDED_VERNACULAR_LEXICON.items():
            if phrase in lower_ans:
                sym = NormalizedClinicalSymptom(
                    original_phrase=phrase,
                    standardized_medical_term=meta["term"],
                    category=meta["cat"],
                    repertory_rubric_equivalent=meta["rubric"]
                )
                # Avoid duplicates
                if not any(s.repertory_rubric_equivalent == sym.repertory_rubric_equivalent for s in session.collected_symptoms):
                    new_symptoms.append(sym)

        session.collected_symptoms.extend(new_symptoms)
        session.completed_answers.append({"query_id": query_id, "answer": patient_answer})

        # Remove answered query from pending
        session.pending_queries = [q for q in session.pending_queries if q.query_id != query_id]

        # 3. Re-evaluate completeness per Organon §153 & INV-03
        has_modality = any(s.category == "MODALITY" for s in session.collected_symptoms)
        has_general_or_sensation = any(s.category in ("SENSATION", "GENERAL", "MENTAL") for s in session.collected_symptoms)
        rubric_count = len(session.collected_symptoms)
        session.repertory_rubric_count = rubric_count

        if rubric_count >= 3 and has_modality and has_general_or_sensation:
            session.state = DialogueState.COMPLETE
            session.can_proceed_to_repertorization = True
            session.pending_queries = [] # Clear remaining non-critical queries
        elif len(session.pending_queries) == 0:
            # If all queries exhausted but still < 3 rubrics, flag ABSTAIN_INSUFFICIENT (INV-03)
            session.state = DialogueState.ABSTAIN_INSUFFICIENT
            session.can_proceed_to_repertorization = False
        else:
            session.state = DialogueState.AWAITING_CLARIFICATION
            session.can_proceed_to_repertorization = False

        return session
