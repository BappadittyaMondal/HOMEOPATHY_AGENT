"""
Unit Tests for Phase 13: Boenninghausen Polarity Analysis (BPA) & Contraindication Index (CI).
"""
from app.repertory.polarity_engine import BoenninghausenPolarityEngine

def test_thermal_polarity_contraindication_pulsatilla():
    """Verify Pulsatilla is flagged as contraindicated in an intensely chilly patient."""
    patient_rubrics = ["GENERALITIES - COLD - air - agg."]
    remedies = ["Hepar sulphuris", "Pulsatilla pratensis", "Arsenicum album"]

    evals = BoenninghausenPolarityEngine.evaluate_patient_polarities(patient_rubrics, remedies)

    # Hepar Sulph: Chilly remedy matching patient -> High positive ΔP, zero CI
    assert evals["Hepar sulphuris"].polarity_difference > 0
    assert evals["Hepar sulphuris"].contraindication_index == 0
    assert evals["Hepar sulphuris"].is_contraindicated is False

    # Pulsatilla: Warm remedy (< Warmth grade 3) -> Negative ΔP, CI >= 3 -> Contraindicated!
    assert evals["Pulsatilla pratensis"].polarity_difference < 0
    assert evals["Pulsatilla pratensis"].contraindication_index >= 3
    assert evals["Pulsatilla pratensis"].is_contraindicated is True
    assert any("WARMTH" in r for r in evals["Pulsatilla pratensis"].contraindicated_rubrics)

def test_motion_polarity_bryonia_vs_rhus_tox():
    """Verify Bryonia vs Rhus tox polarity divergence in motion modalities."""
    # Patient worse from motion
    patient_rubrics = ["EXTREMITIES - PAIN - motion - agg."]
    remedies = ["Bryonia alba", "Rhus toxicodendron"]

    evals = BoenninghausenPolarityEngine.evaluate_patient_polarities(patient_rubrics, remedies)

    # Bryonia matches < motion -> High positive ΔP
    assert evals["Bryonia alba"].polarity_difference >= 3
    assert evals["Bryonia alba"].is_contraindicated is False

    # Rhus tox has > motion grade 3 -> Contraindicated in purely motion-aggravated acute case
    assert evals["Rhus toxicodendron"].contraindication_index >= 3
    assert evals["Rhus toxicodendron"].is_contraindicated is True
