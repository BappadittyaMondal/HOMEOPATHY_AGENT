"""
Unit Tests for Phase 24: Nosodes & Sarcodes Safety Protocol.
"""
from app.safety.nosode_protocol import NosodeSafetyProtocol
from app.models.safety import ToxicitySafetyStatus

def test_nosode_acute_fever_contraindication():
    """Verify strict blocking of deep chronic nosodes during active acute fever/crisis."""
    eval_tub = NosodeSafetyProtocol.evaluate_prescription(
        nosode_name="Tuberculinum",
        is_acute_fever_or_crisis=True
    )
    assert eval_tub.status == ToxicitySafetyStatus.HARD_BLOCKED
    assert eval_tub.permitted is False
    assert "STRICT CLINICAL CONTRAINDICATION" in eval_tub.clinical_warning

    eval_psor = NosodeSafetyProtocol.evaluate_prescription(
        nosode_name="Psorinum",
        is_acute_fever_or_crisis=True
    )
    assert eval_psor.permitted is False

def test_pyrogenium_acute_septic_exception():
    """Verify Pyrogenium is permitted during acute septic fever."""
    eval_pyr = NosodeSafetyProtocol.evaluate_prescription(
        nosode_name="Pyrogenium",
        is_acute_fever_or_crisis=True
    )
    assert eval_pyr.status == ToxicitySafetyStatus.APPROVED
    assert eval_pyr.permitted is True

def test_nosode_interval_lockout():
    """Verify minimum 12-week repetition lockout on chronic nosodes."""
    eval_early = NosodeSafetyProtocol.evaluate_prescription(
        nosode_name="Medorrhinum",
        is_acute_fever_or_crisis=False,
        weeks_since_last_dose=4
    )
    assert eval_early.status == ToxicitySafetyStatus.HARD_BLOCKED
    assert eval_early.permitted is False
    assert "POSOLOGY LOCKOUT" in eval_early.clinical_warning

    eval_safe = NosodeSafetyProtocol.evaluate_prescription(
        nosode_name="Medorrhinum",
        is_acute_fever_or_crisis=False,
        weeks_since_last_dose=14
    )
    assert eval_safe.status == ToxicitySafetyStatus.APPROVED
    assert eval_safe.permitted is True

def test_non_nosode_remedy():
    """Verify standard non-nosode remedies are unhindered by the protocol."""
    eval_bell = NosodeSafetyProtocol.evaluate_prescription("Atropa belladonna")
    assert eval_bell.status == ToxicitySafetyStatus.APPROVED
    assert eval_bell.permitted is True
