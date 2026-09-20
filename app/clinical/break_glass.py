"""
Western Emergency Break-Glass & Acute Critical Care Transfer Gateway (Phase 39).
Hard clinical safety firewall detecting life-threatening physiological decompensation,
enforcing mandatory UI lockout, and generating immutable emergency transfer packets.
"""
from typing import List, Optional
from pydantic import BaseModel, Field

class EmergencyVitals(BaseModel):
    systolic_bp: int
    diastolic_bp: int
    respiratory_rate: int
    heart_rate: int
    gcs_score: int = Field(..., ge=3, le=15)
    spo2_percentage: int = Field(..., ge=0, le=100)
    has_crushing_chest_pain: bool = False
    has_board_like_abdomen: bool = False
    has_anaphylactic_stridor: bool = False

class EmergencyTransferPacket(BaseModel):
    is_emergency_lockout_active: bool
    emergency_level: str  # "CODE_RED_CRITICAL", "CODE_ORANGE_URGENT", "STABLE_OPD"
    qsofa_score: int
    triggered_conditions: List[str]
    immediate_actions_required: List[str]
    palliative_concurrent_support: Optional[str] = None
    statutory_disclaimer: str = (
        "STATUTORY CRITICAL CARE DIRECTIVE: Acute life-threatening medical emergency detected. "
        "Normal outpatient homeopathic prescribing is locked. Immediate emergency dispatch and "
        "transfer to tertiary intensive care / emergency department is legally mandated."
    )

class EmergencyBreakGlassGateway:
    """
    Evaluates emergency telemetry and triggers fail-closed break-glass transfers.
    """

    @classmethod
    def evaluate_emergency_status(cls, vitals: EmergencyVitals) -> EmergencyTransferPacket:
        """
        Evaluates physiological parameters against qSOFA and acute catastrophic criteria.
        """
        triggered = []

        # 1. Calculate qSOFA
        qsofa = 0
        if vitals.respiratory_rate >= 22:
            qsofa += 1
        if vitals.gcs_score < 15:
            qsofa += 1
        if vitals.systolic_bp <= 100:
            qsofa += 1

        if qsofa >= 2:
            triggered.append(f"qSOFA score {qsofa}/3: High risk of septic shock / in-hospital mortality")

        # 2. Acute Coronary Syndrome
        if vitals.has_crushing_chest_pain and (vitals.systolic_bp < 90 or vitals.heart_rate > 110 or vitals.heart_rate < 50):
            triggered.append("Impending Acute Myocardial Infarction / Cardiogenic Shock")

        # 3. Surgical Abdomen / Peritonitis
        if vitals.has_board_like_abdomen:
            triggered.append("Acute Surgical Abdomen / Peritonitis with Visceral Perforation risk")

        # 4. Severe Hypoxemia / Respiratory Arrest
        if vitals.spo2_percentage < 85 or vitals.respiratory_rate > 35:
            triggered.append(f"Severe Hypoxemic Respiratory Failure (SpO2 {vitals.spo2_percentage}%)")

        # 5. Anaphylaxis
        if vitals.has_anaphylactic_stridor:
            triggered.append("Severe Anaphylaxis with Airway Compromise")

        # 6. Coma / Deep Neurotrauma
        if vitals.gcs_score <= 8:
            triggered.append(f"Severe Coma / Intracranial Catastrophe (GCS {vitals.gcs_score}/15)")

        if triggered:
            level = "CODE_RED_CRITICAL"
            lockout = True
            actions = [
                "ACTIVATE CODE RED: Call Emergency Ambulance (108/EMS) immediately.",
                "Administer high-flow supplemental oxygen via non-rebreather mask (15 L/min).",
                "Establish dual large-bore IV access (16G/18G) and initiate crystalloid fluid resuscitation.",
                "Generate printed emergency handover dossier with vitals telemetry and transfer to tertiary ICU.",
                "Lockout standard outpatient electronic prescription until emergency clearance."
            ]
            concurrent = (
                "Concurrent Adjuvant Support: Single aqueous olfaction of Carbo vegetabilis 200C "
                "(cold collapse/air hunger) or Aconitum 200C (panic/agony) may be given concurrently "
                "ONLY while ambulance dispatch and physical resuscitation are underway."
            )
        elif qsofa == 1 or vitals.spo2_percentage < 92:
            level = "CODE_ORANGE_URGENT"
            lockout = False
            actions = [
                "Close clinical observation: Re-evaluate vital signs every 15 minutes.",
                "Prepare emergency transfer vehicle on standby.",
                "If vitals deteriorate, initiate immediate Code Red transfer."
            ]
            concurrent = None
        else:
            level = "STABLE_OPD"
            lockout = False
            actions = ["Vital parameters within acceptable outpatient limits. Proceed with standard consultation."]
            concurrent = None

        return EmergencyTransferPacket(
            is_emergency_lockout_active=lockout,
            emergency_level=level,
            qsofa_score=qsofa,
            triggered_conditions=triggered,
            immediate_actions_required=actions,
            palliative_concurrent_support=concurrent
        )
