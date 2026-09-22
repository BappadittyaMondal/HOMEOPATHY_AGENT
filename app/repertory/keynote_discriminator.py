"""
Dynamic Triplet Keynote Disambiguation Engine (Phase 67).

Addresses repertorial score clustering where the top 2-3 candidate remedies
fall within a close delta (<= 3.5%). Resolves mathematical ties using
Hahnemannian Characteristic Keynotes (Organon §153) and polar modalities:
Thermal, Thirst, Diurnal Timing, Motion, and Laterality.
"""
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class RemedyCandidateScore(BaseModel):
    remedy_name: str
    score: float
    rubric_count: int = 0
    keynote_bonus: float = 0.0
    final_score: float = 0.0

    def model_post_init(self, __context):
        if self.final_score == 0.0:
            self.final_score = self.score + self.keynote_bonus


class PolarCharacteristic(BaseModel):
    thermal: str  # "CHILLY" or "HOT" or "AMBOTHERMAL"
    thirst: str   # "SIP_FREQUENT", "LARGE_INFREQUENT", "LARGE_COLD", "THIRSTLESS", "UNQUENCHABLE"
    agg_time: str # "MIDNIGHT_1_2AM", "4_TO_8PM", "10_TO_11AM", "3AM", "MORNING_WAKING", "NIGHT"
    motion: str   # "WORSE_SLIGHT_MOTION", "BETTER_CONTINUOUS_MOTION", "BETTER_SLOW_WALKING", "RESTLESS"
    laterality: str # "RIGHT", "LEFT", "BILATERAL"
    peculiar_keynote: str


class DisambiguationQuestion(BaseModel):
    question_id: str
    axis: str
    prompt: str
    remedy_options: Dict[str, str]  # remedy -> option text
    clinical_rationale: str


class DisambiguationResult(BaseModel):
    is_tie_detected: bool
    tie_margin_pct: float
    tied_remedies: List[str]
    discriminating_questions: List[DisambiguationQuestion] = Field(default_factory=list)
    ranked_candidates: List[RemedyCandidateScore] = Field(default_factory=list)
    tie_broken_by: Optional[str] = None


class KeynoteDiscriminatorEngine:
    """
    Evaluates candidate clusters, detects ties (delta <= 3.5%),
    and applies polar keynotes to break ties deterministically.
    """

    TIE_THRESHOLD_PCT: float = 0.035  # 3.5% relative delta

    POLAR_DATABASE: Dict[str, PolarCharacteristic] = {
        "Arsenicum album": PolarCharacteristic(
            thermal="CHILLY",
            thirst="SIP_FREQUENT",
            agg_time="MIDNIGHT_1_2AM",
            motion="RESTLESS",
            laterality="RIGHT",
            peculiar_keynote="Fastidious, profound anxiety, anguish with fear of death, burning pains > heat.",
        ),
        "Sulphur": PolarCharacteristic(
            thermal="HOT",
            thirst="LARGE_COLD",
            agg_time="10_TO_11AM",
            motion="WORSE_STANDING",
            laterality="LEFT",
            peculiar_keynote="Burning heat vertex/soles, kicks off covers at night, hunger at 11 AM, philosophical.",
        ),
        "Phosphorus": PolarCharacteristic(
            thermal="CHILLY",
            thirst="LARGE_COLD",
            agg_time="TWILIGHT",
            motion="WORSE_LYING_LEFT_SIDE",
            laterality="LEFT",
            peculiar_keynote="Desires ice-cold water (vomited as soon as warm in stomach), fear of thunderstorms/dark.",
        ),
        "Lycopodium clavatum": PolarCharacteristic(
            thermal="CHILLY",
            thirst="WARM_DRINKS",
            agg_time="4_TO_8PM",
            motion="BETTER_UNCOVERING",
            laterality="RIGHT",
            peculiar_keynote="Symptoms move right to left, 4-8 PM aggravation, excessive flatulence, craves sweets.",
        ),
        "Bryonia alba": PolarCharacteristic(
            thermal="HOT",
            thirst="LARGE_INFREQUENT",
            agg_time="9PM",
            motion="WORSE_SLIGHT_MOTION",
            laterality="RIGHT",
            peculiar_keynote="Aggravation from the slightest movement, thirst for large quantities at long intervals, > firm pressure.",
        ),
        "Rhus toxicodendron": PolarCharacteristic(
            thermal="CHILLY",
            thirst="SIP_FREQUENT",
            agg_time="MIDNIGHT",
            motion="BETTER_CONTINUOUS_MOTION",
            laterality="LEFT",
            peculiar_keynote="Stiffness on first moving, > continuous gentle motion, < cold damp weather, triangular red tongue tip.",
        ),
        "Pulsatilla pratensis": PolarCharacteristic(
            thermal="HOT",
            thirst="THIRSTLESS",
            agg_time="EVENING",
            motion="BETTER_SLOW_WALKING",
            laterality="RIGHT",
            peculiar_keynote="Thirstless in almost all complaints, weeps easily, seeks open fresh air, changeable symptoms.",
        ),
        "Sepia officinalis": PolarCharacteristic(
            thermal="CHILLY",
            thirst="THIRSTLESS",
            agg_time="MORNING_AND_EVENING",
            motion="BETTER_VIGOROUS_EXERCISE",
            laterality="LEFT",
            peculiar_keynote="Indifference to loved ones, bearing down sensation, brown saddle across nose/cheeks.",
        ),
        "Nux vomica": PolarCharacteristic(
            thermal="CHILLY",
            thirst="THIRSTLESS",
            agg_time="MORNING_WAKING",
            motion="WORSE_COLD_OPEN_AIR",
            laterality="RIGHT",
            peculiar_keynote="Hyper-irritable, ineffectual urging for stool, hypersensitive to noise and light, sedentary habits.",
        ),
        "Natrum muriaticum": PolarCharacteristic(
            thermal="HOT",
            thirst="UNQUENCHABLE",
            agg_time="10_TO_11AM",
            motion="WORSE_HEAT_OF_SUN",
            laterality="LEFT",
            peculiar_keynote="Craves salt, aggravation from consolation, headaches from sunrise to sunset, mapped tongue.",
        ),
    }

    def evaluate_candidates(
        self,
        candidates: List[RemedyCandidateScore],
    ) -> DisambiguationResult:
        """
        Evaluates sorted candidate list.
        If top remedies are separated by <= 3.5%, flags tie condition and returns polar questions.
        """
        if not candidates:
            return DisambiguationResult(is_tie_detected=False, tie_margin_pct=0.0, tied_remedies=[])

        sorted_cands = sorted(candidates, key=lambda c: c.score, reverse=True)
        top = sorted_cands[0]

        tied: List[RemedyCandidateScore] = [top]
        max_margin = 0.0

        for cand in sorted_cands[1:]:
            if top.score > 0:
                margin = (top.score - cand.score) / top.score
                if margin <= self.TIE_THRESHOLD_PCT:
                    tied.append(cand)
                    if margin > max_margin:
                        max_margin = margin
                else:
                    break
            else:
                break

        if len(tied) > 1:
            questions = self._generate_discriminating_questions([c.remedy_name for c in tied])
            return DisambiguationResult(
                is_tie_detected=True,
                tie_margin_pct=round(max_margin * 100, 2),
                tied_remedies=[c.remedy_name for c in tied],
                discriminating_questions=questions,
                ranked_candidates=sorted_cands,
            )

        return DisambiguationResult(
            is_tie_detected=False,
            tie_margin_pct=0.0,
            tied_remedies=[top.remedy_name],
            ranked_candidates=sorted_cands,
        )

    def _generate_discriminating_questions(self, remedy_names: List[str]) -> List[DisambiguationQuestion]:
        """Generates targeted polar questions tailored to the tied remedy subset."""
        questions: List[DisambiguationQuestion] = []
        profiles = {name: self.POLAR_DATABASE.get(name) for name in remedy_names if name in self.POLAR_DATABASE}

        if len(profiles) < 2:
            return questions

        # 1. Thermal question if variance exists
        thermals = {name: p.thermal for name, p in profiles.items() if p}
        if len(set(thermals.values())) > 1:
            opts = {
                name: f"Patient is intensely {'CHILLY (craves warmth/blankets)' if thermals[name] == 'CHILLY' else 'HOT (cannot bear heat/warm room)'}"
                for name in thermals
            }
            questions.append(
                DisambiguationQuestion(
                    question_id="POLAR_THERMAL",
                    axis="THERMAL_REACTION",
                    prompt="What is the patient's primary thermal reactivity?",
                    remedy_options=opts,
                    clinical_rationale="Organon §153: Thermal state is a high-ranking general modality for polychrest differentiation.",
                )
            )

        # 2. Thirst modality question if variance exists
        thirsts = {name: p.thirst for name, p in profiles.items() if p}
        if len(set(thirsts.values())) > 1:
            opts = {
                name: f"Thirst pattern: {thirsts[name].replace('_', ' ').lower()}"
                for name in thirsts
            }
            questions.append(
                DisambiguationQuestion(
                    question_id="POLAR_THIRST",
                    axis="THIRST_PATTERN",
                    prompt="Which description best matches the patient's thirst during illness?",
                    remedy_options=opts,
                    clinical_rationale="Thirst characteristics (sips vs gulps vs thirstless) are classical Kentian discriminators.",
                )
            )

        # 3. Peculiar Kentian keynote
        keynotes = {name: p.peculiar_keynote for name, p in profiles.items() if p}
        questions.append(
            DisambiguationQuestion(
                question_id="PECULIAR_KEYNOTE",
                axis="CHARACTERISTIC_KEYNOTE",
                prompt="Which characteristic keynote symptom is predominantly present in the patient?",
                remedy_options=keynotes,
                clinical_rationale="Aphorism 153: Striking, singular, uncommon, and peculiar signs determine the simillimum.",
            )
        )

        return questions

    def break_tie(
        self,
        candidates: List[RemedyCandidateScore],
        confirmed_modality_remedy: str,
        bonus_pct: float = 0.15,
    ) -> DisambiguationResult:
        """
        Applies polar keynote bonus (+15% default) to the confirmed matching remedy,
        re-evaluates rankings, and breaks the tie.
        """
        updated_candidates: List[RemedyCandidateScore] = []
        for cand in candidates:
            c_copy = cand.model_copy()
            if c_copy.remedy_name == confirmed_modality_remedy:
                c_copy.keynote_bonus = round(c_copy.score * bonus_pct, 3)
            else:
                c_copy.keynote_bonus = 0.0
            c_copy.final_score = round(c_copy.score + c_copy.keynote_bonus, 3)
            updated_candidates.append(c_copy)

        sorted_updated = sorted(updated_candidates, key=lambda c: c.final_score, reverse=True)
        top = sorted_updated[0]
        second = sorted_updated[1] if len(sorted_updated) > 1 else None

        margin_after = ((top.final_score - second.final_score) / top.final_score) if second and top.final_score > 0 else 1.0

        return DisambiguationResult(
            is_tie_detected=(margin_after <= self.TIE_THRESHOLD_PCT),
            tie_margin_pct=round(margin_after * 100, 2),
            tied_remedies=[top.remedy_name],
            ranked_candidates=sorted_updated,
            tie_broken_by=f"Keynote confirmation for {confirmed_modality_remedy} (+{int(bonus_pct*100)}% bonus applied)",
        )
