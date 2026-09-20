"""
Unit Tests for Phase 07: Kent's Repertory Digital Graph & Cross-Referencing Engine.
"""
from app.repertory.kent_graph import KentRepertoryGraph

def test_kent_graph_initialization_and_chapters():
    """Verify 37 canonical chapters and initial base nodes."""
    graph = KentRepertoryGraph()
    assert len(graph.CANONICAL_CHAPTERS) == 37
    assert "MIND" in graph.CANONICAL_CHAPTERS
    assert "HEAD" in graph.CANONICAL_CHAPTERS
    assert "GENERALITIES" in graph.CANONICAL_CHAPTERS
    assert len(graph.nodes) >= 9

def test_kent_graph_hierarchy_and_parent_child():
    """Verify parent-child navigation in the rubric tree."""
    graph = KentRepertoryGraph()
    child = graph.get_rubric("HEAD - PAIN - forehead - motion - agg.")
    assert child is not None
    assert child.parent_path == "HEAD - PAIN - forehead - motion"
    assert child.level == 5

    # Check children of parent
    children = graph.get_children("HEAD - PAIN - forehead - motion")
    child_paths = [c.full_path for c in children]
    assert "HEAD - PAIN - forehead - motion - agg." in child_paths

def test_kent_graph_cross_references():
    """Verify cross-reference graph links between synonymous or related rubrics."""
    graph = KentRepertoryGraph()
    node = graph.get_rubric("MIND - ANXIETY - health, about")
    assert node is not None
    assert "MIND - FEAR - disease, of" in node.cross_references

    refs = graph.get_cross_references("MIND - ANXIETY - health, about")
    ref_paths = [r.full_path for r in refs]
    assert "MIND - FEAR - disease, of" in ref_paths

def test_kent_graph_search_and_synonyms():
    """Verify search by token and synonym resolution."""
    graph = KentRepertoryGraph()
    
    # Search by token
    res = graph.search_rubrics("forehead pressure")
    assert len(res) >= 1
    assert any("pressure - amel." in r.full_path for r in res)

    # Search by synonym
    res_syn = graph.search_rubrics("chilly")
    assert len(res_syn) >= 1
    assert any("COLD - air - agg." in r.full_path for r in res_syn)

    # Search by another synonym
    res_nosophobia = graph.search_rubrics("nosophobia")
    assert len(res_nosophobia) >= 1
    assert any("FEAR - disease, of" in r.full_path for r in res_nosophobia)
