"""
Unit Tests for Phase 45: HPI Single-Remedy vs Polypharmacy Interception Engine.
"""
from app.dispensary.polypharmacy_guard import PolypharmacyGuardEngine, PolypharmacyInterceptRequest

def test_polypharmacy_cough_syrup_intercept():
    """Verify interception of multi-ingredient commercial cough syrup."""
    req = PolypharmacyInterceptRequest(
        requested_formulation_name="Commercial Cough Syrup Complex",
        constituent_remedies=["Bryonia", "Drosera", "Ipecacuanha", "Belladonna"],
        commercial_mrp_inr=220.0,
        patient_presenting_complaint="Dry painful cough worse least motion"
    )
    report = PolypharmacyGuardEngine.evaluate_formulation(req)
    assert report.is_polypharmacy_detected is True
    assert report.single_simillimum_recommended == "Bryonia alba"
    assert report.recommended_potency == "30C"
    assert report.cost_savings_percentage > 90.0
    assert "Aphorism 273" in report.aphorism_basis

def test_polypharmacy_digestive_tonic_intercept():
    """Verify interception of commercial digestive drops."""
    req = PolypharmacyInterceptRequest(
        requested_formulation_name="Digestive Tonic Mixture Drops",
        constituent_remedies=["Nux vomica", "Carbo veg", "Lycopodium"],
        commercial_mrp_inr=180.0,
        patient_presenting_complaint="Ineffectual urging and morning pyrosis"
    )
    report = PolypharmacyGuardEngine.evaluate_formulation(req)
    assert report.is_polypharmacy_detected is True
    assert report.single_simillimum_recommended == "Strychnos nux-vomica"
    assert report.cost_savings_percentage > 85.0

def test_pure_single_remedy_prescription():
    """Verify compliance when a single HPI remedy is prescribed."""
    req = PolypharmacyInterceptRequest(
        requested_formulation_name="Sulphur",
        constituent_remedies=["Sulphur"],
        commercial_mrp_inr=12.0,
        patient_presenting_complaint="Burning feet at night"
    )
    report = PolypharmacyGuardEngine.evaluate_formulation(req)
    assert report.is_polypharmacy_detected is False
    assert report.single_simillimum_recommended == "Sulphur"
