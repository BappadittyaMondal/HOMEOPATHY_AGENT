"""
Unit Tests for Phase 38: Iatrogenic Drug Suppression & Tautopathic Cleansing Engine.
"""
from app.clinical.tautopathy import TautopathyEngine, TautopathicCleansingRequest

def test_tautopathy_corticosteroid_chronic_cleansing():
    """Verify Thuja and Cortisone ascending protocol for chronic steroid suppression."""
    req = TautopathicCleansingRequest(
        suppressing_drug_class="CORTICOSTEROID",
        drug_name="Prednisolone",
        duration_months=24,
        presenting_suppression_symptoms=["adrenal suppression", "cushingoid moon face", "suppressed eczema"]
    )
    protocol = TautopathyEngine.generate_cleansing_protocol(req)
    assert protocol.indicated_constitutional_clearing_remedy == "Thuja occidentalis"
    assert protocol.tautopathic_remedy == "Cortisone"
    assert protocol.potency_sequence == ["30C", "200C", "1M"]
    assert "adrenal suppression" in protocol.detox_instructions.lower()

def test_tautopathy_nsaid_clearing():
    """Verify Nux vomica and tautopathic aspirin for chronic analgesic abuse."""
    req = TautopathicCleansingRequest(
        suppressing_drug_class="NSAID",
        drug_name="Ibuprofen",
        duration_months=6,
        presenting_suppression_symptoms=["gastritis", "melena"]
    )
    protocol = TautopathyEngine.generate_cleansing_protocol(req)
    assert protocol.indicated_constitutional_clearing_remedy == "Strychnos nux-vomica"
    assert protocol.tautopathic_remedy == "Acidum acetylsalicylicum"
    assert protocol.potency_sequence == ["30C", "200C"]

def test_tautopathy_vaccinosis():
    """Verify Thuja and Vaccininum for post-vaccinal dyscrasia."""
    req = TautopathicCleansingRequest(
        suppressing_drug_class="VACCINE",
        drug_name="MMR",
        duration_months=18,
        presenting_suppression_symptoms=["post-vaccinal asthma", "loss of speech"]
    )
    protocol = TautopathyEngine.generate_cleansing_protocol(req)
    assert protocol.indicated_constitutional_clearing_remedy == "Thuja occidentalis"
    assert protocol.tautopathic_remedy == "Vaccininum"
