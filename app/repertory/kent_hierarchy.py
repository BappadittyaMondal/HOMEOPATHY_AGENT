"""
Kentian Symptom Hierarchy Classifier.
Classifies rubrics into Mental Generals (Will/Intellect), Physical Generals (Thermals/Cravings),
and Characteristic vs Common Particulars with mathematical weight vector formulation.
"""
from typing import Tuple
from app.models.hierarchy import KentHierarchyTier, SymptomHierarchyEvaluation

class KentHierarchyClassifier:
    """
    Deterministic hierarchical evaluator adhering to Kent's Lectures on Homeopathic Philosophy (Lecture XXXII).
    Assigns vector weights w_i in [1.0, 5.0] for the composite Simillimum calculation.
    """
    
    # Kent Chapter Categorization
    MENTAL_WILL_KEYWORDS = [
        "fear", "anxiety", "delusion", "suicidal", "rage", "anger", "weeping",
        "religious", "jealousy", "loquacity", "hatred", "despair", "restlessness",
        "grief", "malicious", "haughty", "timidity"
    ]
    
    MENTAL_INTELLECT_KEYWORDS = [
        "memory", "mistakes", "comprehension", "confusion", "intellect",
        "dullness", "concentration", "forgetful", "speech"
    ]

    PHYSICAL_GENERAL_CHAPTERS = [
        "GENERALITIES", "SLEEP", "CHILL", "FEVER", "PERSPIRATION"
    ]

    THERMAL_KEYWORDS = [
        "cold", "heat", "warmth", "weather", "chilly", "sun", "draft", "open air",
        "temperature", "season", "winter", "summer", "bath"
    ]

    CRAVING_AVERSION_KEYWORDS = [
        "desires", "aversion", "thirst", "appetite", "food", "drinks", "cravings",
        "sweet", "salt", "sour", "fat", "spicy", "meat", "milk"
    ]

    @classmethod
    def evaluate_rubric(cls, rubric_path: str) -> SymptomHierarchyEvaluation:
        """
        Computes the Kentian tier and canonical weight for any rubric path.
        e.g., 'MIND - FEAR - dark, of the' -> Tier: MENTAL_WILL_AFFECTIONS, Weight: 5.0
        """
        parts = [p.strip().upper() for p in rubric_path.split("-")]
        chapter = parts[0]
        path_lower = rubric_path.lower()

        # 1. Check Mind Chapter (Mental Generals)
        if chapter == "MIND":
            # Check Will & Affections (highest priority: 5.0)
            if any(k in path_lower for k in cls.MENTAL_WILL_KEYWORDS):
                return SymptomHierarchyEvaluation(
                    rubric_path=rubric_path,
                    tier=KentHierarchyTier.MENTAL_WILL_AFFECTIONS,
                    canonical_weight=5.0,
                    chapter=chapter,
                    justification="Mental General: Pertains to Will, Affections, Emotions, or Moral Core (Kent Lecture XXXII)"
                )
            # Check Intellect & Memory (4.0)
            if any(k in path_lower for k in cls.MENTAL_INTELLECT_KEYWORDS):
                return SymptomHierarchyEvaluation(
                    rubric_path=rubric_path,
                    tier=KentHierarchyTier.MENTAL_INTELLECT,
                    canonical_weight=4.0,
                    chapter=chapter,
                    justification="Mental General: Pertains to Intellect, Memory, or Cognitive Faculty"
                )
            # Default Mind general
            return SymptomHierarchyEvaluation(
                rubric_path=rubric_path,
                tier=KentHierarchyTier.MENTAL_WILL_AFFECTIONS,
                canonical_weight=4.5,
                chapter=chapter,
                justification="Mental General: General emotional or psychological disposition"
            )

        # 2. Check Physical Generals (Thermals, Weather, Sleep, Food Cravings)
        if chapter in cls.PHYSICAL_GENERAL_CHAPTERS or "GENERALITIES" in parts:
            if any(k in path_lower for k in cls.THERMAL_KEYWORDS):
                return SymptomHierarchyEvaluation(
                    rubric_path=rubric_path,
                    tier=KentHierarchyTier.PHYSICAL_GENERAL_THERMAL,
                    canonical_weight=3.5,
                    chapter=chapter,
                    justification="Physical General: Thermal reaction to heat/cold, weather, or atmospheric environment"
                )
            if any(k in path_lower for k in cls.CRAVING_AVERSION_KEYWORDS):
                return SymptomHierarchyEvaluation(
                    rubric_path=rubric_path,
                    tier=KentHierarchyTier.PHYSICAL_GENERAL_CRAVING,
                    canonical_weight=3.0,
                    chapter=chapter,
                    justification="Physical General: Constitutional food craving, aversion, or metabolic appetite"
                )
            return SymptomHierarchyEvaluation(
                rubric_path=rubric_path,
                tier=KentHierarchyTier.PHYSICAL_GENERAL_THERMAL,
                canonical_weight=3.0,
                chapter=chapter,
                justification="Physical General: Whole-body modality or systemic response"
            )

        # Stomach / General Cravings & Aversions
        if chapter == "STOMACH" and any(k in path_lower for k in cls.CRAVING_AVERSION_KEYWORDS):
            return SymptomHierarchyEvaluation(
                rubric_path=rubric_path,
                tier=KentHierarchyTier.PHYSICAL_GENERAL_CRAVING,
                canonical_weight=3.0,
                chapter=chapter,
                justification="Physical General: Constitutional food craving/aversion located in Stomach chapter"
            )

        # 3. Particulars (Organ-specific)
        # Check if it has qualifying modalities (Characteristic Particular: 2.5) vs bare common symptom (1.0)
        has_modality = any(mod in path_lower for mod in ["agg.", "amel.", "after", "during", "before", "lying", "motion", "pressure"])
        if has_modality or len(parts) >= 3:
            return SymptomHierarchyEvaluation(
                rubric_path=rubric_path,
                tier=KentHierarchyTier.CHARACTERISTIC_PARTICULAR,
                canonical_weight=2.5,
                chapter=chapter,
                justification="Characteristic Particular: Complete symptom with specific anatomical location, sensation, and modalities"
            )
        
        # 4. Common Particular (1.0)
        return SymptomHierarchyEvaluation(
            rubric_path=rubric_path,
            tier=KentHierarchyTier.COMMON_PARTICULAR,
            canonical_weight=1.0,
            chapter=chapter,
            justification="Common Particular: Non-discriminative, localized symptom without qualifying modalities"
        )
