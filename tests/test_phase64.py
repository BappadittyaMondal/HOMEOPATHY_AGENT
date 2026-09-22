"""
Phase 64 Unit Tests: Printable Clinical Emergency Transfer Dossier Formatter.
Validates generation, cryptographic hashing, and printable formatting across all 5 emergency pathways:
1. Physiological NEWS2/PEWS
2. Psychiatric Crisis
3. Laboratory Panic (including Heavy Metals)
4. Acute Surgical Condition
5. Oncological Pre-Malignancy Biopsy Mandate
"""
import pytest
from app.clinical.transfer_dossier import (
    EmergencyTransferDossier,
    TransferDossierGenerator
)


def test_dossier_from_break_glass_critical():
    """Verify dossier creation from physiological decompensation packet."""
    packet = {
        "emergency_level": "CODE_RED_CRITICAL",
        "is_psychiatric_lockout": False,
        "triggered_conditions": ["NEWS2 Score = 8 (Severe Deterioration)", "SpO2 = 88% on Room Air"],
        "immediate_actions_required": ["High-flow oxygen", "Intravenous access", "Immediate tertiary transfer"]
    }
    dossier = TransferDossierGenerator.from_break_glass_packet(
        packet_dict=packet,
        patient_id="PT-CRIT-101",
        age=58,
        gender="MALE"
    )
    assert dossier.patient_id == "PT-CRIT-101"
    assert dossier.emergency_category == "PHYSIOLOGICAL_COLLAPSE"
    assert dossier.severity_code == "CODE_RED_CRITICAL"
    assert len(dossier.sha256_integrity_hash) == 64
    
    text = dossier.to_printable_text()
    assert "EMERGENCY CLINICAL TRANSFER DOSSIER" in text
    assert "NEWS2 Score = 8" in text
    assert "SHA256:" in text


def test_dossier_from_break_glass_psychiatric():
    """Verify dossier creation from psychiatric crisis packet."""
    packet = {
        "emergency_level": "CODE_RED_PSYCHIATRIC",
        "is_psychiatric_lockout": True,
        "triggered_conditions": ["Active Suicidal Ideation with Intent"],
        "immediate_actions_required": ["Continuous 1-on-1 crisis observation", "Secure environment", "Psychiatric transfer"]
    }
    dossier = TransferDossierGenerator.from_break_glass_packet(
        packet_dict=packet,
        patient_id="PT-PSYCH-102",
        age=29,
        gender="FEMALE"
    )
    assert dossier.emergency_category == "PSYCHIATRIC_CRISIS"
    assert dossier.severity_code == "CODE_RED_PSYCHIATRIC"
    assert "Psychiatric" in dossier.recommended_destination_facility_tier


def test_dossier_from_laboratory_panic():
    """Verify dossier creation from critical lab panic (e.g. Troponin or Arsenic)."""
    dossier = TransferDossierGenerator.from_laboratory_panic(
        patient_id="PT-LAB-103",
        analyte="troponin_i",
        value=0.18,
        limit_desc="ng/mL (Panic High > 0.04 ng/mL)",
        age=65,
        gender="MALE"
    )
    assert dossier.emergency_category == "LABORATORY_PANIC"
    assert "TROPONIN_I" in dossier.primary_diagnosis_summary
    assert len(dossier.sha256_integrity_hash) == 64
    
    printable = dossier.to_printable_text()
    assert "TROPONIN_I = 0.18" in printable


def test_dossier_from_surgical_emergency():
    """Verify dossier creation from surgical emergency (e.g. Acute Appendicitis)."""
    dossier = TransferDossierGenerator.from_surgical_emergency(
        patient_id="PT-SURG-104",
        condition="Acute Appendicitis with perforation risk",
        specialty="General Surgery",
        age=22,
        gender="FEMALE"
    )
    assert dossier.emergency_category == "SURGICAL_INTERVENTION"
    assert dossier.severity_code == "ACUTE_SURGICAL_TRANSFER"
    assert "General Surgery" in dossier.recommended_destination_facility_tier
    
    text = dossier.to_printable_text()
    assert "nil per os (NPO)" in text


def test_dossier_from_oncological_biopsy_mandate():
    """Verify dossier creation from oncological pre-malignancy mandate (INV-17)."""
    dossier = TransferDossierGenerator.from_oncological_biopsy_mandate(
        patient_id="PT-ONC-105",
        lesion="Chronic Arsenical Keratoderma with Induration / Bowenoid Transformation",
        investigation="Dermatopathology Punch Biopsy",
        age=45,
        gender="MALE"
    )
    assert dossier.emergency_category == "ONCOLOGICAL_BIOPSY_MANDATE"
    assert dossier.severity_code == "URGENT_BIOPSY_TRANSFER"
    assert "Cancer Center" in dossier.recommended_destination_facility_tier
    
    text = dossier.to_printable_text()
    assert "Dermatopathology Punch Biopsy" in text
    assert "Bowenoid" in text


def test_dossier_tamper_detection_via_hash():
    """Verify SHA-256 integrity hash detects tampering with diagnosis or payload."""
    dossier = TransferDossierGenerator.from_laboratory_panic(
        patient_id="PT-TEST-106",
        analyte="potassium",
        value=2.1,
        limit_desc="mEq/L (Panic Low < 2.5 mEq/L)"
    )
    original_hash = dossier.sha256_integrity_hash
    assert dossier.compute_hash() == original_hash
    
    # Simulate tampering
    dossier.primary_diagnosis_summary = "Patient is completely normal and healthy"
    tampered_hash = dossier.compute_hash()
    assert tampered_hash != original_hash
