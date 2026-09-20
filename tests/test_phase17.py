"""
Unit Tests for Phase 17: Homoeopathic Pharmacopoeia of India (HPI) Monograph Database.
"""
from app.safety.hpi_monographs import HPIMonographDatabase
from app.models.safety import KingdomEnum

def test_hpi_monograph_retrieval():
    """Verify retrieval of official HPI monograph data."""
    acon = HPIMonographDatabase.get_monograph("Aconitum napellus")
    assert acon is not None
    assert acon.abbreviation == "Acon"
    assert acon.kingdom == KingdomEnum.VEGETABLE
    assert acon.hpi_volume == 1
    assert "Aconitine" in acon.active_alkaloids

    sulph = HPIMonographDatabase.get_monograph("Sulphur")
    assert sulph is not None
    assert sulph.kingdom == KingdomEnum.MINERAL
    assert sulph.is_schedule_e1_toxic is False

def test_hpi_schedule_e1_poison_checks():
    """Verify Schedule E(1) statutory poison designations."""
    assert HPIMonographDatabase.is_schedule_e1("Aconitum napellus") is True
    assert HPIMonographDatabase.is_schedule_e1("Arsenicum album") is True
    assert HPIMonographDatabase.is_schedule_e1("Strychnos nux-vomica") is True
    assert HPIMonographDatabase.is_schedule_e1("Lachesis muta") is True
    assert HPIMonographDatabase.is_schedule_e1("Calcarea carbonica") is False
    assert HPIMonographDatabase.is_schedule_e1("Pulsatilla pratensis") is False

def test_hpi_minimum_allowed_potencies():
    """Verify lowest statutory dispensing dilutions under HPI."""
    # Arsenicum album banned below 6X
    assert HPIMonographDatabase.get_minimum_safe_potency("Arsenicum album") == "6X"
    # Lachesis muta venom banned below 6C
    assert HPIMonographDatabase.get_minimum_safe_potency("Lachesis muta") == "6C"
    # Aconite banned below 3X
    assert HPIMonographDatabase.get_minimum_safe_potency("Aconitum napellus") == "3X"
