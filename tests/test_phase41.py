"""
Unit Tests for Phase 41: Longitudinal Homeopathic EHR Engine.
"""
from app.clinical.longitudinal_ehr import LongitudinalEHREngine
from app.models.ehr import EHRClinicalEncounter

def setup_function():
    LongitudinalEHREngine.reset_store()

def test_longitudinal_trajectory_improving():
    """Verify chronological trajectory calculation with improving vitality."""
    enc1 = EHRClinicalEncounter(
        encounter_id="ENC-001",
        patient_id="PT-100",
        tenant_id="HOSP-KOLKATA",
        encounter_date="2025-01-10",
        chief_complaint="Severe chronic eczema",
        rubrics_selected=["Skin - Eruptions - Eczema"],
        remedy_prescribed="Sulphur",
        potency="200C",
        kent_observation_num=3,
        vitality_score=4.5,
        dominant_miasm="PSORA"
    )
    enc2 = EHRClinicalEncounter(
        encounter_id="ENC-002",
        patient_id="PT-100",
        tenant_id="HOSP-KOLKATA",
        encounter_date="2025-03-15",
        chief_complaint="Mild residual dryness",
        rubrics_selected=["Skin - Dryness"],
        remedy_prescribed="Sac Lac",
        potency="Placebo",
        kent_observation_num=4,
        vitality_score=8.2,
        dominant_miasm="PSORA"
    )

    LongitudinalEHREngine.record_encounter(enc1)
    LongitudinalEHREngine.record_encounter(enc2)

    traj = LongitudinalEHREngine.get_patient_trajectory("HOSP-KOLKATA", "PT-100")
    assert traj is not None
    assert traj.total_encounters == 2
    assert traj.vitality_trend == [4.5, 8.2]
    assert traj.is_vitality_improving is True
    assert "Curative trajectory" in traj.summary_verdict
    assert "Sulphur 200C" in traj.remedy_history[0]

def test_longitudinal_tenant_isolation():
    """Verify strict data partitioning between different clinic tenants."""
    enc_a = EHRClinicalEncounter(
        encounter_id="ENC-A1",
        patient_id="PT-999",
        tenant_id="TENANT-DELHI",
        encounter_date="2026-02-01",
        chief_complaint="Bronchial asthma",
        rubrics_selected=["Respiration - Asthmatic"],
        remedy_prescribed="Arsenicum album",
        potency="200C",
        vitality_score=5.0,
        dominant_miasm="PSORA"
    )
    LongitudinalEHREngine.record_encounter(enc_a)

    # Looking up the same patient under TENANT-MUMBAI must return None
    assert LongitudinalEHREngine.get_patient_trajectory("TENANT-MUMBAI", "PT-999") is None
    # Looking up under TENANT-DELHI succeeds
    traj = LongitudinalEHREngine.get_patient_trajectory("TENANT-DELHI", "PT-999")
    assert traj is not None
    assert traj.total_encounters == 1

def test_longitudinal_empty_record():
    """Verify handling of unknown patient query."""
    assert LongitudinalEHREngine.get_patient_trajectory("NON-EXISTENT", "UNKNOWN") is None
