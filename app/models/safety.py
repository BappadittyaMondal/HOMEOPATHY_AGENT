"""
Clinical Safety, Toxicology, Materia Medica & Follow-up State Machine Domain Contracts (Milestone 3).
Codifies HPI Monographs, 20-Point Q Limits, 26-Point Inimical Matrix, Kent's 12 Observations,
Hering's Law, Second Prescription, Nosodes, and Bowel Nosodes.
"""
from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

# --- Phase 17: HPI Monograph ---
class KingdomEnum(str, Enum):
    VEGETABLE = "VEGETABLE"
    MINERAL = "MINERAL"
    ANIMAL = "ANIMAL"
    NOSODE = "NOSODE"
    SARCODE = "SARCODE"
    IMPONDERABILIA = "IMPONDERABILIA"

class HPIMonograph(BaseModel):
    remedy_name: str
    abbreviation: str
    botanical_chemical_name: str
    kingdom: KingdomEnum
    hpi_volume: int
    minimum_allowed_potency: str  # e.g., "6X", "3C", "Q"
    is_schedule_e1_toxic: bool = False
    active_alkaloids: List[str] = Field(default_factory=list)
    storage_precautions: str = "Store below 25C, protected from light and strong aromatic odors."

# --- Phase 18: Classical Materia Medica ---
class MateriaMedicaEntry(BaseModel):
    remedy_name: str
    guiding_symptoms: List[str]
    mind_keynotes: List[str]
    sphere_of_action: List[str]
    key_modalities_agg: List[str]
    key_modalities_amel: List[str]
    authorities_cited: List[str]  # e.g., ["Hahnemann", "Kent", "Boericke", "Clarke", "Allen"]

# --- Phase 19: Toxicology Limits ---
class ToxicitySafetyStatus(str, Enum):
    APPROVED = "APPROVED"
    WARNING_OVERRIDABLE = "WARNING_OVERRIDABLE"
    HARD_BLOCKED = "HARD_BLOCKED"

class MotherTinctureToxicityRule(BaseModel):
    remedy_name: str
    toxic_constituent: str
    max_daily_dose_ml: float
    banned_below_potency: str
    clinical_hazard: str

class ToxicologyCheckResult(BaseModel):
    remedy_name: str
    requested_potency: str
    requested_daily_dose_ml: float
    status: ToxicitySafetyStatus
    rule_matched: Optional[MotherTinctureToxicityRule] = None
    reason: str
    statutory_reference: str

# --- Phase 20: Inimical Matrix ---
class InimicalRule(BaseModel):
    remedy_a: str
    remedy_b: str
    washout_days: int
    pathogenetic_hazard: str

class InimicalEvaluation(BaseModel):
    candidate_remedy: str
    prior_remedy: str
    days_since_prior: int
    status: ToxicitySafetyStatus
    is_acute_override: bool = False
    hazard_description: str
    clinical_advice: str

# --- Phase 21: Kent's 12 Observations ---
class KentObservationIndex(int, Enum):
    OBSERVATION_1 = 1   # Prolonged aggravation, final decline (Incurable, vitality exhausted)
    OBSERVATION_2 = 2   # Long aggravation, slow gradual recovery (Borderland, deep tissue change)
    OBSERVATION_3 = 3   # Aggravation quick, short, strong, rapid lasting cure (Ideal simillimum)
    OBSERVATION_4 = 4   # Recovery without aggravation (Pure functional or exact match without gross pathology)
    OBSERVATION_5 = 5   # Amelioration first, aggravation later (Superficial remedy or incurable state)
    OBSERVATION_6 = 6   # Too short relief (Structural obstruction or miasmatic barrier)
    OBSERVATION_7 = 7   # Full amelioration but patient systemically worse (Incurable organic destruction)
    OBSERVATION_8 = 8   # Patient proves every remedy (Hypersensitive idiosyncrasy)
    OBSERVATION_9 = 9   # Action of medicine on provers (Drug proving state)
    OBSERVATION_10 = 10 # New symptoms appear (Wrong remedy)
    OBSERVATION_11 = 11 # Old symptoms reappear in reverse order (Hering's Law verified)
    OBSERVATION_12 = 12 # Symptoms move center to periphery, top down (Hering's Law verified)

class FollowUpObservationTelemetry(BaseModel):
    aggravation_occurred: bool
    aggravation_duration_days: int
    aggravation_severity: str  # "MILD", "MODERATE", "SEVERE_VIOLENT"
    general_vitality_improved: bool
    chief_complaint_ameliorated: bool
    new_symptoms_appeared: bool
    old_symptoms_returned: bool
    days_since_prescription: int
    symptoms_take_wrong_direction: bool = False
    amelioration_preceded_aggravation: bool = False
    relief_duration_days: Optional[int] = None
    proves_every_remedy: bool = False
    proving_trial_mode: bool = False

class KentObservationEvaluation(BaseModel):
    observation_number: KentObservationIndex
    title: str
    prognosis: str
    underlying_pathophysiology: str
    action_required: str  # e.g., "SAC_LAC_WAIT", "ANTIDOTE_IMMEDIATELY", "RE_CASE_TAKE"

# --- Phase 22: Hering's Law Directionality ---
class HeringsLawVector(BaseModel):
    head_to_extremities: bool = False     # From above downwards
    inside_to_outside: bool = False       # From more vital internal organ to less vital surface/skin
    center_to_periphery: bool = False     # From trunk/center to fingers/toes
    reverse_chronological_order: bool = False # Oldest symptoms leave last; newest leave first
    concordance_score: int = Field(..., ge=0, le=4)
    is_true_cure: bool
    iatrogenic_suppression_detected: bool
    clinical_verdict: str

# --- Phase 23: Second Prescription ---
class SecondPrescriptionAction(str, Enum):
    SAC_LAC_PLACEBO = "SAC_LAC_PLACEBO"
    WAIT_AND_WATCH = "WAIT_AND_WATCH"
    REPEAT_SAME_POTENCY = "REPEAT_SAME_POTENCY"
    POTENCY_JUMP = "POTENCY_JUMP"             # e.g. 30C -> 200C
    CHANGE_OF_REMEDY = "CHANGE_OF_REMEDY"
    ADMINISTER_ANTIDOTE = "ADMINISTER_ANTIDOTE"
    INTERCURRENT_NOSODE = "INTERCURRENT_NOSODE"

class SecondPrescriptionDecision(BaseModel):
    action: SecondPrescriptionAction
    recommended_potency: Optional[str] = None
    recommended_remedy: Optional[str] = None
    rationale: str
    aphorism_basis: str

# --- Phase 24: Nosodes & Sarcodes ---
class NosodePrescribingRule(BaseModel):
    nosode_name: str
    miasmatic_clearance: str
    acute_contraindication: bool = True  # Strictly contraindicated during acute fever/crisis
    min_interval_weeks: int = 12
    indication_notes: str

# --- Phase 25: Bowel Nosodes ---
class BowelNosodeProfile(BaseModel):
    nosode_name: str
    bach_paterson_group: str
    related_non_bowel_remedies: List[str]
    dysbiosis_symptoms: List[str]
    repeat_lockout_months: int = 3
