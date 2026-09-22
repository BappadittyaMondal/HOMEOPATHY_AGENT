"""
Test Suite for Phase 66: Acute-on-Chronic Case Segregation State Machine (INV-18).
"""
import pytest
from app.clinical.acute_intercurrent import (
    AcuteIntercurrentEngine,
    ChronicCaseState,
    AcuteCaseState,
    RubricCategory,
    RubricItem,
    AcuteChronicContaminationException,
)


def test_register_chronic_case_success():
    engine = AcuteIntercurrentEngine()
    rubrics = [
        RubricItem(rubric_id="MIND_FEAR_OF_DEATH", description="Fear of death with restlessness", category=RubricCategory.CHRONIC_CONSTITUTIONAL),
        RubricItem(rubric_id="GENERALS_COLD_AGGRAVATES", description="Aggravation from cold air/drafts", category=RubricCategory.CHRONIC_CONSTITUTIONAL),
        RubricItem(rubric_id="STOMACH_THIRST_SIP_OFTEN", description="Thirst for small quantities often", category=RubricCategory.CHRONIC_CONSTITUTIONAL),
    ]
    record = engine.register_chronic_case("PAT_CHRONIC_001", rubrics, active_remedy="Arsenicum album", potency="200C")
    assert record.state == ChronicCaseState.ACTIVE
    assert record.active_remedy == "Arsenicum album"
    assert len(record.constitutional_rubrics) == 3


def test_inv18_chronic_contamination_rejected():
    """INV-18: Rejecting acute intercurrent / trauma rubrics in chronic totality."""
    engine = AcuteIntercurrentEngine()
    mixed_rubrics = [
        RubricItem(rubric_id="MIND_FEAR_OF_DEATH", description="Fear of death", category=RubricCategory.CHRONIC_CONSTITUTIONAL),
        RubricItem(rubric_id="TRAUMA_CONTUSION_BLUNT", description="Blunt eye trauma from cricket ball", category=RubricCategory.ACUTE_TRAUMA),
    ]
    with pytest.raises(AcuteChronicContaminationException) as exc_info:
        engine.register_chronic_case("PAT_CHRONIC_002", mixed_rubrics)
    assert "INV-18 VIOLATION" in str(exc_info.value)
    assert "TRAUMA_CONTUSION_BLUNT" in exc_info.value.contaminated_rubrics[0]


def test_inv18_acute_contamination_rejected():
    """INV-18: Rejecting chronic constitutional rubrics in acute intercurrent totality."""
    engine = AcuteIntercurrentEngine()
    mixed_acute = [
        RubricItem(rubric_id="INJURY_SPRAIN_ANKLE", description="Sprain of ankle from stumble", category=RubricCategory.ACUTE_TRAUMA),
        RubricItem(rubric_id="MIND_AILMENTS_FROM_GRIEF", description="Chronic grief 5 years ago", category=RubricCategory.CHRONIC_CONSTITUTIONAL),
    ]
    with pytest.raises(AcuteChronicContaminationException) as exc_info:
        engine.open_acute_intercurrent("PAT_ACUTE_001", "Acute ankle sprain", mixed_acute)
    assert "INV-18 VIOLATION" in str(exc_info.value)
    assert "MIND_AILMENTS_FROM_GRIEF" in exc_info.value.contaminated_rubrics[0]


def test_acute_flare_shelves_chronic_case():
    """Opening acute intercurrent must automatically shelve the chronic case."""
    engine = AcuteIntercurrentEngine()
    chronic_rubrics = [
        RubricItem(rubric_id="SKIN_KERATOSIS_THICK", description="Thick arsenical keratosis", category=RubricCategory.CHRONIC_CONSTITUTIONAL),
        RubricItem(rubric_id="GENERALS_WARMTH_AMEL", description="Warmth ameliorates", category=RubricCategory.CHRONIC_CONSTITUTIONAL),
        RubricItem(rubric_id="MIND_ANXIETY_MIDNIGHT", description="Anxiety after midnight", category=RubricCategory.CHRONIC_CONSTITUTIONAL),
    ]
    engine.register_chronic_case("PAT_003", chronic_rubrics, active_remedy="Arsenicum album", potency="1M")

    status_before = engine.get_patient_case_status("PAT_003")
    assert status_before["chronic_state"] == "ACTIVE"
    assert status_before["has_active_acute"] is False

    acute_rubrics = [
        RubricItem(rubric_id="FEVER_HIGH_SUDDEN", description="Sudden high fever after exposure to dry cold wind", category=RubricCategory.ACUTE_INTERCURRENT),
        RubricItem(rubric_id="MIND_RESTLESS_AGONY", description="Intense agony and restlessness", category=RubricCategory.ACUTE_INTERCURRENT),
    ]
    acute_rec, chronic_rec = engine.open_acute_intercurrent(
        "PAT_003",
        "Sudden acute febrile onset post dry cold wind",
        acute_rubrics,
        acute_remedy="Aconitum napellus",
        acute_potency="30C"
    )

    assert acute_rec.state == AcuteCaseState.ACTIVE
    assert acute_rec.acute_remedy == "Aconitum napellus"
    assert chronic_rec.state == ChronicCaseState.SHELVED
    assert "Acute intercurrent onset" in chronic_rec.shelve_reason

    status_after = engine.get_patient_case_status("PAT_003")
    assert status_after["chronic_state"] == "SHELVED"
    assert status_after["has_active_acute"] is True


def test_acute_resolution_and_chronic_resumption():
    """Resolving acute case transitions chronic case to RE_EVALUATION_PENDING, then can be resumed."""
    engine = AcuteIntercurrentEngine()
    chronic_rubrics = [
        RubricItem(rubric_id="SKIN_ERUPTIONS_PSORA", description="Chronic dry eczema", category=RubricCategory.CHRONIC_CONSTITUTIONAL),
        RubricItem(rubric_id="GENERALS_NIGHT_AGG", description="Night aggravation", category=RubricCategory.CHRONIC_CONSTITUTIONAL),
        RubricItem(rubric_id="MIND_SADNESS", description="Melancholic disposition", category=RubricCategory.CHRONIC_CONSTITUTIONAL),
    ]
    engine.register_chronic_case("PAT_004", chronic_rubrics, active_remedy="Sulphur", potency="200C")

    # Acute flare
    acute_rubrics = [
        RubricItem(rubric_id="STOMACH_VOMITING_FOOD", description="Acute food poisoning gastroenteritis", category=RubricCategory.ACUTE_INTERCURRENT),
    ]
    engine.open_acute_intercurrent("PAT_004", "Acute gastroenteritis", acute_rubrics, acute_remedy="Arsenicum album", acute_potency="30C")

    # Cannot resume while acute is active
    with pytest.raises(ValueError) as exc:
        engine.resume_chronic_case("PAT_004")
    assert "while acute intercurrent" in str(exc.value)

    # Resolve acute
    acute_rec, chronic_rec = engine.resolve_acute_intercurrent("PAT_004", "Gastroenteritis fully subsided after 3 doses of Arsenicum 30C.")
    assert acute_rec.state == AcuteCaseState.RESOLVED
    assert chronic_rec.state == ChronicCaseState.RE_EVALUATION_PENDING

    # Now resume chronic
    resumed_chronic = engine.resume_chronic_case("PAT_004", active_remedy="Sulphur", potency="200C")
    assert resumed_chronic.state == ChronicCaseState.ACTIVE
    assert resumed_chronic.last_resumed_at is not None


def test_multiple_acutes_tracked_in_history():
    """Verify history of multiple resolved acute episodes for same patient."""
    engine = AcuteIntercurrentEngine()
    chronic_rubrics = [
        RubricItem(rubric_id="RUBRIC_A", description="A", category=RubricCategory.CHRONIC_CONSTITUTIONAL),
        RubricItem(rubric_id="RUBRIC_B", description="B", category=RubricCategory.CHRONIC_CONSTITUTIONAL),
        RubricItem(rubric_id="RUBRIC_C", description="C", category=RubricCategory.CHRONIC_CONSTITUTIONAL),
    ]
    engine.register_chronic_case("PAT_005", chronic_rubrics)

    # Episode 1
    engine.open_acute_intercurrent("PAT_005", "Acute flu", [RubricItem(rubric_id="FLU", description="Flu", category=RubricCategory.EPIDEMIC)])
    engine.resolve_acute_intercurrent("PAT_005", "Flu resolved")
    engine.resume_chronic_case("PAT_005")

    # Episode 2
    engine.open_acute_intercurrent("PAT_005", "Trauma eye", [RubricItem(rubric_id="TRAUMA", description="Trauma", category=RubricCategory.ACUTE_TRAUMA)])
    engine.resolve_acute_intercurrent("PAT_005", "Trauma healed")
    engine.resume_chronic_case("PAT_005")

    status = engine.get_patient_case_status("PAT_005")
    assert status["total_historical_acutes"] == 2
    assert status["has_active_acute"] is False
    assert status["chronic_state"] == "ACTIVE"
