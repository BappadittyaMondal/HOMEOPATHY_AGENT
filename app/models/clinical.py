"""
Clinical Specialties, Hospital Operations & Organ Therapeutics Domain Contracts (Milestone 4).
Codifies models for Genius Epidemicus (Ph 26), Pediatrics (Ph 27), Geriatrics (Ph 28),
Female Health (Ph 29), Neuro-Psychiatric (Ph 30), Dermatology & Anti-Suppression (Ph 31),
Respiratory (Ph 32), Gastrointestinal (Ph 33), Musculoskeletal (Ph 34),
Cardiovascular (Ph 35), Urological (Ph 36), and Neurological/Cephalic (Ph 37).
"""
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

# --- Phase 26: Genius Epidemicus ---
class EpidemicCase(BaseModel):
    case_id: str
    patient_id: str
    symptoms: List[str]
    onset_date: str

class GeniusEpidemicusResult(BaseModel):
    total_cases_analyzed: int
    common_symptom_core: List[str]
    primary_remedy: str
    secondary_remedy: Optional[str] = None
    concordance_percentage: float
    aphorism_basis: str = "Organon Aphorisms 100-102: Discovery of the Genius Epidemicus through collective totality"

# --- Phase 27: Pediatrics ---
class PediatricConstitution(BaseModel):
    age_months: int
    weight_kg: float
    fontanelles_closed: bool
    dentition_delayed: bool
    sweat_pattern: str  # e.g., "HEAD_DURING_SLEEP", "SOUR_SMELL", "NORMAL"
    temperament: str    # e.g., "OBSTINATE_TIRED", "TIMID_FEARFUL", "IRRITABLE_WANTS_TO_BE_CARRIED"
    thermals: str       # "CHILLY", "HOT", "AMBITHERMAL"

class PediatricDoseAdvice(BaseModel):
    indicated_remedy: str
    recommended_potency: str
    administration_vehicle: str  # "AQUEOUS_DROPLET", "SUGAR_GLOBULE_DISSOLVED"
    posology_instructions: str

# --- Phase 28: Geriatrics ---
class GeriatricAssessment(BaseModel):
    age_years: int
    vitality_score: float = Field(..., ge=1.0, le=10.0)
    organ_pathology_depth: int = Field(..., ge=0, le=5)
    arteriosclerotic_degeneration: bool = False
    cardiorenal_compromise: bool = False

class GeriatricPrescriptionPlan(BaseModel):
    indicated_remedy: str
    recommended_potency: str
    posology_strategy: str  # "LOW_DECIMAL_ORGAN_SUPPORT", "50_MILLESIMAL_MINIMAL", "HIGH_POTENCY_CONTRAINDICATED"
    safety_warning: str

# --- Phase 29: Female Reproductive Health ---
class MenstrualModalityProfile(BaseModel):
    cycle_length_days: int
    flow_nature: str     # "SCANTY", "PROFUSE_METRORRHAGIC", "DARK_CLOTTED", "ACRID"
    flow_timing: str     # "DELAYED_SUPPRESSED", "TOO_EARLY", "REGULAR"
    modality_with_flow: str  # "BETTER_WHEN_FLOW_FLOWS", "PAIN_PROPORTIONAL_TO_FLOW", "WANDERING"
    concomitants: List[str]

class FemaleHealthPrescription(BaseModel):
    indicated_remedy: str
    recommended_potency: str
    clinical_focus: str
    key_concordance: str

# --- Phase 30: Mental Health & Neuro-Psychiatric ---
class PsychiatricEtiologyProfile(BaseModel):
    primary_etiology: str  # "SILENT_GRIEF", "MORTIFICATION_SUPPRESSED_ANGER", "FRIGHT_SUDDEN_TERROR", "DISAPPOINTMENT"
    mood_state: str        # "WEEPING_CONSOLATION_AGGRAVATES", "WEEPING_CONSOLATION_AMELIORATES", "DEEP_MELANCHOLY_SUICIDAL", "HYSTERICAL_PARADOX"
    somatic_concomitants: List[str]

class MentalHealthPrescription(BaseModel):
    indicated_remedy: str
    recommended_potency: str
    aphorism_basis: str = "Organon Aphorisms 210-230: Mental diseases as altered somatic totalities"
    clinical_guidance: str

# --- Phase 31: Dermatology & Anti-Suppression ---
class DermatologicalLesion(BaseModel):
    lesion_type: str     # "VESICULAR_MOIST", "DRY_SCALY_CRACKED", "PUSTULAR_CRUSTED", "PRURITIC_BURNING"
    topical_suppression_history: bool = False  # e.g., topical corticosteroids applied
    thermal_modality: str  # "WORSE_HEAT_OF_BED", "WORSE_COLD_AIR", "WORSE_WASHING"
    discharge_nature: str  # "HONEY_LIKE_STICKY", "WATERY_BURNING", "NONE"

class SkinSuppressionEvaluation(BaseModel):
    indicated_remedy: str
    recommended_potency: str
    is_suppression_danger: bool
    warning: str

# --- Phase 32: Respiratory ---
class RespiratoryProfile(BaseModel):
    condition_category: str  # "BRONCHIAL_ASTHMA", "ALLERGIC_RHINITIS", "PNEUMONIA"
    time_aggravation: str    # "1_AM_TO_2_AM", "2_AM_TO_5_AM", "EVENING_TWILIGHT", "SLIGHTEST_MOTION"
    postural_modality: str   # "MUST_SIT_BENT_FORWARD", "CANNOT_LIE_DOWN", "BETTER_LYING_ON_AFFECTED_SIDE"
    weather_modality: str    # "COLD_DAMP_FOGGY", "DRY_COLD_WIND", "WARM_ROOM"

class RespiratoryPrescription(BaseModel):
    indicated_remedy: str
    recommended_potency: str
    clinical_sphere: str

# --- Phase 33: Gastrointestinal & Hepatobiliary ---
class GastrointestinalProfile(BaseModel):
    dyspepsia_type: str     # "POSTPRANDIAL_BLOATING_IMMEDIATE", "ACID_PYROSIS_SOUR_ERUCTATION", "HEPATIC_CONGESTION"
    time_modality: str      # "4_PM_TO_8_PM", "MORNING_AFTER_STIMULANTS", "MIDNIGHT"
    stool_character: str    # "INEFFECTUAL_CONSTANT_URGING", "SHEEP_DUNG_HARD", "DIARRHEA_DRIVES_OUT_OF_BED_5AM"
    food_modalities: List[str]

class GastrointestinalPrescription(BaseModel):
    indicated_remedy: str
    recommended_potency: str
    clinical_focus: str

# --- Phase 34: Musculoskeletal & Rheumatic ---
class MusculoskeletalModality(BaseModel):
    motion_modality: str    # "WORSE_FIRST_MOTION_BETTER_CONTINUED", "WORSE_ANY_SLIGHTEST_MOTION", "RESTLESS_MUST_MOVE"
    temperature_modality: str # "BETTER_COLD_APPLICATIONS", "BETTER_HOT_HEAT", "WORSE_COLD_DAMP"
    tissue_involved: str    # "PERIOSTEUM_TENDONS", "SYNOVIAL_JOINTS", "FIBROUS_MUSCLES"

class RheumaticPrescription(BaseModel):
    indicated_remedy: str
    recommended_potency: str
    tissue_affinity: str

# --- Phase 35: Cardiovascular & Peripheral Vascular ---
class CardiovascularProfile(BaseModel):
    symptom_syndrome: str   # "CARDIAC_HYPERTROPHY_DEBILITY", "CONSTRICTION_IRON_BAND", "EXTREME_VENOUS_STASIS", "ARRHYTHMIC_BRADYCARDIA"
    pulse_character: str    # "SLOW_IRREGULAR", "RAPID_HARD_FULL", "THREADY_WEAK"
    chest_concomitants: List[str]

class CardiovascularPrescription(BaseModel):
    indicated_remedy: str
    recommended_potency: str
    statutory_safety_caution: str

# --- Phase 36: Urological & Nephrolithiasis ---
class UrologicalProfile(BaseModel):
    urinary_pain_timing: str # "BEFORE_MICTURITION", "DURING_BURNING_DROP_BY_DROP", "AT_CLOSE_OF_URINATION"
    pain_radiation: str      # "KIDNEY_DOWN_URETER_TO_THIGH", "BLADDER_NECK_SPASM", "LOCALIZED_LUMBAR"
    sediment_nature: str     # "RED_SAND_URIC_ACID", "WHITE_SAND_MUCUS", "BLOOD_CLOTS"

class RenalPrescription(BaseModel):
    indicated_remedy: str
    recommended_potency: str
    affinity: str

# --- Phase 37: Neurological & Cephalic Topography ---
class CephalicTopographyProfile(BaseModel):
    laterality: str         # "LEFT_SIDED", "RIGHT_SIDED", "OCCIPUT_TO_VERTEX", "VERTEX_BURNING"
    pain_pathway: str       # "OCCIPUT_OVER_VERTEX_SETTLING_RIGHT_EYE", "LEFT_SUPRAORBITAL_TO_OCCIPUT", "NAPE_ASCENDING_UPWARDS"
    associated_symptom: str # "PTOSIS_HEAVY_EYELIDS_RELIEVED_PROFUSE_URINATION", "BLINDNESS_PRECEDING_HEADACHE", "THROBBING_CAROTIDS"

class NeurologicalPrescription(BaseModel):
    indicated_remedy: str
    recommended_potency: str
    cephalic_affinity: str
