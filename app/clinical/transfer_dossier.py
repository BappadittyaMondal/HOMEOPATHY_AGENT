"""
Clinical Emergency Transfer Dossier Formatter - Phase 64.
Standardized printable emergency clinical handoff generator across all fail-closed safety pathways:
1. Physiological Decompensation (NEWS2/PEWS/Shock)
2. Psychiatric Crisis (Mental Healthcare Act 2017)
3. Laboratory Panic Values (Electrolytes, Troponin, Heavy Metals - INV-14)
4. Acute Surgical Operative Boundaries (Aphorism 186 - INV-15)
5. Oncological Pre-Malignancy Surveillance (INV-17)
"""
import hashlib
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class EmergencyTransferDossier(BaseModel):
    dossier_id: str
    patient_id: str
    patient_age: Optional[int] = None
    patient_gender: Optional[str] = "UNKNOWN"
    created_at_utc: str
    emergency_category: str  # "PHYSIOLOGICAL_COLLAPSE", "PSYCHIATRIC_CRISIS", "LABORATORY_PANIC", "SURGICAL_INTERVENTION", "ONCOLOGICAL_BIOPSY_MANDATE"
    severity_code: str       # "CODE_RED_CRITICAL", "CODE_RED_PSYCHIATRIC", "CRITICAL_LAB_PANIC", "ACUTE_SURGICAL_TRANSFER", "URGENT_BIOPSY_TRANSFER"
    primary_diagnosis_summary: str
    icd10_code: str
    triggering_findings: List[str]
    immediate_stabilization_instructions: List[str]
    recommended_destination_facility_tier: str
    referring_facility: str = "Homeopathy Hospital Information System (HHIS) Clinical Triage Unit"
    sha256_integrity_hash: str = ""

    def compute_hash(self) -> str:
        """Computes deterministic SHA-256 integrity hash across dossier payload."""
        payload = {
            "dossier_id": self.dossier_id,
            "patient_id": self.patient_id,
            "category": self.emergency_category,
            "severity": self.severity_code,
            "diagnosis": self.primary_diagnosis_summary,
            "icd10": self.icd10_code,
            "triggers": self.triggering_findings
        }
        serialized = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def to_printable_text(self) -> str:
        """Renders an authoritative printable clinical handoff dossier for ambulance dispatch."""
        sep = "=" * 82
        sub_sep = "-" * 82
        triggers_formatted = "\n".join([f"  [!] {item}" for item in self.triggering_findings])
        instructions_formatted = "\n".join([f"  [*] {item}" for item in self.immediate_stabilization_instructions])

        return f"""
{sep}
        EMERGENCY CLINICAL TRANSFER DOSSIER (AMBULANCE & TERTIARY HANDOFF)
{sep}
DOSSIER ID:      {self.dossier_id}
TIMESTAMP (UTC): {self.created_at_utc}
REFERRING UNIT:  {self.referring_facility}
INTEGRITY HASH:  SHA256:{self.sha256_integrity_hash}
{sub_sep}
PATIENT DEMOGRAPHICS:
  Patient ID:     {self.patient_id}
  Age:            {self.patient_age if self.patient_age is not None else 'N/A'} Years
  Gender:         {self.patient_gender}
{sub_sep}
CLINICAL TRIAGE & EMERGENCY CLASSIFICATION:
  Category:       {self.emergency_category}
  Severity Level: {self.severity_code}
  Primary ICD-10: {self.icd10_code} ({self.primary_diagnosis_summary})
{sub_sep}
TRIGGERING CLINICAL & TELEMETRIC FINDINGS:
{triggers_formatted}
{sub_sep}
IMMEDIATE TRANSIT STABILIZATION INSTRUCTIONS:
{instructions_formatted}
{sub_sep}
DESTINATION REQUIREMENT:
  Mandated Tier:  {self.recommended_destination_facility_tier}
{sub_sep}
STATUTORY CLINICAL & LEGAL DECLARATION:
  This patient has been evaluated by the HHIS Clinical Triage & Safety Engine.
  Outpatient homeopathic prescribing is locked in this acute phase.
  Immediate physical ambulance transfer to a fully equipped tertiary emergency 
  facility is legally mandated under the Clinical Establishments Act & Mental Healthcare Act.

Attending Clinician / Triage Officer Signature: ___________________________
RMP Registration Number:                       ___________________________
Date & Physical Dispatch Time:                 ___________________________
{sep}
""".strip()


class TransferDossierGenerator:
    """Factory creating cryptographically signed EmergencyTransferDossier records."""

    @classmethod
    def from_break_glass_packet(
        cls,
        packet_dict: Dict[str, Any],
        patient_id: str,
        age: Optional[int] = None,
        gender: Optional[str] = "UNKNOWN"
    ) -> EmergencyTransferDossier:
        """Creates dossier from Phase 39/53 EmergencyBreakGlassGateway output."""
        now_str = datetime.now(timezone.utc).isoformat()
        dossier_id = f"DOS-BG-{patient_id}-{int(datetime.now(timezone.utc).timestamp())}"
        level = packet_dict.get("emergency_level", "CODE_RED_CRITICAL")
        is_psych = packet_dict.get("is_psychiatric_lockout", False)

        if is_psych:
            cat = "PSYCHIATRIC_CRISIS"
            icd = "F29 / Z91.5"
            diag = "Active Psychiatric Crisis / Suicidal Ideation"
            dest = "Tertiary Psychiatric Hospital / Crisis Intervention Center"
        else:
            cat = "PHYSIOLOGICAL_COLLAPSE"
            icd = "R57.9"
            diag = "Acute Physiological Decompensation (NEWS2/PEWS Emergency)"
            dest = "Tertiary Emergency Care Hospital with 24/7 ICU & Resuscitation Suite"

        dossier = EmergencyTransferDossier(
            dossier_id=dossier_id,
            patient_id=patient_id,
            patient_age=age,
            patient_gender=gender,
            created_at_utc=now_str,
            emergency_category=cat,
            severity_code=level,
            primary_diagnosis_summary=diag,
            icd10_code=icd,
            triggering_findings=packet_dict.get("triggered_conditions", ["Physiological threshold exceeded"]),
            immediate_stabilization_instructions=packet_dict.get("immediate_actions_required", ["Maintain airway, breathing, circulation"]),
            recommended_destination_facility_tier=dest
        )
        dossier.sha256_integrity_hash = dossier.compute_hash()
        return dossier

    @classmethod
    def from_laboratory_panic(
        cls,
        patient_id: str,
        analyte: str,
        value: float,
        limit_desc: str,
        age: Optional[int] = None,
        gender: Optional[str] = "UNKNOWN"
    ) -> EmergencyTransferDossier:
        """Creates dossier from Phase 58/63 LaboratoryPanicException."""
        now_str = datetime.now(timezone.utc).isoformat()
        dossier_id = f"DOS-LAB-{patient_id}-{int(datetime.now(timezone.utc).timestamp())}"

        dossier = EmergencyTransferDossier(
            dossier_id=dossier_id,
            patient_id=patient_id,
            patient_age=age,
            patient_gender=gender,
            created_at_utc=now_str,
            emergency_category="LABORATORY_PANIC",
            severity_code="CRITICAL_LAB_PANIC",
            primary_diagnosis_summary=f"Critical Panic Laboratory Value: {analyte.upper()} ({value} {limit_desc})",
            icd10_code="R79.9",
            triggering_findings=[f"{analyte.upper()} = {value} exceeds critical limit ({limit_desc})"],
            immediate_stabilization_instructions=[
                "Maintain continuous cardiac/vitals telemetry",
                "Do not administer routine oral outpatient medications",
                "Transfer immediately to emergency intensive care"
            ],
            recommended_destination_facility_tier="Tertiary Hospital with Emergency Medical ICU & Advanced Toxicology / Dialysis Capabilities"
        )
        dossier.sha256_integrity_hash = dossier.compute_hash()
        return dossier

    @classmethod
    def from_surgical_emergency(
        cls,
        patient_id: str,
        condition: str,
        specialty: str,
        age: Optional[int] = None,
        gender: Optional[str] = "UNKNOWN"
    ) -> EmergencyTransferDossier:
        """Creates dossier from Phase 58 SurgicalInterventionRequiredException."""
        now_str = datetime.now(timezone.utc).isoformat()
        dossier_id = f"DOS-SURG-{patient_id}-{int(datetime.now(timezone.utc).timestamp())}"

        dossier = EmergencyTransferDossier(
            dossier_id=dossier_id,
            patient_id=patient_id,
            patient_age=age,
            patient_gender=gender,
            created_at_utc=now_str,
            emergency_category="SURGICAL_INTERVENTION",
            severity_code="ACUTE_SURGICAL_TRANSFER",
            primary_diagnosis_summary=f"Acute Operative Pathology: {condition}",
            icd10_code="K35 / K56 / O00",
            triggering_findings=[f"Aphorism 186 operative presentation detected: {condition}"],
            immediate_stabilization_instructions=[
                "Keep patient nil per os (NPO)",
                "Establish intravenous access",
                "Direct emergency transport to operative surgical suite"
            ],
            recommended_destination_facility_tier=f"Tertiary Surgical Center with {specialty} On-Call & 24/7 Operating Theatres"
        )
        dossier.sha256_integrity_hash = dossier.compute_hash()
        return dossier

    @classmethod
    def from_oncological_biopsy_mandate(
        cls,
        patient_id: str,
        lesion: str,
        investigation: str,
        age: Optional[int] = None,
        gender: Optional[str] = "UNKNOWN"
    ) -> EmergencyTransferDossier:
        """Creates dossier from Phase 62 OncologicalBiopsyRequiredException."""
        now_str = datetime.now(timezone.utc).isoformat()
        dossier_id = f"DOS-ONC-{patient_id}-{int(datetime.now(timezone.utc).timestamp())}"

        dossier = EmergencyTransferDossier(
            dossier_id=dossier_id,
            patient_id=patient_id,
            patient_age=age,
            patient_gender=gender,
            created_at_utc=now_str,
            emergency_category="ONCOLOGICAL_BIOPSY_MANDATE",
            severity_code="URGENT_BIOPSY_TRANSFER",
            primary_diagnosis_summary=f"Suspected Pre-Malignant / Neoplastic Keratopathy: {lesion}",
            icd10_code="L85.8 / D04.9",
            triggering_findings=[f"High-risk lesion characteristics detected: {lesion}"],
            immediate_stabilization_instructions=[
                f"Mandate in-person referral for {investigation}",
                "Halt dynamic homeopathic monotherapy pending histopathological clearance",
                "Schedule dermatopathology dermoscopy and tissue punch biopsy"
            ],
            recommended_destination_facility_tier="Regional Comprehensive Cancer Center / Tertiary Hospital Dermatology & Dermatopathology Department"
        )
        dossier.sha256_integrity_hash = dossier.compute_hash()
        return dossier

    @classmethod
    def from_interactive_emergency(
        cls,
        patient_id: str,
        reason: str,
        age: Optional[int] = None,
        gender: Optional[str] = "UNKNOWN"
    ) -> EmergencyTransferDossier:
        """Creates dossier when interactive dialogue detects acute crisis or psychiatric red flag (INV-19)."""
        now_str = datetime.now(timezone.utc).isoformat()
        dossier_id = f"DOS-INV19-{patient_id}-{int(datetime.now(timezone.utc).timestamp())}"

        dossier = EmergencyTransferDossier(
            dossier_id=dossier_id,
            patient_id=patient_id,
            patient_age=age,
            patient_gender=gender,
            created_at_utc=now_str,
            emergency_category="PHYSIOLOGICAL_COLLAPSE",
            severity_code="CODE_RED_CRITICAL",
            primary_diagnosis_summary=f"Emergency Red Flag Detected during Interactive Case Taking: {reason}",
            icd10_code="R68.89 / Z91.5",
            triggering_findings=[f"INV-19 Emergency Sentinel Triggered: {reason}"],
            immediate_stabilization_instructions=[
                "Immediately halt outpatient dialogue questioning",
                "Ensure patient physical airway, breathing, circulation safety",
                "Dispatch emergency psychiatric / acute medical ambulance transfer"
            ],
            recommended_destination_facility_tier="Tertiary Emergency Medical / Psychiatric Crisis Stabilization Unit"
        )
        dossier.sha256_integrity_hash = dossier.compute_hash()
        return dossier


