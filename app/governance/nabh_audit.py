"""
NABH Homoeopathy 2nd Edition Digital Quality & Audit Log System (Phase 44).
Implements a tamper-evident, cryptographically chained (hash-linked) append-only audit ledger
for continuous quality improvement and patient safety compliance under NABH Homoeopathy Standards.
"""
import hashlib
import json
from typing import Dict, List, Optional
from pydantic import BaseModel

class NABHAuditEntry(BaseModel):
    log_id: str
    timestamp: str
    actor_id: str
    action_type: str  # e.g., "PRESCRIPTION_ISSUED", "INIMICAL_OVERRIDE", "EMERGENCY_LOCKOUT", "DATA_ACCESS"
    patient_id: Optional[str] = None
    details: Dict[str, str]
    previous_hash: str
    current_hash: str

class NABHAuditLedger:
    """
    Cryptographically chained immutable audit logger for NABH Homoeopathy 2nd Edition compliance.
    """

    _CHAIN: List[NABHAuditEntry] = []
    _GENESIS_HASH: str = "0000000000000000000000000000000000000000000000000000000000000000"

    @classmethod
    def append_log(
        cls,
        log_id: str,
        timestamp: str,
        actor_id: str,
        action_type: str,
        details: Dict[str, str],
        patient_id: Optional[str] = None
    ) -> NABHAuditEntry:
        """
        Appends an entry to the hash-linked audit chain.
        """
        prev_hash = cls._CHAIN[-1].current_hash if cls._CHAIN else cls._GENESIS_HASH

        payload = f"{log_id}|{timestamp}|{actor_id}|{action_type}|{patient_id}|{json.dumps(details, sort_keys=True)}|{prev_hash}"
        curr_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

        entry = NABHAuditEntry(
            log_id=log_id,
            timestamp=timestamp,
            actor_id=actor_id,
            action_type=action_type,
            patient_id=patient_id,
            details=details,
            previous_hash=prev_hash,
            current_hash=curr_hash
        )
        cls._CHAIN.append(entry)
        return entry

    @classmethod
    def verify_chain_integrity(cls) -> bool:
        """
        Validates the entire audit ledger from genesis to tip to detect any unauthorized tampering.
        """
        if not cls._CHAIN:
            return True

        for i, entry in enumerate(cls._CHAIN):
            expected_prev = cls._CHAIN[i - 1].current_hash if i > 0 else cls._GENESIS_HASH
            if entry.previous_hash != expected_prev:
                return False

            payload = (
                f"{entry.log_id}|{entry.timestamp}|{entry.actor_id}|{entry.action_type}|"
                f"{entry.patient_id}|{json.dumps(entry.details, sort_keys=True)}|{entry.previous_hash}"
            )
            recalculated = hashlib.sha256(payload.encode("utf-8")).hexdigest()
            if recalculated != entry.current_hash:
                return False

        return True

    @classmethod
    def get_logs_for_patient(cls, patient_id: str) -> List[NABHAuditEntry]:
        """Retrieves audit trail specific to a patient ID."""
        return [e for e in cls._CHAIN if e.patient_id == patient_id]

    @classmethod
    def get_chain(cls) -> List[NABHAuditEntry]:
        """Retrieves the full cryptographic audit chain."""
        return list(cls._CHAIN)

    @classmethod
    def reset_chain(cls) -> None:
        """Resets the audit ledger (used in test fixtures)."""
        cls._CHAIN.clear()
