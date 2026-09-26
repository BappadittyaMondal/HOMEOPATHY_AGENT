"""
Multilingual Audio Narration Engine (Phase 84).

Generates plain-language audio narration scripts across English, Hindi, and Bengali
for zero-GPU, zero-server-RAM client-side text-to-speech synthesis using
the W3C Web Speech API (window.speechSynthesis).
Includes accessible browser playback controller scripts with default-muted state.
"""
from typing import Dict, Optional, Tuple

from app.reporting.contracts import NarrationLanguage, AudioNarrationScript, ReportAudience
from app.clinical.master_verifier import MasterHardenedClinicalResult, MasterClinicalWorkflowResult


class MultilingualAudioNarrator:
    """
    Client-side speech synthesis orchestrator and multilingual script generator.
    Translates verified clinical results into culturally calibrated, plain-language audio narrations.
    """

    # Approximate words per minute for speech duration estimation
    WORDS_PER_MINUTE = 135

    @classmethod
    def generate_narration_script(
        cls,
        hardened_result: MasterHardenedClinicalResult,
        language: NarrationLanguage = NarrationLanguage.EN_IN,
        audience: ReportAudience = ReportAudience.PATIENT
    ) -> AudioNarrationScript:
        """
        Generates an AudioNarrationScript tailored to the requested language and audience.
        """
        remedy_name = hardened_result.canonical_remedy_name or "consultation review"
        ehr = hardened_result.ehr_encounter
        draft = hardened_result.approved_draft
        potency = draft.potency if draft else ""
        dosage = draft.dosage_instructions if draft else ""
        vitality = ehr.vitality_score if ehr else 7.0
        dominant_miasm = ehr.dominant_miasm if ehr else "PSORA"
        is_emergency = hardened_result.is_emergency_lockout

        if language == NarrationLanguage.HI_IN:
            sections, full_text = cls._build_hindi_script(
                hardened_result.patient_id, remedy_name, potency, dosage, vitality, is_emergency
            )
        elif language == NarrationLanguage.BN_IN:
            sections, full_text = cls._build_bengali_script(
                hardened_result.patient_id, remedy_name, potency, dosage, vitality, is_emergency
            )
        else:
            sections, full_text = cls._build_english_script(
                hardened_result.patient_id, remedy_name, potency, dosage, vitality, dominant_miasm, is_emergency
            )

        word_count = len(full_text.split())
        estimated_duration = round((word_count / cls.WORDS_PER_MINUTE) * 60.0, 1)

        return AudioNarrationScript(
            language=language,
            script_text=full_text,
            estimated_duration_seconds=estimated_duration,
            sections=sections
        )

    @classmethod
    def _build_english_script(
        cls,
        patient_id: str,
        remedy: str,
        potency: str,
        dosage: str,
        vitality: float,
        miasm: str,
        is_emergency: bool
    ) -> Tuple[Dict[str, str], str]:
        """Generates English clinical care narration."""
        if is_emergency:
            sections = {
                "alert": "Emergency medical alert! Your consultation indicates critical physiological warning signs.",
                "action": "Homeopathic prescribing is suspended under statutory hospital safety rules.",
                "transfer": "Please proceed immediately to the nearest tertiary emergency department or call ambulance services."
            }
            full_text = " ".join(sections.values())
            return sections, full_text

        vitality_tone = "robust" if vitality >= 7.0 else ("moderate" if vitality >= 4.0 else "delicate")

        sections = {
            "summary": f"Welcome to your clinical care summary for patient {patient_id}.",
            "prescription": f"Your verified homeopathic simillimum is {remedy}, potency {potency}.",
            "posology": f"Directions for use: {dosage}." if dosage else f"Take your remedy as advised by your physician.",
            "vitality": f"Your vital reserve tone is assessed as {vitality_tone}, indicating good recuperative capacity.",
            "hahnemannian_rules": (
                "For best efficacy, take the remedy in a clean mouth. "
                "Avoid eating, drinking coffee, or using mint 20 minutes before and after taking the medicine. "
                "Store the medicine away from direct sunlight, camphor, and strong perfumes."
            ),
            "red_flags": (
                "If you experience sudden severe chest pain, extreme breathlessness, or loss of consciousness, "
                "seek emergency western medical care immediately."
            ),
            "follow_up": "Your next follow-up consultation is scheduled in two to three weeks. Thank you."
        }
        full_text = " ".join(sections.values())
        return sections, full_text

    @classmethod
    def _build_hindi_script(
        cls,
        patient_id: str,
        remedy: str,
        potency: str,
        dosage: str,
        vitality: float,
        is_emergency: bool
    ) -> Tuple[Dict[str, str], str]:
        """Generates Hindi clinical care narration (Devanagari script for W3C hi-IN)."""
        if is_emergency:
            sections = {
                "alert": "आपातकालीन चिकित्सा चेतावनी! आपके लक्षणों में गंभीर आपातकालीन संकेत पाए गए हैं।",
                "action": "अस्पताल के सुरक्षा नियमों के तहत होम्योपैथिक दवा अभी रोक दी गई है।",
                "transfer": "कृपया तुरंत नजदीकी आपातकालीन अस्पताल जाएं या एम्बुलेंस को कॉल करें।"
            }
            full_text = " ".join(sections.values())
            return sections, full_text

        sections = {
            "summary": f"मरीज आईडी {patient_id} के लिए होम्योपैथिक परामर्श सारांश।",
            "prescription": f"आपके लिए निर्धारित दवा {remedy} है, पोटेन्सी {potency}।",
            "posology": f"दवा लेने का तरीका: {dosage}।" if dosage else "दवा डॉक्टर के निर्देशानुसार लें।",
            "vitality": f"आपकी जीवन शक्ति का स्तर {vitality:.1f} आंका गया है, जो अनुकूल स्वास्थ्य सुधार को दर्शाता है।",
            "hahnemannian_rules": (
                "दवा हमेशा साफ मुंह में लें। "
                "दवा लेने से बीस मिनट पहले और बाद में कुछ भी न खाएं-पिएं, विशेषकर कॉफी और तेज गंध से बचें। "
                "दवा को धूप, कपूर और मोबाइल फोन से दूर रखें।"
            ),
            "red_flags": "यदि सीने में तेज दर्द, सांस लेने में गंभीर कठिनाई या बेहोशी हो, तो तुरंत नजदीकी अस्पताल के आपातकालीन विभाग में जाएं।",
            "follow_up": "अगला फॉलो-अप परामर्श दो से तीन सप्ताह में निर्धारित है। धन्यवाद।"
        }
        full_text = " ".join(sections.values())
        return sections, full_text

    @classmethod
    def _build_bengali_script(
        cls,
        patient_id: str,
        remedy: str,
        potency: str,
        dosage: str,
        vitality: float,
        is_emergency: bool
    ) -> Tuple[Dict[str, str], str]:
        """Generates Bengali clinical care narration (Bengali script for W3C bn-IN)."""
        if is_emergency:
            sections = {
                "alert": "জরুরি চিকিৎসা সতর্কতা! আপনার উপসর্গে সংকটজনক শারীরিক লক্ষণ ধরা পড়েছে।",
                "action": "হাসপাতালের নিরাপত্তা বিধি অনুযায়ী হোমিওপ্যাথিক ওষুধ স্থগিত করা হলো।",
                "transfer": "অনুগ্রহ করে অবিলম্বে নিকটবর্তী জরুরি হাসপাতালে যান অথবা অ্যাম্বুলেন্স ডাকুন।"
            }
            full_text = " ".join(sections.values())
            return sections, full_text

        sections = {
            "summary": f"রোগী আইডি {patient_id}-এর ক্লিনিকাল পরামর্শ সারাংশ।",
            "prescription": f"আপনার জন্য নির্বাচিত হোমিওপ্যাথিক ওষুধ হলো {remedy}, পোটেন্সি {potency}।",
            "posology": f"ওষুধ সেবনের নিয়ম: {dosage}।" if dosage else "চিকিৎসকের নির্দেশ অনুযায়ী ওষুধ সেবন করুন।",
            "vitality": f"আপনার জীবনীশক্তি স্কোর {vitality:.1f}, যা দ্রুত আরোগ্যের অনুকূল।",
            "hahnemannian_rules": (
                "ওষুধ পরিষ্কার মুখে সেবন করুন। "
                "ওষুধ খাওয়ার ২০ মিনিট আগে ও পরে খাবার, চা-কফি বা ধূমপান পরিহার করুন। "
                "ওষুধটি সরাসরি রোদ, কর্পূর এবং তীব্র সুগন্ধ থেকে দূরে শীতল স্থানে রাখুন।"
            ),
            "red_flags": "যদি তীব্র বুকে ব্যথা, মারাত্মক শ্বাসকষ্ট বা অচেতন হওয়ার মতো উপসর্গ দেখা দেয়, অবিলম্বে নিকটস্থ জরুরি বিভাগে যোগাযোগ করুন।",
            "follow_up": "পরবর্তী পরামর্শ দুই থেকে তিন সপ্তাহের মধ্যে গ্রহণ করবেন। ধন্যবাদ।"
        }
        full_text = " ".join(sections.values())
        return sections, full_text

    @classmethod
    def generate_browser_controller_js(
        cls,
        scripts_by_lang: Dict[NarrationLanguage, AudioNarrationScript]
    ) -> str:
        """
        Renders complete, client-side W3C Web Speech API JavaScript controller
        embedding pre-rendered phonetic scripts for instant playback.
        """
        js_scripts_dict = {}
        for lang, script in scripts_by_lang.items():
            safe_text = script.script_text.replace('"', '\\"').replace("\n", " ")
            js_scripts_dict[lang.value] = safe_text

        js = f"""// Auto-generated Web Speech API Narration Controller
(function() {{
    const NARRATION_SCRIPTS = {js_scripts_dict};
    let synth = window.speechSynthesis;
    let currentUtterance = null;

    window.HomeopathyAudio = {{
        play: function(lang) {{
            if (!synth) {{
                console.warn("W3C Web Speech API not supported.");
                return;
            }}
            synth.cancel();
            const text = NARRATION_SCRIPTS[lang] || NARRATION_SCRIPTS['en-IN'] || '';
            currentUtterance = new SpeechSynthesisUtterance(text);
            currentUtterance.lang = lang;
            currentUtterance.rate = 0.95;
            synth.speak(currentUtterance);
        }},
        pause: function() {{
            if (synth && synth.speaking) synth.pause();
        }},
        resume: function() {{
            if (synth && synth.paused) synth.resume();
        }},
        stop: function() {{
            if (synth) synth.cancel();
        }}
    }};
}})();"""
        return js
