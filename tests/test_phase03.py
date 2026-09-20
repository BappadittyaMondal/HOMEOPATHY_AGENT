"""
Unit Tests for Phase 03: Kentian Symptom Hierarchy Classifier.
"""
from app.repertory.kent_hierarchy import KentHierarchyClassifier
from app.models.hierarchy import KentHierarchyTier

def test_kent_hierarchy_mental_generals():
    """Verify Mental Generals (Will vs Intellect) receive 5.0 and 4.0 weights respectively."""
    # Will / Emotion / Fear
    eval_fear = KentHierarchyClassifier.evaluate_rubric("MIND - FEAR - dark, of the")
    assert eval_fear.tier == KentHierarchyTier.MENTAL_WILL_AFFECTIONS
    assert eval_fear.canonical_weight == 5.0
    assert eval_fear.chapter == "MIND"

    eval_rage = KentHierarchyClassifier.evaluate_rubric("MIND - ANGER - violent")
    assert eval_rage.tier == KentHierarchyTier.MENTAL_WILL_AFFECTIONS
    assert eval_rage.canonical_weight == 5.0

    # Intellect / Memory
    eval_mem = KentHierarchyClassifier.evaluate_rubric("MIND - MEMORY - weakness of memory")
    assert eval_mem.tier == KentHierarchyTier.MENTAL_INTELLECT
    assert eval_mem.canonical_weight == 4.0

def test_kent_hierarchy_physical_generals():
    """Verify Physical Generals (Thermals, Weather, Food Cravings) receive 3.0-3.5 weights."""
    eval_thermal = KentHierarchyClassifier.evaluate_rubric("GENERALITIES - COLD - air - agg.")
    assert eval_thermal.tier == KentHierarchyTier.PHYSICAL_GENERAL_THERMAL
    assert eval_thermal.canonical_weight == 3.5

    eval_craving = KentHierarchyClassifier.evaluate_rubric("STOMACH - APPETITE - cravings - salt")
    assert eval_craving.tier == KentHierarchyTier.PHYSICAL_GENERAL_CRAVING
    assert eval_craving.canonical_weight == 3.0

def test_kent_hierarchy_characteristic_vs_common_particulars():
    """Verify complete symptoms receive 2.5 while bare common symptoms receive 1.0."""
    # Characteristic Particular (Complete with modality)
    eval_char = KentHierarchyClassifier.evaluate_rubric("HEAD - PAIN - forehead - pressure - amel.")
    assert eval_char.tier == KentHierarchyTier.CHARACTERISTIC_PARTICULAR
    assert eval_char.canonical_weight == 2.5

    # Common Particular (Unqualified)
    eval_common = KentHierarchyClassifier.evaluate_rubric("HEAD - PAIN")
    assert eval_common.tier == KentHierarchyTier.COMMON_PARTICULAR
    assert eval_common.canonical_weight == 1.0
