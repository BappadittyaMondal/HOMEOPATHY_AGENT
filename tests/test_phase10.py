"""
Unit Tests for Phase 10: Pluggable Synthetic Repertory Ingestion Adapter.
"""
from app.repertory.synthetic_adapter import SyntheticRepertoryAdapter
from app.models.synthetic import SyntheticDatasetManifest, ExternalRubricPayload
from app.repertory.kent_graph import kent_graph

def test_synthetic_adapter_unauthorized_license():
    """Verify rejection of manifests lacking valid institutional license key."""
    manifest = SyntheticDatasetManifest(
        dataset_name="Pirated_Synthesis_v9",
        version="9.1",
        license_key="INVALID_KEY",
        authorized_institution="Unknown Clinic",
        total_rubrics=1,
        rubrics=[
            ExternalRubricPayload(
                rubric_path="CLINICAL - CHRONIC_FATIGUE",
                chapter="CLINICAL",
                remedies_with_grades={"Ars": 3},
                author_source="Modern Clinical"
            )
        ]
    )
    result = SyntheticRepertoryAdapter.ingest_manifest(manifest)
    assert result.status == "REJECTED_UNAUTHORIZED_LICENSE"
    assert result.rubrics_imported == 0

def test_synthetic_adapter_authorized_ingestion():
    """Verify successful ingestion with valid institutional license."""
    manifest = SyntheticDatasetManifest(
        dataset_name="NIH_Kolkata_Clinical_Additions_2026",
        version="2.0",
        license_key="LIC-ACADEMIC-NIH-KOLKATA-2026-X89",
        authorized_institution="National Institute of Homoeopathy",
        total_rubrics=2,
        rubrics=[
            ExternalRubricPayload(
                rubric_path="CLINICAL - DIABETIC_NEUROPATHY - burning",
                chapter="GENERALITIES",
                remedies_with_grades={"Ars": 3, "Phos": 3, "Sec": 2},
                author_source="NIH Kolkata Research Trial",
                cross_references=["GENERALITIES - BURNING - internal"]
            ),
            ExternalRubricPayload(
                rubric_path="CLINICAL - LONG_COVID - chronic_fatigue",
                chapter="GENERALITIES",
                remedies_with_grades={"Gels": 3, "Kali-p": 3, "Carb-v": 2},
                author_source="NIH Kolkata Research Trial"
            )
        ]
    )
    result = SyntheticRepertoryAdapter.ingest_manifest(manifest)
    assert result.status == "SUCCESS"
    assert result.rubrics_imported == 2
    assert result.new_remedies_added >= 4

    # Verify nodes now exist in digital graph
    node = kent_graph.get_rubric("CLINICAL - DIABETIC_NEUROPATHY - burning")
    assert node is not None
    assert node.remedy_grades["Ars"] == 3
    assert node.remedy_grades["Phos"] == 3
