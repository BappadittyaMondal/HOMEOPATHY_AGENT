"""
Phase 61 Unit Tests: Authoritative Pharmacopoeial Registry Expansion (150 Polychrests & Clinical Remedies).
Validates INV-16 with the 150-remedy HPI database, alias mapping, Schedule E(1) checks, and fail-closed safety.
"""
import pytest
from app.repertory.canonical_registry import (
    CanonicalRemedyRegistry,
    UnresolvedRemedyException,
    SYSTEM_STATUS_BANNER
)


def test_registry_size_exactly_150():
    """Verify registry contains exactly 150 certified canonical remedies."""
    assert CanonicalRemedyRegistry.total_remedies_count() == 150


def test_cutaneous_keratosis_remedies_resolution():
    """Verify resolution of specialized cutaneous & keratolytic remedies."""
    # Antimonium crudum
    ant_c = CanonicalRemedyRegistry.resolve_remedy("Antimonium crudum")
    assert ant_c.canonical_id == "REM-ANTC-032"
    assert ant_c.canonical_abbreviation == "Ant-c."
    assert ant_c.is_schedule_e1 is True
    assert ant_c.min_safe_potency == "3X"

    # Hydrocotyle asiatica
    hydr = CanonicalRemedyRegistry.resolve_remedy("gotu kola")
    assert hydr.canonical_id == "REM-HYDR-033"
    assert "hydrocotyle" in hydr.aliases

    # Radium bromatum
    rad = CanonicalRemedyRegistry.resolve_remedy("radium brom")
    assert rad.canonical_id == "REM-RADBR-034"
    assert rad.min_safe_potency == "6C"

    # Arsenicum iodatum
    ars_i = CanonicalRemedyRegistry.resolve_remedy("arsenic iod")
    assert ars_i.canonical_id == "REM-ARSI-035"
    assert ars_i.is_schedule_e1 is True


def test_cardiorenal_and_organ_remedies_resolution():
    """Verify resolution of organ-specific clinical polychrests."""
    # Crataegus
    crat = CanonicalRemedyRegistry.resolve_remedy("hawthorn")
    assert crat.canonical_id == "REM-CRAT-051"

    # Cactus
    cact = CanonicalRemedyRegistry.resolve_remedy("cactus grandiflorus")
    assert cact.canonical_id == "REM-CACT-052"

    # Digitalis
    dig = CanonicalRemedyRegistry.resolve_remedy("foxglove")
    assert dig.canonical_id == "REM-DIG-053"
    assert dig.is_schedule_e1 is True

    # Berberis
    berb = CanonicalRemedyRegistry.resolve_remedy("berberis vulgaris")
    assert berb.canonical_id == "REM-BERB-074"

    # Symphytum
    symph = CanonicalRemedyRegistry.resolve_remedy("knitbone")
    assert symph.canonical_id == "REM-SYMPH-067"


def test_nosodes_and_deep_miasmatic_remedies_resolution():
    """Verify resolution of biological nosodes and deep miasmatic constitutional remedies."""
    psor = CanonicalRemedyRegistry.resolve_remedy("psorinum")
    assert psor.canonical_id == "REM-PSOR-093"
    assert psor.kingdom == "NOSODE"

    tub = CanonicalRemedyRegistry.resolve_remedy("bacillinum")
    assert tub.canonical_id == "REM-TUB-096"

    carc = CanonicalRemedyRegistry.resolve_remedy("carcinosin")
    assert carc.canonical_id == "REM-CARC-097"

    pyrog = CanonicalRemedyRegistry.resolve_remedy("pyrogenium")
    assert pyrog.canonical_id == "REM-PYROG-098"


def test_tissue_salts_and_mineral_acids_resolution():
    """Verify biochemic tissue salts and mineral acid remedies."""
    kali_p = CanonicalRemedyRegistry.resolve_remedy("potassium phosphate")
    assert kali_p.canonical_id == "REM-KALI-P-146"

    ferr_p = CanonicalRemedyRegistry.resolve_remedy("ferrum phos")
    assert ferr_p.canonical_id == "REM-FERR-P-149"

    nit_ac = CanonicalRemedyRegistry.resolve_remedy("nitric acid")
    assert nit_ac.canonical_id == "REM-NITR-AC-140"
    assert nit_ac.is_schedule_e1 is True


def test_inv_16_unresolved_hallucinated_remedy_raises_exception():
    """Verify INV-16 fail-closed defense: non-existent remedies must raise UnresolvedRemedyException."""
    with pytest.raises(UnresolvedRemedyException) as exc_info:
        CanonicalRemedyRegistry.resolve_remedy("QuantumVibrationalPanacea99X")
    assert "INV-16" in str(exc_info.value)
    assert exc_info.value.query == "QuantumVibrationalPanacea99X"
