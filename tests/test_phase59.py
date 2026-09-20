"""
Tests for Phase 59: Canonical Remedy Registry & Nomenclature Normalization Engine.
Validates INV-16 (Canonical Nomenclature & Abbreviation Normalization) and System Status Banner.
"""
import pytest
from app.repertory.canonical_registry import (
    CanonicalRemedyRegistry,
    UnresolvedRemedyException,
    SYSTEM_STATUS_BANNER
)


def test_inv_16_belladonna_variants_resolve_to_canonical():
    """INV-16: Disparate synonyms and abbreviations for Belladonna resolve to REM-BELL-002."""
    queries = ["Belladonna", "bell", "atropa belladonna", "deadly nightshade", "Bell."]
    for q in queries:
        remedy = CanonicalRemedyRegistry.resolve_remedy(q)
        assert remedy.canonical_id == "REM-BELL-002"
        assert remedy.standard_name == "Atropa belladonna"
        assert remedy.canonical_abbreviation == "Bell."
        assert remedy.is_schedule_e1 is True
        assert remedy.min_safe_potency == "2X"


def test_inv_16_aconite_variants_resolve_to_canonical():
    """INV-16: Synonyms for Aconite resolve to REM-ACON-001 with Schedule E(1) flags."""
    queries = ["aconite", "acon", "Acon.", "wolfsbane", "monkshood", "aconitum napellus"]
    for q in queries:
        remedy = CanonicalRemedyRegistry.resolve_remedy(q)
        assert remedy.canonical_id == "REM-ACON-001"
        assert remedy.standard_name == "Aconitum napellus"
        assert remedy.is_schedule_e1 is True
        assert remedy.min_safe_potency == "3X"


def test_inv_16_nux_vomica_variants():
    """INV-16: Nux vomica aliases resolve to REM-NUX-004."""
    queries = ["nux vomica", "nux vom", "nux-v", "nux", "poison nut"]
    for q in queries:
        remedy = CanonicalRemedyRegistry.resolve_remedy(q)
        assert remedy.canonical_id == "REM-NUX-004"
        assert remedy.standard_name == "Strychnos nux-vomica"
        assert remedy.canonical_abbreviation == "Nux-v."


def test_inv_16_polychrests_resolution():
    """INV-16: High-frequency polychrests resolve unambiguously."""
    mappings = {
        "natrum mur": "REM-NATM-013",
        "nat-m": "REM-NATM-013",
        "rhus tox": "REM-RHUS-007",
        "poison ivy": "REM-RHUS-007",
        "calc carb": "REM-CALC-010",
        "sulphur": "REM-SULPH-005",
        "phosphorus": "REM-PHOS-006",
        "white arsenic": "REM-ARS-009",
        "pure flint": "REM-SIL-015",
        "arnica": "REM-ARN-016",
        "bushmaster": "REM-LACH-011",
        "wind flower": "REM-PULS-014",
        "sepia": "REM-SEP-017",
        "thuja": "REM-THUJ-018",
        "ignatia": "REM-IGN-019",
        "causticum": "REM-CAUST-020",
        "carbo veg": "REM-CARB-021",
        "gelsemium": "REM-GELS-023",
        "china": "REM-CHIN-024",
    }
    for query, expected_id in mappings.items():
        remedy = CanonicalRemedyRegistry.resolve_remedy(query)
        assert remedy.canonical_id == expected_id


def test_inv_16_unresolved_remedy_raises_exception():
    """INV-16: Non-existent or hallucinated remedy names must raise UnresolvedRemedyException."""
    invalid_queries = ["NonExistentRemedyXYZ", "SyntheticaFake100", "RandomNonsenseChemical"]
    for query in invalid_queries:
        with pytest.raises(UnresolvedRemedyException) as exc_info:
            CanonicalRemedyRegistry.resolve_remedy(query)
        assert "UNRESOLVED REMEDY" in str(exc_info.value)
        assert exc_info.value.query == query


def test_statutory_legal_banner():
    """Statutory CDSS Level 2 prototype banner must be non-empty and cite NCH Act 2020."""
    banner = CanonicalRemedyRegistry.get_system_banner()
    assert "CLINICAL_DECISION_SUPPORT_SYSTEM_LEVEL_2" in banner
    assert "MANDATORY HUMAN-IN-THE-LOOP" in banner
    assert "NCH ACT 2020" in banner
    assert banner == SYSTEM_STATUS_BANNER
