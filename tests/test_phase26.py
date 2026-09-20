"""
Unit Tests for Phase 26: Genius Epidemicus & Acute Epidemic Triage Engine.
"""
from app.clinical.genius_epidemicus import GeniusEpidemicusEngine
from app.models.clinical import EpidemicCase

def test_genius_epidemicus_break_bone_dengue_cohort():
    """Verify identification of Eupatorium perfoliatum in a bone-breaking fever outbreak."""
    cases = [
        EpidemicCase(
            case_id=f"EP-00{i}",
            patient_id=f"P-10{i}",
            symptoms=[
                "deep aching in bones as if broken",
                "soreness of eyeballs",
                "chills in back followed by burning fever",
                "thirst for cold water before and during chill"
            ],
            onset_date="2026-09-18"
        )
        for i in range(1, 6)
    ]

    result = GeniusEpidemicusEngine.synthesize_epidemic_cohort(cases)
    assert result.total_cases_analyzed == 5
    assert result.primary_remedy == "Eupatorium perfoliatum"
    assert result.secondary_remedy == "Gelsemium sempervirens"
    assert result.concordance_percentage >= 70.0
    assert any("bones as if broken" in s for s in result.common_symptom_core)

def test_genius_epidemicus_cholera_collapse_cohort():
    """Verify identification of Camphora in sudden collapse cholera epidemic."""
    cases = [
        EpidemicCase(
            case_id=f"CH-00{i}",
            patient_id=f"P-20{i}",
            symptoms=[
                "sudden icy coldness of body with aversion to being covered",
                "rice water copious purging and vomiting",
                "cold sweat on forehead with prostration",
                "asphyctic rapid collapse of vital powers"
            ],
            onset_date="2026-09-19"
        )
        for i in range(1, 4)
    ]

    result = GeniusEpidemicusEngine.synthesize_epidemic_cohort(cases)
    assert result.total_cases_analyzed == 3
    assert result.primary_remedy == "Camphora"
    assert result.secondary_remedy == "Veratrum album"

def test_genius_epidemicus_empty_cohort():
    """Verify handling of empty case cohort."""
    result = GeniusEpidemicusEngine.synthesize_epidemic_cohort([])
    assert result.total_cases_analyzed == 0
    assert "Indeterminate" in result.primary_remedy
    assert result.concordance_percentage == 0.0
