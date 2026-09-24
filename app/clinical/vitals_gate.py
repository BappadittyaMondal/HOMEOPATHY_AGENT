"""
Objective Physiological Vitals Gate Engine (Phase 77).

Enforces INV-21: Mandatory objective numerical physiological vitals
(Pulse, Systolic BP, Diastolic BP, Respiratory Rate, Temperature, SpO2)
prior to acute tele-triage repertorization or acute prescription.
Prevents silent acute myocardial infarction, septic shock, DKA, or respiratory failure
from masquerading as minor acute complaints.
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from app.clinical.break_glass import EmergencyVitals, EmergencyBreakGlassGateway, EmergencyTransferPacket


class MissingVitalsException(Exception):
    """Raised when acute tele-triage/prescribing is attempted without verified physiological vitals (INV-21)."""
    def __init__(self, message: str, patient_id: Optional[str] = None, missing_fields: Optional[List[str]] = None):
        super().__init__(message)
        self.message = message
        self.patient_id = patient_id
        self.missing_fields = missing_fields or []


class CriticalVitalsDecompensationException(Exception):
    """Raised when physiological vitals indicate acute life-threatening decompensation requiring immediate hospital transfer."""
    def __init__(self, message: str, news2_score: int, critical_flags: List[str], transfer_packet: Optional[EmergencyTransferPacket] = None):
        super().__init__(message)
        self.message = message
        self.news2_score = news2_score
        self.critical_flags = critical_flags
        self.transfer_packet = transfer_packet


class ObjectivePhysiologicalVitals(BaseModel):
    """Standardized numerical clinical vitals container."""
    pulse_bpm: int = Field(..., ge=20, le=300, description="Pulse rate in beats per minute")
    systolic_bp: int = Field(..., ge=40, le=320, description="Systolic blood pressure in mmHg")
    diastolic_bp: int = Field(..., ge=20, le=220, description="Diastolic blood pressure in mmHg")
    respiratory_rate: int = Field(..., ge=4, le=80, description="Breaths per minute")
    temperature_celsius: float = Field(..., ge=25.0, le=45.0, description="Body temperature in Celsius")
    spo2_percent: int = Field(..., ge=40, le=100, description="Peripheral capillary oxygen saturation %")
    blood_glucose_mg_dl: Optional[float] = Field(default=None, ge=10.0, le=1500.0, description="Random capillary blood glucose in mg/dL")
    is_on_supplemental_oxygen: bool = False
    consciousness_avpu: str = Field(default="ALERT", description="ALERT, VOICE, PAIN, UNRESPONSIVE")
    recorded_timestamp: Optional[str] = None
    is_device_verified: bool = True


class VitalsGateAssessment(BaseModel):
    """Result of objective physiological vitals verification."""
    is_cleared: bool
    news2_score: int
    vitals: ObjectivePhysiologicalVitals
    clinical_risk_tier: str  # "LOW", "MEDIUM", "HIGH_CRITICAL"
    clinical_summary: str


class ObjectiveVitalsGateEngine:
    """
    Enforces INV-21 by verifying that acute clinical encounters have verified numerical vitals
    and computing the standardized adult NEWS2 score to preempt decompensation.
    """

    @classmethod
    def to_emergency_vitals(cls, vitals: ObjectivePhysiologicalVitals, patient_age_years: int = 35) -> EmergencyVitals:
        """Converts ObjectivePhysiologicalVitals into EmergencyVitals for break-glass evaluation."""
        gcs = 15
        avpu = vitals.consciousness_avpu.upper().strip()
        if avpu == "VOICE":
            gcs = 12
        elif avpu == "PAIN":
            gcs = 8
        elif avpu == "UNRESPONSIVE":
            gcs = 3

        return EmergencyVitals(
            systolic_bp=vitals.systolic_bp,
            diastolic_bp=vitals.diastolic_bp,
            respiratory_rate=vitals.respiratory_rate,
            heart_rate=vitals.pulse_bpm,
            gcs_score=gcs,
            spo2_percentage=vitals.spo2_percent,
            temperature_celsius=vitals.temperature_celsius,
            patient_age_years=patient_age_years,
            is_on_supplemental_oxygen=vitals.is_on_supplemental_oxygen
        )

    @classmethod
    def evaluate_vitals(
        cls,
        vitals: Optional[ObjectivePhysiologicalVitals],
        is_acute: bool = True,
        patient_id: Optional[str] = None,
        patient_age_years: int = 35
    ) -> VitalsGateAssessment:
        """
        Validates acute vitals presence and safe physiological boundaries.
        Raises MissingVitalsException if vitals missing in acute consultation (INV-21).
        Raises CriticalVitalsDecompensationException if NEWS2 >= 7 or acute red flag detected.
        """
        if is_acute and vitals is None:
            raise MissingVitalsException(
                f"OBJECTIVE VITALS GATE MANDATE (INV-21): Acute tele-triage and acute prescribing for "
                f"patient '{patient_id or 'UNKNOWN'}' strictly requires verified numerical physiological vitals "
                f"(Pulse, Systolic BP, Diastolic BP, Respiratory Rate, Temperature, SpO2). "
                f"Abstaining from prescribing to prevent masking severe occult pathologies (MI, Sepsis, DKA).",
                patient_id=patient_id,
                missing_fields=["pulse_bpm", "systolic_bp", "diastolic_bp", "respiratory_rate", "temperature_celsius", "spo2_percent"]
            )

        # For non-acute cases where vitals were not provided, return cleared baseline
        if vitals is None:
            baseline = ObjectivePhysiologicalVitals(
                pulse_bpm=72,
                systolic_bp=120,
                diastolic_bp=80,
                respiratory_rate=16,
                temperature_celsius=37.0,
                spo2_percent=98
            )
            return VitalsGateAssessment(
                is_cleared=True,
                news2_score=0,
                vitals=baseline,
                clinical_risk_tier="LOW",
                clinical_summary="Chronic case with standard baseline vitals."
            )

        # Map to EmergencyVitals and calculate NEWS2
        ev = cls.to_emergency_vitals(vitals, patient_age_years=patient_age_years)
        news2 = EmergencyBreakGlassGateway.calculate_news2(ev)

        critical_flags: List[str] = []
        if vitals.spo2_percent <= 91:
            critical_flags.append(f"Severe Hypoxemia (SpO2 {vitals.spo2_percent}% <= 91%)")
        if vitals.systolic_bp <= 90:
            critical_flags.append(f"Cardiovascular Shock / Hypotension (Systolic BP {vitals.systolic_bp} mmHg <= 90)")
        if vitals.systolic_bp >= 220 or vitals.diastolic_bp >= 130:
            critical_flags.append(f"Hypertensive Crisis (BP {vitals.systolic_bp}/{vitals.diastolic_bp} mmHg)")
        if vitals.pulse_bpm <= 40 or vitals.pulse_bpm >= 131:
            critical_flags.append(f"Critical Arrhythmia / Extreme Rate (Pulse {vitals.pulse_bpm} bpm)")
        if vitals.respiratory_rate <= 8 or vitals.respiratory_rate >= 25:
            critical_flags.append(f"Critical Respiratory Distress (Rate {vitals.respiratory_rate}/min)")
        if vitals.consciousness_avpu.upper() in ["PAIN", "UNRESPONSIVE"]:
            critical_flags.append(f"Altered Consciousness / Coma Scale (AVPU: {vitals.consciousness_avpu})")
        if vitals.blood_glucose_mg_dl is not None:
            if vitals.blood_glucose_mg_dl <= 50.0:
                critical_flags.append(f"Severe Hypoglycemic Coma Risk (Glucose {vitals.blood_glucose_mg_dl} mg/dL)")
            elif vitals.blood_glucose_mg_dl >= 400.0:
                critical_flags.append(f"Severe Hyperglycemic Hyperosmolar / DKA Risk (Glucose {vitals.blood_glucose_mg_dl} mg/dL)")

        if news2 >= 7 or len(critical_flags) > 0:
            # Trigger Emergency Lockout
            transfer = EmergencyBreakGlassGateway.evaluate_emergency_status(ev)
            if not transfer.is_emergency_lockout_active and len(critical_flags) > 0:
                transfer.is_emergency_lockout_active = True
                transfer.emergency_level = "CODE_RED_CRITICAL"
                transfer.triggered_conditions.extend(critical_flags)

            raise CriticalVitalsDecompensationException(
                f"CRITICAL CARE DECOMPENSATION LOCKOUT (INV-21 / INV-06): Patient NEWS2 score is {news2} "
                f"with critical triggers: {'; '.join(critical_flags or ['NEWS2 >= 7'])}. "
                f"Outpatient homeopathic prescribing is locked. Emergency transfer packet generated.",
                news2_score=news2,
                critical_flags=critical_flags,
                transfer_packet=transfer
            )

        risk_tier = "LOW" if news2 <= 4 else "MEDIUM"
        return VitalsGateAssessment(
            is_cleared=True,
            news2_score=news2,
            vitals=vitals,
            clinical_risk_tier=risk_tier,
            clinical_summary=f"Physiological vitals stable. NEWS2 score {news2} ({risk_tier} risk)."
        )
