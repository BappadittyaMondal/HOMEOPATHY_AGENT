"""
Obstetric Gestational Trimester Contraindication Firewall & Pediatric Protection (Phase 57).
Codifies statutory and classical homeopathic obstetric contraindications (INV-12)
and DPDP Act 2023 Section 9 mandatory pediatric guardian consent verification (INV-13).
"""
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class PregnancyStatus(str, Enum):
    NOT_PREGNANT = "NOT_PREGNANT"
    TRIMESTER_1 = "TRIMESTER_1"  # Weeks 1-12 (Peak organogenesis & teratogenic/abortive vulnerability)
    TRIMESTER_2 = "TRIMESTER_2"  # Weeks 13-27
    TRIMESTER_3 = "TRIMESTER_3"  # Weeks 28-40 (Preterm labor & uterine tone risk)
    POST_PARTUM = "POST_PARTUM"
    LACTATING = "LACTATING"


class PediatricConsentRequiredException(Exception):
    """Raised when prescribing for a minor (< 18y) without verifiable guardian consent (INV-13)."""
    def __init__(self, message: str, patient_age: int):
        super().__init__(message)
        self.message = message
        self.patient_age = patient_age


class ObstetricBlockException(Exception):
    """Raised when an abortifacient/emmenagogue is prescribed during contraindicated gestation (INV-12)."""
    def __init__(self, message: str, remedy: str, status: PregnancyStatus):
        super().__init__(message)
        self.message = message
        self.remedy = remedy
        self.status = status


class PediatricGuardianConsent(BaseModel):
    guardian_name: str
    guardian_relationship: str  # Father, Mother, Legal Guardian
    consent_timestamp: str
    is_verified: bool = True
    national_id_last4: Optional[str] = None


class PatientObstetricProfile(BaseModel):
    pregnancy_status: PregnancyStatus = PregnancyStatus.NOT_PREGNANT
    gestational_weeks: Optional[int] = Field(default=None, ge=1, le=44)
    is_lactating: bool = False
    guardian_consent: Optional[PediatricGuardianConsent] = None


class ObstetricCheckResult(BaseModel):
    is_permitted: bool
    contraindication_level: str  # "SAFE", "WARNING_MONITORED", "HARD_BLOCK"
    reason: str
    statutory_warning: Optional[str] = None


class ObstetricSafetyFirewall:
    """
    Deterministic safety firewall guarding obstetric patients and minor children.
    Implements INV-12 (Obstetric Trimester Firewall) and INV-13 (Pediatric Guardian Consent).
    """

    # Classical Abortifacients, Uterine Stimulants, and Violent Emmenagogues
    # Key: Remedy Name Substring -> (banned_statuses, hazard_description)
    RESTRICTED_OBSTETRIC_REMEDIES: Dict[str, Dict[str, Any]] = {
        "sabina": {
            "banned_statuses": [PregnancyStatus.TRIMESTER_1, PregnancyStatus.TRIMESTER_2, PregnancyStatus.TRIMESTER_3],
            "hazard": "Violent pelvic congestion and intense uterine contractions; classical homeopathic abortifacient.",
            "min_safe_potency": "200C_WITH_SPECIALIST_CONSULT"
        },
        "secale cornutum": {
            "banned_statuses": [PregnancyStatus.TRIMESTER_1, PregnancyStatus.TRIMESTER_2, PregnancyStatus.TRIMESTER_3],
            "hazard": "Ergot alkaloids induce prolonged unphysiological uterine tetany and placental infarction.",
            "min_safe_potency": "200C_WITH_SPECIALIST_CONSULT"
        },
        "cantharis": {
            "banned_statuses": [PregnancyStatus.TRIMESTER_1, PregnancyStatus.TRIMESTER_3],
            "hazard": "Cantharidin causes intense pelvic vascular irritation and reflex uterine expulsion.",
            "min_safe_potency": "30C"
        },
        "cimicifuga racemosa": {
            "banned_statuses": [PregnancyStatus.TRIMESTER_1, PregnancyStatus.TRIMESTER_3],
            "hazard": "Estrogenic triterpene glycosides cause reflex uterine cramping and threatened miscarriage.",
            "min_safe_potency": "200C"
        },
        "caulophyllum": {
            "banned_statuses": [PregnancyStatus.TRIMESTER_1],
            "hazard": "Caulosaponin produces powerful cervical softening and uterine tone enhancement (banned in T1).",
            "min_safe_potency": "30C"
        },
        "apis mellifica": {
            "banned_statuses": [PregnancyStatus.TRIMESTER_1],
            "hazard": "Venom peptide melittin causes uterine mucosal irritation and metrorrhagia.",
            "min_safe_potency": "30C"
        },
        "pulsatilla": {
            "banned_statuses": [PregnancyStatus.TRIMESTER_1],
            "hazard": "Strong emmenagogue action in low dilutions can stimulate premature menstrual flow in early pregnancy.",
            "min_safe_potency": "30C"
        }
    }

    @classmethod
    def evaluate_obstetric_safety(
        cls,
        remedy_name: str,
        potency: str,
        profile: PatientObstetricProfile,
        raise_on_block: bool = True
    ) -> ObstetricCheckResult:
        """
        Evaluates whether a prescribed remedy is safe for the patient's gestational status (INV-12).
        """
        if profile.pregnancy_status == PregnancyStatus.NOT_PREGNANT and not profile.is_lactating:
            return ObstetricCheckResult(
                is_permitted=True,
                contraindication_level="SAFE",
                reason="Patient is not pregnant or lactating; standard posology applies."
            )

        rem_lower = remedy_name.strip().lower()

        for key, rule in cls.RESTRICTED_OBSTETRIC_REMEDIES.items():
            if key in rem_lower:
                if profile.pregnancy_status in rule["banned_statuses"]:
                    msg = (
                        f"OBSTETRIC CONTRAINDICATION (INV-12): Remedy '{remedy_name}' is strictly contraindicated "
                        f"during {profile.pregnancy_status.value}. Hazard: {rule['hazard']}"
                    )
                    if raise_on_block:
                        raise ObstetricBlockException(
                            message=msg,
                            remedy=remedy_name,
                            status=profile.pregnancy_status
                        )
                    return ObstetricCheckResult(
                        is_permitted=False,
                        contraindication_level="HARD_BLOCK",
                        reason=msg,
                        statutory_warning="MANDATORY OBSTETRIC SAFETY INTERCEPTION: Abortifacient / emmenagogue risk."
                    )

        return ObstetricCheckResult(
            is_permitted=True,
            contraindication_level="SAFE",
            reason=f"Remedy '{remedy_name}' has no documented abortifacient contraindications for {profile.pregnancy_status.value}."
        )

    @classmethod
    def evaluate_pediatric_consent(
        cls,
        patient_age_years: int,
        consent: Optional[PediatricGuardianConsent]
    ) -> bool:
        """
        Enforces DPDP Act 2023 Section 9: Children (< 18y) require verified guardian consent (INV-13).
        """
        if patient_age_years < 18:
            if consent is None or not consent.is_verified or not consent.guardian_name.strip():
                raise PediatricConsentRequiredException(
                    message=(
                        f"DPDP ACT 2023 SECTION 9 VIOLATION (INV-13): Patient is a minor (age {patient_age_years}). "
                        f"Verifiable parental or legal guardian consent is mandatory before clinical prescribing."
                    ),
                    patient_age=patient_age_years
                )
        return True
