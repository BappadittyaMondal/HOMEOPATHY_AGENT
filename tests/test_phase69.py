"""
Test Suite for Phase 69: Static Geospatial Indian District Groundwater Risk Correlator (Geo-Epi).
"""
import pytest
from app.clinical.geo_aquifer_registry import (
    GeoAquiferRegistry,
    ContaminantType,
    GeoRiskLevel,
)


def test_lookup_bengal_arsenic_pincode():
    """PIN code 743xxx (North/South 24 Parganas) maps to hyper-endemic arsenic aquifer."""
    registry = GeoAquiferRegistry()
    profile = registry.lookup_by_pincode("743262")
    assert profile.state == "West Bengal"
    assert profile.risk_level == GeoRiskLevel.HYPER_ENDEMIC
    assert profile.primary_contaminant == ContaminantType.ARSENIC
    assert "Arsenic" in profile.cgwb_reference
    assert "Arsenicum album" in profile.suggested_constitutional_remedies
    assert any("Urine Arsenic" in s for s in profile.mandatory_screenings)


def test_lookup_nalgonda_fluoride_pincode():
    """PIN code 508xxx (Nalgonda) maps to hyper-endemic fluoride aquifer."""
    registry = GeoAquiferRegistry()
    profile = registry.lookup_by_pincode("508001")
    assert profile.state == "Telangana"
    assert profile.risk_level == GeoRiskLevel.HYPER_ENDEMIC
    assert profile.primary_contaminant == ContaminantType.FLUORIDE
    assert "Fluoricum acidum" in profile.suggested_constitutional_remedies
    assert any("Fluoride" in s for s in profile.mandatory_screenings)


def test_lookup_baseline_pincode():
    """Non-endemic PIN code defaults to low baseline."""
    registry = GeoAquiferRegistry()
    profile = registry.lookup_by_pincode("110001")  # New Delhi
    assert profile.risk_level == GeoRiskLevel.LOW_BASELINE
    assert profile.primary_contaminant == ContaminantType.NONE_DETECTED
    assert len(profile.mandatory_screenings) == 0


def test_lookup_by_district():
    """Fuzzy district matching for Nadia, West Bengal."""
    registry = GeoAquiferRegistry()
    profile = registry.lookup_by_district("Nadia District")
    assert profile.state == "West Bengal"
    assert profile.risk_level == GeoRiskLevel.HYPER_ENDEMIC
    assert profile.primary_contaminant == ContaminantType.ARSENIC


def test_patient_exposure_evaluation_longterm():
    """Patient with 15 years groundwater exposure in 743xxx has mandatory toxicology screening mandated."""
    registry = GeoAquiferRegistry()
    eval_res = registry.evaluate_exposure(
        patient_id="PAT_BENGAL_001",
        pin_code="743126",
        years_exposed=15.0,
    )
    assert eval_res.toxicology_screening_mandated is True
    assert "CRITICAL EPIDEMIOLOGICAL ALERT" in eval_res.clinical_advisory
    assert "Aphorism §4" in eval_res.profile.obstacle_to_cure_warning
    assert "INV-14" in eval_res.clinical_advisory


def test_patient_exposure_evaluation_short_term():
    """Patient with short exposure in endemic zone has caution without forced toxicology mandate."""
    registry = GeoAquiferRegistry()
    eval_res = registry.evaluate_exposure(
        patient_id="PAT_VISITOR_002",
        pin_code="743126",
        years_exposed=0.5,
    )
    assert eval_res.toxicology_screening_mandated is False
    assert "CAUTION" in eval_res.clinical_advisory
