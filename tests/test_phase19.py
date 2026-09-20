"""
Unit Tests for Phase 19: Statutory Toxicology Limits & Alkaloid Safety Firewall.
"""
from app.safety.toxicology_caps import ToxicologySafetyFirewall
from app.models.safety import ToxicitySafetyStatus

def test_hard_block_sub_threshold_potency():
    """Verify statutory blocking of dilutions below HPI safety thresholds."""
    # Arsenicum album banned below 6X
    res_ars_3x = ToxicologySafetyFirewall.evaluate_prescription("Arsenicum album", "3X")
    assert res_ars_3x.status == ToxicitySafetyStatus.HARD_BLOCKED
    assert "STATUTORY SAFETY VIOLATION" in res_ars_3x.reason

    # Lachesis muta snake venom banned below 6C (dilution order 12)
    res_lach_q = ToxicologySafetyFirewall.evaluate_prescription("Lachesis muta", "Q")
    assert res_lach_q.status == ToxicitySafetyStatus.HARD_BLOCKED

    res_lach_3c = ToxicologySafetyFirewall.evaluate_prescription("Lachesis muta", "3C")
    assert res_lach_3c.status == ToxicitySafetyStatus.HARD_BLOCKED

    # Aconitum napellus banned below 3X
    res_acon_1x = ToxicologySafetyFirewall.evaluate_prescription("Aconitum napellus", "1X")
    assert res_acon_1x.status == ToxicitySafetyStatus.HARD_BLOCKED

def test_approved_compliant_high_potencies():
    """Verify approval of toxic remedies prepared in compliant, safe dilutions."""
    # Arsenicum album at 30C (well above 6X)
    res_ars_30c = ToxicologySafetyFirewall.evaluate_prescription("Arsenicum album", "30C")
    assert res_ars_30c.status == ToxicitySafetyStatus.APPROVED
    assert "conforms to statutory dilution" in res_ars_30c.reason

    # Lachesis at 200C
    res_lach_200c = ToxicologySafetyFirewall.evaluate_prescription("Lachesis muta", "200C")
    assert res_lach_200c.status == ToxicitySafetyStatus.APPROVED

    # Nux vomica at 6X (allowed: minimum is 2X)
    res_nux_6x = ToxicologySafetyFirewall.evaluate_prescription("Strychnos nux-vomica", "6X")
    assert res_nux_6x.status == ToxicitySafetyStatus.APPROVED

def test_safe_non_toxic_remedies():
    """Verify remedies not under Schedule E(1) statutory toxicity rules pass cleanly."""
    res_calc = ToxicologySafetyFirewall.evaluate_prescription("Calcarea carbonica", "30C")
    assert res_calc.status == ToxicitySafetyStatus.APPROVED
    assert res_calc.rule_matched is None

def test_potency_scaling_parser():
    """Verify robust parsing of diverse potency strings."""
    assert ToxicologySafetyFirewall._potency_to_decimal_dilution_factor("Q") == 0.0
    assert ToxicologySafetyFirewall._potency_to_decimal_dilution_factor("MT") == 0.0
    assert ToxicologySafetyFirewall._potency_to_decimal_dilution_factor("3X") == 3.0
    assert ToxicologySafetyFirewall._potency_to_decimal_dilution_factor("6X") == 6.0
    assert ToxicologySafetyFirewall._potency_to_decimal_dilution_factor("6C") == 12.0
    assert ToxicologySafetyFirewall._potency_to_decimal_dilution_factor("30C") == 60.0
    assert ToxicologySafetyFirewall._potency_to_decimal_dilution_factor("200C") == 400.0
    assert ToxicologySafetyFirewall._potency_to_decimal_dilution_factor("1M") == 2000.0
    assert ToxicologySafetyFirewall._potency_to_decimal_dilution_factor("LM 0/1") == 50000.0
