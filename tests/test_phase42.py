"""
Unit Tests for Phase 42: WHO ICD-11 TM1 & Western ICD-10 Dual-Coding Engine.
"""
from app.governance.dual_coding import DualCodingEngine

def test_dual_coding_allergic_asthma_sycosis():
    """Verify dual coding for allergic asthma under sycotic miasm."""
    res = DualCodingEngine.resolve_dual_coding("allergic asthma", "SYCOSIS")
    assert res.western_icd10_code == "J45.0"
    assert "allergic asthma" in res.western_icd10_title.lower()
    assert res.who_icd11_tm1_code == "TM1-HOM-02"
    assert res.ayush_namaste_code == "HOM-SYC-002"
    assert res.abdm_compliant is True

def test_dual_coding_eczema_psora():
    """Verify dual coding for eczema under psoric miasm."""
    res = DualCodingEngine.resolve_dual_coding("eczema", "PSORA")
    assert res.western_icd10_code == "L20.9"
    assert res.who_icd11_tm1_code == "TM1-HOM-01"
    assert res.ayush_namaste_code == "HOM-PSO-001"

def test_dual_coding_renal_calculus():
    """Verify dual coding for renal calculus."""
    res = DualCodingEngine.resolve_dual_coding("renal calculus", "SYCOSIS")
    assert res.western_icd10_code == "N20.0"

def test_dual_coding_unspecified_fallback():
    """Verify fallback for unlisted medical conditions."""
    res = DualCodingEngine.resolve_dual_coding("rare idiopathic syndrome xyz", "TUBERCULAR")
    assert res.western_icd10_code == "R69"
    assert res.who_icd11_tm1_code == "TM1-HOM-04"
    assert res.ayush_namaste_code == "HOM-TUB-004"
