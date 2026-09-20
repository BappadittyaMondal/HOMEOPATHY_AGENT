"""
Western Emergency Break-Glass & Acute Critical Care Transfer Gateway (Phase 39 & Phase 53).
Hard clinical safety firewall detecting life-threatening physiological decompensation,
psychiatric crisis / suicidality, and age-banded deterioration (NEWS2 / PEWS).
Enforces mandatory UI lockout and generates immutable emergency transfer packets.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class EmergencyVitals(BaseModel):
    systolic_bp: int
    diastolic_bp: int
    respiratory_rate: int
    heart_rate: int
    gcs_score: int = Field(default=15, ge=3, le=15)
    spo2_percentage: int = Field(default=98, ge=0, le=100)
    temperature_celsius: float = Field(default=37.0, ge=25.0, le=45.0)
    patient_age_years: int = Field(default=35, ge=0, le=130)
    is_on_supplemental_oxygen: bool = False
    has_crushing_chest_pain: bool = False
    has_board_like_abdomen: bool = False
    has_anaphylactic_stridor: bool = False
    has_suicidal_ideation: bool = False
    has_acute_psychosis: bool = False


class EmergencyTransferPacket(BaseModel):
    is_emergency_lockout_active: bool
    emergency_level: str  # "CODE_RED_CRITICAL", "CODE_RED_PSYCHIATRIC", "CODE_ORANGE_URGENT", "STABLE_OPD"
    qsofa_score: int
    news2_score: Optional[int] = None
    pews_score: Optional[int] = None
    is_psychiatric_lockout: bool = False
    triggered_conditions: List[str]
    immediate_actions_required: List[str]
    palliative_concurrent_support: Optional[str] = None
    statutory_disclaimer: str = (
        "STATUTORY CRITICAL CARE DIRECTIVE: Acute life-threatening medical or psychiatric emergency detected. "
        "Normal outpatient homeopathic prescribing is locked. Immediate emergency dispatch and "
        "transfer to tertiary emergency / intensive care or psychiatric crisis unit is legally mandated."
    )


class EmergencyBreakGlassGateway:
    """
    Evaluates emergency telemetry and triggers fail-closed break-glass transfers.
    Implements INV-05 (Psychiatric Crisis Firewall) and INV-06 (NEWS2 / PEWS Scoring).
    """

    @classmethod
    def calculate_news2(cls, vitals: EmergencyVitals) -> int:
        """Calculates adult NEWS2 (National Early Warning Score 2) for patients >= 18."""
        score = 0

        # 1. Respiration Rate
        if vitals.respiratory_rate <= 8:
            score += 3
        elif 9 <= vitals.respiratory_rate <= 11:
            score += 1
        elif 12 <= vitals.respiratory_rate <= 20:
            score += 0
        elif 21 <= vitals.respiratory_rate <= 24:
            score += 2
        else:  # >= 25
            score += 3

        # 2. SpO2 Scale 1
        if vitals.spo2_percentage <= 91:
            score += 3
        elif vitals.spo2_percentage in (92, 93):
            score += 2
        elif vitals.spo2_percentage in (94, 95):
            score += 1

        # 3. Supplemental Oxygen
        if vitals.is_on_supplemental_oxygen:
            score += 2

        # 4. Systolic Blood Pressure
        if vitals.systolic_bp <= 90:
            score += 3
        elif 91 <= vitals.systolic_bp <= 100:
            score += 2
        elif 101 <= vitals.systolic_bp <= 110:
            score += 1
        elif vitals.systolic_bp >= 220:
            score += 3

        # 5. Heart Rate
        if vitals.heart_rate <= 40:
            score += 3
        elif 41 <= vitals.heart_rate <= 50:
            score += 1
        elif 91 <= vitals.heart_rate <= 110:
            score += 1
        elif 111 <= vitals.heart_rate <= 130:
            score += 2
        elif vitals.heart_rate >= 131:
            score += 3

        # 6. Consciousness (GCS < 15)
        if vitals.gcs_score < 15:
            score += 3

        # 7. Temperature
        if vitals.temperature_celsius <= 35.0:
            score += 3
        elif 35.1 <= vitals.temperature_celsius <= 36.0:
            score += 1
        elif 38.1 <= vitals.temperature_celsius <= 39.0:
            score += 1
        elif vitals.temperature_celsius >= 39.1:
            score += 2

        return score

    @classmethod
    def calculate_pews(cls, vitals: EmergencyVitals) -> int:
        """Calculates Pediatric Early Warning Score (PEWS) for age < 18."""
        score = 0
        # Behavior / GCS
        if vitals.gcs_score <= 10:
            score += 3
        elif vitals.gcs_score < 15:
            score += 2

        # Cardiovascular (Heart rate & BP)
        if vitals.heart_rate > 160 or vitals.heart_rate < 60:
            score += 3
        elif vitals.heart_rate > 140 or vitals.systolic_bp < 80:
            score += 2

        # Respiratory
        if vitals.respiratory_rate > 50 or vitals.spo2_percentage < 90:
            score += 3
        elif vitals.respiratory_rate > 40 or vitals.spo2_percentage < 94:
            score += 2

        return score

    @classmethod
    def evaluate_emergency_status(cls, vitals: EmergencyVitals) -> EmergencyTransferPacket:
        """
        Evaluates physiological parameters against qSOFA, NEWS2/PEWS, and psychiatric red flags.
        """
        triggered: List[str] = []
        is_pediatric = vitals.patient_age_years < 18

        # --- Check Psychiatric Crisis Firewall (INV-05) ---
        if vitals.has_suicidal_ideation or vitals.has_acute_psychosis:
            reason = "Active Suicidal Ideation / Severe Psychotic Crisis" if vitals.has_suicidal_ideation else "Acute Psychotic Excitation / Extreme Agitation"
            return EmergencyTransferPacket(
                is_emergency_lockout_active=True,
                emergency_level="CODE_RED_PSYCHIATRIC",
                qsofa_score=0,
                is_psychiatric_lockout=True,
                triggered_conditions=[reason],
                immediate_actions_required=[
                    "IMMEDIATE PSYCHIATRIC CRISIS MOBILIZATION: Do NOT leave patient unattended.",
                    "Initiate 24/7 continuous 1-on-1 observation and remove all hazardous objects.",
                    "Halt and lock all standard outpatient electronic prescribing.",
                    "Arrange urgent transfer to hospital psychiatric emergency department / crisis team."
                ],
                statutory_disclaimer=(
                    "STATUTORY PSYCHIATRIC EMERGENCY DIRECTIVE: Patient exhibits acute suicidal despair or delirium. "
                    "Outpatient homeopathic prescribing is locked. Immediate psychiatric emergency referral is mandatory "
                    "under the Mental Healthcare Act 2017."
                )
            )

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

        # 2. Age-Stratified Scoring (INV-06)
        news2_val = None
        pews_val = None
        if is_pediatric:
            pews_val = cls.calculate_pews(vitals)
            if pews_val >= 5:
                triggered.append(f"Pediatric PEWS score {pews_val}: High risk pediatric physiological collapse")
        else:
            news2_val = cls.calculate_news2(vitals)
            if news2_val >= 7:
                triggered.append(f"Adult NEWS2 score {news2_val}: High-risk clinical deterioration trigger")

        # 3. Acute Coronary Syndrome
        if vitals.has_crushing_chest_pain and (vitals.systolic_bp < 90 or vitals.heart_rate > 110 or vitals.heart_rate < 50):
            triggered.append("Impending Acute Myocardial Infarction / Cardiogenic Shock")

        # 4. Surgical Abdomen / Peritonitis
        if vitals.has_board_like_abdomen:
            triggered.append("Acute Surgical Abdomen / Peritonitis with Visceral Perforation risk")

        # 5. Severe Hypoxemia / Respiratory Arrest
        if vitals.spo2_percentage < 85 or vitals.respiratory_rate > 35:
            triggered.append(f"Severe Hypoxemic Respiratory Failure (SpO2 {vitals.spo2_percentage}%)")

        # 6. Anaphylaxis
        if vitals.has_anaphylactic_stridor:
            triggered.append("Severe Anaphylaxis with Airway Compromise")

        # 7. Coma / Deep Neurotrauma
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
        elif qsofa == 1 or vitals.spo2_percentage < 92 or (news2_val and news2_val >= 5):
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
            actions = ["Routine outpatient homeopathic consultation permitted."]
            concurrent = None

        return EmergencyTransferPacket(
            is_emergency_lockout_active=lockout,
            emergency_level=level,
            qsofa_score=qsofa,
            news2_score=news2_val,
            pews_score=pews_val,
            is_psychiatric_lockout=False,
            triggered_conditions=triggered,
            immediate_actions_required=actions,
            palliative_concurrent_support=concurrent
        )
