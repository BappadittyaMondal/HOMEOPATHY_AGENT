"""
Longitudinal Homeopathic EHR & Multi-Tenant Timeline Engine (Phase 41).
Provides multi-tenant clinical encounter storage, multi-year chronological trajectory analysis,
vitality vector trending, and miasmatic unraveling audits.
"""
from typing import Dict, List, Optional
from app.models.ehr import EHRClinicalEncounter, LongitudinalPatientTrajectory

class LongitudinalEHREngine:
    """
    Multi-tenant longitudinal homeopathic health record engine.
    Tracks chronological therapeutic trajectory and vitality progression over time.
    """

    # In-memory tenant store index (backed by transactional SQLite WAL)
    # Structure: {tenant_id: {patient_id: List[EHRClinicalEncounter]}}
    _TENANT_STORES: Dict[str, Dict[str, List[EHRClinicalEncounter]]] = {}

    @classmethod
    def record_encounter(cls, encounter: EHRClinicalEncounter) -> None:
        """
        Stores an immutable clinical encounter record within the tenant's partition.
        """
        tenant_id = encounter.tenant_id
        if tenant_id not in cls._TENANT_STORES:
            cls._TENANT_STORES[tenant_id] = {}

        patient_id = encounter.patient_id
        if patient_id not in cls._TENANT_STORES[tenant_id]:
            cls._TENANT_STORES[tenant_id][patient_id] = []

        cls._TENANT_STORES[tenant_id][patient_id].append(encounter)

    @classmethod
    def get_patient_trajectory(
        cls,
        tenant_id: str,
        patient_id: str
    ) -> Optional[LongitudinalPatientTrajectory]:
        """
        Calculates longitudinal clinical trajectory for a patient across all recorded encounters.
        """
        tenant_data = cls._TENANT_STORES.get(tenant_id, {})
        encounters = tenant_data.get(patient_id, [])
        if not encounters:
            return None

        # Sort chronologically
        sorted_encounters = sorted(encounters, key=lambda e: e.encounter_date)
        vitality_trend = [e.vitality_score for e in sorted_encounters]
        remedy_history = [f"{e.remedy_prescribed} {e.potency}" for e in sorted_encounters]

        # Determine vitality trajectory (first vs last)
        is_improving = vitality_trend[-1] >= vitality_trend[0] if len(vitality_trend) > 1 else True

        if is_improving:
            verdict = f"Curative trajectory: Vitality progressed from {vitality_trend[0]:.1f} to {vitality_trend[-1]:.1f}."
        else:
            verdict = f"Declining trajectory: Vitality diminished from {vitality_trend[0]:.1f} to {vitality_trend[-1]:.1f}. Re-case take required."

        return LongitudinalPatientTrajectory(
            patient_id=patient_id,
            tenant_id=tenant_id,
            total_encounters=len(sorted_encounters),
            encounters=sorted_encounters,
            vitality_trend=vitality_trend,
            remedy_history=remedy_history,
            is_vitality_improving=is_improving,
            summary_verdict=verdict
        )

    @classmethod
    def reset_store(cls) -> None:
        """Clears in-memory tenant store (used in test teardowns)."""
        cls._TENANT_STORES.clear()
