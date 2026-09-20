"""
Unit Tests for Phase 30: Mental Health & Neuro-Psychiatric Engine.
"""
from app.clinical.mental_health import MentalHealthEngine
from app.models.clinical import PsychiatricEtiologyProfile

def test_mental_health_aurum_suicidal_melancholy():
    """Verify Aurum metallicum in profound suicidal depression with worthlessness."""
    profile = PsychiatricEtiologyProfile(
        primary_etiology="DISAPPOINTMENT",
        mood_state="DEEP_MELANCHOLY_SUICIDAL",
        somatic_concomitants=["thinks has neglected duty", "longs for death", "relieved by religious music"]
    )
    rx = MentalHealthEngine.evaluate_psychiatric_case(profile)
    assert rx.indicated_remedy == "Aurum metallicum"
    assert rx.recommended_potency == "1M"
    assert "psychotic depression" in rx.clinical_guidance.lower()

def test_mental_health_ignatia_acute_grief():
    """Verify Ignatia in acute silent grief with involuntary sighing."""
    profile = PsychiatricEtiologyProfile(
        primary_etiology="SILENT_GRIEF",
        mood_state="HYSTERICAL_PARADOX",
        somatic_concomitants=["frequent deep involuntary sighing", "sensation of globus hystericus in throat"]
    )
    rx = MentalHealthEngine.evaluate_psychiatric_case(profile)
    assert rx.indicated_remedy == "Ignatia amara"
    assert rx.recommended_potency == "200C"
    assert "bereavement" in rx.clinical_guidance.lower()

def test_mental_health_natrum_mur_consolation_aggravates():
    """Verify Natrum mur in chronic grief where sympathy enrages."""
    profile = PsychiatricEtiologyProfile(
        primary_etiology="SILENT_GRIEF",
        mood_state="WEEPING_CONSOLATION_AGGRAVATES",
        somatic_concomitants=["dwelling on past hurts", "craving for large amounts of salt"]
    )
    rx = MentalHealthEngine.evaluate_psychiatric_case(profile)
    assert rx.indicated_remedy == "Natrum muriaticum"
    assert rx.recommended_potency == "200C"

def test_mental_health_staphysagria_suppressed_anger():
    """Verify Staphysagria in suppressed indignation and mortification."""
    profile = PsychiatricEtiologyProfile(
        primary_etiology="MORTIFICATION_SUPPRESSED_ANGER",
        mood_state="WEEPING_CONSOLATION_AGGRAVATES",
        somatic_concomitants=["trembling from anger", "throws things when pushed too far"]
    )
    rx = MentalHealthEngine.evaluate_psychiatric_case(profile)
    assert rx.indicated_remedy == "Staphysagria"
    assert rx.recommended_potency == "200C"

def test_mental_health_aconite_fright_fear_death():
    """Verify Aconite in sudden terrifying fright with prediction of death."""
    profile = PsychiatricEtiologyProfile(
        primary_etiology="FRIGHT_SUDDEN_TERROR",
        mood_state="HYSTERICAL_PARADOX",
        somatic_concomitants=["intense fear of death", "predicts exact day and hour"]
    )
    rx = MentalHealthEngine.evaluate_psychiatric_case(profile)
    assert rx.indicated_remedy == "Aconitum napellus"
    assert rx.recommended_potency == "200C"
