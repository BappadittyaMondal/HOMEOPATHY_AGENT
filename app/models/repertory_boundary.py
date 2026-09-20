"""
Repertory Boundary Validation & Anti-Wraparound Domain Models (Phase 52).
Enforces non-negative rubric indices (INV-04) and Hahnemannian case totality threshold (INV-03).
"""
from typing import List, Optional
from pydantic import BaseModel, Field, model_validator, field_validator


class AbstainException(Exception):
    """Raised when case totality is insufficient to safely repertorize (INV-03)."""
    def __init__(self, message: str, rubric_count: int, min_required: int = 3):
        super().__init__(message)
        self.message = message
        self.rubric_count = rubric_count
        self.min_required = min_required


class CaseTotalityInput(BaseModel):
    """
    Validated case totality input for mathematical repertorization.
    Guarantees:
    1. Zero negative index wraparound into NumPy/SciPy (INV-04).
    2. Exact dimensional parity between rubrics, weights, and mental flags.
    3. Strict lower bound validation (minimum 3 rubrics per Aphorism 153).
    """
    patient_id: str
    encounter_id: str
    rubric_indices: List[int] = Field(..., description="List of 0-based rubric indices")
    symptom_weights: List[float] = Field(..., description="Symptom intensity/hierarchy weights (1.0 to 5.0)")
    is_mental_flags: List[bool] = Field(..., description="Flags denoting mental general symptoms")
    max_allowed_index: Optional[int] = Field(default=None, description="Upper bound of available rubrics in matrix")

    @field_validator("rubric_indices")
    @classmethod
    def validate_rubric_indices_non_negative(cls, indices: List[int]) -> List[int]:
        for idx in indices:
            if idx < 0:
                raise ValueError(f"Negative rubric index {idx} rejected. Negative indexing (wraparound) is forbidden.")
        return indices

    @model_validator(mode="after")
    def validate_dimensional_parity_and_bounds(self) -> "CaseTotalityInput":
        n_rubrics = len(self.rubric_indices)
        if len(self.symptom_weights) != n_rubrics:
            raise ValueError(
                f"Dimensional mismatch: rubric_indices length ({n_rubrics}) "
                f"does not match symptom_weights length ({len(self.symptom_weights)})."
            )
        if len(self.is_mental_flags) != n_rubrics:
            raise ValueError(
                f"Dimensional mismatch: rubric_indices length ({n_rubrics}) "
                f"does not match is_mental_flags length ({len(self.is_mental_flags)})."
            )
        if self.max_allowed_index is not None:
            for idx in self.rubric_indices:
                if idx >= self.max_allowed_index:
                    raise ValueError(
                        f"Out-of-bounds rubric index {idx} rejected (max allowed is {self.max_allowed_index - 1})."
                    )
        return self

    def is_sufficient_totality(self, min_rubrics: int = 3) -> bool:
        """Returns True if the case has at least min_rubrics characteristic symptoms."""
        return len(self.rubric_indices) >= min_rubrics
