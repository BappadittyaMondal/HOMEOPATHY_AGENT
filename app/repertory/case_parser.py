"""
Hahnemannian Semantic Case Parser (Aphorisms 83-104).
Extracts Location, Sensation, Modality, and Concomitants (LSMC) into structured candidate rubrics.
"""
import re
from typing import List, Tuple
from app.models.case_taking import (
    CompleteSymptom, 
    CandidateRubricMatch, 
    ModalityDetail, 
    ModalityPolarityEnum, 
    SymptomCategoryEnum, 
    VerificationStatusEnum,
    CaseTakingExtractionResult
)

class HahnemannCaseParser:
    """
    Deterministic rule-based clinical semantic extractor.
    Parses unstructured consultation transcripts into Kentian LSMC anatomy.
    """
    
    # Anatomical Locations Mapping
    LOCATIONS = {
        "head": ("HEAD", SymptomCategoryEnum.CHARACTERISTIC_PARTICULAR),
        "forehead": ("HEAD - FOREHEAD", SymptomCategoryEnum.CHARACTERISTIC_PARTICULAR),
        "temple": ("HEAD - TEMPLE", SymptomCategoryEnum.CHARACTERISTIC_PARTICULAR),
        "occiput": ("HEAD - OCCIPUT", SymptomCategoryEnum.CHARACTERISTIC_PARTICULAR),
        "throat": ("THROAT", SymptomCategoryEnum.CHARACTERISTIC_PARTICULAR),
        "stomach": ("STOMACH", SymptomCategoryEnum.CHARACTERISTIC_PARTICULAR),
        "abdomen": ("ABDOMEN", SymptomCategoryEnum.CHARACTERISTIC_PARTICULAR),
        "chest": ("CHEST", SymptomCategoryEnum.CHARACTERISTIC_PARTICULAR),
        "back": ("BACK", SymptomCategoryEnum.CHARACTERISTIC_PARTICULAR),
        "skin": ("SKIN", SymptomCategoryEnum.PHYSICAL_GENERAL),
        "mind": ("MIND", SymptomCategoryEnum.MENTAL_GENERAL),
        "sleep": ("SLEEP", SymptomCategoryEnum.PHYSICAL_GENERAL),
        "joints": ("EXTREMITIES - JOINTS", SymptomCategoryEnum.CHARACTERISTIC_PARTICULAR),
        "knee": ("EXTREMITIES - KNEE", SymptomCategoryEnum.CHARACTERISTIC_PARTICULAR)
    }

    # Sensations Quality Mapping
    SENSATIONS = {
        "throbbing": "PAIN - throbbing",
        "pulsating": "PAIN - pulsating",
        "burning": "PAIN - burning",
        "stitching": "PAIN - stitching",
        "stabbing": "PAIN - stitching",
        "cramping": "PAIN - cramping",
        "tearing": "PAIN - tearing",
        "numbness": "NUMBNESS",
        "itching": "ITCHING",
        "dryness": "DRYNESS",
        "heaviness": "HEAVINESS"
    }

    # Mental Symptoms Lexicon (Kent Chapter: MIND)
    MENTAL_KEYWORDS = {
        "anger": ("MIND - ANGER - ailments after", 5.0),
        "anxiety": ("MIND - ANXIETY - health, about", 4.5),
        "fear": ("MIND - FEAR - dark, of the", 4.5),
        "weeping": ("MIND - WEEPING - tearful mood", 4.0),
        "restless": ("MIND - RESTLESSNESS", 4.5),
        "irritab": ("MIND - IRRITABILITY", 4.0),
        "grief": ("MIND - GRIEF - ailments from", 5.0),
        "jealous": ("MIND - JEALOUSY", 4.5)
    }

    # Modality Triggers and Polarities
    MODALITY_PATTERNS = [
        # Aggravations (<)
        (r"(?:worse|aggravated|increased|intensified|\<)\s+(?:from|by|in|during|at)?\s+([a-zA-Z\s]+?)(?:[,.]|$|better|>)", ModalityPolarityEnum.AGGRAVATION),
        # Ameliorations (>)
        (r"(?:better|relieved|ameliorated|decreased|\>)\s+(?:from|by|in|with|during)?\s+([a-zA-Z\s]+?)(?:[,.]|$|worse|<)", ModalityPolarityEnum.AMELIORATION)
    ]

    @classmethod
    def parse_narrative(
        cls, 
        encounter_id: str, 
        patient_id: str, 
        text: str
    ) -> CaseTakingExtractionResult:
        """
        Parses consultation narrative into structured LSMC symptoms and rubric candidates.
        """
        sentences = re.split(r"[.\n;]+", text)
        complete_symptoms: List[CompleteSymptom] = []
        candidates: List[CandidateRubricMatch] = []

        # 1. Process Mental Symptoms First (Kentian Primacy)
        lower_text = text.lower()
        for keyword, (rubric_path, weight) in cls.MENTAL_KEYWORDS.items():
            if keyword in lower_text:
                # Find matching context sentence
                ctx = next((s.strip() for s in sentences if keyword in s.lower()), keyword)
                sym = CompleteSymptom(
                    raw_source_text=ctx,
                    location="Mind / Affective Emotional Sphere",
                    sensation=f"Emotional disturbance related to {keyword}",
                    category=SymptomCategoryEnum.MENTAL_GENERAL,
                    is_srp=False
                )
                complete_symptoms.append(sym)
                candidates.append(CandidateRubricMatch(
                    symptom_id=sym.symptom_id,
                    source_phrase=ctx,
                    proposed_rubric_path=rubric_path,
                    confidence_score=0.92,
                    hierarchical_weight=weight,
                    status=VerificationStatusEnum.PENDING_REVIEW
                ))

        # 2. Process Physical / Particular Symptoms (Sentence by Sentence)
        for sentence in sentences:
            sentence_clean = sentence.strip()
            if not sentence_clean or len(sentence_clean) < 5:
                continue
            
            s_lower = sentence_clean.lower()
            
            detected_loc = None
            detected_cat = SymptomCategoryEnum.COMMON_PARTICULAR
            for loc_key, (loc_rubric, cat) in cls.LOCATIONS.items():
                if loc_key in s_lower:
                    detected_loc = loc_rubric
                    detected_cat = cat
                    break
            
            detected_sens = None
            for sens_key, sens_rubric in cls.SENSATIONS.items():
                if sens_key in s_lower:
                    detected_sens = sens_rubric
                    break

            # If an anatomical location or sensation is detected
            if detected_loc or detected_sens:
                loc_label = detected_loc or "GENERALITIES"
                sens_label = detected_sens or "PAIN"
                
                # Extract Modalities
                modalities: List[ModalityDetail] = []
                for pattern, polarity in cls.MODALITY_PATTERNS:
                    matches = re.finditer(pattern, s_lower)
                    for match in matches:
                        trigger_text = match.group(1).strip()
                        if len(trigger_text) > 2 and len(trigger_text) < 40:
                            modalities.append(ModalityDetail(
                                trigger=trigger_text,
                                polarity=polarity
                            ))

                # Check for Strange, Rare, and Peculiar (SRP) Paradoxes
                # e.g., chills with thirst, headache relieved by tight pressure or cold application
                is_srp = False
                if "tight" in s_lower and "better" in s_lower:
                    is_srp = True
                elif "thirstless" in s_lower and "fever" in s_lower:
                    is_srp = True

                weight = 4.5 if is_srp else (3.0 if detected_cat == SymptomCategoryEnum.PHYSICAL_GENERAL else 2.5)

                sym = CompleteSymptom(
                    raw_source_text=sentence_clean,
                    location=loc_label,
                    sensation=sens_label,
                    modalities=modalities,
                    category=detected_cat,
                    is_srp=is_srp
                )
                complete_symptoms.append(sym)

                # Formulate Proposed Rubric Path
                if detected_loc and detected_sens:
                    proposed_path = f"{detected_loc} - {detected_sens}"
                elif detected_loc:
                    proposed_path = f"{detected_loc} - PAIN"
                else:
                    proposed_path = f"GENERALITIES - {detected_sens}"

                # Append primary candidate
                candidates.append(CandidateRubricMatch(
                    symptom_id=sym.symptom_id,
                    source_phrase=sentence_clean,
                    proposed_rubric_path=proposed_path,
                    confidence_score=0.88,
                    hierarchical_weight=weight,
                    status=VerificationStatusEnum.PENDING_REVIEW
                ))

                # Append modality candidate if present
                for mod in modalities:
                    mod_prefix = "amel." if mod.polarity == ModalityPolarityEnum.AMELIORATION else "agg."
                    mod_rubric = f"{proposed_path} - {mod.trigger} - {mod_prefix}"
                    candidates.append(CandidateRubricMatch(
                        symptom_id=sym.symptom_id,
                        source_phrase=f"{mod.polarity.value}: {mod.trigger}",
                        proposed_rubric_path=mod_rubric,
                        confidence_score=0.82,
                        hierarchical_weight=weight,
                        status=VerificationStatusEnum.PENDING_REVIEW
                    ))

        return CaseTakingExtractionResult(
            encounter_id=encounter_id,
            patient_id=patient_id,
            complete_symptoms=complete_symptoms,
            candidate_rubrics=candidates,
            total_extracted=len(candidates),
            pending_verification_count=len(candidates)
        )
