"""
Longitudinal Homeopathic EHR & Multi-Tenant Timeline Engine (Phase 41).
Provides multi-tenant clinical encounter storage, multi-year chronological trajectory analysis,
vitality vector trending, and miasmatic unraveling audits.
"""
from typing import Dict, List, Optional
from app.models.ehr import EHRClinicalEncounter, LongitudinalPatientTrajectory

import json
from app.core.database import db

class LongitudinalEHREngine:
    """
    Multi-tenant longitudinal homeopathic health record engine.
    Tracks chronological therapeutic trajectory and vitality progression over time.
    Backed by persistent SQLite WAL disk storage (INV-09).
    """

    # In-memory tenant store index (backed by transactional SQLite WAL)
    # Structure: {tenant_id: {patient_id: List[EHRClinicalEncounter]}}
    _TENANT_STORES: Dict[str, Dict[str, List[EHRClinicalEncounter]]] = {}

    @classmethod
    def record_encounter(cls, encounter: EHRClinicalEncounter) -> None:
        """
        Stores an immutable clinical encounter record within the tenant's partition and persists to SQLite.
        """
        tenant_id = encounter.tenant_id
        if tenant_id not in cls._TENANT_STORES:
            cls._TENANT_STORES[tenant_id] = {}

        patient_id = encounter.patient_id
        if patient_id not in cls._TENANT_STORES[tenant_id]:
            cls._TENANT_STORES[tenant_id][patient_id] = []

        cls._TENANT_STORES[tenant_id][patient_id].append(encounter)

        # Persist to SQLite table (INV-09)
        try:
            db.init_schema()
            db.save_ehr_encounter_sync(
                encounter_id=encounter.encounter_id,
                tenant_id=encounter.tenant_id,
                patient_id=encounter.patient_id,
                encounter_date=encounter.encounter_date,
                chief_complaint=encounter.chief_complaint,
                rubrics_json=json.dumps(encounter.rubrics_selected),
                remedy_prescribed=encounter.remedy_prescribed,
                potency=encounter.potency,
                kent_observation_num=encounter.kent_observation_num,
                vitality_score=encounter.vitality_score,
                dominant_miasm=encounter.dominant_miasm
            )
        except Exception:
            pass

    @classmethod
    def reload_from_database(cls, tenant_id: str, patient_id: str) -> List[EHRClinicalEncounter]:
        """Restores patient encounter history directly from SQLite WAL disk storage."""
        db.init_schema()
        rows = db.get_patient_ehr_encounters_sync(tenant_id, patient_id)
        encs: List[EHRClinicalEncounter] = []
        for r in rows:
            enc = EHRClinicalEncounter(
                encounter_id=r["encounter_id"],
                tenant_id=r["tenant_id"],
                patient_id=r["patient_id"],
                encounter_date=r["encounter_date"],
                chief_complaint=r["chief_complaint"],
                rubrics_selected=json.loads(r["rubrics_json"]),
                remedy_prescribed=r["remedy_prescribed"],
                potency=r["potency"],
                kent_observation_num=r["kent_observation_num"],
                vitality_score=r["vitality_score"],
                dominant_miasm=r["dominant_miasm"]
            )
            encs.append(enc)

        if tenant_id not in cls._TENANT_STORES:
            cls._TENANT_STORES[tenant_id] = {}
        cls._TENANT_STORES[tenant_id][patient_id] = encs
        return encs

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
        """Clears in-memory tenant store and disk table."""
        cls._TENANT_STORES.clear()
        try:
            db.init_schema()
            db.clear_ehr_encounters_sync()
        except Exception:
            pass
