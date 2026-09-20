"""
Unit Tests for Phase 18: Classical Materia Medica RAG Knowledge Engine.
"""
from app.safety.materia_medica import MateriaMedicaKnowledgeEngine

def test_materia_medica_lookup():
    """Verify detailed pathogenetic profile retrieval."""
    ars = MateriaMedicaKnowledgeEngine.get_entry("Arsenicum album")
    assert ars is not None
    assert ars.remedy_name == "Arsenicum album"
    assert any("prostration" in s.lower() for s in ars.guiding_symptoms)
    assert any("fastidious" in s.lower() for s in ars.mind_keynotes)
    assert "Hahnemann (Materia Medica Pura)" in ars.authorities_cited

    sulph = MateriaMedicaKnowledgeEngine.get_entry("Sulphur")
    assert sulph is not None
    assert any("11:00 AM" in s for s in sulph.guiding_symptoms)
    assert "Warmth of bed" in sulph.key_modalities_agg

def test_materia_medica_keynote_search():
    """Verify search across guiding symptoms and mind keynotes."""
    results = MateriaMedicaKnowledgeEngine.search_keynotes("thirstlessness")
    assert len(results) >= 1
    assert any(r["remedy_name"] == "Pulsatilla pratensis" for r in results)

    results_time = MateriaMedicaKnowledgeEngine.search_keynotes("4:00 PM to 8:00 PM")
    assert len(results_time) >= 1
    assert results_time[0]["remedy_name"] == "Lycopodium clavatum"

def test_materia_medica_nonexistent():
    """Verify graceful handling of non-existent remedy."""
    assert MateriaMedicaKnowledgeEngine.get_entry("UnknownRemedyXYZ") is None
    assert MateriaMedicaKnowledgeEngine.search_keynotes("NonExistentKeynotePhrase12345") == []
