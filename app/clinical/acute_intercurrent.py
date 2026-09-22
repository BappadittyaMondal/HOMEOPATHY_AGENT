"""
Acute-on-Chronic Case Segregation State Machine (Phase 66 - INV-18).

Enforces Samuel Hahnemann's Organon of Medicine (§38–40, §73) and Kent's principles:
When an acute intercurrent condition (trauma, acute epidemic, acute poisoning/flare)
strikes a chronic patient, the chronic constitutional case must be SHELVED.
Mixing acute and chronic rubrics in the same totality vector is strictly prohibited,
as it corrupts the simillimum calculation (INV-18).
"""
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from pydantic import BaseModel, Field


class ChronicCaseState(str, Enum):
    ACTIVE = "ACTIVE"
    SHELVED = "SHELVED"
    RE_EVALUATION_PENDING = "RE_EVALUATION_PENDING"
    CLOSED = "CLOSED"


class AcuteCaseState(str, Enum):
    ACTIVE = "ACTIVE"
    RESOLVED = "RESOLVED"
    ESCALATED_EMERGENCY = "ESCALATED_EMERGENCY"


class RubricCategory(str, Enum):
    CHRONIC_CONSTITUTIONAL = "CHRONIC_CONSTITUTIONAL"
    ACUTE_INTERCURRENT = "ACUTE_INTERCURRENT"
    ACUTE_TRAUMA = "ACUTE_TRAUMA"
    EPIDEMIC = "EPIDEMIC"


class AcuteChronicContaminationException(Exception):
    """Raised when an attempt is made to contaminate chronic totality with acute rubrics or vice versa (INV-18)."""
    def __init__(self, message: str, contaminated_rubrics: List[str], target_context: str):
        super().__init__(message)
        self.message = message
        self.contaminated_rubrics = contaminated_rubrics
        self.target_context = target_context


class RubricItem(BaseModel):
    rubric_id: str
    description: str
    category: RubricCategory
    weight: float = Field(default=1.0, ge=0.1, le=5.0)


class ChronicCaseRecord(BaseModel):
    case_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str
    state: ChronicCaseState = ChronicCaseState.ACTIVE
    constitutional_rubrics: List[RubricItem] = Field(default_factory=list)
    active_remedy: Optional[str] = None
    potency: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    shelved_at: Optional[str] = None
    shelve_reason: Optional[str] = None
    last_resumed_at: Optional[str] = None


class AcuteCaseRecord(BaseModel):
    acute_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str
    chronic_case_id: Optional[str] = None
    state: AcuteCaseState = AcuteCaseState.ACTIVE
    presenting_complaint: str
    acute_rubrics: List[RubricItem] = Field(default_factory=list)
    acute_remedy: Optional[str] = None
    acute_potency: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    resolved_at: Optional[str] = None
    resolution_summary: Optional[str] = None


class AcuteIntercurrentEngine:
    """
    Manages acute-on-chronic segregation and prevents cross-contamination (INV-18).
    Maintains in-memory clinical state per patient with strict transactional isolation.
    """
    def __init__(self):
        self._chronic_cases: Dict[str, ChronicCaseRecord] = {}  # keyed by patient_id
        self._acute_cases: Dict[str, List[AcuteCaseRecord]] = {}  # keyed by patient_id

    def register_chronic_case(
        self,
        patient_id: str,
        rubrics: List[RubricItem],
        active_remedy: Optional[str] = None,
        potency: Optional[str] = None,
    ) -> ChronicCaseRecord:
        """Registers or initializes an active chronic constitutional case."""
        # Enforce INV-18 purity
        self.validate_rubric_purity(RubricCategory.CHRONIC_CONSTITUTIONAL, rubrics)

        record = ChronicCaseRecord(
            patient_id=patient_id,
            state=ChronicCaseState.ACTIVE,
            constitutional_rubrics=rubrics,
            active_remedy=active_remedy,
            potency=potency,
        )
        self._chronic_cases[patient_id] = record
        return record

    def validate_rubric_purity(self, expected_context: RubricCategory, rubrics: List[RubricItem]) -> None:
        """
        Validates that rubrics belong strictly to the expected clinical context.
        Raises AcuteChronicContaminationException on contamination (INV-18).
        """
        contaminated: List[str] = []
        if expected_context == RubricCategory.CHRONIC_CONSTITUTIONAL:
            for r in rubrics:
                if r.category in (RubricCategory.ACUTE_INTERCURRENT, RubricCategory.ACUTE_TRAUMA, RubricCategory.EPIDEMIC):
                    contaminated.append(f"{r.rubric_id} ({r.category.value})")
            if contaminated:
                raise AcuteChronicContaminationException(
                    message=f"INV-18 VIOLATION: Cannot mix acute intercurrent/trauma rubrics into chronic constitutional totality: {contaminated}",
                    contaminated_rubrics=contaminated,
                    target_context="CHRONIC_CONSTITUTIONAL",
                )
        else:
            # Acute context expects acute/trauma/epidemic rubrics
            for r in rubrics:
                if r.category == RubricCategory.CHRONIC_CONSTITUTIONAL:
                    contaminated.append(f"{r.rubric_id} ({r.category.value})")
            if contaminated:
                raise AcuteChronicContaminationException(
                    message=f"INV-18 VIOLATION: Cannot mix chronic constitutional rubrics into acute intercurrent totality: {contaminated}",
                    contaminated_rubrics=contaminated,
                    target_context="ACUTE_INTERCURRENT",
                )

    def open_acute_intercurrent(
        self,
        patient_id: str,
        presenting_complaint: str,
        acute_rubrics: List[RubricItem],
        acute_remedy: Optional[str] = None,
        acute_potency: Optional[str] = None,
    ) -> Tuple[AcuteCaseRecord, Optional[ChronicCaseRecord]]:
        """
        Opens an acute intercurrent case.
        If an active chronic case exists, it is automatically SHELVED to prevent totality contamination.
        """
        # Validate acute rubric purity
        self.validate_rubric_purity(RubricCategory.ACUTE_INTERCURRENT, acute_rubrics)

        chronic_case = self._chronic_cases.get(patient_id)
        chronic_id = None
        if chronic_case:
            chronic_case.state = ChronicCaseState.SHELVED
            chronic_case.shelved_at = datetime.now(timezone.utc).isoformat()
            chronic_case.shelve_reason = f"Acute intercurrent onset: {presenting_complaint}"
            chronic_id = chronic_case.case_id

        acute_record = AcuteCaseRecord(
            patient_id=patient_id,
            chronic_case_id=chronic_id,
            state=AcuteCaseState.ACTIVE,
            presenting_complaint=presenting_complaint,
            acute_rubrics=acute_rubrics,
            acute_remedy=acute_remedy,
            acute_potency=acute_potency,
        )

        if patient_id not in self._acute_cases:
            self._acute_cases[patient_id] = []
        self._acute_cases[patient_id].append(acute_record)

        return acute_record, chronic_case

    def resolve_acute_intercurrent(
        self,
        patient_id: str,
        resolution_summary: str,
    ) -> Tuple[AcuteCaseRecord, Optional[ChronicCaseRecord]]:
        """
        Marks active acute intercurrent case as RESOLVED.
        Transitions the shelved chronic case to RE_EVALUATION_PENDING per Hahnemannian rules.
        """
        acute_list = self._acute_cases.get(patient_id, [])
        active_acute = next((a for a in reversed(acute_list) if a.state == AcuteCaseState.ACTIVE), None)
        if not active_acute:
            raise ValueError(f"No active acute intercurrent case found for patient '{patient_id}'.")

        active_acute.state = AcuteCaseState.RESOLVED
        active_acute.resolved_at = datetime.now(timezone.utc).isoformat()
        active_acute.resolution_summary = resolution_summary

        chronic_case = self._chronic_cases.get(patient_id)
        if chronic_case and chronic_case.state == ChronicCaseState.SHELVED:
            chronic_case.state = ChronicCaseState.RE_EVALUATION_PENDING

        return active_acute, chronic_case

    def resume_chronic_case(
        self,
        patient_id: str,
        updated_rubrics: Optional[List[RubricItem]] = None,
        active_remedy: Optional[str] = None,
        potency: Optional[str] = None,
    ) -> ChronicCaseRecord:
        """
        Resumes the chronic constitutional case after post-acute re-evaluation.
        Enforces that updated rubrics remain strictly constitutional (INV-18).
        """
        chronic_case = self._chronic_cases.get(patient_id)
        if not chronic_case:
            raise ValueError(f"No chronic case on record for patient '{patient_id}'.")

        # Check if an active acute case is still unresolved
        active_acute = next((a for a in self._acute_cases.get(patient_id, []) if a.state == AcuteCaseState.ACTIVE), None)
        if active_acute:
            raise ValueError(
                f"Cannot resume chronic case while acute intercurrent '{active_acute.acute_id}' is still ACTIVE."
            )

        if updated_rubrics:
            self.validate_rubric_purity(RubricCategory.CHRONIC_CONSTITUTIONAL, updated_rubrics)
            chronic_case.constitutional_rubrics = updated_rubrics

        if active_remedy:
            chronic_case.active_remedy = active_remedy
        if potency:
            chronic_case.potency = potency

        chronic_case.state = ChronicCaseState.ACTIVE
        chronic_case.last_resumed_at = datetime.now(timezone.utc).isoformat()
        return chronic_case

    def get_patient_case_status(self, patient_id: str) -> Dict[str, Any]:
        """Returns the current clinical state of the patient's cases."""
        chronic = self._chronic_cases.get(patient_id)
        acutes = self._acute_cases.get(patient_id, [])
        active_acute = next((a for a in reversed(acutes) if a.state == AcuteCaseState.ACTIVE), None)

        return {
            "patient_id": patient_id,
            "chronic_state": chronic.state.value if chronic else None,
            "chronic_remedy": chronic.active_remedy if chronic else None,
            "has_active_acute": active_acute is not None,
            "active_acute_id": active_acute.acute_id if active_acute else None,
            "active_acute_complaint": active_acute.presenting_complaint if active_acute else None,
            "active_acute_remedy": active_acute.acute_remedy if active_acute else None,
            "total_historical_acutes": len(acutes),
        }
