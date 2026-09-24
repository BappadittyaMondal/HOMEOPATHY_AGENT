"""
Explicit Vitality Mandate & Low-Reserve Safety Engine (Phase 76).

Eliminates silent default fallbacks in chronic constitutional prescribing.
Enforces INV-20: No chronic homeopathic prescription can be drafted or signed
without an explicit, validated PatientVitalityAssessment.
Protects fragile geriatric and multi-morbid patients from high-potency aggravations (Kent Observation 1).
"""
from typing import Optional
from app.models.vitality import PatientVitalityAssessment, ConstitutionTemperamentEnum


class VitalityUnassessedException(Exception):
    """Raised when chronic constitutional prescribing is attempted without explicit vitality evaluation (INV-20)."""
    def __init__(self, message: str, patient_id: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.patient_id = patient_id


class KentObservation1HazardException(Exception):
    """Raised when high centesimal potency is attempted on a patient with depleted vitality (V <= 3.5) and deep pathology."""
    def __init__(self, message: str, vitality_score: float, pathological_depth: int, attempted_potency: str):
        super().__init__(message)
        self.message = message
        self.vitality_score = vitality_score
        self.pathological_depth = pathological_depth
        self.attempted_potency = attempted_potency


class ExplicitVitalityMandateEngine:
    """
    Enforces INV-20 by validating that chronic constitutional cases have explicit,
    clinically scored vitality metrics and protecting depleted patients.
    """

    @classmethod
    def validate_chronic_vitality(
        cls,
        vitality_assessment: Optional[PatientVitalityAssessment],
        is_acute: bool = False,
        patient_id: Optional[str] = None
    ) -> PatientVitalityAssessment:
        """
        Validates that chronic cases have an explicit vitality assessment.
        Raises VitalityUnassessedException if None.
        """
        if is_acute:
            # Acute cases are directed by immediate acute symptom totality (Organon §73)
            # but if vitality is provided, we return it.
            return vitality_assessment or PatientVitalityAssessment(
                susceptibility_score=5.0,
                vital_force_score=5.0,
                pathological_depth=1,
                temperament=ConstitutionTemperamentEnum.SANGUINE_ACTIVE,
                posology_scaling_factor=12.5,
                clinical_recommendation="Acute temporary assessment"
            )

        if vitality_assessment is None:
            raise VitalityUnassessedException(
                f"VITALITY ASSESSMENT MANDATE (INV-20): Chronic constitutional prescribing for patient "
                f"'{patient_id or 'UNKNOWN'}' requires explicit vitality scoring. Silent defaults are strictly prohibited.",
                patient_id=patient_id
            )

        return vitality_assessment

    @classmethod
    def verify_potency_reserve_safety(
        cls,
        vitality: PatientVitalityAssessment,
        potency_str: str
    ):
        """
        Guards against high centesimal potencies (200C, 1M, 10M, 50M, CM) in depleted vitality (V <= 3.5)
        and deep organic structural pathology (depth >= 3).
        """
        is_depleted = vitality.vital_force_score <= 3.5
        is_deep_pathology = vitality.pathological_depth >= 3

        if is_depleted and is_deep_pathology:
            pot_upper = potency_str.upper().strip()
            # High centesimals to reject: 200C, 1M, 10M, 50M, CM, or plain 200, 1000
            high_potency_tokens = ["200C", "1M", "10M", "50M", "CM", "200"]
            if any(token in pot_upper for token in high_potency_tokens):
                raise KentObservation1HazardException(
                    f"KENT OBSERVATION 1 COLLAPSE HAZARD: Patient vital force score {vitality.vital_force_score} <= 3.5 "
                    f"with pathological depth {vitality.pathological_depth} >= 3 cannot tolerate high potency '{potency_str}'. "
                    f"Mandate low decimal (3X, 6X) or 50-Millesimal (LM 0/1) aqueous divided doses.",
                    vitality_score=vitality.vital_force_score,
                    pathological_depth=vitality.pathological_depth,
                    attempted_potency=potency_str
                )
